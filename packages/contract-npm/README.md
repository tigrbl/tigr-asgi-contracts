# @tigr/asgi-contract

Generated TypeScript and TSX contract surfaces for the Tigr ASGI contract. Generated from the canonical `contract/` directory in this repository.

The npm package exposes TypeScript registries and validators plus TSX helpers for UI-facing contract rendering.

## Contract Package Matrix

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | `tigr-asgi-contract` | `0.1.0` | `packages/contract-py` | 15 | Pydantic models plus validator helpers |
| npm | **`@tigr/asgi-contract`** | `0.1.0` | `packages/contract-npm` | 18 | TypeScript surface plus TSX badges/views |
| rust | `tigr_asgi_contract_rs` | `0.1.0` | `packages/contract-rs` | 15 | Serde-friendly enums, models, validators |

## Generated Surface Matrix

| Module | Export surface |
| --- | --- |
| `bindings` | `src/bindings.ts` |
| `capabilities` | `src/capabilities.ts` |
| `compatibility` | `src/compatibility.ts` |
| `completion` | `src/completion.ts` |
| `events` | `src/events.ts` |
| `exchanges` | `src/exchanges.ts` |
| `families` | `src/families.ts` |
| `ids` | `src/ids.ts` |
| `models` | `src/models.ts` |
| `registry` | `src/registry.ts` |
| `scope` | `src/scope.ts` |
| `scope_types` | `src/scope_types.ts` |
| `subevents` | `src/subevents.ts` |
| `validators` | `src/validators.ts` |
| `tsx/BindingBadge` | `tsx/BindingBadge` |
| `tsx/FamilyBadge` | `tsx/FamilyBadge` |
| `tsx/ScopeView` | `tsx/ScopeView` |
| `tsx/SubeventBadge` | `tsx/SubeventBadge` |

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
