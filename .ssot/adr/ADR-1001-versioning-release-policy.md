# ADR-1001: Versioning and release policy

# Versioning

All artifact packages and downstream contract packages share the same contract version.

The root `VERSION` file is the authoritative version marker.

The following packages must align with `VERSION`:

- `packages/artifacts-py/pyproject.toml`
- `packages/artifacts-npm/package.json`
- `packages/artifacts-rs/Cargo.toml`
- `packages/contract-py/pyproject.toml`
- `packages/contract-npm/package.json`
- `packages/contract-rs/Cargo.toml`

Use:

```bash
python tools/check_versions.py
```

before promotion.
