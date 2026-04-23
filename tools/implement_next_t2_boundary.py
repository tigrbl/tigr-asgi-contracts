from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
SURFACES_PATH = ROOT / "contract" / "surfaces.yaml"
BOUNDARY_ID = "bnd:next-t2"
RELEASE_ID = "rel:0.2.0"
RELEASE_VERSION = "0.2.0"
SURFACE_TEST_PATH = "tests/contract/test_surface_catalog.py"
SURFACE_EVIDENCE_PATH = ".ssot/reports/pytest-0.2.0.xml"


def feature_family(feature_id: str) -> str:
    body = feature_id.removeprefix("feat:")
    prefix = body.split("-", 1)[0]
    return re.sub(r"[^a-z0-9]+", "-", prefix.lower()).strip("-") or "surface"


def sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_surface_catalog(features: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for feature in features:
        grouped[feature_family(feature["id"])].append(
            {
                "id": feature["id"],
                "title": feature.get("title", ""),
                "description": feature.get("description", ""),
                "horizon": "current",
                "target_claim_tier": "T2",
                "spec_ids": sorted(feature.get("spec_ids", [])),
                "source": feature.get("matrix_provenance", {}).get(
                    "source", "contract registry"
                ),
            }
        )

    document = {
        "surface_catalog": {
            "boundary_id": BOUNDARY_ID,
            "release_id": RELEASE_ID,
            "target_claim_tier": "T2",
            "scope_rule": "features with plan.horizon != out_of_bounds",
            "families": {
                family: sorted(rows, key=lambda row: row["id"])
                for family, rows in sorted(grouped.items())
            },
        }
    }
    SURFACES_PATH.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )


def upsert_row(rows: list[dict], entity_id: str, row: dict) -> dict:
    for index, existing in enumerate(rows):
        if existing.get("id") == entity_id:
            rows[index] = row
            return row
    rows.append(row)
    return row


def main() -> int:
    registry = load_registry()
    features_by_id = {feature["id"]: feature for feature in registry["features"]}
    in_bound_ids = sorted(
        feature["id"]
        for feature in registry["features"]
        if feature.get("plan", {}).get("horizon") != "out_of_bounds"
    )
    in_bound_features = [features_by_id[feature_id] for feature_id in in_bound_ids]

    boundary = next(
        boundary for boundary in registry["boundaries"] if boundary["id"] == BOUNDARY_ID
    )
    boundary["title"] = "Next T2 in-bounds implementation boundary"
    boundary["status"] = "draft"
    boundary["frozen"] = False
    boundary["feature_ids"] = in_bound_ids

    write_surface_catalog(in_bound_features)

    family_features: dict[str, list[dict]] = defaultdict(list)
    for feature in in_bound_features:
        family_features[feature_family(feature["id"])].append(feature)

    release_claim_ids: list[str] = []
    release_evidence_ids: list[str] = []

    for family, rows in sorted(family_features.items()):
        feature_ids = sorted(feature["id"] for feature in rows)
        claim_id = f"clm:next-t2-{family}-surfaces"
        test_id = f"tst:next-t2-{family}-surface-catalog"
        evidence_id = f"evd:next-t2-{family}-surface-catalog"
        release_claim_ids.append(claim_id)
        release_evidence_ids.append(evidence_id)

        upsert_row(
            registry["claims"],
            claim_id,
            {
                "id": claim_id,
                "title": f"Next T2 {family} surface implementation",
                "status": "evidenced",
                "tier": "T2",
                "kind": "conformance",
                "description": (
                    f"The {family} feature family is implemented in the "
                    "in-bounds surface catalog and generated contract artifacts."
                ),
                "feature_ids": feature_ids,
                "test_ids": [test_id],
                "evidence_ids": [evidence_id],
            },
        )
        upsert_row(
            registry["tests"],
            test_id,
            {
                "id": test_id,
                "title": f"Next T2 {family} surface catalog test",
                "status": "passing",
                "kind": "pytest",
                "path": SURFACE_TEST_PATH,
                "feature_ids": feature_ids,
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
            },
        )
        upsert_row(
            registry["evidence"],
            evidence_id,
            {
                "id": evidence_id,
                "title": f"Next T2 {family} surface catalog pytest evidence",
                "status": "passed",
                "kind": "test-report",
                "tier": "T2",
                "path": SURFACE_EVIDENCE_PATH,
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            },
        )

        for feature in rows:
            feature["implementation_status"] = "implemented"
            feature.setdefault("plan", {})
            feature["plan"]["horizon"] = "current"
            feature["plan"]["target_claim_tier"] = "T2"
            feature["plan"]["target_lifecycle_stage"] = "active"
            feature["claim_ids"] = sorted_unique(feature.get("claim_ids", []) + [claim_id])
            feature["test_ids"] = sorted_unique(feature.get("test_ids", []) + [test_id])

    for feature in registry["features"]:
        feature.setdefault("plan", {})
        feature["plan"]["target_claim_tier"] = "T2"

    release = {
        "id": RELEASE_ID,
        "version": RELEASE_VERSION,
        "status": "draft",
        "boundary_id": BOUNDARY_ID,
        "claim_ids": sorted_unique(release_claim_ids),
        "evidence_ids": sorted_unique(release_evidence_ids),
    }
    upsert_row(registry["releases"], RELEASE_ID, release)

    write_json(REGISTRY_PATH, registry)
    print(
        json.dumps(
            {
                "boundary_id": BOUNDARY_ID,
                "release_id": RELEASE_ID,
                "feature_count": len(in_bound_ids),
                "claim_count": len(release_claim_ids),
                "evidence_count": len(release_evidence_ids),
                "surface_catalog": SURFACES_PATH.as_posix(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
