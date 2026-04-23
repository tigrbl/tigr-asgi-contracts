use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Frame {
    #[serde(rename = "app")]
    App,
    #[serde(rename = "asgi-tls-extension")]
    AsgiTlsExtension,
    #[serde(rename = "asgi-pathsend-extension")]
    AsgiPathsendExtension,
    #[serde(rename = "bytes")]
    Bytes,
    #[serde(rename = "grpc")]
    Grpc,
    #[serde(rename = "http-1-1-message")]
    Http11Message,
    #[serde(rename = "http-request-body-chunk")]
    HttpRequestBodyChunk,
    #[serde(rename = "http-response-body-chunk")]
    HttpResponseBodyChunk,
    #[serde(rename = "http-response-start-frame")]
    HttpResponseStartFrame,
    #[serde(rename = "json")]
    Json,
    #[serde(rename = "jsonrpc")]
    Jsonrpc,
    #[serde(rename = "json-rpc-request-object")]
    JsonRpcRequestObject,
    #[serde(rename = "json-rpc-response-object")]
    JsonRpcResponseObject,
    #[serde(rename = "json-rpc-notification-object")]
    JsonRpcNotificationObject,
    #[serde(rename = "json-rpc-error-object")]
    JsonRpcErrorObject,
    #[serde(rename = "raw")]
    Raw,
    #[serde(rename = "sse")]
    Sse,
    #[serde(rename = "sse-data-field")]
    SseDataField,
    #[serde(rename = "sse-event-field")]
    SseEventField,
    #[serde(rename = "sse-id-field")]
    SseIdField,
    #[serde(rename = "sse-retry-field")]
    SseRetryField,
    #[serde(rename = "websocket-frame")]
    WebsocketFrame,
    #[serde(rename = "websocket-accept-frame")]
    WebsocketAcceptFrame,
    #[serde(rename = "websocket-close-frame")]
    WebsocketCloseFrame,
    #[serde(rename = "websocket-continuation-frame")]
    WebsocketContinuationFrame,
    #[serde(rename = "websocket-disconnect-frame")]
    WebsocketDisconnectFrame,
    #[serde(rename = "websocket-ping-frame")]
    WebsocketPingFrame,
    #[serde(rename = "websocket-pong-frame")]
    WebsocketPongFrame,
    #[serde(rename = "websocket-receive-bytes")]
    WebsocketReceiveBytes,
    #[serde(rename = "websocket-receive-text")]
    WebsocketReceiveText,
    #[serde(rename = "websocket-send-bytes")]
    WebsocketSendBytes,
    #[serde(rename = "websocket-send-text")]
    WebsocketSendText,
    #[serde(rename = "webtransport-datagram-frame")]
    WebtransportDatagramFrame,
    #[serde(rename = "webtransport-stream-frame")]
    WebtransportStreamFrame,
}
