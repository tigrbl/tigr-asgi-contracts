use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Compatibility {
    pub contract_name: String,
    pub contract_version: String,
    pub serde_version: u32,
    pub schema_draft: String,
    pub min_tigrcorn_version: Option<String>,
    pub min_tigrbl_version: Option<String>,
}
