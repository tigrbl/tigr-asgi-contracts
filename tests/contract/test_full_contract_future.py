from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"
REGISTRY = ROOT / ".ssot" / "registry.json"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((CONTRACT / name).read_text(encoding="utf-8"))


def test_protocol_registry_maps_every_binding_protocol() -> None:
    bindings = load_yaml("bindings.yaml")["bindings"]
    protocols = load_yaml("protocols.yaml")["protocols"]

    expected = {
        protocol
        for binding in bindings.values()
        for protocol in binding["protocols"]
    }
    assert expected <= set(protocols)
    assert protocols["asgi.pathsend"]["binding"] == "http.stream"
    assert all(row["binding"] in bindings for row in protocols.values())


def test_automata_cover_all_subevent_families() -> None:
    subevents = load_yaml("subevents.yaml")["subevents"]
    automata = load_yaml("automata.yaml")["automata"]

    assert set(automata) == set(subevents)
    for family, automaton in automata.items():
        transition_events = {row["event"] for row in automaton["transitions"]}
        assert transition_events <= set(subevents[family])
        assert automaton["initial"]
        assert automaton["terminal"]


def test_frames_and_extensions_are_schema_backed() -> None:
    frames = load_yaml("frames.yaml")["frames"]
    extensions = load_yaml("extensions.yaml")["extensions"]
    schemas = {path.name for path in (CONTRACT / "schemas").glob("*.schema.json")}

    assert "asgi-tls-extension" in frames
    assert "asgi-pathsend-extension" in frames
    assert "asgi.tls" in extensions
    assert "asgi.pathsend" in extensions
    assert {"tls.schema.json", "pathsend.schema.json", "frames.schema.json", "extensions.schema.json"} <= schemas


def test_new_contract_schemas_are_valid_json_schema() -> None:
    for name in [
        "automata.schema.json",
        "extensions.schema.json",
        "frames.schema.json",
        "pathsend.schema.json",
        "protocols.schema.json",
        "tls.schema.json",
    ]:
        schema = json.loads((CONTRACT / "schemas" / name).read_text(encoding="utf-8"))
        validator_for(schema).check_schema(schema)


def test_full_contract_future_boundary_has_only_implemented_in_bound_features() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    boundary = next(row for row in registry["boundaries"] if row["id"] == "bnd:full-contract-future")
    features = {row["id"]: row for row in registry["features"]}

    assert boundary["feature_ids"]
    assert boundary["status"] in {"draft", "frozen"}
    for feature_id in boundary["feature_ids"]:
        feature = features[feature_id]
        assert feature["plan"]["horizon"] != "out_of_bounds"
        assert feature["plan"]["target_claim_tier"] == "T2"
        assert feature["implementation_status"] == "implemented"
        assert feature.get("test_ids")
        assert feature.get("claim_ids")


def test_pathsend_event_is_in_event_contract() -> None:
    event_schema = json.loads((CONTRACT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
    assert "http.response.pathsend" in event_schema["properties"]["type"]["enum"]
