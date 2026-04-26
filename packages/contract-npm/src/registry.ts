export const BINDING_FAMILY_MATRIX = {
  "rest": {
    "request": "R",
    "session": "F",
    "message": "F",
    "stream": "O",
    "datagram": "F"
  },
  "jsonrpc": {
    "request": "R",
    "session": "F",
    "message": "F",
    "stream": "O",
    "datagram": "F"
  },
  "http.stream": {
    "request": "R",
    "session": "F",
    "message": "F",
    "stream": "R",
    "datagram": "F"
  },
  "sse": {
    "request": "R",
    "session": "R",
    "message": "R",
    "stream": "R",
    "datagram": "F"
  },
  "websocket": {
    "request": "F",
    "session": "R",
    "message": "R",
    "stream": "F",
    "datagram": "F"
  },
  "webtransport": {
    "request": "F",
    "session": "R",
    "message": "O",
    "stream": "R",
    "datagram": "R"
  }
} as const;

export const FAMILY_SUBEVENT_MATRIX = {
  "request": {
    "request.open": "R",
    "request.body_in": "R",
    "request.chunk_in": "R",
    "request.accept": "R",
    "request.close": "R",
    "request.disconnect": "R",
    "response.open": "R",
    "response.body_out": "R",
    "response.chunk_out": "R",
    "response.close": "R",
    "response.emit_complete": "R"
  },
  "session": {
    "session.open": "R",
    "session.accept": "R",
    "session.ready": "R",
    "session.heartbeat": "R",
    "session.sync": "R",
    "session.close": "R",
    "session.disconnect": "R",
    "session.emit_complete": "R"
  },
  "message": {
    "message.in": "R",
    "message.decode": "R",
    "message.handle": "R",
    "message.out": "R",
    "message.ack": "R",
    "message.nack": "R",
    "message.replay": "R",
    "message.snapshot": "R",
    "message.emit_complete": "R"
  },
  "stream": {
    "stream.open": "R",
    "stream.chunk_in": "R",
    "stream.chunk_out": "R",
    "stream.flush": "R",
    "stream.finalize": "R",
    "stream.abort": "R",
    "stream.close": "R",
    "stream.emit_complete": "R"
  },
  "datagram": {
    "datagram.in": "R",
    "datagram.handle": "R",
    "datagram.out": "R",
    "datagram.ack": "R",
    "datagram.emit_complete": "R"
  }
} as const;

