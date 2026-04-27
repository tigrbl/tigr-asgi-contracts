use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Family {
    #[serde(rename = "request")]
    Request,
    #[serde(rename = "session")]
    Session,
    #[serde(rename = "message")]
    Message,
    #[serde(rename = "stream")]
    Stream,
    #[serde(rename = "datagram")]
    Datagram,
    #[serde(rename = "lifespan")]
    Lifespan,
}
