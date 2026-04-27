use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct FamilyCapabilities {
    pub request: bool,
    pub session: bool,
    pub message: bool,
    pub stream_in: bool,
    pub stream_out: bool,
    pub datagram: bool,
    pub lifespan: bool,
}
