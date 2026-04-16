#!/usr/bin/env python3
"""Migrate tigr_asgi_contract registry matrix entries into SSOT features via CLI."""

from __future__ import annotations

import json
import subprocess
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT_REGISTRY_PATH = ROOT / ".ssot/registry.json"
CONTRACT_REGISTRY_PATH = ROOT / "packages/contract-py/src/tigr_asgi_contract/registry.py"

CODE_TO_STATUS = {
    "R": "implemented",
    "D": "implemented",
    "O": "partial",
    "F": "absent",
}
DEFAULT_CLAIM_IDS = ["clm:bindings"]
DEFAULT_TEST_IDS = ["tst:contract-test-legality"]
CODE_LABEL = {
    "R": "required",
    "D": "derived",
    "O": "optional",
    "F": "forbidden",
}


def load_contract_registry():
    spec = spec_from_file_location("tigr_registry", CONTRACT_REGISTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load contract registry: {CONTRACT_REGISTRY_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_existing_feature_ids() -> set[str]:
    data = json.loads(SSOT_REGISTRY_PATH.read_text())
    return {f["id"] for f in data.get("features", [])}


def norm(token: str) -> str:
    return token.replace(".", "-").replace("_", "-")


def create_feature(feature_id: str, title: str, description: str, code: str) -> bool:
    cmd = [
        "ssot-registry",
        "feature",
        "create",
        str(ROOT),
        "--id",
        feature_id,
        "--title",
        title,
        "--description",
        description,
        "--implementation-status",
        CODE_TO_STATUS[code],
        "--claim-tier",
        "T2",
        "--horizon",
        "out_of_bounds",
        "--lifecycle-stage",
        "active",
        "--target-lifecycle-stage",
        "active",
        "--claim-ids",
        *DEFAULT_CLAIM_IDS,
        "--test-ids",
        *DEFAULT_TEST_IDS,
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)
    return True


def migrate() -> tuple[int, int]:
    reg = load_contract_registry()
    existing = load_existing_feature_ids()
    created = 0
    skipped = 0

    for binding, families in sorted(reg.BINDING_FAMILY_MATRIX.items()):
        for family, code in sorted(families.items()):
            fid = f"feat:binding-family-{norm(binding)}-{norm(family)}"
            if fid in existing:
                skipped += 1
                continue
            title = f"Binding family {binding} × {family}"
            description = f"From BINDING_FAMILY_MATRIX: code {code} ({CODE_LABEL[code]})."
            create_feature(fid, title, description, code)
            created += 1

    for family, subevents in sorted(reg.FAMILY_SUBEVENT_MATRIX.items()):
        for subevent, code in sorted(subevents.items()):
            fid = f"feat:family-subevent-{norm(family)}-{norm(subevent)}"
            if fid in existing:
                skipped += 1
                continue
            title = f"Family subevent {family} × {subevent}"
            description = f"From FAMILY_SUBEVENT_MATRIX: code {code} ({CODE_LABEL[code]})."
            create_feature(fid, title, description, code)
            created += 1

    for binding, subevents in sorted(reg.BINDING_SUBEVENT_MATRIX.items()):
        for subevent, code in sorted(subevents.items()):
            fid = f"feat:binding-subevent-{norm(binding)}-{norm(subevent)}"
            if fid in existing:
                skipped += 1
                continue
            title = f"Binding subevent {binding} × {subevent}"
            description = f"From BINDING_SUBEVENT_MATRIX: code {code} ({CODE_LABEL[code]})."
            create_feature(fid, title, description, code)
            created += 1

    return created, skipped


def main() -> None:
    created, skipped = migrate()
    print(f"Created {created} features; skipped {skipped} existing features.")


if __name__ == "__main__":
    main()
