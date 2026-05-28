# Send Event Outline

This note captures the proposed outbound `send` event coverage for
`tigr-asgi-contract`. In ASGI terms, `send` is the async callable, and the
events below are the outbound message dictionaries passed to that callable.

The contract should classify canonical ASGI send events with attributes rather
than introduce a second event-name system. Where one ASGI send event can
represent multiple transport lanes, the contract should derive classification
from the scope plus payload discriminators such as stream direction, stream id,
or selected binding.

The proposed classification row shape is:

```text
event + channel + scope_type + binding + family + exchange + direction
```

For this file, `channel` is always `send`.

## HTTP Send Events

| Send event | Scope | Binding(s) | Purpose |
| --- | --- | --- | --- |
| `http.response.start` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Emit response status and headers. |
| `http.response.body` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Emit response body bytes or body chunks. |
| `http.response.pathsend` | `http` | `http.stream` / extension | Emit file/path-send extension payload. |
| `http.response.trailers` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Proposed: emit HTTP trailers after body when announced. |
| `http.response.informational` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Proposed: emit 1xx informational response such as `103 Early Hints`. |

## HTTP Send Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `http.response.start` | `send` | `rest`, `jsonrpc`, `http.stream`, `sse` | `request` | `unary` | `server_to_client` |
| `http.response.body` | `send` | `rest`, `jsonrpc`; bounded body | `request` | `unary` | `server_to_client` |
| `http.response.body` | `send` | `http.stream`; chunked body | `stream` | `server_stream` | `server_to_client` |
| `http.response.body` | `send` | `sse`; event-stream body | `stream` | `server_stream` | `server_to_client` |
| `http.response.trailers` | `send` | `rest`, `jsonrpc` | `request` | `unary` | `server_to_client` |
| `http.response.trailers` | `send` | `http.stream`, `sse` | `stream` | `server_stream` | `server_to_client` |
| `http.response.informational` | `send` | `rest`, `jsonrpc`, `http.stream`, `sse` | `request` | `unary` | `server_to_client` |

## WebSocket Send Events

| Send event | Scope | Purpose |
| --- | --- | --- |
| `websocket.accept` | `websocket` | Accept the WebSocket connection and optionally select subprotocol. |
| `websocket.send` | `websocket` | Emit outbound WebSocket message. |
| `websocket.close` | `websocket` | Close or reject the WebSocket connection. |

## WebSocket Send Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `websocket.accept` | `send` | `scheme=ws/wss` | `session` | `unary` | `server_to_client` |
| `websocket.send` | `send` | text or bytes message | `message` | `duplex` | `server_to_client` |
| `websocket.close` | `send` | close or reject | `session` | `unary` | `server_to_client` |

## WebTransport Send Events

| Send event | Scope | Purpose |
| --- | --- | --- |
| `webtransport.accept` | `webtransport` | Accept WebTransport session. |
| `webtransport.stream.send` | `webtransport` | Emit bytes/chunks on a WebTransport stream. |
| `webtransport.stream.close` | `webtransport` | Close/finish a WebTransport stream. |
| `webtransport.stream.reset` | `webtransport` | Reset a WebTransport stream. |
| `webtransport.stream.stop_sending` | `webtransport` | Request peer stop sending on a stream. |
| `webtransport.datagram.send` | `webtransport` | Emit WebTransport datagram. |
| `webtransport.close` | `webtransport` | Close WebTransport session. |

## WebTransport Send Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `webtransport.accept` | `send` | session accept | `session` | `unary` | `server_to_client` |
| `webtransport.stream.send` | `send` | `stream_direction=bidi` | `stream` | `duplex` | `server_to_client` |
| `webtransport.stream.send` | `send` | `stream_direction=server_to_client` | `stream` | `server_stream` | `server_to_client` |
| `webtransport.stream.close` | `send` | `stream_direction=bidi` | `stream` | `duplex` | `server_to_client` |
| `webtransport.stream.close` | `send` | `stream_direction=server_to_client` | `stream` | `server_stream` | `server_to_client` |
| `webtransport.stream.reset` | `send` | `stream_direction=bidi` | `stream` | `duplex` | `server_to_client` |
| `webtransport.stream.reset` | `send` | `stream_direction=client_to_server` | `stream` | `client_stream` | `server_to_client` |
| `webtransport.stream.reset` | `send` | `stream_direction=server_to_client` | `stream` | `server_stream` | `server_to_client` |
| `webtransport.stream.stop_sending` | `send` | target `stream_direction=bidi` | `stream` | `duplex` | `server_to_client` |
| `webtransport.stream.stop_sending` | `send` | target `stream_direction=client_to_server` | `stream` | `client_stream` | `server_to_client` |
| `webtransport.stream.stop_sending` | `send` | target `stream_direction=server_to_client` | `stream` | `server_stream` | `server_to_client` |
| `webtransport.datagram.send` | `send` | datagram payload | `datagram` | `duplex` | `server_to_client` |
| `webtransport.close` | `send` | session close | `session` | `unary` | `server_to_client` |

## Lifespan Send Events

| Send event | Scope | Purpose |
| --- | --- | --- |
| `lifespan.startup.complete` | `lifespan` | App startup succeeded. |
| `lifespan.startup.failed` | `lifespan` | App startup failed. |
| `lifespan.shutdown.complete` | `lifespan` | App shutdown succeeded. |
| `lifespan.shutdown.failed` | `lifespan` | App shutdown failed. |

## Cross-Cutting Send Events

| Send event | Scope | Purpose |
| --- | --- | --- |
| `transport.emit.complete` | `http`, `websocket`, `webtransport` | Contract-level completion marker after outbound emission. |
| `transport.emit.failed` | `http`, `websocket`, `webtransport` | Contract-level failure marker after outbound emission fails. |

## Boundary

Canonical ASGI send event names remain names such as:

```text
http.response.body
websocket.send
webtransport.datagram.send
```

Contract classification should be derived from the ASGI event name, channel,
scope, and payload discriminators. It should not require a parallel event-name
field.
