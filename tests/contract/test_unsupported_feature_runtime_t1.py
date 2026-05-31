from __future__ import annotations

import json
from pathlib import Path

import yaml

from tigr_asgi_contract import (
    UNSUPPORTED_FEATURE_CATEGORIES,
    unsupported_feature_category,
    unsupported_feature_declaration_errors,
    validate_unsupported_feature_declaration,
    validate_unsupported_feature_runtime,
)


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ssot" / "registry.json"
SURFACES = ROOT / "contract" / "surfaces.yaml"


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _supported_surface_ids() -> set[str]:
    surface_catalog = yaml.safe_load(SURFACES.read_text(encoding="utf-8"))["surface_catalog"]
    return {
        row["id"]
        for rows in surface_catalog["families"].values()
        for row in rows
    }


def _unsupported_feature_ids() -> set[str]:
    claim = next(
        row for row in _registry()["claims"]
        if row["id"] == "clm:unsupported-feature-declarations-t0"
    )
    return set(claim["feature_ids"])


def _unsupported_features() -> list[dict]:
    ids = _unsupported_feature_ids()
    return [row for row in _registry()["features"] if row["id"] in ids]


def test_unsupported_feature_runtime_categories_cover_registry_rows() -> None:
    unsupported = _unsupported_features()
    categories = {unsupported_feature_category(row["id"]) for row in unsupported}

    assert len(unsupported) == 334
    assert categories == set(UNSUPPORTED_FEATURE_CATEGORIES)


def test_unsupported_feature_runtime_validates_every_unsupported_declaration() -> None:
    supported_surface_ids = _supported_surface_ids()

    for feature in _unsupported_features():
        assert validate_unsupported_feature_runtime(feature["id"]), feature["id"]
        assert unsupported_feature_declaration_errors(feature, supported_surface_ids) == [], feature["id"]
        assert validate_unsupported_feature_declaration(feature, supported_surface_ids), feature["id"]


def test_unsupported_feature_runtime_rejects_malformed_declarations() -> None:
    supported_surface_ids = _supported_surface_ids()
    feature = _unsupported_features()[0]

    not_implemented = {**feature, "implementation_status": "absent"}
    assert "not_implemented:" + feature["id"] in unsupported_feature_declaration_errors(not_implemented, supported_surface_ids)
    assert not validate_unsupported_feature_declaration(not_implemented, supported_surface_ids)

    no_runtime = {**feature, "id": "feat:not-a-known-unsupported-surface"}
    errors = unsupported_feature_declaration_errors(no_runtime, supported_surface_ids)
    assert "unknown_unsupported_feature_category:feat:not-a-known-unsupported-surface" in errors
    assert "runtime_not_unsupported:feat:not-a-known-unsupported-surface" in errors
    assert not validate_unsupported_feature_declaration(no_runtime, supported_surface_ids)

    surface_conflict = {
        **feature,
        "id": next(iter(supported_surface_ids)),
    }
    assert any(
        error.startswith("declared_unsupported_but_surface_supported:")
        for error in unsupported_feature_declaration_errors(surface_conflict, supported_surface_ids)
    )
