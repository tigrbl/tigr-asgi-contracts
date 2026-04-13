from __future__ import annotations
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contract"

def test_webtransport_datagram_required() -> None:
    data = yaml.safe_load((CONTRACT / "legality" / "binding_family.yaml").read_text(encoding="utf-8"))
    assert data["binding_family"]["webtransport"]["datagram"] == "R"
