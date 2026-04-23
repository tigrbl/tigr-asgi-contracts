use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Protocol {
    #[serde(rename = "http.rest")]
    HttpRest,
    #[serde(rename = "https.rest")]
    HttpsRest,
    #[serde(rename = "http.jsonrpc")]
    HttpJsonrpc,
    #[serde(rename = "https.jsonrpc")]
    HttpsJsonrpc,
    #[serde(rename = "http.stream")]
    HttpStream,
    #[serde(rename = "https.stream")]
    HttpsStream,
    #[serde(rename = "http.sse")]
    HttpSse,
    #[serde(rename = "https.sse")]
    HttpsSse,
    #[serde(rename = "ws")]
    Ws,
    #[serde(rename = "wss")]
    Wss,
    #[serde(rename = "webtransport")]
    Webtransport,
    #[serde(rename = "asgi.pathsend")]
    AsgiPathsend,
}