export const BINDING_SUBEVENT_MATRIX = {
  "rest": {
    "request.open": "R",
    "request.body_in": "R",
    "request.chunk_in": "F",
    "request.accept": "O",
    "request.close": "R",
    "request.disconnect": "O",
    "response.open": "R",
    "response.body_out": "R",
    "response.chunk_out": "F",
    "response.close": "O",
    "response.emit_complete": "R",
    "session.open": "F",
    "session.accept": "F",
    "session.ready": "F",
    "session.heartbeat": "F",
    "session.sync": "F",
    "session.close": "F",
    "session.disconnect": "F",
    "session.emit_complete": "F",
    "message.in": "F",
    "message.decode": "F",
    "message.handle": "F",
    "message.out": "F",
    "message.ack": "F",
    "message.nack": "F",
    "message.replay": "F",
    "message.snapshot": "F",
    "message.emit_complete": "F",
    "stream.open": "O",
    "stream.chunk_in": "O",
    "stream.chunk_out": "O",
    "stream.flush": "F",
    "stream.finalize": "O",
    "stream.abort": "F",
    "stream.close": "O",
    "stream.emit_complete": "O",
    "datagram.in": "F",
    "datagram.handle": "F",
    "datagram.out": "F",
    "datagram.ack": "F",
    "datagram.emit_complete": "F"
  },
  "jsonrpc": {
    "request.open": "R",
    "request.body_in": "R",
    "request.chunk_in": "F",
    "request.accept": "O",
    "request.close": "R",
    "request.disconnect": "O",
    "response.open": "R",
    "response.body_out": "R",
    "response.chunk_out": "F",
    "response.close": "O",
    "response.emit_complete": "R",
    "session.open": "F",
    "session.accept": "F",
    "session.ready": "F",
    "session.heartbeat": "F",
    "session.sync": "F",
    "session.close": "F",
    "session.disconnect": "F",
    "session.emit_complete": "F",
    "message.in": "F",
    "message.decode": "D",
    "message.handle": "F",
    "message.out": "F",
    "message.ack": "F",
    "message.nack": "F",
    "message.replay": "F",
    "message.snapshot": "F",
    "message.emit_complete": "F",
    "stream.open": "O",
    "stream.chunk_in": "O",
    "stream.chunk_out": "O",
    "stream.flush": "F",
    "stream.finalize": "O",
    "stream.abort": "F",
    "stream.close": "O",
    "stream.emit_complete": "O",
    "datagram.in": "F",
    "datagram.handle": "F",
    "datagram.out": "F",
    "datagram.ack": "F",
    "datagram.emit_complete": "F"
  },
  "http.stream": {
    "request.open": "R",
    "request.body_in": "O",
    "request.chunk_in": "D",
    "request.accept": "O",
    "request.close": "R",
    "request.disconnect": "O",
    "response.open": "R",
    "response.body_out": "O",
    "response.chunk_out": "D",
    "response.close": "O",
    "response.emit_complete": "R",
    "session.open": "F",
    "session.accept": "F",
    "session.ready": "F",
    "session.heartbeat": "F",
    "session.sync": "F",
    "session.close": "F",
    "session.disconnect": "F",
    "session.emit_complete": "F",
    "message.in": "F",
    "message.decode": "F",
    "message.handle": "F",
    "message.out": "F",
    "message.ack": "F",
    "message.nack": "F",
    "message.replay": "F",
    "message.snapshot": "F",
    "message.emit_complete": "F",
    "stream.open": "R",
    "stream.chunk_in": "R",
    "stream.chunk_out": "R",
    "stream.flush": "O",
    "stream.finalize": "R",
    "stream.abort": "O",
    "stream.close": "R",
    "stream.emit_complete": "R",
    "datagram.in": "F",
    "datagram.handle": "F",
    "datagram.out": "F",
    "datagram.ack": "F",
    "datagram.emit_complete": "F"
  },
  "sse": {
    "request.open": "R",
    "request.body_in": "O",
    "request.chunk_in": "F",
    "request.accept": "O",
    "request.close": "R",
    "request.disconnect": "O",
    "response.open": "O",
    "response.body_out": "F",
    "response.chunk_out": "D",
    "response.close": "O",
    "response.emit_complete": "R",
    "session.open": "R",
    "session.accept": "R",
    "session.ready": "R",
    "session.heartbeat": "O",
    "session.sync": "O",
    "session.close": "R",
    "session.disconnect": "O",
    "session.emit_complete": "O",
    "message.in": "F",
    "message.decode": "F",
    "message.handle": "F",
    "message.out": "R",
    "message.ack": "F",
    "message.nack": "F",
    "message.replay": "O",
    "message.snapshot": "O",
    "message.emit_complete": "R",
    "stream.open": "R",
    "stream.chunk_in": "F",
    "stream.chunk_out": "R",
    "stream.flush": "O",
    "stream.finalize": "O",
    "stream.abort": "O",
    "stream.close": "R",
    "stream.emit_complete": "R",
    "datagram.in": "F",
    "datagram.handle": "F",
    "datagram.out": "F",
    "datagram.ack": "F",
    "datagram.emit_complete": "F"
  },
  "websocket": {
    "request.open": "F",
    "request.body_in": "F",
    "request.chunk_in": "F",
    "request.accept": "F",
    "request.close": "F",
    "request.disconnect": "F",
    "response.open": "F",
    "response.body_out": "F",
    "response.chunk_out": "F",
    "response.close": "F",
    "response.emit_complete": "F",
    "session.open": "R",
    "session.accept": "R",
    "session.ready": "R",
    "session.heartbeat": "O",
    "session.sync": "O",
    "session.close": "R",
    "session.disconnect": "O",
    "session.emit_complete": "O",
    "message.in": "R",
    "message.decode": "O",
    "message.handle": "R",
    "message.out": "R",
    "message.ack": "O",
    "message.nack": "O",
    "message.replay": "O",
    "message.snapshot": "O",
    "message.emit_complete": "R",
    "stream.open": "F",
    "stream.chunk_in": "F",
    "stream.chunk_out": "F",
    "stream.flush": "F",
    "stream.finalize": "F",
    "stream.abort": "F",
    "stream.close": "F",
    "stream.emit_complete": "F",
    "datagram.in": "F",
    "datagram.handle": "F",
    "datagram.out": "F",
    "datagram.ack": "F",
    "datagram.emit_complete": "F"
  },
  "webtransport": {
    "request.open": "F",
    "request.body_in": "F",
    "request.chunk_in": "F",
    "request.accept": "F",
    "request.close": "F",
    "request.disconnect": "F",
    "response.open": "F",
    "response.body_out": "F",
    "response.chunk_out": "F",
    "response.close": "F",
    "response.emit_complete": "F",
    "session.open": "R",
    "session.accept": "R",
    "session.ready": "R",
    "session.heartbeat": "O",
    "session.sync": "O",
    "session.close": "R",
    "session.disconnect": "O",
    "session.emit_complete": "O",
    "message.in": "O",
    "message.decode": "O",
    "message.handle": "O",
    "message.out": "O",
    "message.ack": "O",
    "message.nack": "O",
    "message.replay": "O",
    "message.snapshot": "O",
    "message.emit_complete": "O",
    "stream.open": "R",
    "stream.chunk_in": "R",
    "stream.chunk_out": "R",
    "stream.flush": "O",
    "stream.finalize": "R",
    "stream.abort": "O",
    "stream.close": "R",
    "stream.emit_complete": "R",
    "datagram.in": "R",
    "datagram.handle": "R",
    "datagram.out": "R",
    "datagram.ack": "O",
    "datagram.emit_complete": "R"
  }
} as const;

