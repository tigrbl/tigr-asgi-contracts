from __future__ import annotations
from pathlib import Path
import json
import sys
from pathlib import Path
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
    emit_enum("bindings", "Binding", list(d["bindings"].keys()))
    emit_enum("exchanges", "Exchange", d["exchanges"])
    emit_enum("families", "Family", d["families"])
    emit_enum("subevents", "Subevent", d["all_subevents"])
    emit_enum("completion", "EmitCompletionLevel", list(d["completion"]["levels"].keys()))

    write(OUT / "version.py", f'CONTRACT_VERSION = "{d["version"]}"\nCONTRACT_SERDE_VERSION = {d["compatibility"]["serde_version"]}\n')
    write(OUT / "capabilities.py", 'from pydantic import BaseModel\n\n\nclass FamilyCapabilities(BaseModel):\n    request: bool = False\n    session: bool = False\n    message: bool = False\n    stream_in: bool = False\n    stream_out: bool = False\n    datagram: bool = False\n')
    write(OUT / "compatibility.py", 'from pydantic import BaseModel\n\n\nclass Compatibility(BaseModel):\n    contract_name: str\n    contract_version: str\n    serde_version: int\n    schema_draft: str\n    min_tigrcorn_version: str | None = None\n    min_tigrbl_version: str | None = None\n')
    write(OUT / "ids.py", 'from pydantic import BaseModel\n\n\nclass UnitIds(BaseModel):\n    unit_id: str | None = None\n    parent_unit_id: str | None = None\n    session_id: str | None = None\n    stream_id: int | None = None\n    datagram_id: int | None = None\n    emit_id: str | None = None\n')
    write(OUT / "models.py", 'from pydantic import BaseModel\nfrom .capabilities import FamilyCapabilities\n\n\nclass TlsMetadata(BaseModel):\n    version: str | None = None\n    cipher: str | None = None\n    verified: bool = False\n    peer_identity: str | None = None\n    peer_cert: dict | None = None\n\n\nclass TransportMetadata(BaseModel):\n    binding: str\n    network: str\n    secure: bool\n    alpn: str | None = None\n    tls: TlsMetadata | None = None\n    framing: str | None = None\n\n\nclass WebSocketScopeExt(BaseModel):\n    subprotocol: str | None = None\n\n\nclass SseScopeExt(BaseModel):\n    retry_ms: int | None = None\n    last_event_id: str | None = None\n\n\nclass WebTransportScopeExt(BaseModel):\n    session_id: str | None = None\n    supports_datagrams: bool = False\n    supports_bidi_streams: bool = False\n    supports_uni_streams: bool = False\n    max_datagram_size: int | None = None\n\n\nclass ScopeExt(BaseModel):\n    transport: TransportMetadata\n    family_capabilities: FamilyCapabilities\n    websocket: WebSocketScopeExt | None = None\n    sse: SseScopeExt | None = None\n    webtransport: WebTransportScopeExt | None = None\n\n\nclass DerivedEvent(BaseModel):\n    family: str\n    subevent: str\n    repeated: bool = False\n')
    write(OUT / "scope.py", 'from pydantic import BaseModel\nfrom .models import ScopeExt\n\n\nclass ContractScope(BaseModel):\n    type: str\n    asgi: dict\n    scheme: str\n    http_version: str | None = None\n    method: str | None = None\n    path: str\n    query_string: bytes = b""\n    headers: list[tuple[bytes, bytes]]\n    client: tuple[str, int] | None = None\n    server: tuple[str, int] | None = None\n    ext: ScopeExt\n')
    events = list(d["schemas"]["event.schema.json"]["properties"]["type"]["enum"])
    event_members = "\n".join(f"    {member_name(v)} = {v!r}" for v in events)
    write(OUT / "events.py", f'from ._enum_compat import StrEnum\nfrom pydantic import BaseModel, Field\n\n\nclass TransportEventType(StrEnum):\n{event_members}\n\n\nclass ContractEvent(BaseModel):\n    type: TransportEventType\n    payload: dict = Field(default_factory=dict)\n')
    registry_content = "BINDING_FAMILY_MATRIX = " + json.dumps(d["binding_family"], indent=2) + "\n\n"
    registry_content += "FAMILY_SUBEVENT_MATRIX = " + json.dumps(d["family_subevent"], indent=2) + "\n\n"
    registry_content += "BINDING_SUBEVENT_MATRIX = " + json.dumps(d["binding_subevent"], indent=2) + "\n"
    write(OUT / "registry.py", registry_content)
    write(OUT / "validators.py", 'from __future__ import annotations\nfrom .registry import BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX\n\n\ndef binding_supports_family(binding: str, family: str) -> bool:\n    return BINDING_FAMILY_MATRIX[binding][family] != "F"\n\n\ndef family_supports_subevent(family: str, subevent: str) -> bool:\n    return FAMILY_SUBEVENT_MATRIX[family].get(subevent) != "F"\n\n\ndef binding_supports_subevent(binding: str, subevent: str) -> bool:\n    return BINDING_SUBEVENT_MATRIX[binding].get(subevent) != "F"\n\n\ndef binding_family_legality(binding: str, family: str) -> str:\n    return BINDING_FAMILY_MATRIX[binding][family]\n\n\ndef binding_subevent_legality(binding: str, subevent: str) -> str:\n    return BINDING_SUBEVENT_MATRIX[binding][subevent]\n')
    init_text = '''from .version import CONTRACT_VERSION, CONTRACT_SERDE_VERSION
from .scope_types import ScopeType
from .bindings import Binding
from .exchanges import Exchange
from .families import Family
from .subevents import Subevent
from .completion import EmitCompletionLevel
from .capabilities import FamilyCapabilities
from .compatibility import Compatibility
from .ids import UnitIds
from .models import TlsMetadata, TransportMetadata, WebSocketScopeExt, SseScopeExt, WebTransportScopeExt, ScopeExt, DerivedEvent
from .scope import ContractScope
from .events import TransportEventType, ContractEvent
from .validators import binding_supports_family, family_supports_subevent, binding_supports_subevent, binding_family_legality, binding_subevent_legality

__all__ = [
    "CONTRACT_VERSION", "CONTRACT_SERDE_VERSION", "ScopeType", "Binding", "Exchange", "Family", "Subevent",
    "EmitCompletionLevel", "FamilyCapabilities", "Compatibility", "UnitIds", "TlsMetadata", "TransportMetadata",
    "WebSocketScopeExt", "SseScopeExt", "WebTransportScopeExt", "ScopeExt", "DerivedEvent", "ContractScope",
    "TransportEventType", "ContractEvent", "binding_supports_family", "family_supports_subevent",
    "binding_supports_subevent", "binding_family_legality", "binding_subevent_legality",
]
'''
    write(OUT / "__init__.py", init_text)

if __name__ == "__main__":
    main()
