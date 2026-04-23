export enum TransportEventType {
  HTTP_REQUEST = "http.request",
  HTTP_DISCONNECT = "http.disconnect",
  HTTP_RESPONSE_START = "http.response.start",
  HTTP_RESPONSE_BODY = "http.response.body",
  HTTP_RESPONSE_PATHSEND = "http.response.pathsend",
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
  LIFESPAN_STARTUP = "lifespan.startup",
  LIFESPAN_STARTUP_COMPLETE = "lifespan.startup.complete",
  LIFESPAN_STARTUP_FAILED = "lifespan.startup.failed",
  LIFESPAN_SHUTDOWN = "lifespan.shutdown",
  LIFESPAN_SHUTDOWN_COMPLETE = "lifespan.shutdown.complete",
  LIFESPAN_SHUTDOWN_FAILED = "lifespan.shutdown.failed",
  TRANSPORT_EMIT_COMPLETE = "transport.emit.complete",
}
export interface ContractEvent {
  type: TransportEventType;
  message?: string | null;
  payload?: Record<string, unknown>;
}
