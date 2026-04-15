# Contract governance specification

# Contract governance

`contract/` is the single canonical source-of-truth directory.

## Repository rules

- YAML, JSON Schema, manifest, and checksums must exist only under `contract/`.
- No package subtree may contain checked-in duplicate artifact copies.
- Downstream contract packages are generated from `contract/`.
- Generated outputs are committed and reviewed, but never edited by hand.

## Ownership

This repository owns:

- contract identifiers
- legality matrices
- compatibility rules
- structured schemas
- generated downstream contract packages

This repository does **not** own:

- Tigrcorn server runtime behavior
- Tigrbl framework runtime behavior
- ASGI3 itself

It defines the contract that those systems implement.
