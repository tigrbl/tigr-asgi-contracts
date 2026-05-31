from __future__ import annotations

import json
from pathlib import Path

import yaml

from tigr_asgi_contract import (
    binding_family_legality,
    binding_subevent_legality,
    family_subevent_legality,
    validate_binding_family,
    validate_binding_subevent,
    validate_family_subevent,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"
REGISTRY = ROOT / ".ssot" / "registry.json"
SURFACES = ROOT / "contract" / "surfaces.yaml"


def _load_yaml(name: str) -> dict:
    return yaml.safe_load((CONTRACT / name).read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    return value.replace(".", "-").replace("_", "-")


def _feature_maps() -> tuple[list[dict], dict[str, dict]]:
    features = json.loads(REGISTRY.read_text(encoding="utf-8"))["features"]
    return features, {row["id"]: row for row in features}


def _unsupported_feature_ids() -> set[str]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    claim = next(
        row for row in registry["claims"]
        if row["id"] == "clm:unsupported-feature-declarations-t0"
    )
    return set(claim["feature_ids"])


def _unsupported_features() -> list[dict]:
    features, _ = _feature_maps()
    ids = _unsupported_feature_ids()
    return [row for row in features if row["id"] in ids]


def test_unsupported_features_are_current_implemented_rejection_declarations() -> None:
    unsupported = _unsupported_features()

    assert unsupported
    for feature in unsupported:
        assert feature["implementation_status"] == "implemented", feature["id"]
        assert feature["lifecycle"]["stage"] == "active", feature["id"]
        assert feature["plan"]["horizon"] == "current", feature["id"]
        assert feature["plan"]["target_lifecycle_stage"] == "active", feature["id"]
        assert "clm:unsupported-feature-declarations-t0" in feature["claim_ids"], feature["id"]
        assert "clm:unsupported-feature-runtime-rejection-t1" in feature["claim_ids"], feature["id"]
        assert "tst:unsupported-feature-declarations-t0" in feature["test_ids"], feature["id"]
        assert "tst:unsupported-feature-runtime-rejection-t1" in feature["test_ids"], feature["id"]
        note = feature["lifecycle"].get("note", "")
        assert "Unsupported" in note or "unsupported" in note or "fail" in note, feature["id"]


def test_unsupported_features_are_not_current_supported_surface_catalog_entries() -> None:
    surface_catalog = yaml.safe_load(SURFACES.read_text(encoding="utf-8"))["surface_catalog"]
    supported_surface_ids = {
        row["id"]
        for rows in surface_catalog["families"].values()
        for row in rows
    }

    unsupported_ids = _unsupported_feature_ids()
    assert unsupported_ids
    assert supported_surface_ids.isdisjoint(unsupported_ids)


def test_unsupported_binding_family_features_are_runtime_forbidden() -> None:
    _, features = _feature_maps()
    binding_family = _load_yaml("legality/binding_family.yaml")["binding_family"]

    for binding, family_rows in binding_family.items():
        for family, code in family_rows.items():
            if code != "F":
                continue
            feature_id = f"feat:binding-family-{_slug(binding)}-{_slug(family)}"
            assert features[feature_id]["implementation_status"] == "implemented"
            assert binding_family_legality(binding, family) == "F"
            assert validate_binding_family(binding, family) is False


def test_unsupported_family_subevent_features_are_runtime_forbidden() -> None:
    _, features = _feature_maps()
    family_subevent = _load_yaml("legality/family_subevent.yaml")["family_subevent"]

    for family, subevent_rows in family_subevent.items():
        for subevent, code in subevent_rows.items():
            if code != "F":
                continue
            feature_id = f"feat:family-subevent-{_slug(family)}-{_slug(subevent)}"
            assert features[feature_id]["implementation_status"] == "implemented"
            assert family_subevent_legality(family, subevent) == "F"
            assert validate_family_subevent(family, subevent) is False


def test_unsupported_binding_subevent_features_are_runtime_forbidden() -> None:
    _, features = _feature_maps()
    binding_subevent = _load_yaml("legality/binding_subevent.yaml")["binding_subevent"]

    for binding, subevent_rows in binding_subevent.items():
        for subevent, code in subevent_rows.items():
            if code != "F":
                continue
            feature_id = f"feat:binding-subevent-{_slug(binding)}-{_slug(subevent)}"
            assert features[feature_id]["implementation_status"] == "implemented"
            assert binding_subevent_legality(binding, subevent) == "F"
            assert validate_binding_subevent(binding, subevent) is False


def test_unsupported_scope_subevent_features_are_not_canonical_subevent_rows() -> None:
    subevents = _load_yaml("subevents.yaml")["subevents"]
    canonical_subevents = {subevent for rows in subevents.values() for subevent in rows}

    unsupported_scope_rows = [
        row for row in _unsupported_features()
        if row["id"].startswith("feat:scope-scope-")
    ]
    assert unsupported_scope_rows

    unsupported_suffixes = {
        "request.accept",
        "response.close",
        "message.ack",
        "message.nack",
        "stream.abort",
        "datagram.ack",
        "datagram.close",
    }
    for feature in unsupported_scope_rows:
        assert any(
            suffix.replace(".", "-") in feature["id"]
            for suffix in unsupported_suffixes
        ) or "-webtransport-message-" in feature["id"], feature["id"]
    assert canonical_subevents.isdisjoint(unsupported_suffixes)
