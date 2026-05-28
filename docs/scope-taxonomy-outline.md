# Scope Taxonomy Outline

This note captures the proposed scope-level taxonomy for `tigr-asgi-contract`.
It is intentionally limited to the ASGI scope envelope and scope extensions.
Receive/send event classification is a separate contract concern derived from
ASGI event names, the `send` or `receive` channel, scope metadata, and event
payload discriminators.

## Scope Types

| Scope type | Covers | Notes |
| --- | --- | --- |
| `http` | H1.1, H2, H3 HTTP requests | REST, JSON-RPC, HTTP streams, and SSE all live under `type=http`. |
| `websocket` | `ws` and `wss` connections | WebSocket upgrade/session scope. |
| `webtransport` | WebTransport over H3/QUIC | Session scope for WebTransport streams and datagrams. |
| `lifespan` | ASGI startup/shutdown | App/server lifecycle. |

## HTTP Scopes

| Scope variant | `type` | `scheme` | `http_version` | Binding | Security |
| --- | --- | --- | --- | --- | --- |
| H1.1 REST | `http` | `http` | `1.1` | `rest` | Plain |
| H1.1 REST TLS | `http` | `https` | `1.1` | `rest` | TLS / optional mTLS |
| H2 REST | `http` | `https` usually | `2` | `rest` | TLS / optional mTLS |
| H3 REST | `http` | `https` | `3` | `rest` | TLS / QUIC / optional mTLS |
| H1.1 JSON-RPC | `http` | `http` | `1.1` | `jsonrpc` | Plain |
| H1.1 JSON-RPC TLS | `http` | `https` | `1.1` | `jsonrpc` | TLS / optional mTLS |
| H2 JSON-RPC | `http` | `https` usually | `2` | `jsonrpc` | TLS / optional mTLS |
| H3 JSON-RPC | `http` | `https` | `3` | `jsonrpc` | TLS / QUIC / optional mTLS |
| H1.1 HTTP stream | `http` | `http` | `1.1` | `http.stream` | Plain |
| H1.1 HTTP stream TLS | `http` | `https` | `1.1` | `http.stream` | TLS / optional mTLS |
| H2 HTTP stream | `http` | `https` usually | `2` | `http.stream` | TLS / optional mTLS |
| H3 HTTP stream | `http` | `https` | `3` | `http.stream` | TLS / QUIC / optional mTLS |
| H1.1 SSE | `http` | `http` | `1.1` | `sse` | Plain |
| H1.1 SSE TLS | `http` | `https` | `1.1` | `sse` | TLS / optional mTLS |
| H2 SSE | `http` | `https` usually | `2` | `sse` | TLS / optional mTLS |
| H3 SSE | `http` | `https` | `3` | `sse` | TLS / QUIC / optional mTLS |

## WebSocket Scopes

| Scope variant | `type` | `scheme` | `http_version` | Binding | Security |
| --- | --- | --- | --- | --- | --- |
| WS over H1.1 | `websocket` | `ws` | `1.1` | `websocket` | Plain |
| WSS over H1.1 | `websocket` | `wss` | `1.1` | `websocket` | TLS / optional mTLS |
| WS over H2 | `websocket` | `ws` / `wss` | `2` | `websocket` | Extended CONNECT semantics |
| WSS over H2 | `websocket` | `wss` | `2` | `websocket` | TLS / optional mTLS |
| WS over H3 | `websocket` | `ws` / `wss` | `3` | `websocket` | Extended CONNECT over H3 if supported |
| WSS over H3 | `websocket` | `wss` | `3` | `websocket` | TLS / QUIC / optional mTLS |

## WebTransport Scopes

| Scope variant | `type` | `scheme` | `http_version` | Binding | Security |
| --- | --- | --- | --- | --- | --- |
| WT over H3 | `webtransport` | `https` / `wts` convention | `3` | `webtransport` | TLS / QUIC |
| WT over H3 mTLS | `webtransport` | `https` / `wts` convention | `3` | `webtransport` | TLS / QUIC / mTLS |

## Lifespan Scope

| Scope variant | `type` | Binding | Notes |
| --- | --- | --- | --- |
| App lifespan | `lifespan` | none | Startup/shutdown lifecycle. |

## Scope Extension Areas

| Extension area | Applies to | Fields |
| --- | --- | --- |
| `ext.transport` | All transport scopes | `binding`, `network`, `secure`, `alpn`, `tls`, `framing` |
| `ext.websocket` | `websocket` | Selected/requested subprotocols |
| `ext.sse` | `http` with `sse` binding | `last_event_id`, `retry_ms` |
| `ext.webtransport` | `webtransport` | `session_id`, bidi/unidi/datagram support, max datagram size |
| `ext.mtls` or `ext.transport.tls` | TLS scopes | Client cert presence, verification, peer identity, trust source |
| `ext.forwarded` | Proxied HTTP/WS/WT | Trusted forwarded scheme/host/client metadata |
| `ext.http` | HTTP scopes | Optional effective protocol metadata and stream id for H2/H3 if needed |

## Scope Boundary

The canonical scope types should remain:

```text
http
websocket
webtransport
lifespan
```

Scope variants are expressed through:

- `scheme`
- `http_version`
- `ext.transport.binding`
- `ext.transport.network`
- `ext.transport.alpn`
- TLS / mTLS metadata
- transport-specific extensions such as `ext.websocket`, `ext.sse`, and
  `ext.webtransport`

The scope should not contain receive/send event names or parallel classifier
event names such as:

```text
http.rest.request.receive
ws.message.emit
wt.bidi_stream.chunk_receive
```

Those examples are better represented as canonical event names plus attributes
such as `channel`, `binding`, `family`, `exchange`, and `direction`. That
classification belongs to event validation and contract registry metadata, not
the scope envelope itself.
