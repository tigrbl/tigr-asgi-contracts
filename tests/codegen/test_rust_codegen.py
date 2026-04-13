from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_rust_generated_files_exist() -> None:
    assert (ROOT / "packages" / "contract-rs" / "src" / "bindings.rs").exists()
    assert (ROOT / "packages" / "contract-rs" / "src" / "models.rs").exists()
