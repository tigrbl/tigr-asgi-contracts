from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"

def test_checksums_contains_manifest() -> None:
    text = (CONTRACT / "checksums.txt").read_text(encoding="utf-8")
    assert "manifest.json" in text
