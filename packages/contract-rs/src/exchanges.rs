use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Exchange {
    #[serde(rename = "unary")]
    Unary,
    #[serde(rename = "server_stream")]
    ServerStream,
    #[serde(rename = "duplex")]
    Duplex,
}