export const PROTOCOLS = {
  "http.rest": {
    "binding": "rest",
    "transport": "http",
    "secure": false,
    "scope_type": "http"
  },
  "https.rest": {
    "binding": "rest",
    "transport": "http",
    "secure": true,
    "scope_type": "http"
  },
  "http.jsonrpc": {
    "binding": "jsonrpc",
    "transport": "http",
    "secure": false,
    "scope_type": "http"
  },
  "https.jsonrpc": {
    "binding": "jsonrpc",
    "transport": "http",
    "secure": true,
    "scope_type": "http"
  },
  "http.stream": {
    "binding": "http.stream",
    "transport": "http",
    "secure": false,
    "scope_type": "http"
  },
  "https.stream": {
    "binding": "http.stream",
    "transport": "http",
    "secure": true,
    "scope_type": "http"
  },
  "http.sse": {
    "binding": "sse",
    "transport": "http",
    "secure": false,
    "scope_type": "http"
  },
  "https.sse": {
    "binding": "sse",
    "transport": "http",
    "secure": true,
    "scope_type": "http"
  },
  "ws": {
    "binding": "websocket",
    "transport": "websocket",
    "secure": false,
    "scope_type": "websocket"
  },
  "wss": {
    "binding": "websocket",
    "transport": "websocket",
    "secure": true,
    "scope_type": "websocket"
  },
  "webtransport": {
    "binding": "webtransport",
    "transport": "webtransport",
    "secure": true,
    "scope_type": "webtransport"
  },
  "asgi.pathsend": {
    "binding": "http.stream",
    "transport": "http",
    "secure": false,
    "scope_type": "http"
  }
} as const;

