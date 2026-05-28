use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Direction {
    #[serde(rename = "client_to_server")]
    ClientToServer,
    #[serde(rename = "server_to_client")]
    ServerToClient,
    #[serde(rename = "app_to_server")]
    AppToServer,
    #[serde(rename = "server_to_app")]
    ServerToApp,
    #[serde(rename = "system")]
    System,
}
