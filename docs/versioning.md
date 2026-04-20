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

To auto-increment the next release version across every manifest, use:

```bash
python tools/bump_release_version.py --bump patch
```

Valid bump types are `patch`, `minor`, and `major`.

The `prepare-release` GitHub workflow uses the same script and commits only version metadata changes before optionally triggering `release-candidate`.
