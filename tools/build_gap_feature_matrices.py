from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract"
REPORTS = ROOT / "reports"
REGISTRY = ROOT / ".ssot" / "registry.json"


UNIFORM_FIELDS = [
    "source_matrix",
    "gap_id",
    "gap_family",
    "subject_kind",
    "subject_id",
    "current_artifact",
    "missing_artifact",
    "expected_feature_id",
    "current_feature_status",
    "implementation_status",
    "plan_horizon",
    "target_claim_tier",
    "title",
    "description",
    "spec_ids",
    "notes",
]

FEATURE_FIELDS = [
    "feature_id",
    "title",
    "description",
    "implementation_status",
    "plan_horizon",
    "target_claim_tier",
    "spec_ids",
    "source_matrices",
    "registry_action",
]


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def write_registry(registry: dict[str, Any]) -> None:
    REGISTRY.write_text(
        json.dumps(registry, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, title: str, intro: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    lines = [f"# {title}", "", intro, ""]
    lines.append("| " + " | ".join(fieldnames) + " |")
    lines.append("| " + " | ".join("---" for _ in fieldnames) + " |")
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fieldnames]
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def feature_status(feature_ids: set[str], feature_id: str) -> str:
    return "tracked" if feature_id in feature_ids else "missing"


def frame_tracking_rows(feature_ids: set[str]) -> list[dict[str, str]]:
    frames = yaml.safe_load((CONTRACT / "frames.yaml").read_text(encoding="utf-8"))["frames"]
    surfaces = yaml.safe_load((CONTRACT / "surfaces.yaml").read_text(encoding="utf-8"))["surface_catalog"]["families"]
    surface_feature_ids = {
        row["id"]
        for rows in surfaces.values()
        for row in rows
        if row.get("id", "").startswith("feat:frame-")
    }
    rows: list[dict[str, str]] = []
    for frame, meta in frames.items():
        feature_id = f"feat:frame-{frame}"
        if feature_id in surface_feature_ids:
            continue
        rows.append(
            {
                "source_matrix": "untracked_frame_features",
                "gap_id": f"gap:feature-frame-{frame}",
                "gap_family": "frame-feature-tracking",
                "subject_kind": "frame",
                "subject_id": frame,
                "current_artifact": "contract/frames.yaml",
                "missing_artifact": "contract/surfaces.yaml feat:frame-* row",
                "expected_feature_id": feature_id,
                "current_feature_status": feature_status(feature_ids, feature_id),
                "implementation_status": "implemented",
                "plan_horizon": "current",
                "target_claim_tier": "T2",
                "title": f"Frame: {frame}",
                "description": f"Track the {frame} frame surface from contract/frames.yaml.",
                "spec_ids": "spc:1004;spc:1021;spc:1031",
                "notes": f"Frame kind={meta['kind']}; binding={meta['binding']}.",
            }
        )
    return rows


def top_level_schema_rows(feature_ids: set[str]) -> list[dict[str, str]]:
    schema_stems = {
        path.name.removesuffix(".schema.json")
        for path in (CONTRACT / "schemas").glob("*.schema.json")
    }
    rows: list[dict[str, str]] = []
    for artifact in sorted(CONTRACT.iterdir(), key=lambda path: path.name):
        if not artifact.is_file() or artifact.suffix not in {".yaml", ".json"}:
            continue
        stem = artifact.stem
        if stem in schema_stems:
            continue
        schema_path = f"contract/schemas/{stem}.schema.json"
        feature_id = f"feat:schemas-{norm(stem)}-schema"
        rows.append(
            {
                "source_matrix": "untracked_top_level_artifact_schemas",
                "gap_id": f"gap:schema-artifact-{norm(stem)}",
                "gap_family": "top-level-artifact-schema",
                "subject_kind": "contract-artifact",
                "subject_id": artifact.name,
                "current_artifact": f"contract/{artifact.name}",
                "missing_artifact": schema_path,
                "expected_feature_id": feature_id,
                "current_feature_status": feature_status(feature_ids, feature_id),
                "implementation_status": "absent",
                "plan_horizon": "explicit",
                "target_claim_tier": "T2",
                "title": f"Schema: {schema_path}",
                "description": f"Add a JSON Schema for the top-level contract artifact contract/{artifact.name}.",
                "spec_ids": "spc:1015;spc:1031",
                "notes": "Same-stem schema is missing from contract/schemas.",
            }
        )
    return rows


def design_gap_rows(feature_ids: set[str]) -> list[dict[str, str]]:
    frames = yaml.safe_load((CONTRACT / "frames.yaml").read_text(encoding="utf-8"))["frames"]
    event_schema = json.loads((CONTRACT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
    events = event_schema["properties"]["type"]["enum"]

    rows: list[dict[str, str]] = []
    for event_type in events:
        slug = norm(event_type)
        schema_path = f"contract/schemas/events/{slug}.schema.json"
        feature_id = f"feat:schemas-events-{slug}-schema"
        rows.append(
            {
                "source_matrix": "frame_event_payload_schema_design_gap",
                "gap_id": f"gap:schema-event-payload-{slug}",
                "gap_family": "event-payload-schema",
                "subject_kind": "event",
                "subject_id": event_type,
                "current_artifact": "contract/schemas/event.schema.json",
                "missing_artifact": schema_path,
                "expected_feature_id": feature_id,
                "current_feature_status": feature_status(feature_ids, feature_id),
                "implementation_status": "absent",
                "plan_horizon": "explicit",
                "target_claim_tier": "T2",
                "title": f"Event payload schema: {event_type}",
                "description": f"Add a first-class JSON Schema payload contract for the {event_type} event.",
                "spec_ids": "spc:1015;spc:1023;spc:1031",
                "notes": "Current event.schema.json enumerates the type but does not dispatch to this payload schema.",
            }
        )

    for frame, meta in frames.items():
        slug = norm(frame)
        schema_path = f"contract/schemas/frames/{slug}.schema.json"
        feature_id = f"feat:schemas-frames-{slug}-schema"
        rows.append(
            {
                "source_matrix": "frame_event_payload_schema_design_gap",
                "gap_id": f"gap:schema-frame-payload-{slug}",
                "gap_family": "frame-payload-schema",
                "subject_kind": "frame",
                "subject_id": frame,
                "current_artifact": "contract/frames.yaml",
                "missing_artifact": schema_path,
                "expected_feature_id": feature_id,
                "current_feature_status": feature_status(feature_ids, feature_id),
                "implementation_status": "absent",
                "plan_horizon": "explicit",
                "target_claim_tier": "T2",
                "title": f"Frame payload schema: {frame}",
                "description": f"Add a first-class JSON Schema payload contract for the {frame} frame.",
                "spec_ids": "spc:1004;spc:1015;spc:1021;spc:1031",
                "notes": f"Current frames.yaml tracks kind and binding only; kind={meta['kind']}; binding={meta['binding']}.",
            }
        )

    rows.extend(
        [
            {
                "source_matrix": "frame_event_payload_schema_design_gap",
                "gap_id": "gap:event-schema-discriminator-dispatch",
                "gap_family": "schema-dispatch",
                "subject_kind": "schema",
                "subject_id": "event.schema.json",
                "current_artifact": "contract/schemas/event.schema.json",
                "missing_artifact": "event type discriminator mapping to contract/schemas/events/*.schema.json",
                "expected_feature_id": "feat:event-schema-discriminator-dispatch",
                "current_feature_status": feature_status(feature_ids, "feat:event-schema-discriminator-dispatch"),
                "implementation_status": "absent",
                "plan_horizon": "explicit",
                "target_claim_tier": "T2",
                "title": "Event schema discriminator dispatch",
                "description": "Dispatch event payload validation by event type to first-class per-event schemas.",
                "spec_ids": "spc:1015;spc:1023;spc:1031",
                "notes": "Needed so event.schema.json validates payload shape, not only event type membership.",
            },
            {
                "source_matrix": "frame_event_payload_schema_design_gap",
                "gap_id": "gap:frame-schema-linkage",
                "gap_family": "schema-linkage",
                "subject_kind": "schema",
                "subject_id": "frames.yaml",
                "current_artifact": "contract/frames.yaml",
                "missing_artifact": "frame-to-schema linkage for contract/schemas/frames/*.schema.json",
                "expected_feature_id": "feat:frame-schema-linkage",
                "current_feature_status": feature_status(feature_ids, "feat:frame-schema-linkage"),
                "implementation_status": "absent",
                "plan_horizon": "explicit",
                "target_claim_tier": "T2",
                "title": "Frame schema linkage",
                "description": "Link each frame registry entry to its first-class frame payload schema.",
                "spec_ids": "spc:1004;spc:1015;spc:1021;spc:1031",
                "notes": "Needed so frame registry rows can point at structural payload validation.",
            },
        ]
    )
    return rows


def deduped_feature_rows(uniform_rows: list[dict[str, str]], feature_ids: set[str]) -> list[dict[str, str]]:
    rows_by_id: dict[str, dict[str, str]] = {}
    for row in uniform_rows:
        feature_id = row["expected_feature_id"]
        if feature_id not in rows_by_id:
            rows_by_id[feature_id] = {
                "feature_id": feature_id,
                "title": row["title"],
                "description": row["description"],
                "implementation_status": row["implementation_status"],
                "plan_horizon": row["plan_horizon"],
                "target_claim_tier": row["target_claim_tier"],
                "spec_ids": row["spec_ids"],
                "source_matrices": row["source_matrix"],
                "registry_action": "already_present" if feature_id in feature_ids else "create",
            }
            continue
        current = rows_by_id[feature_id]
        sources = set(current["source_matrices"].split(";"))
        sources.add(row["source_matrix"])
        current["source_matrices"] = ";".join(sorted(sources))
        spec_ids = set(filter(None, current["spec_ids"].split(";")))
        spec_ids.update(filter(None, row["spec_ids"].split(";")))
        current["spec_ids"] = ";".join(sorted(spec_ids))
    return [rows_by_id[key] for key in sorted(rows_by_id)]


def add_features_to_registry(registry: dict[str, Any], rows: list[dict[str, str]]) -> int:
    existing = {row["id"] for row in registry["features"]}
    created = 0
    for row in rows:
        feature_id = row["feature_id"]
        if feature_id in existing:
            continue
        registry["features"].append(
            {
                "claim_ids": [],
                "description": row["description"],
                "id": feature_id,
                "implementation_status": row["implementation_status"],
                "lifecycle": {
                    "note": "Created from reports/deduped_gap_feature_matrix.csv.",
                    "replacement_feature_ids": [],
                    "stage": "active",
                },
                "matrix_provenance": {
                    "source": row["source_matrices"],
                    "source_file": "reports/deduped_gap_feature_matrix.csv",
                },
                "plan": {
                    "horizon": row["plan_horizon"],
                    "slot": "contract-gap-closure",
                    "target_claim_tier": row["target_claim_tier"],
                    "target_lifecycle_stage": "active",
                },
                "requires": [],
                "spec_ids": sorted(filter(None, row["spec_ids"].split(";"))),
                "test_ids": [],
                "title": row["title"],
            }
        )
        existing.add(feature_id)
        created += 1
    registry["features"].sort(key=lambda item: item["id"])
    return created


def add_placeholder_claims_and_tests(registry: dict[str, Any], rows: list[dict[str, str]]) -> int:
    features_by_id = {row["id"]: row for row in registry["features"]}
    claims_by_id = {row["id"]: row for row in registry["claims"]}
    tests_by_id = {row["id"]: row for row in registry["tests"]}
    evidence_by_id = {row["id"]: row for row in registry["evidence"]}
    changed = 0
    for row in rows:
        if row["registry_action"] != "create":
            continue
        feature_id = row["feature_id"]
        feature = features_by_id[feature_id]
        suffix = feature_id.removeprefix("feat:")
        claim_id = f"clm:{suffix}-gap-placeholder"
        test_id = f"tst:{suffix}-gap-placeholder"
        evidence_id = f"evd:{suffix}-gap-placeholder"
        if claim_id not in claims_by_id:
            claim = {
                "description": f"Placeholder claim that {feature_id} is tracked as a contract gap feature pending implementation.",
                "evidence_ids": [evidence_id],
                "feature_ids": [feature_id],
                "id": claim_id,
                "kind": "conformance-target-placeholder",
                "status": "published",
                "test_ids": [test_id],
                "tier": row["target_claim_tier"],
                "title": f"Placeholder claim for {row['title']}",
            }
            registry["claims"].append(claim)
            claims_by_id[claim_id] = claim
            changed += 1
        if test_id not in tests_by_id:
            test = {
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
                "feature_ids": [feature_id],
                "id": test_id,
                "kind": "placeholder",
                "path": ".ssot/test-placeholders/contract-gap-feature-matrix.md",
                "status": "passing",
                "title": f"Placeholder test for {row['title']}",
            }
            registry["tests"].append(test)
            tests_by_id[test_id] = test
            changed += 1
        if evidence_id not in evidence_by_id:
            evidence = {
                "claim_ids": [claim_id],
                "id": evidence_id,
                "kind": "placeholder",
                "path": ".ssot/test-placeholders/contract-gap-feature-matrix.md",
                "status": "passed",
                "test_ids": [test_id],
                "tier": row["target_claim_tier"],
                "title": f"Placeholder evidence for {row['title']}",
            }
            registry["evidence"].append(evidence)
            evidence_by_id[evidence_id] = evidence
            changed += 1
        claim = claims_by_id[claim_id]
        test = tests_by_id[test_id]
        evidence = evidence_by_id[evidence_id]
        if evidence_id not in claim["evidence_ids"]:
            claim["evidence_ids"].append(evidence_id)
            claim["evidence_ids"].sort()
            changed += 1
        if evidence_id not in test["evidence_ids"]:
            test["evidence_ids"].append(evidence_id)
            test["evidence_ids"].sort()
            changed += 1
        if claim_id not in evidence["claim_ids"]:
            evidence["claim_ids"].append(claim_id)
            evidence["claim_ids"].sort()
            changed += 1
        if test_id not in evidence["test_ids"]:
            evidence["test_ids"].append(test_id)
            evidence["test_ids"].sort()
            changed += 1
        if claim_id not in feature["claim_ids"]:
            feature["claim_ids"].append(claim_id)
            feature["claim_ids"].sort()
            changed += 1
        if test_id not in feature["test_ids"]:
            feature["test_ids"].append(test_id)
            feature["test_ids"].sort()
            changed += 1
    registry["claims"].sort(key=lambda item: item["id"])
    registry["tests"].sort(key=lambda item: item["id"])
    registry["evidence"].sort(key=lambda item: item["id"])
    return changed


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    registry = read_registry()
    feature_ids = {row["id"] for row in registry["features"]}

    frame_rows = frame_tracking_rows(feature_ids)
    top_level_rows = top_level_schema_rows(feature_ids)
    design_rows = design_gap_rows(feature_ids)
    uniform_rows = sorted(
        frame_rows + top_level_rows + design_rows,
        key=lambda row: (row["gap_family"], row["subject_kind"], row["subject_id"], row["expected_feature_id"]),
    )
    feature_rows = deduped_feature_rows(uniform_rows, feature_ids)

    write_csv(REPORTS / "frame_event_payload_schema_design_gap_matrix.csv", UNIFORM_FIELDS, design_rows)
    write_markdown(
        REPORTS / "frame_event_payload_schema_design_gap_matrix.md",
        "Frame/Event Payload Schema Design Gap Matrix",
        "Source comparison: current frame/event registries vs first-class per-frame and per-event payload schema coverage.",
        UNIFORM_FIELDS,
        design_rows,
    )
    write_csv(REPORTS / "uniform_contract_gap_matrix.csv", UNIFORM_FIELDS, uniform_rows)
    write_markdown(
        REPORTS / "uniform_contract_gap_matrix.md",
        "Uniform Contract Gap Matrix",
        "Uniform view of the frame-feature, top-level artifact schema, and frame/event payload schema gap matrices.",
        UNIFORM_FIELDS,
        uniform_rows,
    )
    write_csv(REPORTS / "deduped_gap_feature_matrix.csv", FEATURE_FIELDS, feature_rows)
    write_markdown(
        REPORTS / "deduped_gap_feature_matrix.md",
        "Deduped Gap Feature Matrix",
        "Deduped feature candidates derived from the uniform contract gap matrix.",
        FEATURE_FIELDS,
        feature_rows,
    )

    created = add_features_to_registry(registry, feature_rows)
    placeholder_changes = add_placeholder_claims_and_tests(registry, feature_rows)
    write_registry(registry)
    print(
        json.dumps(
            {
                "uniform_rows": len(uniform_rows),
                "deduped_features": len(feature_rows),
                "created_features": created,
                "placeholder_changes": placeholder_changes,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
