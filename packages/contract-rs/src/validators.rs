use crate::bindings::Binding;
use crate::families::Family;
use crate::models::EventClassification;

pub fn binding_supports_family(binding: Binding, family: Family) -> bool {
    match (binding, family) {
        (Binding::Rest, Family::Request) => true,
        (Binding::Rest, Family::Stream) => true,
        (Binding::Jsonrpc, Family::Request) => true,
        (Binding::Jsonrpc, Family::Stream) => true,
        (Binding::HttpStream, Family::Request) => true,
        (Binding::HttpStream, Family::Stream) => true,
        (Binding::Sse, Family::Request) => true,
        (Binding::Sse, Family::Session) => true,
        (Binding::Sse, Family::Message) => true,
        (Binding::Sse, Family::Stream) => true,
        (Binding::Websocket, Family::Session) => true,
        (Binding::Websocket, Family::Message) => true,
        (Binding::Webtransport, Family::Session) => true,
        (Binding::Webtransport, Family::Stream) => true,
        (Binding::Webtransport, Family::Datagram) => true,
        (Binding::Lifespan, Family::Lifespan) => true,
        _ => false,
    }
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
