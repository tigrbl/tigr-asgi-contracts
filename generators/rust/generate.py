from __future__ import annotations
from pathlib import Path
import json
import sys
from pathlib import Path
ROOT0 = Path(__file__).resolve().parents[1]
if str(ROOT0) not in sys.path:
    sys.path.insert(0, str(ROOT0))
from common import contract_data, member_name, pascal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages" / "contract-rs" / "src"

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def emit_enum(module_name: str, enum_name: str, values: list[str]) -> None:
    members = []
    for v in values:
        members.append(f'    #[serde(rename = "{v}")]\n    {pascal(v)},')
    body = "\n".join(members)
    write(OUT / f"{module_name}.rs", f'use serde::{{Deserialize, Serialize}};\n\n#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]\npub enum {enum_name} {{\n{body}\n}}\n')

def main() -> None:
    d = contract_data()
    emit_enum("scope_types", "ScopeType", d["scope_types"])
    emit_enum("bindings", "Binding", list(d["bindings"].keys()))
    emit_enum("protocols", "Protocol", list(d["protocols"].keys()))
    emit_enum("exchanges", "Exchange", d["exchanges"])
    emit_enum("families", "Family", d["families"])
    emit_enum("frames", "Frame", list(d["frames"].keys()))
    emit_enum("completion", "EmitCompletionLevel", list(d["completion"]["levels"].keys()))
    # Subevent is string alias to preserve dots
    write(OUT / "subevents.rs", 'pub type Subevent = &' + "'static str;\n")

    write(OUT / "version.rs", f'pub const CONTRACT_VERSION: &str = "{d["version"]}";\npub const CONTRACT_SERDE_VERSION: u32 = {d["compatibility"]["serde_version"]};\n')
    write(OUT / "capabilities.rs", '''use serde::{Deserialize, Serialize};\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct FamilyCapabilities {\n    pub request: bool,\n    pub session: bool,\n    pub message: bool,\n    pub stream_in: bool,\n    pub stream_out: bool,\n    pub datagram: bool,\n}\n''')
    write(OUT / "compatibility.rs", '''use serde::{Deserialize, Serialize};\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct Compatibility {\n    pub contract_name: String,\n    pub contract_version: String,\n    pub serde_version: u32,\n    pub schema_draft: String,\n    pub min_tigrcorn_version: Option<String>,\n    pub min_tigrbl_version: Option<String>,\n}\n''')
    write(OUT / "ids.rs", '''use serde::{Deserialize, Serialize};\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct UnitIds {\n    pub unit_id: Option<String>,\n    pub parent_unit_id: Option<String>,\n    pub session_id: Option<String>,\n    pub stream_id: Option<u64>,\n    pub datagram_id: Option<u64>,\n    pub emit_id: Option<String>,\n}\n''')
    write(OUT / "models.rs", '''use serde::{Deserialize, Serialize};\nuse crate::capabilities::FamilyCapabilities;\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct TlsMetadata {\n    pub version: Option<String>,\n    pub cipher: Option<String>,\n    pub verified: bool,\n    pub peer_identity: Option<String>,\n    pub peer_cert: Option<serde_json::Value>,\n}\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct TransportMetadata {\n    pub binding: String,\n    pub network: String,\n    pub secure: bool,\n    pub alpn: Option<String>,\n    pub tls: Option<TlsMetadata>,\n    pub framing: Option<String>,\n}\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct WebSocketScopeExt {\n    pub subprotocol: Option<String>,\n}\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct SseScopeExt {\n    pub retry_ms: Option<u64>,\n    pub last_event_id: Option<String>,\n}\n\n#[derive(Debug, Clone, Default, Serialize, Deserialize)]\npub struct WebTransportScopeExt {\n    pub session_id: Option<String>,\n    pub supports_datagrams: bool,\n    pub supports_bidi_streams: bool,\n    pub supports_uni_streams: bool,\n    pub max_datagram_size: Option<u64>,\n}\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct ScopeExt {\n    pub transport: TransportMetadata,\n    pub family_capabilities: FamilyCapabilities,\n    pub websocket: Option<WebSocketScopeExt>,\n    pub sse: Option<SseScopeExt>,\n    pub webtransport: Option<WebTransportScopeExt>,\n}\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct DerivedEvent {\n    pub family: String,\n    pub subevent: String,\n    pub repeated: bool,\n}\n''')
    write(OUT / "scope.rs", '''use serde::{Deserialize, Serialize};\nuse crate::models::ScopeExt;\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct ContractScope {\n    pub r#type: String,\n    pub asgi: serde_json::Value,\n    pub scheme: String,\n    pub http_version: Option<String>,\n    pub method: Option<String>,\n    pub path: String,\n    pub query_string: Vec<u8>,\n    pub headers: Vec<(Vec<u8>, Vec<u8>)>,\n    pub client: Option<(String, u16)>,\n    pub server: Option<(String, u16)>,\n    pub ext: ScopeExt,\n}\n''')
    events = d["schemas"]["event.schema.json"]["properties"]["type"]["enum"]
    event_members = "\n".join([f'    #[serde(rename = "{v}")]\n    {pascal(v)},' for v in events])
    write(OUT / "events.rs", f'''use serde::{{Deserialize, Serialize}};\n\n#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]\npub enum TransportEventType {{\n{event_members}\n}}\n\nimpl Default for TransportEventType {{\n    fn default() -> Self {{\n        Self::HttpRequest\n    }}\n}}\n\n#[derive(Debug, Clone, Serialize, Deserialize)]\npub struct ContractEvent {{\n    pub r#type: TransportEventType,\n    pub message: Option<String>,\n    pub payload: serde_json::Map<String, serde_json::Value>,\n}}\n''')

    binding_supports_family_arms = []
    for b, fmap in d["binding_family"].items():
        for fam, leg in fmap.items():
            if leg != "F":
                binding_supports_family_arms.append(f'        (Binding::{pascal(b)}, Family::{pascal(fam)}) => true,')
    write(OUT / "validators.rs", f'''use crate::bindings::Binding;\nuse crate::families::Family;\n\npub fn binding_supports_family(binding: Binding, family: Family) -> bool {{\n    match (binding, family) {{\n{chr(10).join(binding_supports_family_arms)}\n        _ => false,\n    }}\n}}\n''')

    protocol_rows = []
    for protocol, metadata in d["protocols"].items():
        protocol_rows.append(
            f'    ("{protocol}", "{metadata["binding"]}", "{metadata["transport"]}", {str(metadata["secure"]).lower()}, "{metadata["scope_type"]}"),'
        )
    automata_rows = []
    for family, automaton in d["automata"].items():
        for transition in automaton["transitions"]:
            automata_rows.append(
                f'    ("{family}", "{transition["from"]}", "{transition["event"]}", "{transition["to"]}"),'
            )
    write(OUT / "registry.rs", "pub const REQUEST_SUBEVENTS: &[&str] = &[" + ", ".join(json.dumps(s) for s in d["subevents_by_family"]["request"]) + "];\n\n" + "pub const PROTOCOLS: &[(&str, &str, &str, bool, &str)] = &[\n" + "\n".join(protocol_rows) + "\n];\n\n" + "pub const AUTOMATA_TRANSITIONS: &[(&str, &str, &str, &str)] = &[\n" + "\n".join(automata_rows) + "\n];\n")
    write(OUT / "lib.rs", '''pub mod version;\npub mod scope_types;\npub mod bindings;\npub mod protocols;\npub mod exchanges;\npub mod families;\npub mod frames;\npub mod subevents;\npub mod capabilities;\npub mod completion;\npub mod compatibility;\npub mod ids;\npub mod models;\npub mod scope;\npub mod events;\npub mod validators;\npub mod registry;\n''')

if __name__ == "__main__":
    main()

