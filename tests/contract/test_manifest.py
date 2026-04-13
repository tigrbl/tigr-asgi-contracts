from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"

def test_manifest_exists() -> None:
    manifest = json.loads((CONTRACT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["contract_version"] == "0.1.0"
    assert manifest["serde_version"] == 1
    assert manifest["files"]
