from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT0 = Path(__file__).resolve().parents[1]
if str(ROOT0) not in sys.path:
    sys.path.insert(0, str(ROOT0))

from common import contract_data, pascal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages" / "contract-rs" / "src"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def emit_enum(module_name: str, enum_name: str, values: list[str]) -> None:
    members = []
    for value in values:
        members.append(f'    #[serde(rename = "{value}")]\n    {pascal(value)},')
    body = "\n".join(members)
    write(
        OUT / f"{module_name}.rs",
        f'use serde::{{Deserialize, Serialize}};\n\n'
        f"#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]\n"
        f"pub enum {enum_name} {{\n{body}\n}}\n",
    )


def main() -> None:
    data = contract_data()

    emit_enum("scope_types", "ScopeType", data["scope_types"])
    emit_enum("channels", "Channel", data["channels"])
    emit_enum("directions", "Direction", data["directions"])
    emit_enum("framing", "Framing", data["framings"])
    emit_enum("bindings", "Binding", list(data["bindings"].keys()))
    emit_enum("protocols", "Protocol", list(data["protocols"].keys()))
    emit_enum("exchanges", "Exchange", data["exchanges"])
    emit_enum("families", "Family", data["families"])
    emit_enum("frames", "Frame", list(data["frames"].keys()))
    emit_enum("completion", "EmitCompletionLevel", list(data["completion"]["levels"].keys()))
    write(OUT / "subevents.rs", "pub type Subevent = &'static str;\n")

    write(
        OUT / "version.rs",
        f'pub const CONTRACT_VERSION: &str = "{data["version"]}";\n'
        f'pub const CONTRACT_SERDE_VERSION: u32 = {data["compatibility"]["serde_version"]};\n',
    )
    write(OUT / "capabilities.rs", """use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct FamilyCapabilities {
    pub request: bool,
    pub session: bool,
    pub message: bool,
    pub stream_in: bool,
    pub stream_out: bool,
    pub datagram: bool,
    pub lifespan: bool,
}
""")
    write(OUT / "compatibility.rs", """use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Compatibility {
    pub contract_name: String,
    pub contract_version: String,
    pub serde_version: u32,
    pub schema_draft: String,
    pub min_tigrcorn_version: Option<String>,
    pub min_tigrbl_version: Option<String>,
}
""")
    write(OUT / "ids.rs", """use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct UnitIds {
    pub unit_id: Option<String>,
    pub parent_unit_id: Option<String>,
    pub session_id: Option<String>,
    pub stream_id: Option<u64>,
    pub datagram_id: Option<u64>,
    pub emit_id: Option<String>,
}
""")
    write(OUT / "models.rs", """use crate::capabilities::FamilyCapabilities;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TlsMetadata {
    pub version: Option<String>,
    pub cipher: Option<String>,
    pub verified: bool,
    pub peer_identity: Option<String>,
    pub peer_cert: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransportMetadata {
    pub binding: String,
    pub network: String,
    pub secure: bool,
    pub alpn: Option<String>,
    pub tls: Option<TlsMetadata>,
    pub framing: Option<String>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct WebSocketScopeExt {
    pub subprotocol: Option<String>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SseScopeExt {
    pub retry_ms: Option<u64>,
    pub last_event_id: Option<String>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct WebTransportScopeExt {
    pub session_id: Option<String>,
    pub supports_datagrams: bool,
    pub supports_bidi_streams: bool,
    pub supports_uni_streams: bool,
    pub max_datagram_size: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScopeExt {
    pub transport: TransportMetadata,
    pub family_capabilities: FamilyCapabilities,
    pub websocket: Option<WebSocketScopeExt>,
    pub sse: Option<SseScopeExt>,
    pub webtransport: Option<WebTransportScopeExt>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DerivedEvent {
    pub family: String,
    pub subevent: String,
    pub repeated: bool,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EventClassification {
    pub event: String,
    pub channel: String,
    pub scope_type: String,
    pub binding: String,
    pub family: String,
    pub exchange: String,
    pub direction: String,
    #[serde(default)]
    pub allowed_framings: Vec<String>,
    #[serde(default)]
    pub required_scope_fields: Vec<String>,
    #[serde(default)]
    pub required_payload_fields: Vec<String>,
    #[serde(default)]
    pub capability_gates: Vec<String>,
    pub stream_direction: Option<String>,
}
""")
    write(OUT / "scope.rs", """use crate::models::ScopeExt;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractScope {
    pub r#type: String,
    pub asgi: serde_json::Value,
    pub scheme: String,
    pub http_version: Option<String>,
    pub method: Option<String>,
    pub path: String,
    pub query_string: Vec<u8>,
    pub headers: Vec<(Vec<u8>, Vec<u8>)>,
    pub client: Option<(String, u16)>,
    pub server: Option<(String, u16)>,
    pub ext: ScopeExt,
}
""")
    events = data["schemas"]["event.schema.json"]["properties"]["type"]["enum"]
    event_members = "\n".join([f'    #[serde(rename = "{value}")]\n    {pascal(value)},' for value in events])
    write(OUT / "events.rs", f"""use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TransportEventType {{
{event_members}
}}

impl Default for TransportEventType {{
    fn default() -> Self {{
        Self::HttpRequest
    }}
}}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractEvent {{
    pub r#type: TransportEventType,
    pub message: Option<String>,
    pub payload: serde_json::Map<String, serde_json::Value>,
}}
""")

    binding_supports_family_arms = []
    for binding, family_map in data["binding_family"].items():
        for family, legality in family_map.items():
            if legality != "F":
                binding_supports_family_arms.append(f"        (Binding::{pascal(binding)}, Family::{pascal(family)}) => true,")

    write(OUT / "validators.rs", f"""use crate::bindings::Binding;
use crate::families::Family;
use crate::models::EventClassification;

pub fn binding_supports_family(binding: Binding, family: Family) -> bool {{
    match (binding, family) {{
{chr(10).join(binding_supports_family_arms)}
        _ => false,
    }}
}}

pub fn validate_framing_for_classification(framing: Option<&str>, classification: &EventClassification) -> bool {{
    match framing {{
        None => true,
        Some(value) => crate::registry::FRAMINGS.contains(&value)
            && classification.allowed_framings.iter().any(|allowed| allowed == value),
    }}
}}

pub fn validate_event_payload(
    event_type: &str,
    payload: &serde_json::Map<String, serde_json::Value>,
    classification: Option<&EventClassification>,
) -> bool {{
    if payload.contains_key("subsurface") {{
        return false;
    }}
    if event_type == "http.response.pathsend" && !payload.get("path").is_some_and(|value| value.is_string()) {{
        return false;
    }}
    if event_type.contains(".stream.") && !payload.contains_key("stream_id") {{
        return false;
    }}
    if event_type.contains(".datagram.") && !payload.contains_key("datagram_id") {{
        return false;
    }}
    if let Some(classification) = classification {{
        if classification
            .required_payload_fields
            .iter()
            .any(|field| !payload.contains_key(field))
        {{
            return false;
        }}
        if let Some(framing) = payload.get("framing").and_then(|value| value.as_str()) {{
            if !validate_framing_for_classification(Some(framing), classification) {{
                return false;
            }}
            if framing == "jsonrpc"
                && payload
                    .get("jsonrpc_complete")
                    .and_then(|value| value.as_bool())
                    != Some(true)
            {{
                return false;
            }}
            if framing == "ndjson"
                && payload
                    .get("jsonrpc_complete")
                    .and_then(|value| value.as_bool())
                    == Some(true)
            {{
                return false;
            }}
        }}
    }}
    true
}}
""")

    protocol_rows = []
    for protocol, metadata in data["protocols"].items():
        protocol_rows.append(
            f'    ("{protocol}", "{metadata["binding"]}", "{metadata["transport"]}", {str(metadata["secure"]).lower()}, "{metadata["scope_type"]}"),'
        )
    automata_rows = []
    for family, automaton in data["automata"].items():
        for transition in automaton["transitions"]:
            automata_rows.append(
                f'    ("{family}", "{transition["from"]}", "{transition["event"]}", "{transition["to"]}"),'
            )
    event_classifications_json = json.dumps(data["event_classifications"], indent=2)
    write(
        OUT / "registry.rs",
        "pub const CHANNELS: &[&str] = &["
        + ", ".join(json.dumps(value) for value in data["channels"])
        + "];\n\n"
        + "pub const DIRECTIONS: &[&str] = &["
        + ", ".join(json.dumps(value) for value in data["directions"])
        + "];\n\n"
        + "pub const FRAMINGS: &[&str] = &["
        + ", ".join(json.dumps(value) for value in data["framings"])
        + "];\n\n"
        + "pub const EVENT_CLASSIFICATIONS_JSON: &str = r#\""
        + event_classifications_json
        + "\"#;\n\n"
        + "pub const REQUEST_SUBEVENTS: &[&str] = &["
        + ", ".join(json.dumps(value) for value in data["subevents_by_family"]["request"])
        + "];\n\n"
        + "pub const PROTOCOLS: &[(&str, &str, &str, bool, &str)] = &[\n"
        + "\n".join(protocol_rows)
        + "\n];\n\n"
        + "pub const AUTOMATA_TRANSITIONS: &[(&str, &str, &str, &str)] = &[\n"
        + "\n".join(automata_rows)
        + "\n];\n",
    )
    write(OUT / "lib.rs", """pub mod version;
pub mod scope_types;
pub mod channels;
pub mod directions;
pub mod framing;
pub mod bindings;
pub mod protocols;
pub mod exchanges;
pub mod families;
pub mod frames;
pub mod subevents;
pub mod capabilities;
pub mod completion;
pub mod compatibility;
pub mod ids;
pub mod models;
pub mod scope;
pub mod events;
pub mod validators;
pub mod registry;
""")


if __name__ == "__main__":
    main()
