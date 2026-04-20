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

## SSOT conformance

Within this repository, SSOT conformance additionally requires:

1. `ssot-registry 0.2.10` validation passes
2. optional contract features are tracked as implemented rather than partial
3. every implemented feature is claim-covered, while forbidden rows remain validated through the legality matrices and tests
4. the current repo version has a non-draft SSOT boundary/release pair
5. checked-in SSOT reports match the current validator output
