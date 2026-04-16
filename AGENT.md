# Agent Operating Guide: `ssot-registry` (Required)

This repository uses **`ssot-registry`** as the canonical system-of-record for planning, implementation tracking, test tracking, claims, evidence, and release management.

> **Policy:** Agents are required to use `ssot-registry` for all feature/release lifecycle work. Do not maintain parallel tracking in ad-hoc files.

## Tool references used for this guide
- CLI help (`ssot-registry -h`, plus domain command help for `feature`, `test`, `claim`, `evidence`, `release`, `registry`).
- PyPI package details for `ssot-registry` (current package `0.2.2`, Python `>=3.10`, homepage/repo at `github.com/groupsum/ssot-registry`).

## Canonical files and paths
- Registry root: `.ssot/`
- Canonical registry document: `.ssot/registry.json`
- Reports and generated artifacts: `.ssot/reports/`

Use repository root (`.`) as the command path unless you need a specific file path.

## Core operating loop (every substantive change)
1. Update registry entities first (`feature`, `test`, `claim`, `evidence`, `issue`, `risk`, `boundary`, `release`) using CLI commands.
2. Link entities so traceability is explicit.
3. Validate the registry.
4. Evaluate claims and verify evidence.
5. Gate release operations via certify → promote → publish.

## 1) Feature tracking
Use features to represent deliverable behavior and planning intent.

### Create or update a feature
```bash
ssot-registry feature create . \
  --id FEAT-XXXX \
  --title "Short feature title" \
  --description "What is being delivered" \
  --implementation-status absent \
  --lifecycle-stage active \
  --horizon current \
  --claim-tier T2
```

Useful fields:
- `--implementation-status`: `absent|partial|implemented`
- `--lifecycle-stage`: `active|deprecated|obsolete|removed`
- Planning fields: `--horizon`, `--claim-tier`, `--target-lifecycle-stage`, `--slot`

### Plan and lifecycle transitions
```bash
ssot-registry feature plan . --ids FEAT-XXXX --horizon next --claim-tier T2
ssot-registry feature lifecycle set . --ids FEAT-XXXX --stage active
```

### Link feature dependencies and coverage
```bash
ssot-registry feature link . --id FEAT-XXXX --test-ids TEST-XXXX --claim-ids CLAIM-XXXX
```

## 2) Feature-test tracking
Tests track verification status and coverage for features/claims/evidence.

### Create a test record
```bash
ssot-registry test create . \
  --id TEST-XXXX \
  --title "Integration test for FEAT-XXXX" \
  --status planned \
  --kind integration \
  --test-path tests/path/to/test_file.py \
  --feature-ids FEAT-XXXX \
  --claim-ids CLAIM-XXXX
```

### Maintain links
```bash
ssot-registry test link . --id TEST-XXXX --feature-ids FEAT-XXXX --claim-ids CLAIM-XXXX --evidence-ids EVID-XXXX
```

## 3) Claims tracking
Claims are explicit assertions about system behavior, quality, or compliance.

### Create a claim
```bash
ssot-registry claim create . \
  --id CLAIM-XXXX \
  --title "Claim statement" \
  --kind quality \
  --status declared \
  --tier T2 \
  --feature-ids FEAT-XXXX \
  --test-ids TEST-XXXX
```

### Evaluate and advance claim status
```bash
ssot-registry claim evaluate .
ssot-registry claim set-status . --id CLAIM-XXXX --status asserted
```

Typical lifecycle statuses include:
`proposed -> declared -> implemented -> asserted -> evidenced -> certified -> promoted -> published`
(with `blocked`/`retired` as special cases).

## 4) Evidence tracking
Evidence points to concrete artifacts (test reports, logs, attestations, etc.).

### Create evidence
```bash
ssot-registry evidence create . \
  --id EVID-XXXX \
  --title "Evidence for CLAIM-XXXX" \
  --kind test_report \
  --status collected \
  --tier T2 \
  --evidence-path .ssot/reports/example-report.json \
  --claim-ids CLAIM-XXXX \
  --test-ids TEST-XXXX
```

### Verify evidence integrity/references
```bash
ssot-registry evidence verify .
```

## 5) Release management
Releases aggregate claims/evidence under a boundary and move through gated states.

### Create release
```bash
ssot-registry release create . \
  --id REL-XXXX \
  --version 0.0.0 \
  --status draft \
  --boundary-id BOUNDARY-XXXX \
  --claim-ids CLAIM-XXXX \
  --evidence-ids EVID-XXXX
```

### Add/remove scoped quality records
```bash
ssot-registry release add-claim . --id REL-XXXX --claim-ids CLAIM-YYYY
ssot-registry release add-evidence . --id REL-XXXX --evidence-ids EVID-YYYY
```

### Gate transitions (must be sequential)
```bash
ssot-registry release certify . --release-id REL-XXXX --write-report
ssot-registry release promote . --release-id REL-XXXX
ssot-registry release publish . --release-id REL-XXXX
```

Use `release revoke` when necessary to explicitly invalidate a release.

## 6) Validation and exports (required checks)
Run before merge/PR handoff:

```bash
ssot-registry validate . --write-report
ssot-registry claim evaluate .
ssot-registry evidence verify .
ssot-registry registry export .
```

Recommended optional graph export:
```bash
ssot-registry graph export .
```

## 7) Minimal workflow checklist for agents
For any feature-level change:
1. Create/update `feature`.
2. Create/update linked `test` records.
3. Create/update linked `claim` records.
4. Create/update linked `evidence` rows.
5. Run `validate`, `claim evaluate`, `evidence verify`.
6. If shipping: update `release`, then `certify -> promote -> publish`.

## 8) Command-discovery quick rule
When uncertain about parameters, inspect help first:

```bash
ssot-registry -h
ssot-registry <domain> -h
ssot-registry <domain> <subcommand> -h
```

Domains include: `feature`, `test`, `claim`, `evidence`, `release`, `issue`, `risk`, `boundary`, `adr`, `spec`, `graph`, `registry`, `validate`, `upgrade`, `init`.