export const AUTOMATA = {
  "request": {
    "initial": "idle",
    "terminal": [
      "closed",
      "disconnected"
    ],
    "transitions": [
      {
        "from": "idle",
        "event": "request.open",
        "to": "open"
      },
      {
        "from": "open",
        "event": "request.body_in",
        "to": "open"
      },
      {
        "from": "open",
        "event": "request.chunk_in",
        "to": "open"
      },
      {
        "from": "open",
        "event": "request.accept",
        "to": "accepted"
      },
      {
        "from": "accepted",
        "event": "response.open",
        "to": "responding"
      },
      {
        "from": "responding",
        "event": "response.body_out",
        "to": "responding"
      },
      {
        "from": "responding",
        "event": "response.chunk_out",
        "to": "responding"
      },
      {
        "from": "responding",
        "event": "response.emit_complete",
        "to": "completing"
      },
      {
        "from": "completing",
        "event": "response.close",
        "to": "closed"
      },
      {
        "from": "open",
        "event": "request.disconnect",
        "to": "disconnected"
      }
    ]
  },
  "session": {
    "initial": "idle",
    "terminal": [
      "closed",
      "disconnected"
    ],
    "transitions": [
      {
        "from": "idle",
        "event": "session.open",
        "to": "open"
      },
      {
        "from": "open",
        "event": "session.accept",
        "to": "accepted"
      },
      {
        "from": "accepted",
        "event": "session.ready",
        "to": "ready"
      },
      {
        "from": "ready",
        "event": "session.heartbeat",
        "to": "ready"
      },
      {
        "from": "ready",
        "event": "session.sync",
        "to": "ready"
      },
      {
        "from": "ready",
        "event": "session.emit_complete",
        "to": "ready"
      },
      {
        "from": "ready",
        "event": "session.close",
        "to": "closed"
      },
      {
        "from": "ready",
        "event": "session.disconnect",
        "to": "disconnected"
      }
    ]
  },
  "message": {
    "initial": "idle",
    "terminal": [
      "complete",
      "rejected"
    ],
    "transitions": [
      {
        "from": "idle",
        "event": "message.in",
        "to": "received"
      },
      {
        "from": "received",
        "event": "message.decode",
        "to": "decoded"
      },
      {
        "from": "decoded",
        "event": "message.handle",
        "to": "handled"
      },
      {
        "from": "handled",
        "event": "message.out",
        "to": "emitted"
      },
      {
        "from": "emitted",
        "event": "message.ack",
        "to": "complete"
      },
      {
        "from": "emitted",
        "event": "message.nack",
        "to": "rejected"
      },
      {
        "from": "complete",
        "event": "message.replay",
        "to": "emitted"
      },
      {
        "from": "complete",
        "event": "message.snapshot",
        "to": "complete"
      },
      {
        "from": "emitted",
        "event": "message.emit_complete",
        "to": "complete"
      }
    ]
  },
  "stream": {
    "initial": "idle",
    "terminal": [
      "closed",
      "aborted"
    ],
    "transitions": [
      {
        "from": "idle",
        "event": "stream.open",
        "to": "open"
      },
      {
        "from": "open",
        "event": "stream.chunk_in",
        "to": "open"
      },
      {
        "from": "open",
        "event": "stream.chunk_out",
        "to": "open"
      },
      {
        "from": "open",
        "event": "stream.flush",
        "to": "open"
      },
      {
        "from": "open",
        "event": "stream.finalize",
        "to": "finalizing"
      },
      {
        "from": "finalizing",
        "event": "stream.emit_complete",
        "to": "closed"
      },
      {
        "from": "open",
        "event": "stream.close",
        "to": "closed"
      },
      {
        "from": "open",
        "event": "stream.abort",
        "to": "aborted"
      }
    ]
  },
  "datagram": {
    "initial": "idle",
    "terminal": [
      "acknowledged"
    ],
    "transitions": [
      {
        "from": "idle",
        "event": "datagram.in",
        "to": "received"
      },
      {
        "from": "received",
        "event": "datagram.handle",
        "to": "handled"
      },
      {
        "from": "handled",
        "event": "datagram.out",
        "to": "emitted"
      },
      {
        "from": "emitted",
        "event": "datagram.ack",
        "to": "acknowledged"
      },
      {
        "from": "acknowledged",
        "event": "datagram.emit_complete",
        "to": "acknowledged"
      }
    ]
  }
} as const;

