export enum TransportEventType {
  HTTP_REQUEST = "http.request",
  HTTP_DISCONNECT = "http.disconnect",
  HTTP_RESPONSE_START = "http.response.start",
  HTTP_RESPONSE_BODY = "http.response.body",
  WEBSOCKET_CONNECT = "websocket.connect",
  WEBSOCKET_RECEIVE = "websocket.receive",
  WEBSOCKET_DISCONNECT = "websocket.disconnect",
  WEBSOCKET_ACCEPT = "websocket.accept",
  WEBSOCKET_SEND = "websocket.send",
  WEBSOCKET_CLOSE = "websocket.close",
  WEBTRANSPORT_CONNECT = "webtransport.connect",
  WEBTRANSPORT_ACCEPT = "webtransport.accept",
  WEBTRANSPORT_STREAM_RECEIVE = "webtransport.stream.receive",
  WEBTRANSPORT_STREAM_SEND = "webtransport.stream.send",
  WEBTRANSPORT_DATAGRAM_RECEIVE = "webtransport.datagram.receive",
  WEBTRANSPORT_DATAGRAM_SEND = "webtransport.datagram.send",
  WEBTRANSPORT_DISCONNECT = "webtransport.disconnect",
  WEBTRANSPORT_CLOSE = "webtransport.close",
  TRANSPORT_EMIT_COMPLETE = "transport.emit.complete",
}
export interface ContractEvent {
  type: TransportEventType;
  payload?: Record<string, unknown>;
}
