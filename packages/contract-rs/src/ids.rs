use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct UnitIds {
    pub unit_id: Option<String>,
    pub parent_unit_id: Option<String>,
    pub session_id: Option<String>,
    pub stream_id: Option<u64>,
    pub datagram_id: Option<u64>,
    pub emit_id: Option<String>,
}
