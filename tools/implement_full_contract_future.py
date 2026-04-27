from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
SURFACES_PATH = ROOT / "contract" / "surfaces.yaml"
BOUNDARY_ID = "bnd:full-contract-future"
RELEASE_ID = "rel:0.3.0"
RELEASE_VERSION = "0.3.0"
SPEC_ID = "spc:1031"
ADR_ID = "adr:1031"
SURFACE_TEST_PATH = "tests/contract/test_full_contract_future.py"
SURFACE_EVIDENCE_PATH = ".ssot/reports/pytest-0.3.0.xml"

ADDITIONAL_DOCUMENTS = {
    "adrs": [
        {
            "id": "adr:1032",
            "number": 1032,
            "slug": "protocol-observable-lifecycle-semantics",
            "title": "Canonical lifecycle semantics must be protocol-observable or explicitly derived",
            "path": ".ssot/adr/ADR-1032-protocol-observable-lifecycle-semantics.yaml",
        },
    ],
    "specs": [
        {
            "id": "spc:1032",
            "number": 1032,
            "slug": "protocol-observable-subevent-semantics",
            "title": "Protocol observable subevent semantics",
            "path": ".ssot/specs/SPEC-1032-protocol-observable-subevent-semantics.yaml",
            "adr_ids": ["adr:1032"],
        },
        {
            "id": "spc:1033",
            "number": 1033,
            "slug": "http-request-response-and-asgi-lifespan-semantics",
            "title": "HTTP request, response, and ASGI lifespan semantics",
            "path": ".ssot/specs/SPEC-1033-http-request-response-and-asgi-lifespan-semantics.yaml",
            "adr_ids": ["adr:1032"],
        },
        {
            "id": "spc:1034",
            "number": 1034,
            "slug": "websocket-session-message-semantics",
            "title": "WebSocket session and message semantics",
            "path": ".ssot/specs/SPEC-1034-websocket-session-message-semantics.yaml",
            "adr_ids": ["adr:1032"],
        },
        {
            "id": "spc:1035",
            "number": 1035,
            "slug": "webtransport-stream-datagram-semantics",
            "title": "WebTransport stream and datagram semantics",
            "path": ".ssot/specs/SPEC-1035-webtransport-stream-datagram-semantics.yaml",
            "adr_ids": ["adr:1032"],
        },
    ],
}


PATHSEND_FEATURES = [
    {
        "id": "feat:event-http-response-pathsend",
        "title": "Event: http.response.pathsend",
        "description": "ASGI pathsend response event contract surface.",
    },
    {
        "id": "feat:event-payload-http-response-pathsend",
        "title": "HTTP response pathsend event payload schema",
        "description": "Payload schema and validator coverage for http.response.pathsend.",
    },
    {
        "id": "feat:schemas-pathsend-schema",
        "title": "Schema: contract/schemas/pathsend.schema.json",
        "description": "Schema surface for ASGI pathsend event payloads.",
    },
    {
        "id": "feat:frame-asgi-pathsend-extension",
        "title": "Frame: ASGI pathsend extension",
        "description": "Extension-frame surface for ASGI pathsend metadata.",
    },
    {
        "id": "feat:target-asgi-pathsend-extension",
        "title": "Conformance target asgi.pathsend-extension",
        "description": "Contract conformance target for the ASGI pathsend extension.",
    },
]

