# Receive Event Outline

This note captures the proposed inbound `receive` event coverage for
`tigr-asgi-contract`. In ASGI terms, `receive` is the async callable, and the
events below are the inbound message dictionaries yielded by that callable from
the server transport toward the app/runtime.

The contract should classify canonical ASGI receive events with attributes
rather than introduce a second event-name system. Where one ASGI receive event
can represent multiple transport lanes, the contract should derive
classification from the scope plus payload discriminators such as stream
direction, stream id, selected binding, or continuation flags.

The proposed classification row shape is:

```text
event + channel + scope_type + binding + family + exchange + direction
```

For this file, `channel` is always `receive`.

## HTTP Receive Events

| Receive event | Scope | Binding(s) | Purpose |
| --- | --- | --- | --- |
| `http.request` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Receive HTTP request body or request body chunk. |
| `http.disconnect` | `http` | `rest`, `jsonrpc`, `http.stream`, `sse` | Peer disconnected before/during request or response handling. |

## HTTP Receive Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `http.request` | `receive` | `rest` | `request` | `unary` | `client_to_server` |
| `http.request` | `receive` | `jsonrpc` | `request` | `unary` | `client_to_server` |
| `http.request` | `receive` | `http.stream`; chunked body | `stream` | `client_stream` | `client_to_server` |
| `http.request` | `receive` | `sse` | `request` | `unary` | `client_to_server` |
| `http.disconnect` | `receive` | `rest`, `jsonrpc`, `sse` | `request` | `unary` | `client_to_server` |
| `http.disconnect` | `receive` | `http.stream` | `stream` | `client_stream` | `client_to_server` |

## WebSocket Receive Events

| Receive event | Scope | Purpose |
| --- | --- | --- |
| `websocket.connect` | `websocket` | Client requested WebSocket connection. |
| `websocket.receive` | `websocket` | Inbound WebSocket message. |
| `websocket.disconnect` | `websocket` | Client disconnected WebSocket session. |

## WebSocket Receive Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `websocket.connect` | `receive` | `scheme=ws/wss` | `session` | `unary` | `client_to_server` |
| `websocket.receive` | `receive` | text or bytes message | `message` | `duplex` | `client_to_server` |
| `websocket.disconnect` | `receive` | disconnect event | `session` | `unary` | `client_to_server` |

## WebTransport Receive Events

| Receive event | Scope | Purpose |
| --- | --- | --- |
| `webtransport.connect` | `webtransport` | Client requested WebTransport session. |
| `webtransport.stream.receive` | `webtransport` | Inbound WebTransport stream chunk. |
| `webtransport.stream.close` | `webtransport` | Peer closed/finished a WebTransport stream. |
| `webtransport.stream.reset` | `webtransport` | Peer reset a WebTransport stream. |
| `webtransport.stream.stop_sending` | `webtransport` | Peer requested stop sending. |
| `webtransport.datagram.receive` | `webtransport` | Inbound WebTransport datagram. |
| `webtransport.disconnect` | `webtransport` | Peer disconnected WebTransport session. |
| `webtransport.close` | `webtransport` | Peer closed WebTransport session. |

## WebTransport Receive Classification

| Event | Channel | Binding / condition | Family | Exchange | Direction |
| --- | --- | --- | --- | --- | --- |
| `webtransport.connect` | `receive` | session connect | `session` | `unary` | `client_to_server` |
| `webtransport.stream.receive` | `receive` | `stream_direction=bidi` | `stream` | `duplex` | `client_to_server` |
| `webtransport.stream.receive` | `receive` | `stream_direction=client_to_server` | `stream` | `client_stream` | `client_to_server` |
| `webtransport.stream.close` | `receive` | `stream_direction=bidi` | `stream` | `duplex` | `client_to_server` |
| `webtransport.stream.close` | `receive` | `stream_direction=client_to_server` | `stream` | `client_stream` | `client_to_server` |
| `webtransport.stream.reset` | `receive` | `stream_direction=bidi` | `stream` | `duplex` | `client_to_server` |
| `webtransport.stream.reset` | `receive` | `stream_direction=client_to_server` | `stream` | `client_stream` | `client_to_server` |
| `webtransport.stream.reset` | `receive` | `stream_direction=server_to_client` | `stream` | `server_stream` | `client_to_server` |
| `webtransport.stream.stop_sending` | `receive` | target `stream_direction=bidi` | `stream` | `duplex` | `client_to_server` |
| `webtransport.stream.stop_sending` | `receive` | target `stream_direction=client_to_server` | `stream` | `client_stream` | `client_to_server` |
| `webtransport.stream.stop_sending` | `receive` | target `stream_direction=server_to_client` | `stream` | `server_stream` | `client_to_server` |
| `webtransport.datagram.receive` | `receive` | datagram payload | `datagram` | `duplex` | `client_to_server` |
| `webtransport.disconnect` | `receive` | session disconnect | `session` | `unary` | `client_to_server` |
| `webtransport.close` | `receive` | session close | `session` | `unary` | `client_to_server` |

## Lifespan Receive Events

| Receive event | Scope | Purpose |
| --- | --- | --- |
| `lifespan.startup` | `lifespan` | Server asks app to start. |
| `lifespan.shutdown` | `lifespan` | Server asks app to shut down. |

## Cross-Cutting Receive Notes

| Concern | Applies to | Notes |
| --- | --- | --- |
| Body/chunk continuation | `http.request`, `webtransport.stream.receive` | Track `more_body`, `fin`, or equivalent continuation flag. |
| Stream identity | WebTransport streams, H2/H3 stream-aware scopes if modeled | Track `stream_id` where available. |
| Session identity | WebSocket / WebTransport | Track `session_id` where the contract adds an explicit session extension. |
| Datagram identity | WebTransport datagrams | Optional `datagram_id` is useful for tracing and evidence. |
| Framing | HTTP body, WebSocket message, WebTransport stream/datagram | Scope, binding, or event classification should declare legal framings; event payload carries bytes/text. |

## Boundary

Canonical ASGI receive event names remain names such as:

```text
http.request
websocket.receive
webtransport.stream.receive
```

Contract classification should be derived from the ASGI event name, channel,
scope, and payload discriminators. It should not require a parallel event-name
field.
