from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

def test_manifest_exists() -> None:
    manifest = json.loads((CONTRACT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["contract_version"] == VERSION
    assert manifest["serde_version"] == 1
    assert manifest["files"]
