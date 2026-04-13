use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Binding {
    #[serde(rename = "rest")]
    Rest,
    #[serde(rename = "jsonrpc")]
    Jsonrpc,
    #[serde(rename = "http.stream")]
    HttpStream,
    #[serde(rename = "sse")]
    Sse,
    #[serde(rename = "websocket")]
    Websocket,
    #[serde(rename = "webtransport")]
    Webtransport,
}
