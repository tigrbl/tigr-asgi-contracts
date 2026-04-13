from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_ts_registry_exists() -> None:
    assert (ROOT / "packages" / "contract-npm" / "src" / "registry.ts").exists()
