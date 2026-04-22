# Proposed Schema Matrix

| Schema path | Category | Status | Parent / referenced by | Purpose | Needed for |
| --- | --- | --- | --- | --- | --- |
| contract/schemas/scope.schema.json | scope-root | exists | root | Canonical ASGI connection scope object | Root object for all scope validation |
| contract/schemas/asgi.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI metadata object with version and spec_version | ASGI version compatibility and per-protocol spec negotiation |
| contract/schemas/scope-type.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Scope type enum | Shared enum for http websocket lifespan webtransport |
| contract/schemas/scheme.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | URI scheme enum and constraints | http https ws wss and proxy-derived scheme validation |
| contract/schemas/http-version.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | HTTP protocol version enum | HTTP/1.0 HTTP/1.1 HTTP/2 and future H3 profile alignment |
| contract/schemas/method.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | HTTP method constraints | REST JSON-RPC HTTP stream and FastAPI route method validation |
| contract/schemas/path.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Decoded ASGI path constraints | Decoded UTF-8 path excluding query string |
| contract/schemas/raw-path.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Raw path byte encoding schema | Original path bytes preservation and percent-encoding fidelity |
| contract/schemas/root-path.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI root_path mount prefix schema | FastAPI mounts proxy prefixes and sub-application routing |
| contract/schemas/query-string.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Raw query_string bytes schema | Preserve raw query bytes ordering repeated params and percent encoding |
| contract/schemas/headers.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Header list schema preserving duplicates and order | ASGI header correctness for HTTP WebSocket H2 H3 |
| contract/schemas/header-pair.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Single byte-safe header pair schema | Reusable header item with explicit byte encoding |
| contract/schemas/client.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI client tuple schema | Remote peer address and proxy-derived effective client |
| contract/schemas/server.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI server tuple schema | Host port and Unix socket path with null port support |
| contract/schemas/state.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI state namespace schema | Lifespan state propagation into request scopes |
| contract/schemas/extensions.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | ASGI extensions object schema | Standard and project extension container |
| contract/schemas/transport.schema.json | scope-child | exists | contract/schemas/scope.schema.json | Transport metadata schema | Binding network secure ALPN TLS and framing metadata |
| contract/schemas/family-capabilities.schema.json | scope-child | proposed | contract/schemas/scope.schema.json | Family capability flags schema | Request session message stream datagram capability declaration |
| contract/schemas/ext/websocket.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | WebSocket scope extension | Subprotocol and WebSocket-specific metadata |
| contract/schemas/ext/sse.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | SSE scope extension | Retry and last-event-id metadata |
| contract/schemas/ext/webtransport.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | WebTransport scope extension | Session stream datagram capability metadata |
| contract/schemas/ext/tls.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | ASGI TLS extension-compatible metadata | HTTPS WSS TLS version cipher server/client certificate data |
| contract/schemas/ext/mtls.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | mTLS client identity extension | Client certificate chain verified identity and verification errors |
| contract/schemas/ext/forwarded.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | Trusted forwarded header metadata | Proxy forwarding trust chain effective scheme client server root_path |
| contract/schemas/ext/proxy-protocol.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | PROXY protocol metadata | HAProxy PROXY v1/v2 preface and TLV data |
| contract/schemas/ext/discovery.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | Transport/service discovery metadata | Discovery source and advertised alternatives |
| contract/schemas/ext/alt-svc.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | Alt-Svc advertisement schema | HTTP alternative service advertisement for h2 h3 etc |
| contract/schemas/ext/svcb.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | DNS SVCB record schema | Service binding parameters such as alpn port hints ech |
| contract/schemas/ext/https-rr.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | DNS HTTPS RR schema | HTTPS record specialization of SVCB |
| contract/schemas/ext/ech.schema.json | scope-extension | proposed | contract/schemas/extensions.schema.json | ECH configuration advertisement schema | Encrypted ClientHello discovery metadata |
| contract/schemas/event.schema.json | event | exists | contract/schemas/event.schema.json | Transport event union schema | Top-level event type dispatch |
| contract/schemas/events/http-request.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI http.request payload schema | Request body chunks body and more_body |
| contract/schemas/events/http-disconnect.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI http.disconnect payload schema | Client/server disconnect observation |
| contract/schemas/events/http-response-start.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI http.response.start payload schema | Status response headers and trailers flag |
| contract/schemas/events/http-response-body.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI http.response.body payload schema | Response body chunks and more_body |
| contract/schemas/events/http-response-trailers.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI http.response.trailers payload schema | Response trailers after body |
| contract/schemas/events/websocket-connect.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.connect payload schema | WebSocket handshake receive event |
| contract/schemas/events/websocket-accept.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.accept payload schema | Subprotocol and handshake response headers |
| contract/schemas/events/websocket-receive.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.receive payload schema | Text bytes exclusivity for inbound messages |
| contract/schemas/events/websocket-send.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.send payload schema | Text bytes exclusivity for outbound messages |
| contract/schemas/events/websocket-close.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.close payload schema | Close code and reason |
| contract/schemas/events/websocket-disconnect.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI websocket.disconnect payload schema | Disconnect code and reason |
| contract/schemas/events/lifespan-startup.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.startup schema | Application startup lifecycle receive frame |
| contract/schemas/events/lifespan-startup-complete.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.startup.complete schema | Successful startup send frame |
| contract/schemas/events/lifespan-startup-failed.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.startup.failed schema | Startup failure send frame with message |
| contract/schemas/events/lifespan-shutdown.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.shutdown schema | Application shutdown lifecycle receive frame |
| contract/schemas/events/lifespan-shutdown-complete.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.shutdown.complete schema | Successful shutdown send frame |
| contract/schemas/events/lifespan-shutdown-failed.schema.json | event | proposed | contract/schemas/event.schema.json | ASGI lifespan.shutdown.failed schema | Shutdown failure send frame with message |
| contract/schemas/events/webtransport-connect.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport connect event schema | Session connect event |
| contract/schemas/events/webtransport-accept.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport accept event schema | Session accept event |
| contract/schemas/events/webtransport-stream-receive.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport stream receive schema | Inbound stream chunk payload |
| contract/schemas/events/webtransport-stream-send.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport stream send schema | Outbound stream chunk payload |
| contract/schemas/events/webtransport-datagram-receive.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport datagram receive schema | Inbound datagram payload |
| contract/schemas/events/webtransport-datagram-send.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport datagram send schema | Outbound datagram payload |
| contract/schemas/events/webtransport-disconnect.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport disconnect schema | Session disconnect event |
| contract/schemas/events/webtransport-close.schema.json | event | proposed | contract/schemas/event.schema.json | WebTransport close schema | Session close code reason and stream/datagram closure |
| contract/schemas/events/transport-emit-complete.schema.json | event | proposed | contract/schemas/event.schema.json | Emission completion event schema | Accepted/flushed completion semantics |
| contract/schemas/framing/raw.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Raw payload framing schema | Opaque WebSocket/WebTransport payloads |
| contract/schemas/framing/bytes.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Bytes payload framing schema | Binary HTTP/body payloads with explicit encoding |
| contract/schemas/framing/json.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON payload framing schema | REST stream SSE WebSocket WebTransport JSON payloads |
| contract/schemas/framing/jsonrpc.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC union envelope schema | JSON-RPC transport envelope dispatch |
| contract/schemas/framing/jsonrpc-request.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC request object schema | method params id request correlation |
| contract/schemas/framing/jsonrpc-response.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC response object schema | result id response correlation |
| contract/schemas/framing/jsonrpc-error.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC error object schema | error code message data correlation |
| contract/schemas/framing/jsonrpc-notification.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC notification object schema | method params without id |
| contract/schemas/framing/jsonrpc-batch.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | JSON-RPC batch array schema | Multiple JSON-RPC envelopes in one payload |
| contract/schemas/framing/sse.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | SSE stream framing union schema | SSE field/event parsing |
| contract/schemas/framing/sse-event.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Single SSE event schema | event data id retry comments heartbeat lines |
| contract/schemas/framing/multipart.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Multipart body schema | Multipart/form-data and multipart/mixed envelopes |
| contract/schemas/framing/multipart-part.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Multipart part schema | Part headers body chunks names filenames |
| contract/schemas/framing/app.schema.json | framing-envelope | proposed | contract/schemas/transport.schema.json | Application envelope schema | App-defined multiplex keys and discriminators |
| contract/schemas/frames/http2.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | HTTP/2 frame/profile schema | DATA HEADERS RST_STREAM SETTINGS PUSH_PROMISE PING GOAWAY WINDOW_UPDATE CONTINUATION |
| contract/schemas/frames/http3.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | HTTP/3 frame/profile schema | DATA HEADERS SETTINGS PUSH_PROMISE CANCEL_PUSH GOAWAY MAX_PUSH_ID H3 DATAGRAM |
| contract/schemas/frames/quic.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | QUIC transport frame schema | STREAM DATAGRAM RESET_STREAM STOP_SENDING CONNECTION_CLOSE path and connection-id lifecycle |
| contract/schemas/frames/capsule.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | HTTP Capsule protocol frame schema | Capsule type context id and payload for H3 extensions |
| contract/schemas/frames/http-datagram.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | HTTP Datagram frame schema | Datagram context IDs for H3/QUIC extension flows |
| contract/schemas/frames/websocket-frame.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | WebSocket protocol frame schema | opcode fin continuation ping pong close text binary |
| contract/schemas/frames/webtransport-stream.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | WebTransport stream frame schema | Stream id direction reset stop-sending and payload chunks |
| contract/schemas/frames/webtransport-datagram.schema.json | protocol-frame | proposed | contract/schemas/transport.schema.json | WebTransport datagram frame schema | Datagram context size payload and drop/error metadata |
