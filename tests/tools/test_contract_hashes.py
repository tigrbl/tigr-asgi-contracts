from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


def load_module(name: str):
    module_path = Path(__file__).resolve().parents[2] / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_contract_hashes_are_lf_canonical(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.yaml"
    artifact.write_bytes(b"one: 1\r\ntwo: 2\r\n")
    expected = hashlib.sha256(b"one: 1\ntwo: 2\n").hexdigest()

    assert load_module("build_manifest").sha256(artifact) == expected
    assert load_module("build_checksums").sha256(artifact) == expected
