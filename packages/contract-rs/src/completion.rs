use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum EmitCompletionLevel {
    #[serde(rename = "accepted_by_runtime")]
    AcceptedByRuntime,
    #[serde(rename = "flushed_to_transport")]
    FlushedToTransport,
}
