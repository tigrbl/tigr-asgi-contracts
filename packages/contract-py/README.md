# tigr-asgi-contract

Generated Python enums, models, and validators for the Tigr ASGI contract. Generated from the canonical `contract/` directory in this repository.

The Python package exposes enum-like values, Pydantic models, registry helpers, and validators.

## Contract Package Matrix

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | **`tigr-asgi-contract`** | `0.1.0` | `packages/contract-py` | 15 | Pydantic models plus validator helpers |
| npm | `@tigr/asgi-contract` | `0.1.0` | `packages/contract-npm` | 18 | TypeScript surface plus TSX badges/views |
| rust | `tigr_asgi_contract_rs` | `0.1.0` | `packages/contract-rs` | 15 | Serde-friendly enums, models, validators |

## Generated Surface Matrix

| Module | Export surface |
| --- | --- |
| `bindings` | `tigr_asgi_contract/bindings.py` |
| `capabilities` | `tigr_asgi_contract/capabilities.py` |
| `compatibility` | `tigr_asgi_contract/compatibility.py` |
| `completion` | `tigr_asgi_contract/completion.py` |
| `events` | `tigr_asgi_contract/events.py` |
| `exchanges` | `tigr_asgi_contract/exchanges.py` |
| `families` | `tigr_asgi_contract/families.py` |
| `ids` | `tigr_asgi_contract/ids.py` |
| `models` | `tigr_asgi_contract/models.py` |
| `registry` | `tigr_asgi_contract/registry.py` |
| `scope` | `tigr_asgi_contract/scope.py` |
| `scope_types` | `tigr_asgi_contract/scope_types.py` |
| `subevents` | `tigr_asgi_contract/subevents.py` |
| `validators` | `tigr_asgi_contract/validators.py` |
| `version` | `tigr_asgi_contract/version.py` |

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
