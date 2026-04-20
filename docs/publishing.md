# Publishing

This repository uses a strict six-step release lifecycle:

1. **Generate**
2. **Test**
3. **Prepare**
4. **Promote**
5. **Publish**
6. **Release**

## Exact sequence

### Author sequence

1. Edit `contract/`
2. Run:
   - `python tools/validate_yaml.py`
   - `python tools/validate_jsonschema.py`
   - `python tools/build_manifest.py`
   - `python tools/build_checksums.py`
   - `python tools/generate_all.py`
   - `python tools/check_versions.py`
   - `pytest -q`
3. Commit source contract changes and generated downstream outputs together.

### CI sequence

1. Validate YAML and JSON Schema.
2. Rebuild `manifest.json` and `checksums.txt` and fail if tracked files change.
3. Regenerate downstream packages and fail if tracked files change.
4. Run parity tests.

### Promotion sequence

Promotion is the creation of an immutable release-candidate bundle.

The release-candidate workflow performs:

1. validation
2. regeneration
3. clean-tree verification
4. tests
5. package build
6. bundle upload
7. optional GitHub release creation tagged as `tigr-asgi-contracts==<version>`
8. optional PyPI publish of the Python wheel/sdist bundle

### Prepare sequence

Preparation bumps the unified repo version before promotion.

The `prepare-release` workflow performs:

1. version bump across `VERSION` and all package manifests
2. version consistency verification
3. commit and push of version-only metadata changes
4. optional dispatch of `release-candidate` with explicit GitHub Release and PyPI publish toggles

### Publish sequence

Publishing uses the promoted candidate as the source of truth.

- PyPI publishes from the promoted wheel/sdist artifacts.
- npm publishes from the promoted tarballs.
- crates.io publishes from the promoted source tag / commit.

### Release sequence

The final GitHub release happens **after** ecosystem publication succeeds.

That means:

- do **not** create the final public release first
- publish to registries first
- finalize the GitHub release last

## Do GitHub workflows commit generation?

No.

GitHub workflows do not commit generated artifacts.

- authors generate and commit locally
- `prepare-release` may commit version metadata only
- CI regenerates and checks cleanliness
- release workflows regenerate in ephemeral workspaces only
- no workflow mutates the canonical history during validation, promotion, or publish
