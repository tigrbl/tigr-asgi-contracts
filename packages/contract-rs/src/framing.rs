use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Framing {
    #[serde(rename = "json")]
    Json,
    #[serde(rename = "jsonrpc")]
    Jsonrpc,
    #[serde(rename = "ndjson")]
    Ndjson,
    #[serde(rename = "sse")]
    Sse,
    #[serde(rename = "text")]
    Text,
    #[serde(rename = "bytes")]
    Bytes,
    #[serde(rename = "binary")]
    Binary,
}
