use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TransportEventType {
    #[serde(rename = "http.request")]
    HttpRequest,
    #[serde(rename = "http.disconnect")]
    HttpDisconnect,
    #[serde(rename = "http.response.start")]
    HttpResponseStart,
    #[serde(rename = "http.response.body")]
    HttpResponseBody,
    #[serde(rename = "websocket.connect")]
    WebsocketConnect,
    #[serde(rename = "websocket.receive")]
    WebsocketReceive,
    #[serde(rename = "websocket.disconnect")]
    WebsocketDisconnect,
    #[serde(rename = "websocket.accept")]
    WebsocketAccept,
    #[serde(rename = "websocket.send")]
    WebsocketSend,
    #[serde(rename = "websocket.close")]
    WebsocketClose,
    #[serde(rename = "webtransport.connect")]
    WebtransportConnect,
    #[serde(rename = "webtransport.accept")]
    WebtransportAccept,
    #[serde(rename = "webtransport.stream.receive")]
    WebtransportStreamReceive,
    #[serde(rename = "webtransport.stream.send")]
    WebtransportStreamSend,
    #[serde(rename = "webtransport.datagram.receive")]
    WebtransportDatagramReceive,
    #[serde(rename = "webtransport.datagram.send")]
    WebtransportDatagramSend,
    #[serde(rename = "webtransport.disconnect")]
    WebtransportDisconnect,
    #[serde(rename = "webtransport.close")]
    WebtransportClose,
    #[serde(rename = "transport.emit.complete")]
    TransportEmitComplete,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ContractEvent {
    pub r#type: TransportEventType,
    pub payload: serde_json::Map<String, serde_json::Value>,
}
