use crate::bindings::Binding;
use crate::families::Family;
use crate::models::EventClassification;

pub const LEGALITY_CODES: &[&str] = &["R", "O", "D", "F"];
pub const LEGALITY_ALLOWED_CODES: &[&str] = &["R", "O", "D"];

pub fn binding_family_legality(binding: Binding, family: Family) -> &'static str {
    match (binding, family) {
        (Binding::Rest, Family::Request) => "R",
        (Binding::Rest, Family::Session) => "F",
        (Binding::Rest, Family::Message) => "F",
        (Binding::Rest, Family::Stream) => "O",
        (Binding::Rest, Family::Datagram) => "F",
        (Binding::Rest, Family::Lifespan) => "F",
        (Binding::Jsonrpc, Family::Request) => "R",
        (Binding::Jsonrpc, Family::Session) => "F",
        (Binding::Jsonrpc, Family::Message) => "F",
        (Binding::Jsonrpc, Family::Stream) => "O",
        (Binding::Jsonrpc, Family::Datagram) => "F",
        (Binding::Jsonrpc, Family::Lifespan) => "F",
        (Binding::HttpStream, Family::Request) => "R",
        (Binding::HttpStream, Family::Session) => "F",
        (Binding::HttpStream, Family::Message) => "F",
        (Binding::HttpStream, Family::Stream) => "R",
        (Binding::HttpStream, Family::Datagram) => "F",
        (Binding::HttpStream, Family::Lifespan) => "F",
        (Binding::Sse, Family::Request) => "R",
        (Binding::Sse, Family::Session) => "R",
        (Binding::Sse, Family::Message) => "R",
        (Binding::Sse, Family::Stream) => "R",
        (Binding::Sse, Family::Datagram) => "F",
        (Binding::Sse, Family::Lifespan) => "F",
        (Binding::Websocket, Family::Request) => "F",
        (Binding::Websocket, Family::Session) => "R",
        (Binding::Websocket, Family::Message) => "R",
        (Binding::Websocket, Family::Stream) => "F",
        (Binding::Websocket, Family::Datagram) => "F",
        (Binding::Websocket, Family::Lifespan) => "F",
        (Binding::Webtransport, Family::Request) => "F",
        (Binding::Webtransport, Family::Session) => "R",
        (Binding::Webtransport, Family::Message) => "F",
        (Binding::Webtransport, Family::Stream) => "R",
        (Binding::Webtransport, Family::Datagram) => "R",
        (Binding::Webtransport, Family::Lifespan) => "F",
        (Binding::Lifespan, Family::Request) => "F",
        (Binding::Lifespan, Family::Session) => "F",
        (Binding::Lifespan, Family::Message) => "F",
        (Binding::Lifespan, Family::Stream) => "F",
        (Binding::Lifespan, Family::Datagram) => "F",
        (Binding::Lifespan, Family::Lifespan) => "R",
    }
}

pub fn binding_supports_family(binding: Binding, family: Family) -> bool {
    LEGALITY_ALLOWED_CODES.contains(&binding_family_legality(binding, family))
}

pub fn validate_binding_family(binding: Binding, family: Family) -> bool {
    binding_supports_family(binding, family)
}

pub fn validate_framing_for_classification(framing: Option<&str>, classification: &EventClassification) -> bool {
    match framing {
        None => true,
        Some(value) => crate::registry::FRAMINGS.contains(&value)
            && classification.allowed_framings.iter().any(|allowed| allowed == value),
    }
}

pub fn validate_event_payload(
    event_type: &str,
    payload: &serde_json::Map<String, serde_json::Value>,
    classification: Option<&EventClassification>,
) -> bool {
    if payload.contains_key("subsurface") {
        return false;
    }
    if event_type == "http.response.pathsend" && !payload.get("path").is_some_and(|value| value.is_string()) {
        return false;
    }
    if event_type.contains(".stream.") && !payload.contains_key("stream_id") {
        return false;
    }
    if event_type.contains(".datagram.") && !payload.contains_key("datagram_id") {
        return false;
    }
    if let Some(classification) = classification {
        if classification
            .required_payload_fields
            .iter()
            .any(|field| !payload.contains_key(field))
        {
            return false;
        }
        if let Some(framing) = payload.get("framing").and_then(|value| value.as_str()) {
            if !validate_framing_for_classification(Some(framing), classification) {
                return false;
            }
            if framing == "jsonrpc"
                && payload
                    .get("jsonrpc_complete")
                    .and_then(|value| value.as_bool())
                    != Some(true)
            {
                return false;
            }
            if framing == "ndjson"
                && payload
                    .get("jsonrpc_complete")
                    .and_then(|value| value.as_bool())
                    == Some(true)
            {
                return false;
            }
        }
    }
    true
}
