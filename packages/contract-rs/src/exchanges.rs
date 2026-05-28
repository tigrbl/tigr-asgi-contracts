use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Exchange {
    #[serde(rename = "unary")]
    Unary,
    #[serde(rename = "client_stream")]
    ClientStream,
    #[serde(rename = "server_stream")]
    ServerStream,
    #[serde(rename = "duplex")]
    Duplex,
}
