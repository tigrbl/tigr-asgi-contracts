from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
VALIDATION_REPORT_PATH = ROOT / ".ssot" / "reports" / "validation.report.json"
VERSION_PATH = ROOT / "VERSION"


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_all_features_are_claim_covered_and_complete() -> None:
    registry = load_registry()
    features = registry["features"]
    assert all(feature["implementation_status"] != "partial" for feature in features)
    assert all(
        feature["implementation_status"] != "implemented" or feature.get("claim_ids")
        for feature in features
    )
    assert all(
        feature["implementation_status"] != "absent" or not feature.get("claim_ids")
        for feature in features
    )
    assert all(
        feature["implementation_status"] != "implemented" or feature["plan"]["horizon"] == "current"
        for feature in features
    )
    assert all(
        feature["implementation_status"] != "absent" or feature["plan"]["horizon"] == "out_of_bounds"
        for feature in features
    )


def test_current_release_matches_repo_version() -> None:
    registry = load_registry()
    version = VERSION_PATH.read_text(encoding="utf-8").strip()

    boundary_id = f"bnd:{version}"
    release_id = f"rel:{version}"
    boundaries = {row["id"]: row for row in registry["boundaries"]}
    releases = {row["id"]: row for row in registry["releases"]}

    assert boundary_id in boundaries
    assert boundaries[boundary_id]["status"] != "draft"
    assert release_id in releases
    assert releases[release_id]["version"] == version
    assert releases[release_id]["status"] != "draft"


def test_validation_report_is_green_and_blockers_are_empty() -> None:
    registry = load_registry()
    report = json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))

    assert report["passed"] is True
    assert report["failures"] == []
    assert registry.get("issues", []) == []
    assert registry.get("risks", []) == []