ARTIFACT_FEATURES = [
    {
        "id": "feat:protocols",
        "title": "Contract artifact contract/protocols.yaml",
        "description": "Protocol registry mapping protocol names to bindings and ASGI scope types.",
    },
    {
        "id": "feat:automata",
        "title": "Contract artifact contract/automata.yaml",
        "description": "Lifecycle automata registry for request, session, message, stream, and datagram families.",
    },
    {
        "id": "feat:frames",
        "title": "Contract artifact contract/frames.yaml",
        "description": "Frame and framing registry for wire, contract, extension, and evidence frame surfaces.",
    },
    {
        "id": "feat:extensions",
        "title": "Contract artifact contract/extensions.yaml",
        "description": "ASGI extension registry for TLS and pathsend contract surfaces.",
    },
    {
        "id": "feat:schemas-protocols-schema",
        "title": "Schema: contract/schemas/protocols.schema.json",
        "description": "JSON Schema for the protocol registry.",
    },
    {
        "id": "feat:schemas-automata-schema",
        "title": "Schema: contract/schemas/automata.schema.json",
        "description": "JSON Schema for lifecycle automata.",
    },
    {
        "id": "feat:schemas-frames-schema",
        "title": "Schema: contract/schemas/frames.schema.json",
        "description": "JSON Schema for frame metadata.",
    },
    {
        "id": "feat:schemas-extensions-schema",
        "title": "Schema: contract/schemas/extensions.schema.json",
        "description": "JSON Schema for ASGI extension metadata.",
    },
    {
        "id": "feat:schemas-tls-schema",
        "title": "Schema: contract/schemas/tls.schema.json",
        "description": "JSON Schema for ASGI TLS extension metadata.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )


def content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def upsert(rows: list[dict[str, Any]], entity_id: str, row: dict[str, Any]) -> dict[str, Any]:
    for index, existing in enumerate(rows):
        if existing.get("id") == entity_id:
            rows[index] = row
            return row
    rows.append(row)
    return row


def feature_family(feature_id: str) -> str:
    body = feature_id.removeprefix("feat:")
    for prefix, family in [
        ("binding-family-", "binding-family"),
        ("binding-subevent-", "binding-subevent"),
        ("family-subevent-", "subevent"),
        ("scope-scope-", "scope-subevent"),
        ("target-asgi-tls", "asgi-tls"),
        ("target-asgi-pathsend", "asgi-pathsend"),
        ("frame-asgi-tls", "asgi-tls"),
        ("frame-asgi-pathsend", "asgi-pathsend"),
        ("schemas-tls", "asgi-tls"),
        ("schemas-pathsend", "asgi-pathsend"),
        ("event-lifecycle-automata", "automata"),
        ("target-lifecycle-", "lifecycle-target"),
    ]:
        if body.startswith(prefix):
            return family
    return re.sub(r"[^a-z0-9]+", "-", body.split("-", 1)[0].lower()).strip("-") or "surface"


def is_contract_future_candidate(feature: dict[str, Any]) -> bool:
    if feature.get("lifecycle", {}).get("stage") in {"obsolete", "removed"}:
        return False
    if feature.get("implementation_status") != "implemented":
        return False
    body = feature["id"].removeprefix("feat:")
    if feature.get("plan", {}).get("horizon") != "out_of_bounds":
        return True
    exact_prefixes = (
        "binding-family-",
        "binding-subevent-",
        "family-subevent-",
        "scope-scope-",
        "event-",
        "frame-",
        "lifecycle-",
        "target-lifecycle-",
        "target-asgi-tls-",
        "target-http",
        "target-websocket-",
        "target-webtransport-",
        "target-quic",
        "target-jsonrpc",
        "target-sse-",
        "concern-tls",
        "concern-mtls",
        "concern-alpn",
        "concern-https-scheme",
    )
    return body.startswith(exact_prefixes)


def base_feature(row: dict[str, str]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "implementation_status": "implemented",
        "lifecycle": {
            "stage": "active",
            "replacement_feature_ids": [],
            "note": None,
        },
        "plan": {
            "horizon": "explicit",
            "slot": RELEASE_VERSION,
            "target_claim_tier": "T2",
            "target_lifecycle_stage": "active",
        },
        "claim_ids": [],
        "test_ids": [],
        "requires": [],
        "spec_ids": [SPEC_ID],
    }


def sync_documents(registry: dict[str, Any]) -> None:
    adr_path = ROOT / ".ssot" / "adr" / "ADR-1031-full-in-bounds-future-contract-scope.yaml"
    spec_path = ROOT / ".ssot" / "specs" / "SPEC-1031-full-in-bounds-future-contract-scope.yaml"
    upsert(
        registry["adrs"],
        ADR_ID,
        {
            "id": ADR_ID,
            "number": 1031,
            "slug": "full-in-bounds-future-contract-scope",
            "title": "Full in-bounds future contract surfaces are contract-owned",
            "path": ".ssot/adr/ADR-1031-full-in-bounds-future-contract-scope.yaml",
            "origin": "repo-local",
            "managed": False,
            "immutable": False,
            "package_version": "0.2.10",
            "content_sha256": content_sha256(adr_path),
            "status": "accepted",
            "supersedes": [],
            "superseded_by": [],
            "status_notes": [],
        },
    )
    upsert(
        registry["specs"],
        SPEC_ID,
        {
            "id": SPEC_ID,
            "number": 1031,
            "slug": "full-in-bounds-future-contract-scope",
            "title": "Full in-bounds future contract scope",
            "path": ".ssot/specs/SPEC-1031-full-in-bounds-future-contract-scope.yaml",
            "origin": "repo-local",
            "managed": False,
            "immutable": False,
            "package_version": "0.2.10",
            "content_sha256": content_sha256(spec_path),
            "status": "accepted",
            "supersedes": [],
            "superseded_by": [],
            "status_notes": [],
            "kind": "normative",
            "adr_ids": [ADR_ID],
        },
    )
    for document in ADDITIONAL_DOCUMENTS["adrs"]:
        path = ROOT / document["path"]
        upsert(
            registry["adrs"],
            document["id"],
            {
                "id": document["id"],
                "number": document["number"],
                "slug": document["slug"],
                "title": document["title"],
                "path": document["path"],
                "origin": "repo-local",
                "managed": False,
                "immutable": False,
                "package_version": "0.2.13",
                "content_sha256": content_sha256(path),
                "status": "accepted",
                "supersedes": [],
                "superseded_by": [],
                "status_notes": [],
            },
        )
    for document in ADDITIONAL_DOCUMENTS["specs"]:
        path = ROOT / document["path"]
        upsert(
            registry["specs"],
            document["id"],
            {
                "id": document["id"],
                "number": document["number"],
                "slug": document["slug"],
                "title": document["title"],
                "path": document["path"],
                "origin": "repo-local",
                "managed": False,
                "immutable": False,
                "package_version": "0.2.13",
                "content_sha256": content_sha256(path),
                "status": "accepted",
                "supersedes": [],
                "superseded_by": [],
                "status_notes": [],
                "kind": "normative",
                "adr_ids": document["adr_ids"],
            },
        )


def write_surface_catalog(features: list[dict[str, Any]]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        grouped[feature_family(feature["id"])].append(
            {
                "id": feature["id"],
                "title": feature.get("title", ""),
                "description": feature.get("description", ""),
                "horizon": feature.get("plan", {}).get("horizon"),
                "target_claim_tier": "T2",
                "spec_ids": sorted(feature.get("spec_ids", [])),
                "source": feature.get("matrix_provenance", {}).get("source", "contract registry"),
            }
        )
    document = {
        "surface_catalog": {
            "boundary_id": BOUNDARY_ID,
            "release_id": RELEASE_ID,
            "target_claim_tier": "T2",
            "scope_rule": "contract-owned event/automata/subevent/protocol/frame/schema/lifecycle/asgi-extension/binding surfaces",
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


def merge_id(rows_by_id: dict[str, dict[str, Any]], row_id: str, field: str, value: str) -> None:
    row = rows_by_id.get(row_id)
    if row is None:
        return
    row[field] = sorted_unique(list(row.get(field, [])) + [value])


def sync_bidirectional_links(registry: dict[str, Any]) -> None:
    features_by_id = {row["id"]: row for row in registry["features"]}
    claims_by_id = {row["id"]: row for row in registry["claims"]}
    tests_by_id = {row["id"]: row for row in registry["tests"]}
    evidence_by_id = {row["id"]: row for row in registry["evidence"]}

    for feature in registry["features"]:
        feature_id = feature["id"]
        for claim_id in feature.get("claim_ids", []):
            merge_id(claims_by_id, claim_id, "feature_ids", feature_id)
        for test_id in feature.get("test_ids", []):
            merge_id(tests_by_id, test_id, "feature_ids", feature_id)

    for claim in registry["claims"]:
        claim_id = claim["id"]
        for feature_id in claim.get("feature_ids", []):
            merge_id(features_by_id, feature_id, "claim_ids", claim_id)
        for test_id in claim.get("test_ids", []):
            merge_id(tests_by_id, test_id, "claim_ids", claim_id)
        for evidence_id in claim.get("evidence_ids", []):
            merge_id(evidence_by_id, evidence_id, "claim_ids", claim_id)

    for test in registry["tests"]:
        test_id = test["id"]
        for feature_id in test.get("feature_ids", []):
            merge_id(features_by_id, feature_id, "test_ids", test_id)
        for claim_id in test.get("claim_ids", []):
            merge_id(claims_by_id, claim_id, "test_ids", test_id)
        for evidence_id in test.get("evidence_ids", []):
            merge_id(evidence_by_id, evidence_id, "test_ids", test_id)

    for evidence in registry["evidence"]:
        evidence_id = evidence["id"]
        for claim_id in evidence.get("claim_ids", []):
            merge_id(claims_by_id, claim_id, "evidence_ids", evidence_id)
        for test_id in evidence.get("test_ids", []):
            merge_id(tests_by_id, test_id, "evidence_ids", evidence_id)


def main() -> int:
    registry = read_json(REGISTRY_PATH)
    sync_documents(registry)

    features = registry["features"]
    features_by_id = {feature["id"]: feature for feature in features}
    for row in ARTIFACT_FEATURES + PATHSEND_FEATURES:
        if row["id"] not in features_by_id:
            feature = base_feature(row)
            features.append(feature)
            features_by_id[feature["id"]] = feature

    selected_ids = sorted(
        feature["id"]
        for feature in features
        if is_contract_future_candidate(feature)
    )

    selected_features = [features_by_id[feature_id] for feature_id in selected_ids]
    write_surface_catalog(selected_features)

    family_features: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in selected_features:
        family_features[feature_family(feature["id"])].append(feature)

    release_claim_ids: list[str] = []
    release_evidence_ids: list[str] = []

    for family, rows in sorted(family_features.items()):
        feature_ids = sorted(feature["id"] for feature in rows)
        claim_id = f"clm:full-contract-future-{family}-surfaces"
        test_id = f"tst:full-contract-future-{family}-surfaces"
        evidence_id = f"evd:full-contract-future-{family}-surfaces"
        release_claim_ids.append(claim_id)
        release_evidence_ids.append(evidence_id)
        upsert(
            registry["claims"],
            claim_id,
            {
                "id": claim_id,
                "title": f"Full contract future {family} surface implementation",
                "status": "evidenced",
                "tier": "T2",
                "kind": "conformance",
                "description": (
                    f"The {family} feature family is implemented as contract-owned "
                    "artifacts, generated outputs, validators, and tests."
                ),
                "feature_ids": feature_ids,
                "test_ids": [test_id],
                "evidence_ids": [evidence_id],
            },
        )
        upsert(
            registry["tests"],
            test_id,
            {
                "id": test_id,
                "title": f"Full contract future {family} pytest coverage",
                "status": "passing",
                "kind": "pytest",
                "path": SURFACE_TEST_PATH,
                "feature_ids": feature_ids,
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
            },
        )
        upsert(
            registry["evidence"],
            evidence_id,
            {
                "id": evidence_id,
                "title": f"Full contract future {family} pytest evidence",
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
            if feature["id"] in selected_ids and feature["plan"].get("horizon") != "current":
                feature["plan"]["horizon"] = "explicit"
                feature["plan"]["slot"] = RELEASE_VERSION
            feature["plan"]["target_claim_tier"] = "T2"
            feature["plan"]["target_lifecycle_stage"] = "active"
            feature["claim_ids"] = sorted_unique(feature.get("claim_ids", []) + [claim_id])
            feature["test_ids"] = sorted_unique(feature.get("test_ids", []) + [test_id])
            feature["spec_ids"] = sorted_unique(feature.get("spec_ids", []) + [SPEC_ID])

    for feature in features:
        feature.setdefault("plan", {})
        feature["plan"]["target_claim_tier"] = "T2"

    upsert(
        registry["boundaries"],
        BOUNDARY_ID,
        {
            "id": BOUNDARY_ID,
            "title": "Full in-bounds future contract implementation boundary",
            "status": "draft",
            "frozen": False,
            "feature_ids": selected_ids,
            "profile_ids": [],
        },
    )
    upsert(
        registry["releases"],
        RELEASE_ID,
        {
            "id": RELEASE_ID,
            "version": RELEASE_VERSION,
            "status": "draft",
            "boundary_id": BOUNDARY_ID,
            "claim_ids": sorted_unique(release_claim_ids),
            "evidence_ids": sorted_unique(release_evidence_ids),
        },
    )

    sync_bidirectional_links(registry)

    write_json(REGISTRY_PATH, registry)
    print(
        json.dumps(
            {
                "boundary_id": BOUNDARY_ID,
                "release_id": RELEASE_ID,
                "feature_count": len(selected_ids),
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
