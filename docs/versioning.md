# Versioning

All artifact packages and downstream contract packages share the same contract version.

The root `VERSION` file is the authoritative version marker.

Stable releases use `X.Y.Z`.

Prereleases use `X.Y.Z-devN`.

This keeps one version string usable across Python, npm, Cargo, and GitHub release tags.

The following packages must align with `VERSION`:

- `packages/artifacts-py/pyproject.toml`
- `packages/artifacts-npm/package.json`
- `packages/artifacts-rs/Cargo.toml`
- `packages/contract-py/pyproject.toml`
- `packages/contract-npm/package.json`
- `packages/contract-rs/Cargo.toml`

Use:

```bash
uv run --frozen python tools/check_versions.py
```

before promotion.

To auto-increment the next release version across every manifest, use:

```bash
uv run --frozen python tools/bump_release_version.py --bump patch
```

Valid bump types are `patch`, `minor`, `major`, and `finalize`.

- `patch` from `0.1.0` -> `0.1.1-dev1`
- `patch` from `0.1.1-dev1` -> `0.1.1-dev2`
- `minor` from `0.1.0` -> `0.2.0-dev1`
- `major` from `0.1.0` -> `1.0.0-dev1`
- `finalize` from `0.1.1-dev2` -> `0.1.1`

All GitHub releases tag automatically as `tigr-asgi-contracts==<version>`.

The `prepare-release` GitHub workflow uses the same script, commits only version metadata changes, then runs the release-candidate bundle workflow and can optionally trigger the publish workflow for PyPI, npm, and crates.io.
