# Publishing specification

# Publishing

This repository uses a strict five-step release lifecycle:

1. **Generate**
2. **Test**
3. **Promote**
4. **Publish**
5. **Release**

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
7. prerelease creation

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

GitHub workflows regenerate only to verify determinism.

- authors generate and commit locally
- CI regenerates and checks cleanliness
- release workflows regenerate in ephemeral workspaces only
- no workflow mutates the canonical history during validation, promotion, or publish
