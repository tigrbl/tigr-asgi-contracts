use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ScopeType {
    #[serde(rename = "http")]
    Http,
    #[serde(rename = "websocket")]
    Websocket,
    #[serde(rename = "lifespan")]
    Lifespan,
    #[serde(rename = "webtransport")]
    Webtransport,
}
