# Contract governance

`contract/` is the single canonical source-of-truth directory.

## Repository rules

- YAML, JSON Schema, manifest, and checksums must exist only under `contract/`.
- No package subtree may contain checked-in duplicate artifact copies.
- Downstream contract packages are generated from `contract/`.
- Generated outputs are committed and reviewed, but never edited by hand.
- `.ssot/` is generated and reviewed alongside contract changes.
- The SSOT certification workflow is pinned to local `ssot-registry 0.2.10`.

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

## SSOT authority

- The published PyPI README is the conceptual lifecycle reference.
- The locally installed `ssot-registry 0.2.10` validator is authoritative for this repository.
- `profile` entities are intentionally out of scope for this repo until the local validator requires them.

## Certification objects

- The current repo version owns a version-aligned SSOT boundary `bnd:<VERSION>`.
- The current repo version owns a version-aligned SSOT release `rel:<VERSION>`.
- Day-to-day regeneration keeps that boundary/release pair in sync as an active candidate over the currently implemented feature set.
- Release workflows advance the candidate through `freeze`, `certify`, `promote`, and `publish` in ephemeral workspaces.
