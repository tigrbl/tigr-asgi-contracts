# tigr-asgi-contracts

![source-of-truth](https://img.shields.io/badge/source_of_truth-contract%2F-blue)
![artifacts](https://img.shields.io/badge/artifacts-yaml%20%7C%20json%20%7C%20manifest%20%7C%20checksums-green)
![contracts](https://img.shields.io/badge/contracts-python%20%7C%20rust%20%7C%20ts%2Ftsx-purple)
![asgi3](https://img.shields.io/badge/asgi3-compatible-black)
![exchanges](https://img.shields.io/badge/exchanges-3-orange)
![families](https://img.shields.io/badge/runtime_families-5-orange)

Neutral contract repository for an **ASGI3-compatible semantic transport contract** shared by downstream implementations such as **Tigrcorn** and **Tigrbl**.

This repository publishes two classes of packages:

- **artifact packages**: canonical YAML registries, JSON Schemas, manifest, checksums
- **downstream contract packages**: generated Python, Rust, and TS / TSX enums, models, and validators

`contract/` is the only canonical source-of-truth directory.

---

## Overview

The purpose of this repository is to give multiple implementations a single contract to implement without making any one implementation the source of truth.

The contract covers:

- scope types
- bindings
- exchanges
- runtime families
- subevents
- transport capabilities
- compatibility metadata
- identifiers
- legality matrices
- JSON Schemas for structured objects

The repository does **not** implement server runtime behavior or framework execution behavior. It defines the contract that those systems consume.

---

## Contract model

### Exchange patterns

| Exchange | Meaning |
|---|---|
| `unary` | one request → one response |
| `server_stream` | one setup request → many outbound units |
| `duplex` | long-lived session with repeated inbound/outbound units |

### Runtime families

| Family | Meaning |
|---|---|
| `request` | bounded unary invocation |
| `session` | long-lived association |
| `message` | discrete logical message |
| `stream` | ordered chunk flow |
| `datagram` | packet-like unit |

### Public binding matrix

| Binding | Exchange | Families |
|---|---|---|
| `rest` | `unary` | request |
| `jsonrpc` | `unary` | request |
| `http.stream` | `server_stream` | request, stream |
| `sse` | `server_stream` | request, session, message, stream |
| `websocket` | `duplex` | session, message |
| `webtransport` | `duplex` | session, stream, datagram |

---

## Repository layout

```text
contract/                 # single canonical source of truth
packages/artifacts-*      # publish artifact packages
packages/contract-*       # publish generated downstream contracts
generators/               # compile contract/ into language-native packages
tools/                    # validation, generation, packaging, version checks
tests/                    # contract, codegen, parity
```

---

## Package overview

### Artifact packages

| Ecosystem | Package | Contents |
|---|---|---|
| PyPI | `tigr-contract-artifacts` | yaml, json, manifest, checksums |
| npm | `@tigr/contract-artifacts` | yaml, json, manifest, checksums |
| crates.io | `tigr_contract_artifacts_rs` | embedded artifact accessors over yaml/json/manifest/checksums |

### Downstream contract packages

| Ecosystem | Package | Contents |
|---|---|---|
| PyPI | `tigr-asgi-contract` | enums, models, validators |
| npm | `@tigr/asgi-contract` | enums, validators, TS types, TSX types |
| crates.io | `tigr_asgi_contract_rs` | enums, models, validators |

---

## Source-of-truth policy

- `contract/` is canonical.
- Downstream packages are generated from `contract/`.
- Generated outputs are committed for review and versioning.
- CI regenerates and verifies cleanliness; CI does **not** auto-commit generated changes.

---

## Usage examples

### Python artifact package

```python
from tigr_contract_artifacts.access import contract_root, manifest, load_yaml

root = contract_root()
print(root)
print(manifest()["contract_version"])
print(load_yaml("bindings.yaml"))
```

### npm artifact package

```ts
import manifest from "@tigr/contract-artifacts/manifest" assert { type: "json" };
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const manifestPath = require.resolve("@tigr/contract-artifacts/manifest");
const contractDir = path.dirname(manifestPath);
const bindings = fs.readFileSync(path.join(contractDir, "bindings.yaml"), "utf8");
console.log(manifest.contract_version);
console.log(bindings);
```

### Rust artifact crate

```rust
use tigr_contract_artifacts_rs::access::{manifest, checksums, load_yaml};

fn main() {
    let m = manifest();
    println!("{}", m["contract_version"]);
    let bindings = load_yaml("bindings.yaml");
    println!("{:?}", bindings);
    println!("{}", checksums());
}
```

### Python downstream contract package

```python
from tigr_asgi_contract.bindings import Binding
from tigr_asgi_contract.families import Family
from tigr_asgi_contract.validators import binding_supports_family

assert binding_supports_family(Binding.WEBSOCKET, Family.MESSAGE)
```

### TypeScript / TSX downstream contract package

```ts
import { Binding, Family, bindingSupportsFamily } from "@tigr/asgi-contract";

console.log(bindingSupportsFamily(Binding.Websocket, Family.Message));
```

```tsx
import { BindingBadge } from "@tigr/asgi-contract/tsx/BindingBadge";

export function Demo() {
  return <BindingBadge binding="websocket" />;
}
```

### Rust downstream contract crate

```rust
use tigr_asgi_contract_rs::{Binding, Family};
use tigr_asgi_contract_rs::validators::binding_supports_family;

fn main() {
    assert!(binding_supports_family(Binding::Websocket, Family::Message));
}
```

---

## Authoring

### Exact local sequence

1. Edit files under `contract/`
2. Validate YAML and JSON Schema
3. Rebuild `manifest.json` and `checksums.txt`
4. Generate downstream packages
5. Run tests
6. Commit both source and generated outputs

### Commands

```bash
python tools/validate_yaml.py
python tools/validate_jsonschema.py
python tools/build_manifest.py
python tools/build_checksums.py
python tools/generate_all.py
python tools/check_versions.py
pytest -q
```

### Important rule

Do not hand-edit generated files under:

- `packages/contract-py/`
- `packages/contract-rs/`
- `packages/contract-npm/`

---

## Generate, test, promote, publish, release

### Exact sequence

1. **Generate**
2. **Test**
3. **Promote**
4. **Publish**
5. **Release**

### Meaning

#### Generate
Recompute generated downstream packages from `contract/`.

#### Test
Validate artifacts, verify regeneration cleanliness, and run parity tests.

#### Promote
Create an immutable release-candidate bundle and attach it to a GitHub prerelease.

#### Publish
Publish the promoted candidate to PyPI, npm, and crates.io.

#### Release
Only after publish succeeds, finalize the public GitHub release.

### Why release comes last

The final GitHub release should only exist once ecosystem publication succeeded.

---

## GitHub Actions policy

### Pull requests and main branch

CI performs:

- artifact validation
- manifest/checksum rebuild verification
- regeneration verification
- parity testing

### Manual generation workflow

A manual generation workflow exists for previewing generated outputs, but it does **not** commit changes.

### Release-candidate workflow

The release-candidate workflow:

- validates
- regenerates
- verifies clean state
- tests
- builds packages
- uploads the release bundle
- creates a prerelease

### Publish workflow

The publish workflow:

- consumes the promoted release-candidate
- publishes packages
- finalizes the GitHub release

---

## Public operation

This repository is intended for public, multi-ecosystem consumption.

For public operation:

- contract version must be consistent across all packages
- checksums must be reproducible
- generated outputs must be deterministic
- parity tests must pass before promotion
- registry publication should use protected environments and trusted publishing

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Additional docs

- [docs/publishing.md](docs/publishing.md)
- [docs/versioning.md](docs/versioning.md)
- [docs/conformance.md](docs/conformance.md)
- [docs/contract-governance.md](docs/contract-governance.md)
