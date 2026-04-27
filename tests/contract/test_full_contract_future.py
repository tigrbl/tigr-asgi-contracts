from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"
REGISTRY = ROOT / ".ssot" / "registry.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate_readmes import SUBEVENT_EVENT_MAP  # noqa: E402


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
        assert transition_events == set(subevents[family])
        assert automaton["initial"]
        assert automaton["terminal"]


def test_protocol_observable_subevent_semantics() -> None:
    subevents = load_yaml("subevents.yaml")["subevents"]
    all_subevents = {subevent for rows in subevents.values() for subevent in rows}

    assert "request.accept" not in all_subevents
    assert "response.close" not in all_subevents
    assert "message.ack" not in all_subevents
    assert "message.nack" not in all_subevents
    assert "stream.abort" not in all_subevents
    assert "datagram.ack" not in all_subevents

    assert SUBEVENT_EVENT_MAP["request.dispatch"] == []
    assert "webtransport.close" not in SUBEVENT_EVENT_MAP["stream.close"]
    assert "webtransport.close" not in SUBEVENT_EVENT_MAP["stream.reset"]
    assert "webtransport.close" not in SUBEVENT_EVENT_MAP["stream.stop_sending"]
    assert "webtransport.datagram.send" not in SUBEVENT_EVENT_MAP["datagram.emit_complete"]
    assert "transport.emit.failed" in SUBEVENT_EVENT_MAP["datagram.emit_failed"]


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


def test_protocol_observable_ssot_traceability() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    specs = {row["id"]: row for row in registry["specs"]}
    features = {row["id"]: row for row in registry["features"]}
    claims = {row["id"]: row for row in registry["claims"]}

    for spec_id in {"spc:1032", "spc:1033", "spc:1034", "spc:1035"}:
        assert specs[spec_id]["adr_ids"] == ["adr:1032"]

    new_features = {
        "feat:family-subevent-request-request-dispatch": ({"spc:1032", "spc:1033"}, {"implemented"}),
        "feat:family-subevent-request-response-finalize": ({"spc:1032", "spc:1033"}, {"implemented"}),
        "feat:family-subevent-lifespan-lifespan-startup": ({"spc:1032", "spc:1033"}, {"implemented"}),
        "feat:family-subevent-lifespan-lifespan-shutdown-failed": ({"spc:1032", "spc:1033"}, {"implemented"}),
        "feat:family-subevent-session-session-reject": ({"spc:1032", "spc:1034"}, {"implemented"}),
        "feat:family-subevent-message-message-emit-failed": ({"spc:1032", "spc:1034"}, {"implemented"}),
        "feat:family-subevent-stream-stream-reset": ({"spc:1032", "spc:1035"}, {"implemented"}),
        "feat:family-subevent-stream-stream-stop-sending": ({"spc:1032", "spc:1035"}, {"implemented"}),
        "feat:family-subevent-datagram-datagram-emit-failed": ({"spc:1032", "spc:1035"}, {"implemented"}),
        "feat:binding-subevent-webtransport-stream-reset": (
            {"spc:1032", "spc:1035"},
            {"implemented", "partial"},
        ),
        "feat:scope-scope-webtransport-datagram-datagram-emit-failed": (
            {"spc:1032", "spc:1035"},
            {"implemented", "partial"},
        ),
    }
    for feature_id, (expected_specs, expected_statuses) in new_features.items():
        feature = features[feature_id]
        assert feature["implementation_status"] in expected_statuses
        assert feature["lifecycle"]["stage"] == "active"
        assert expected_specs <= set(feature["spec_ids"])
        assert feature["test_ids"]
        assert any(claims[claim_id]["evidence_ids"] for claim_id in feature["claim_ids"])

    obsolete_replacements = {
        "feat:family-subevent-request-request-accept": {
            "feat:family-subevent-request-request-dispatch",
        },
        "feat:family-subevent-request-response-close": {
            "feat:family-subevent-request-response-finalize",
        },
        "feat:family-subevent-message-message-ack": {
            "feat:family-subevent-message-message-emit-complete",
        },
        "feat:family-subevent-message-message-nack": {
            "feat:family-subevent-message-message-emit-failed",
        },
        "feat:family-subevent-stream-stream-abort": {
            "feat:family-subevent-stream-stream-reset",
            "feat:family-subevent-stream-stream-stop-sending",
        },
        "feat:family-subevent-datagram-datagram-ack": {
            "feat:family-subevent-datagram-datagram-emit-complete",
        },
        "feat:scope-scope-webtransport-datagram-datagram-close": {
            "feat:scope-scope-webtransport-datagram-datagram-emit-complete",
        },
    }
    for feature_id, expected_replacements in obsolete_replacements.items():
        feature = features[feature_id]
        assert feature["implementation_status"] in {"absent", "partial"}
        assert feature["lifecycle"]["stage"] == "obsolete"
        assert feature["plan"]["horizon"] == "out_of_bounds"
        assert feature["plan"]["target_lifecycle_stage"] == "obsolete"
        assert "spc:1032" in feature["spec_ids"]
        assert expected_replacements <= set(feature["lifecycle"]["replacement_feature_ids"])
        for replacement_id in expected_replacements:
            replacement = features[replacement_id]
            assert replacement["test_ids"]
            assert any(claims[claim_id]["evidence_ids"] for claim_id in replacement["claim_ids"])


def test_pathsend_event_is_in_event_contract() -> None:
    event_schema = json.loads((CONTRACT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
    assert "http.response.pathsend" in event_schema["properties"]["type"]["enum"]
