use crate::bindings::Binding;
use crate::families::Family;

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
        (Binding::Webtransport, Family::Message) => true,
        (Binding::Webtransport, Family::Stream) => true,
        (Binding::Webtransport, Family::Datagram) => true,
        _ => false,
    }
}
