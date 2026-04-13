use serde::{Deserialize, Serialize};
use crate::models::ScopeExt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractScope {
    pub r#type: String,
    pub asgi: serde_json::Value,
    pub scheme: String,
    pub http_version: Option<String>,
    pub method: Option<String>,
    pub path: String,
    pub query_string: Vec<u8>,
    pub headers: Vec<(Vec<u8>, Vec<u8>)>,
    pub client: Option<(String, u16)>,
    pub server: Option<(String, u16)>,
    pub ext: ScopeExt,
}
