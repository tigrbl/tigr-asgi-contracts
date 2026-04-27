# Untracked Frame Features Matrix

Source comparison: `contract/frames.yaml` frame definitions vs `feat:frame-*` rows in `contract/surfaces.yaml`.

| Frame | Kind | Binding | Expected feature ID | Current tracking | Source |
| --- | --- | --- | --- | --- | --- |
| `asgi-tls-extension` | `extension-frame` | `*` | `feat:frame-asgi-tls-extension` | missing | `contract/frames.yaml` |
| `grpc` | `contract-framing` | `http.stream` | `feat:frame-grpc` | missing | `contract/frames.yaml` |
| `http-request-body-chunk` | `wire-frame` | `http.stream` | `feat:frame-http-request-body-chunk` | missing | `contract/frames.yaml` |
| `http-response-body-chunk` | `wire-frame` | `http.stream` | `feat:frame-http-response-body-chunk` | missing | `contract/frames.yaml` |
| `http-response-start-frame` | `wire-frame` | `rest` | `feat:frame-http-response-start-frame` | missing | `contract/frames.yaml` |
| `json-rpc-request-object` | `contract-framing` | `jsonrpc` | `feat:frame-json-rpc-request-object` | missing | `contract/frames.yaml` |
| `json-rpc-response-object` | `contract-framing` | `jsonrpc` | `feat:frame-json-rpc-response-object` | missing | `contract/frames.yaml` |
| `json-rpc-notification-object` | `contract-framing` | `jsonrpc` | `feat:frame-json-rpc-notification-object` | missing | `contract/frames.yaml` |
| `json-rpc-error-object` | `contract-framing` | `jsonrpc` | `feat:frame-json-rpc-error-object` | missing | `contract/frames.yaml` |
| `sse-data-field` | `contract-framing` | `sse` | `feat:frame-sse-data-field` | missing | `contract/frames.yaml` |
| `sse-event-field` | `contract-framing` | `sse` | `feat:frame-sse-event-field` | missing | `contract/frames.yaml` |
| `sse-id-field` | `contract-framing` | `sse` | `feat:frame-sse-id-field` | missing | `contract/frames.yaml` |
| `sse-retry-field` | `contract-framing` | `sse` | `feat:frame-sse-retry-field` | missing | `contract/frames.yaml` |
| `websocket-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-frame` | missing | `contract/frames.yaml` |
| `websocket-accept-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-accept-frame` | missing | `contract/frames.yaml` |
| `websocket-close-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-close-frame` | missing | `contract/frames.yaml` |
| `websocket-continuation-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-continuation-frame` | missing | `contract/frames.yaml` |
| `websocket-disconnect-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-disconnect-frame` | missing | `contract/frames.yaml` |
| `websocket-ping-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-ping-frame` | missing | `contract/frames.yaml` |
| `websocket-pong-frame` | `wire-frame` | `websocket` | `feat:frame-websocket-pong-frame` | missing | `contract/frames.yaml` |
| `websocket-receive-bytes` | `wire-frame` | `websocket` | `feat:frame-websocket-receive-bytes` | missing | `contract/frames.yaml` |
| `websocket-receive-text` | `wire-frame` | `websocket` | `feat:frame-websocket-receive-text` | missing | `contract/frames.yaml` |
| `websocket-send-bytes` | `wire-frame` | `websocket` | `feat:frame-websocket-send-bytes` | missing | `contract/frames.yaml` |
| `websocket-send-text` | `wire-frame` | `websocket` | `feat:frame-websocket-send-text` | missing | `contract/frames.yaml` |
