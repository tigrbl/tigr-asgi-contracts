from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_ts_generated_files_exist() -> None:
    assert (ROOT / "packages" / "contract-npm" / "src" / "bindings.ts").exists()
    assert (ROOT / "packages" / "contract-npm" / "tsx" / "ScopeView.tsx").exists()
