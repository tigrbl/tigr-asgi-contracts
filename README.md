# tigr-asgi-contracts

`contract/` is the canonical source of truth for the Tigr ASGI contract. This repository publishes canonical artifacts plus generated downstream contract packages for Python, npm, and Rust.

## Release Matrix

| Field | Value |
| --- | --- |
| Contract name | `tigr-asgi-contract` |
| Contract version | `0.1.0` |
| Artifact version | `0.1.0` |
| Serde version | `1` |
| Schema draft | `2020-12` |
| Bindings | 6 |
| Families | 5 |
| Scope types | 4 |
| Schemas | 8 |
| Legality matrices | 3 |
| Tracked artifact files | 20 |

## Binding Matrix

Status counts derive from `contract/legality/binding_family.yaml` and `contract/legality/binding_subevent.yaml`.

| Binding | Scope | Exchange | Protocols | Required families | Optional families | Required subevents | Optional subevents | Derived subevents | Framing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rest` | `http` | `unary` | `http.rest`, `https.rest` | `request` | `stream` | 6 | 9 | 0 | `json`, `bytes` |
| `jsonrpc` | `http` | `unary` | `http.jsonrpc`, `https.jsonrpc` | `request` | `stream` | 6 | 9 | 1 | `jsonrpc` |
| `http.stream` | `http` | `server_stream` | `http.stream`, `https.stream` | `request`, `stream` | - | 10 | 7 | 2 | `bytes`, `json` |
| `sse` | `http` | `server_stream` | `http.sse`, `https.sse` | `request`, `session`, `message`, `stream` | - | 13 | 14 | 1 | `sse`, `json` |
| `websocket` | `websocket` | `duplex` | `ws`, `wss` | `session`, `message` | - | 8 | 9 | 0 | `raw`, `json`, `jsonrpc` |
| `webtransport` | `webtransport` | `duplex` | `webtransport` | `session`, `stream`, `datagram` | `message` | 15 | 16 | 0 | `raw`, `json`, `jsonrpc`, `app` |

## Family Matrix

| Family | Subevents | Examples |
| --- | --- | --- |
| `request` | 11 | `request.open`, `request.body_in`, `request.chunk_in`, `request.accept` ... |
| `session` | 8 | `session.open`, `session.accept`, `session.ready`, `session.heartbeat` ... |
| `message` | 9 | `message.in`, `message.decode`, `message.handle`, `message.out` ... |
| `stream` | 8 | `stream.open`, `stream.chunk_in`, `stream.chunk_out`, `stream.flush` ... |
| `datagram` | 6 | `datagram.in`, `datagram.handle`, `datagram.out`, `datagram.ack` ... |

## Artifact Packages

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | `tigr-contract-artifacts` | `0.1.0` | `packages/artifacts-py` | 1 | Filesystem access helpers over vendored artifacts |
| npm | `@tigr/contract-artifacts` | `0.1.0` | `packages/artifacts-npm` | 4 | Package exports over vendored artifact files |
| rust | `tigr_contract_artifacts_rs` | `0.1.0` | `packages/artifacts-rs` | 1 | Embedded accessors for YAML, JSON, manifest, checksums |

## Contract Packages

| Ecosystem | Package | Version | Path | Surface files | Notes |
| --- | --- | --- | --- | --- | --- |
| python | `tigr-asgi-contract` | `0.1.0` | `packages/contract-py` | 15 | Pydantic models plus validator helpers |
| npm | `@tigr/asgi-contract` | `0.1.0` | `packages/contract-npm` | 18 | TypeScript surface plus TSX badges/views |
| rust | `tigr_asgi_contract_rs` | `0.1.0` | `packages/contract-rs` | 15 | Serde-friendly enums, models, validators |

## Repository Layout

```text
contract/                 # canonical registries, schemas, manifest, checksums
generators/               # language generators used for downstream packages
packages/artifacts-*      # artifact distributions
packages/contract-*       # generated downstream contract distributions
tools/                    # validation, packaging, checksum, manifest, README generation
tests/                    # contract, codegen, and parity coverage
```

## Authoring Workflow

1. Edit files under `contract/`.
2. Rebuild generated artifacts and READMEs.
3. Run validation and tests.
4. Commit source and generated outputs together.

```bash
python tools/validate_yaml.py
python tools/validate_jsonschema.py
python tools/generate_all.py
python tools/check_versions.py
pytest -q
```

Do not hand-edit generated outputs under `packages/contract-*`, `contract/manifest.json`, `contract/checksums.txt`, or these generated README files. Regenerate them from source.

## Additional Docs

- [docs/publishing.md](docs/publishing.md)
- [docs/versioning.md](docs/versioning.md)
- [docs/conformance.md](docs/conformance.md)
- [docs/contract-governance.md](docs/contract-governance.md)
