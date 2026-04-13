use serde::{Deserialize, Serialize};
use crate::capabilities::FamilyCapabilities;

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
