# Conformance Target Test Placeholders

This file is the shared placeholder path for row-level conformance target tests.
Each `tst:target-*-placeholder` row represents a planned target-inventory test
for one target ID in `SPEC-1036`.

The future executable checks should verify that each target feature has:

- `spec_ids` linkage to `spc:1036` and `spc:1040`.
- `spc:1039` linkage when the target is draft, draft-conditional, living, or working-draft.
- A stable target identifier derived from the `SPEC-1036` target ID.
- Review metadata for draft and living targets.
- No claim of downstream runtime conformance without external runtime evidence.
