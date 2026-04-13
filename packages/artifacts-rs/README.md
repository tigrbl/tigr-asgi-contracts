# tigr_contract_artifacts_rs

Canonical Rust artifact crate for the Tigr ASGI contract. Generated from the canonical `contract/` directory in this repository.

Rust consumers get embedded artifact accessors without needing runtime filesystem lookups.

## Artifact Package Matrix

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | `tigr-contract-artifacts` | `0.1.0` | `packages/artifacts-py` | 1 | Filesystem access helpers over vendored artifacts |
| npm | `@tigr/contract-artifacts` | `0.1.0` | `packages/artifacts-npm` | 4 | Package exports over vendored artifact files |
| rust | **`tigr_contract_artifacts_rs`** | `0.1.0` | `packages/artifacts-rs` | 1 | Embedded accessors for YAML, JSON, manifest, checksums |

## Artifact Inventory Matrix

| Artifact path | Category | SHA-256 |
| --- | --- | --- |
| `bindings.yaml` | registry | `fa1438b1363b` |
| `capabilities.yaml` | registry | `389e6a905497` |
| `compatibility.yaml` | registry | `7f79f950b450` |
| `completion.yaml` | registry | `036f6b37c6bc` |
| `exchanges.yaml` | registry | `6c7f8728836f` |
| `families.yaml` | registry | `75debe47a1e6` |
| `ids.yaml` | registry | `aec52c6b3ef7` |
| `legality/binding_family.yaml` | legality | `d73cf6ef3095` |
| `legality/binding_subevent.yaml` | legality | `d6935ac0f993` |
| `legality/family_subevent.yaml` | legality | `36fda0df963c` |
| `schemas/compatibility.schema.json` | schema | `309ba3093d34` |
| `schemas/completion.schema.json` | schema | `26e6082df0cd` |
| `schemas/event.schema.json` | schema | `67bb67ddeaab` |
| `schemas/scope.schema.json` | schema | `2698752580f8` |
| `schemas/sse.schema.json` | schema | `42e060246611` |
| `schemas/transport.schema.json` | schema | `865875cec84c` |
| `schemas/websocket.schema.json` | schema | `b4e38fad362c` |
| `schemas/webtransport.schema.json` | schema | `e6f9300bfe82` |
| `scope_types.yaml` | registry | `620b4d20180e` |
| `subevents.yaml` | registry | `b0abf1e13da9` |

## Contract Coverage Matrix

| Field | Value |
| --- | --- |
| Contract version | `0.1.0` |
| Bindings | 6 |
| Families | 5 |
| Scope types | 4 |
| Schemas | 8 |
| Legality matrices | 3 |

See the repository-level README for the cross-ecosystem contract and package overview.
