# tigr_asgi_contract_rs

Generated Rust enums, models, and validators for the Tigr ASGI contract. Generated from the canonical `contract/` directory in this repository.

The Rust crate exposes serde-friendly enums, models, registries, and validator helpers.

## Contract Package Matrix

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | `tigr-asgi-contract` | `0.1.0` | `packages/contract-py` | 15 | Pydantic models plus validator helpers |
| npm | `@tigr/asgi-contract` | `0.1.0` | `packages/contract-npm` | 18 | TypeScript surface plus TSX badges/views |
| rust | **`tigr_asgi_contract_rs`** | `0.1.0` | `packages/contract-rs` | 15 | Serde-friendly enums, models, validators |

## Generated Surface Matrix

| Module | Export surface |
| --- | --- |
| `bindings` | `src/bindings.rs` |
| `capabilities` | `src/capabilities.rs` |
| `compatibility` | `src/compatibility.rs` |
| `completion` | `src/completion.rs` |
| `events` | `src/events.rs` |
| `exchanges` | `src/exchanges.rs` |
| `families` | `src/families.rs` |
| `ids` | `src/ids.rs` |
| `models` | `src/models.rs` |
| `registry` | `src/registry.rs` |
| `scope` | `src/scope.rs` |
| `scope_types` | `src/scope_types.rs` |
| `subevents` | `src/subevents.rs` |
| `validators` | `src/validators.rs` |
| `version` | `src/version.rs` |

## Binding Support Matrix

| Binding | Exchange | Required families | Optional families | Required subevents | Optional subevents | Derived subevents |
| --- | --- | --- | --- | --- | --- | --- |
| `rest` | `unary` | `request` | `stream` | 6 | 9 | 0 |
| `jsonrpc` | `unary` | `request` | `stream` | 6 | 9 | 1 |
| `http.stream` | `server_stream` | `request`, `stream` | - | 10 | 7 | 2 |
| `sse` | `server_stream` | `request`, `session`, `message`, `stream` | - | 13 | 14 | 1 |
| `websocket` | `duplex` | `session`, `message` | - | 8 | 9 | 0 |
| `webtransport` | `duplex` | `session`, `stream`, `datagram` | `message` | 15 | 16 | 0 |

See the repository-level README for authoring workflow, release sequencing, and cross-ecosystem package context.
