from __future__ import annotations
from pathlib import Path
import json
import sys
from pathlib import Path
from pprint import pformat
ROOT0 = Path(__file__).resolve().parents[1]
if str(ROOT0) not in sys.path:
    sys.path.insert(0, str(ROOT0))
from common import contract_data, member_name

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages" / "contract-py" / "src" / "tigr_asgi_contract"

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def emit_enum(module_name: str, class_name: str, values: list[str]) -> None:
    body = "\n".join(f"    {member_name(v)} = {v!r}" for v in values)
    write(OUT / f"{module_name}.py", f"from ._enum_compat import StrEnum\n\n\nclass {class_name}(StrEnum):\n{body}\n")

def main() -> None:
    d = contract_data()
    write(OUT / "_enum_compat.py", 'from __future__ import annotations\nfrom enum import Enum\n\ntry:\n    from enum import StrEnum\nexcept ImportError:\n    class StrEnum(str, Enum):\n        pass\n')
    emit_enum("scope_types", "ScopeType", d["scope_types"])
    emit_enum("channels", "Channel", d["channels"])
    emit_enum("directions", "Direction", d["directions"])
    emit_enum("framing", "Framing", d["framings"])
    emit_enum("bindings", "Binding", list(d["bindings"].keys()))
    emit_enum("protocols", "Protocol", list(d["protocols"].keys()))
    emit_enum("exchanges", "Exchange", d["exchanges"])
    emit_enum("families", "Family", d["families"])
    emit_enum("subevents", "Subevent", d["all_subevents"])
    emit_enum("frames", "Frame", list(d["frames"].keys()))
    emit_enum("completion", "EmitCompletionLevel", list(d["completion"]["levels"].keys()))

    write(OUT / "version.py", f'CONTRACT_VERSION = "{d["version"]}"\nCONTRACT_SERDE_VERSION = {d["compatibility"]["serde_version"]}\n')
    write(OUT / "capabilities.py", 'from pydantic import BaseModel\n\n\nclass FamilyCapabilities(BaseModel):\n    request: bool = False\n    session: bool = False\n    message: bool = False\n    stream_in: bool = False\n    stream_out: bool = False\n    datagram: bool = False\n    lifespan: bool = False\n')
    write(OUT / "compatibility.py", 'from pydantic import BaseModel\n\n\nclass Compatibility(BaseModel):\n    contract_name: str\n    contract_version: str\n    serde_version: int\n    schema_draft: str\n    min_tigrcorn_version: str | None = None\n    min_tigrbl_version: str | None = None\n')
    write(OUT / "ids.py", 'from pydantic import BaseModel\n\n\nclass UnitIds(BaseModel):\n    unit_id: str | None = None\n    parent_unit_id: str | None = None\n    session_id: str | None = None\n    stream_id: int | None = None\n    datagram_id: int | None = None\n    emit_id: str | None = None\n')
    write(OUT / "models.py", 'from pydantic import BaseModel, Field\nfrom .capabilities import FamilyCapabilities\n\n\nclass TlsMetadata(BaseModel):\n    version: str | None = None\n    cipher: str | None = None\n    verified: bool = False\n    peer_identity: str | None = None\n    peer_cert: dict | None = None\n\n\nclass TransportMetadata(BaseModel):\n    binding: str\n    network: str\n    secure: bool\n    alpn: str | None = None\n    tls: TlsMetadata | None = None\n    framing: str | None = None\n\n\nclass WebSocketScopeExt(BaseModel):\n    subprotocol: str | None = None\n\n\nclass SseScopeExt(BaseModel):\n    retry_ms: int | None = None\n    last_event_id: str | None = None\n\n\nclass WebTransportScopeExt(BaseModel):\n    session_id: str | None = None\n    supports_datagrams: bool = False\n    supports_bidi_streams: bool = False\n    supports_uni_streams: bool = False\n    max_datagram_size: int | None = None\n\n\nclass ScopeExt(BaseModel):\n    transport: TransportMetadata\n    family_capabilities: FamilyCapabilities\n    websocket: WebSocketScopeExt | None = None\n    sse: SseScopeExt | None = None\n    webtransport: WebTransportScopeExt | None = None\n\n\nclass DerivedEvent(BaseModel):\n    family: str\n    subevent: str\n    repeated: bool = False\n\n\nclass EventClassification(BaseModel):\n    event: str\n    channel: str\n    scope_type: str\n    binding: str\n    family: str\n    exchange: str\n    direction: str\n    allowed_framings: list[str] = Field(default_factory=list)\n    required_scope_fields: list[str] = Field(default_factory=list)\n    required_payload_fields: list[str] = Field(default_factory=list)\n    capability_gates: list[str] = Field(default_factory=list)\n    stream_direction: str | None = None\n')
    write(OUT / "scope.py", 'from pydantic import BaseModel\nfrom .models import ScopeExt\n\n\nclass ContractScope(BaseModel):\n    type: str\n    asgi: dict\n    scheme: str\n    http_version: str | None = None\n    method: str | None = None\n    path: str\n    query_string: bytes = b""\n    headers: list[tuple[bytes, bytes]]\n    client: tuple[str, int] | None = None\n    server: tuple[str, int] | None = None\n    ext: ScopeExt\n')
    events = list(d["schemas"]["event.schema.json"]["properties"]["type"]["enum"])
    event_members = "\n".join(f"    {member_name(v)} = {v!r}" for v in events)
    write(OUT / "events.py", f'from ._enum_compat import StrEnum\nfrom pydantic import BaseModel, Field\n\n\nclass TransportEventType(StrEnum):\n{event_members}\n\n\nclass ContractEvent(BaseModel):\n    type: TransportEventType\n    message: str | None = None\n    payload: dict = Field(default_factory=dict)\n')
    registry_content = "BINDING_FAMILY_MATRIX = " + json.dumps(d["binding_family"], indent=2) + "\n\n"
    registry_content += "FAMILY_SUBEVENT_MATRIX = " + json.dumps(d["family_subevent"], indent=2) + "\n\n"
    registry_content += "BINDING_SUBEVENT_MATRIX = " + json.dumps(d["binding_subevent"], indent=2) + "\n"
    registry_content += "\nPROTOCOLS = " + pformat(d["protocols"], sort_dicts=True) + "\n"
    registry_content += "\nAUTOMATA = " + pformat(d["automata"], sort_dicts=True) + "\n"
    registry_content += "\nFRAMES = " + pformat(d["frames"], sort_dicts=True) + "\n"
    registry_content += "\nEXTENSIONS = " + pformat(d["extensions"], sort_dicts=True) + "\n"
    registry_content += "\nCHANNELS = " + pformat(d["channels"], sort_dicts=True) + "\n"
    registry_content += "\nDIRECTIONS = " + pformat(d["directions"], sort_dicts=True) + "\n"
    registry_content += "\nFRAMINGS = " + pformat(d["framings"], sort_dicts=True) + "\n"
    registry_content += "\nEVENT_CLASSIFICATIONS = " + pformat(d["event_classifications"], sort_dicts=True) + "\n"
    write(OUT / "registry.py", registry_content)
    write(OUT / "validators.py", 'from __future__ import annotations\nfrom typing import Any\nfrom .registry import AUTOMATA, BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX, PROTOCOLS, EVENT_CLASSIFICATIONS, FRAMINGS\nfrom .models import EventClassification\n\n\ndef _scope_value(scope: Any, key: str, default: Any = None) -> Any:\n    if isinstance(scope, dict):\n        return scope.get(key, default)\n    return getattr(scope, key, default)\n\n\ndef _binding_from_scope(scope: Any) -> str | None:\n    ext = _scope_value(scope, "ext", {}) or {}\n    transport = ext.get("transport") if isinstance(ext, dict) else getattr(ext, "transport", None)\n    if isinstance(transport, dict):\n        return transport.get("binding")\n    return getattr(transport, "binding", None)\n\n\ndef _webtransport_ext(scope: Any) -> Any:\n    ext = _scope_value(scope, "ext", {}) or {}\n    return ext.get("webtransport") if isinstance(ext, dict) else getattr(ext, "webtransport", None)\n\n\ndef _has_capability(scope: Any, gate: str) -> bool:\n    wt = _webtransport_ext(scope)\n    if wt is None:\n        return False\n    if isinstance(wt, dict):\n        return bool(wt.get(gate))\n    return bool(getattr(wt, gate, False))\n\n\ndef binding_supports_family(binding: str, family: str) -> bool:\n    return BINDING_FAMILY_MATRIX[binding][family] != "F"\n\n\ndef family_supports_subevent(family: str, subevent: str) -> bool:\n    return FAMILY_SUBEVENT_MATRIX[family].get(subevent) != "F"\n\n\ndef binding_supports_subevent(binding: str, subevent: str) -> bool:\n    return BINDING_SUBEVENT_MATRIX[binding].get(subevent) != "F"\n\n\ndef binding_family_legality(binding: str, family: str) -> str:\n    return BINDING_FAMILY_MATRIX[binding][family]\n\n\ndef binding_subevent_legality(binding: str, subevent: str) -> str:\n    return BINDING_SUBEVENT_MATRIX[binding][subevent]\n\n\ndef protocol_binding(protocol: str) -> str:\n    return PROTOCOLS[protocol]["binding"]\n\n\ndef event_classification_candidates(scope: Any, channel: str, event_type: str, payload: dict | None = None) -> list[EventClassification]:\n    payload = payload or {}\n    scope_type = _scope_value(scope, "type")\n    binding = _binding_from_scope(scope)\n    rows = []\n    for row in EVENT_CLASSIFICATIONS:\n        if row["event"] != event_type or row["channel"] != channel:\n            continue\n        if row["scope_type"] != scope_type:\n            continue\n        if binding is not None and row["binding"] != binding:\n            continue\n        if row.get("stream_direction") and payload.get("stream_direction") != row["stream_direction"]:\n            continue\n        if any(not _has_capability(scope, gate) for gate in row.get("capability_gates", [])):\n            continue\n        rows.append(EventClassification(**row))\n    return rows\n\n\ndef classify_event(scope: Any, channel: str, event_type: str, payload: dict | None = None) -> EventClassification:\n    rows = event_classification_candidates(scope, channel, event_type, payload)\n    if not rows:\n        raise ValueError(f"No event classification for {channel}:{event_type}")\n    return rows[0]\n\n\ndef validate_event_classification(scope: Any, channel: str, event_type: str, payload: dict | None = None) -> bool:\n    try:\n        classify_event(scope, channel, event_type, payload)\n    except ValueError:\n        return False\n    return True\n\n\ndef validate_framing_for_classification(framing: str | None, classification: EventClassification | dict) -> bool:\n    if framing is None:\n        return True\n    if framing not in FRAMINGS:\n        return False\n    allowed = classification.allowed_framings if isinstance(classification, EventClassification) else classification.get("allowed_framings", [])\n    return framing in allowed\n\n\ndef validate_event_payload(event_type: str, payload: dict, classification: EventClassification | dict | None = None) -> bool:\n    if not isinstance(payload, dict) or "subsurface" in payload:\n        return False\n    if event_type == "http.response.pathsend" and not (isinstance(payload.get("path"), str) and payload["path"]):\n        return False\n    if ".stream." in event_type and "stream_id" not in payload:\n        return False\n    if ".datagram." in event_type and "datagram_id" not in payload:\n        return False\n    if classification is not None:\n        required = classification.required_payload_fields if isinstance(classification, EventClassification) else classification.get("required_payload_fields", [])\n        if any(field not in payload for field in required):\n            return False\n        framing = payload.get("framing")\n        if framing is not None and not validate_framing_for_classification(framing, classification):\n            return False\n        if framing == "jsonrpc" and not payload.get("jsonrpc_complete", False):\n            return False\n        if framing == "ndjson" and payload.get("jsonrpc_complete", False):\n            return False\n    return True\n\n\ndef validate_automata_sequence(family: str, subevents: list[str]) -> bool:\n    automaton = AUTOMATA[family]\n    state = automaton["initial"]\n    transitions = {(row["from"], row["event"]): row["to"] for row in automaton["transitions"]}\n    for subevent in subevents:\n        next_state = transitions.get((state, subevent))\n        if next_state is None:\n            return False\n        state = next_state\n    return state in set(automaton["terminal"]) or bool(subevents)\n')
    init_text = '''from .version import CONTRACT_VERSION, CONTRACT_SERDE_VERSION
from .scope_types import ScopeType
from .channels import Channel
from .directions import Direction
from .framing import Framing
from .bindings import Binding
from .protocols import Protocol
from .exchanges import Exchange
from .families import Family
from .subevents import Subevent
from .frames import Frame
from .completion import EmitCompletionLevel
from .capabilities import FamilyCapabilities
from .compatibility import Compatibility
from .ids import UnitIds
from .models import TlsMetadata, TransportMetadata, WebSocketScopeExt, SseScopeExt, WebTransportScopeExt, ScopeExt, DerivedEvent, EventClassification
from .scope import ContractScope
from .events import TransportEventType, ContractEvent
from .validators import binding_supports_family, family_supports_subevent, binding_supports_subevent, binding_family_legality, binding_subevent_legality, protocol_binding, event_classification_candidates, classify_event, validate_event_classification, validate_framing_for_classification, validate_automata_sequence, validate_event_payload
from .schema_registry import EVENT_PAYLOAD_SCHEMA_PATHS, FRAME_PAYLOAD_SCHEMA_PATHS, EVENT_SCHEMA_IDS, FRAME_SCHEMA_IDS, event_payload_schema_path, frame_payload_schema_path, event_has_payload_schema, frame_has_payload_schema, validate_event_payload_schema, validate_frame_payload_schema

__all__ = [
    "CONTRACT_VERSION", "CONTRACT_SERDE_VERSION", "ScopeType", "Channel", "Direction", "Framing", "Binding", "Protocol", "Exchange", "Family", "Subevent", "Frame",
    "EmitCompletionLevel", "FamilyCapabilities", "Compatibility", "UnitIds", "TlsMetadata", "TransportMetadata",
    "WebSocketScopeExt", "SseScopeExt", "WebTransportScopeExt", "ScopeExt", "DerivedEvent", "EventClassification", "ContractScope",
    "TransportEventType", "ContractEvent", "binding_supports_family", "family_supports_subevent",
    "binding_supports_subevent", "binding_family_legality", "binding_subevent_legality", "protocol_binding",
    "event_classification_candidates", "classify_event", "validate_event_classification", "validate_framing_for_classification",
    "validate_automata_sequence", "validate_event_payload",
    "EVENT_PAYLOAD_SCHEMA_PATHS", "FRAME_PAYLOAD_SCHEMA_PATHS", "EVENT_SCHEMA_IDS", "FRAME_SCHEMA_IDS",
    "event_payload_schema_path", "frame_payload_schema_path", "event_has_payload_schema", "frame_has_payload_schema",
    "validate_event_payload_schema", "validate_frame_payload_schema",
]
'''
    write(OUT / "__init__.py", init_text)

if __name__ == "__main__":
    main()