export const FRAMES = {
  "app": {
    "kind": "contract-framing",
    "binding": "webtransport"
  },
  "asgi-tls-extension": {
    "kind": "extension-frame",
    "binding": "*"
  },
  "asgi-pathsend-extension": {
    "kind": "extension-frame",
    "binding": "http.stream"
  },
  "bytes": {
    "kind": "contract-framing",
    "binding": "http.stream"
  },
  "grpc": {
    "kind": "contract-framing",
    "binding": "http.stream"
  },
  "http-1-1-message": {
    "kind": "wire-frame",
    "binding": "rest"
  },
  "http-request-body-chunk": {
    "kind": "wire-frame",
    "binding": "http.stream"
  },
  "http-response-body-chunk": {
    "kind": "wire-frame",
    "binding": "http.stream"
  },
  "http-response-start-frame": {
    "kind": "wire-frame",
    "binding": "rest"
  },
  "json": {
    "kind": "contract-framing",
    "binding": "rest"
  },
  "jsonrpc": {
    "kind": "contract-framing",
    "binding": "jsonrpc"
  },
  "json-rpc-request-object": {
    "kind": "contract-framing",
    "binding": "jsonrpc"
  },
  "json-rpc-response-object": {
    "kind": "contract-framing",
    "binding": "jsonrpc"
  },
  "json-rpc-notification-object": {
    "kind": "contract-framing",
    "binding": "jsonrpc"
  },
  "json-rpc-error-object": {
    "kind": "contract-framing",
    "binding": "jsonrpc"
  },
  "raw": {
    "kind": "contract-framing",
    "binding": "websocket"
  },
  "sse": {
    "kind": "contract-framing",
    "binding": "sse"
  },
  "sse-data-field": {
    "kind": "contract-framing",
    "binding": "sse"
  },
  "sse-event-field": {
    "kind": "contract-framing",
    "binding": "sse"
  },
  "sse-id-field": {
    "kind": "contract-framing",
    "binding": "sse"
  },
  "sse-retry-field": {
    "kind": "contract-framing",
    "binding": "sse"
  },
  "websocket-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-accept-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-close-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-continuation-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-disconnect-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-ping-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-pong-frame": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-receive-bytes": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-receive-text": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-send-bytes": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "websocket-send-text": {
    "kind": "wire-frame",
    "binding": "websocket"
  },
  "webtransport-datagram-frame": {
    "kind": "wire-frame",
    "binding": "webtransport"
  },
  "webtransport-stream-frame": {
    "kind": "wire-frame",
    "binding": "webtransport"
  }
} as const;

export const EXTENSIONS = {
  "asgi.tls": {
    "scope_key": "tls",
    "fields": {
      "version": {
        "type": "string",
        "required": false
      },
      "cipher": {
        "type": "string",
        "required": false
      },
      "verified": {
        "type": "boolean",
        "required": false
      },
      "peer_identity": {
        "type": "string",
        "required": false
      },
      "peer_cert": {
        "type": "object",
        "required": false
      }
    }
  },
  "asgi.pathsend": {
    "event_type": "http.response.pathsend",
    "fields": {
      "path": {
        "type": "string",
        "required": true
      },
      "stat_result": {
        "type": "object",
        "required": false
      },
      "headers": {
        "type": "array",
        "required": false
      }
    }
  }
} as const;
