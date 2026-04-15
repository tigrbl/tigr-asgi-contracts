# Conformance specification

# Conformance

Conformance in this repository means:

1. contract artifacts are valid
2. generated downstream packages are deterministic
3. Python, Rust, and TS outputs remain in parity with the canonical contract
4. release bundles are built from validated, deterministic inputs

## Conformance lanes

- artifact validation
- generation cleanliness
- Python parity tests
- Rust parity tests
- TS parity tests
- cross-language roundtrip checks

## Downstream conformance

This repository defines the contract only.

Separate integration/conformance suites are responsible for proving:

- Tigrcorn ↔ ASGI3 compatibility
- Tigrcorn ↔ Tigrbl compatibility
- versioned compatibility across releases
