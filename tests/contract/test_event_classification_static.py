from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((CONTRACT / name).read_text(encoding="utf-8"))


def test_classification_artifacts_exist_and_use_legal_values() -> None:
    channels = set(load_yaml("channels.yaml")["channels"])
    directions = set(load_yaml("directions.yaml")["directions"])
    framings = set(load_yaml("framing.yaml")["framings"])
    scope_types = set(load_yaml("scope_types.yaml")["scope_types"])
    bindings = set(load_yaml("bindings.yaml")["bindings"])
    families = set(load_yaml("families.yaml")["families"])
    exchanges = set(load_yaml("exchanges.yaml")["exchanges"])
    assert channels == {"receive", "send"}
    assert "client_stream" in exchanges
    assert framings == {"json", "jsonrpc", "ndjson", "sse", "text", "bytes", "binary"}

    rows = load_yaml("event_classification.yaml")["event_classifications"]
    for row in rows:
        assert "subsurface" not in row
        assert row["channel"] in channels
        assert row["direction"] in directions
        assert row["scope_type"] in scope_types
        assert row["binding"] in bindings
        assert row["family"] in families
        assert row["exchange"] in exchanges
        assert set(row.get("allowed_framings", [])) <= framings

    row_events = {row["event"] for row in rows}
    schema_events = set(load_yaml("schemas/event.schema.json")["properties"]["type"]["enum"])
    assert row_events == schema_events


def test_webtransport_has_native_session_stream_datagram_only() -> None:
    bindings = load_yaml("bindings.yaml")["bindings"]
    binding_family = load_yaml("legality/binding_family.yaml")["binding_family"]
    binding_subevent = load_yaml("legality/binding_subevent.yaml")["binding_subevent"]
    rows = load_yaml("event_classification.yaml")["event_classifications"]

    assert bindings["webtransport"]["families"] == {
        "session": "required",
        "stream": "required",
        "datagram": "required",
    }
    assert binding_family["webtransport"]["message"] == "F"
    assert all(
        value == "F"
        for key, value in binding_subevent["webtransport"].items()
        if key.startswith("message.")
    )
    assert all(
        row["family"] != "message"
        for row in rows
        if row["scope_type"] == "webtransport"
    )


def test_scope_transport_metadata_stays_under_ext_transport() -> None:
    scope_schema = load_yaml("schemas/scope.schema.json")
    transport_schema = load_yaml("schemas/transport.schema.json")

    assert "ext" in scope_schema["required"]
    assert scope_schema["properties"]["ext"]["$ref"] == "transport.schema.json#/$defs/scopeExt"
    assert "transport" in transport_schema["$defs"]["scopeExt"]["properties"]
    metadata_properties = transport_schema["$defs"]["transportMetadata"]["properties"]
    assert "alpn" in metadata_properties
    assert "tls" in metadata_properties
    assert "framing" in metadata_properties
    assert {"json", "jsonrpc", "ndjson", "sse", "text", "bytes", "binary"} <= set(
        metadata_properties["framing"]["enum"]
    )
