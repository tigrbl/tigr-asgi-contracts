from __future__ import annotations

import json
from pathlib import Path

import yaml

from tigr_asgi_contract import (
    LEGALITY_ALLOWED_CODES,
    LEGALITY_CODES,
    binding_family_legality,
    binding_subevent_legality,
    binding_supports_family,
    binding_supports_subevent,
    family_subevent_legality,
    family_supports_subevent,
    is_derived_legality,
    is_forbidden_legality,
    is_optional_legality,
    is_required_legality,
    legality_matrix_errors,
    validate_binding_family,
    validate_binding_subevent,
    validate_family_subevent,
    validate_legality_matrices,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"
REGISTRY = ROOT / ".ssot" / "registry.json"


def _load_yaml(name: str) -> dict:
    return yaml.safe_load((CONTRACT / name).read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    return value.replace(".", "-").replace("_", "-")


def _feature_expectation(code: str) -> tuple[str, str]:
    if code == "F":
        return "obsolete", "out_of_bounds"
    return "active", "current"


def test_legality_matrices_are_complete_and_use_known_codes() -> None:
    binding_family = _load_yaml("legality/binding_family.yaml")["binding_family"]
    binding_subevent = _load_yaml("legality/binding_subevent.yaml")["binding_subevent"]
    family_subevent = _load_yaml("legality/family_subevent.yaml")["family_subevent"]
    bindings = set(_load_yaml("bindings.yaml")["bindings"])
    families = set(_load_yaml("families.yaml")["families"])
    subevents = {subevent for rows in family_subevent.values() for subevent in rows}

    assert set(LEGALITY_CODES) == {"R", "O", "D", "F"}
    assert set(LEGALITY_ALLOWED_CODES) == {"R", "O", "D"}
    assert set(binding_family) == bindings
    assert set(binding_subevent) == bindings

    for binding, family_rows in binding_family.items():
        assert set(family_rows) == families, binding
        assert set(family_rows.values()) <= set(LEGALITY_CODES)

    for family, subevent_rows in family_subevent.items():
        assert set(subevent_rows.values()) <= set(LEGALITY_CODES)
        assert subevent_rows

    for binding, subevent_rows in binding_subevent.items():
        assert set(subevent_rows) == subevents, binding
        assert set(subevent_rows.values()) <= set(LEGALITY_CODES)

    assert legality_matrix_errors() == []
    assert validate_legality_matrices()


def test_legality_runtime_matches_matrix_values() -> None:
    binding_family = _load_yaml("legality/binding_family.yaml")["binding_family"]
    binding_subevent = _load_yaml("legality/binding_subevent.yaml")["binding_subevent"]
    family_subevent = _load_yaml("legality/family_subevent.yaml")["family_subevent"]

    for binding, family_rows in binding_family.items():
        for family, code in family_rows.items():
            assert binding_family_legality(binding, family) == code
            assert binding_supports_family(binding, family) is (code != "F")
            assert validate_binding_family(binding, family) is (code != "F")

    for family, subevent_rows in family_subevent.items():
        for subevent, code in subevent_rows.items():
            assert family_subevent_legality(family, subevent) == code
            assert family_supports_subevent(family, subevent) is (code != "F")
            assert validate_family_subevent(family, subevent) is (code != "F")

    for binding, subevent_rows in binding_subevent.items():
        for subevent, code in subevent_rows.items():
            assert binding_subevent_legality(binding, subevent) == code
            assert binding_supports_subevent(binding, subevent) is (code != "F")
            assert validate_binding_subevent(binding, subevent) is (code != "F")


def test_legality_runtime_fails_closed_for_unknown_and_forbidden_rows() -> None:
    assert binding_family_legality("webtransport", "message") == "F"
    assert not binding_supports_family("webtransport", "message")
    assert not validate_binding_family("webtransport", "message")

    assert binding_subevent_legality("webtransport", "message.in") == "F"
    assert not binding_supports_subevent("webtransport", "message.in")
    assert not validate_binding_subevent("webtransport", "message.in")

    assert family_subevent_legality("message", "message.ack") == "F"
    assert not family_supports_subevent("message", "message.ack")
    assert not validate_family_subevent("message", "message.ack")

    assert binding_family_legality("not-a-binding", "request") == "F"
    assert binding_family_legality("rest", "not-a-family") == "F"
    assert family_subevent_legality("not-a-family", "message.in") == "F"
    assert family_subevent_legality("message", "not-a-subevent") == "F"
    assert binding_subevent_legality("not-a-binding", "message.in") == "F"
    assert binding_subevent_legality("websocket", "not-a-subevent") == "F"


def test_legality_code_helpers_are_exact() -> None:
    assert is_required_legality("R")
    assert is_optional_legality("O")
    assert is_derived_legality("D")
    assert is_forbidden_legality("F")
    assert not is_required_legality("O")
    assert not is_optional_legality("D")
    assert not is_derived_legality("F")
    assert not is_forbidden_legality("R")


def test_legality_feature_rows_match_canonical_matrix_status() -> None:
    features = {row["id"]: row for row in json.loads(REGISTRY.read_text(encoding="utf-8"))["features"]}
    binding_family = _load_yaml("legality/binding_family.yaml")["binding_family"]
    binding_subevent = _load_yaml("legality/binding_subevent.yaml")["binding_subevent"]
    family_subevent = _load_yaml("legality/family_subevent.yaml")["family_subevent"]
    known_feature_ids: set[str] = set()

    def assert_row(feature_id: str, code: str) -> None:
        known_feature_ids.add(feature_id)
        feature = features[feature_id]
        expected_stage, expected_horizon = _feature_expectation(code)
        assert feature["implementation_status"] == "implemented", feature_id
        assert feature["lifecycle"]["stage"] == expected_stage, feature_id
        assert feature["plan"]["horizon"] == expected_horizon, feature_id
        assert feature["plan"]["target_lifecycle_stage"] == expected_stage, feature_id
        assert feature["test_ids"], feature_id
        assert feature["claim_ids"], feature_id

    for binding, family_rows in binding_family.items():
        for family, code in family_rows.items():
            assert_row(f"feat:binding-family-{_slug(binding)}-{_slug(family)}", code)

    for family, subevent_rows in family_subevent.items():
        for subevent, code in subevent_rows.items():
            assert_row(f"feat:family-subevent-{_slug(family)}-{_slug(subevent)}", code)

    for binding, subevent_rows in binding_subevent.items():
        for subevent, code in subevent_rows.items():
            assert_row(f"feat:binding-subevent-{_slug(binding)}-{_slug(subevent)}", code)

    for feature_id, feature in features.items():
        if not feature_id.startswith(
            ("feat:binding-family-", "feat:binding-subevent-", "feat:family-subevent-")
        ):
            continue
        if feature_id in known_feature_ids:
            continue
        assert feature["implementation_status"] == "implemented", feature_id
        assert feature["lifecycle"]["stage"] == "obsolete", feature_id
        assert feature["plan"]["horizon"] == "out_of_bounds", feature_id
        assert feature["plan"]["target_lifecycle_stage"] == "obsolete", feature_id
