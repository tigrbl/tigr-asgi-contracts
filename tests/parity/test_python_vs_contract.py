from __future__ import annotations
import yaml
from pathlib import Path
from tigr_asgi_contract import Binding

ROOT = Path(__file__).resolve().parents[2]

def test_python_bindings_match_contract() -> None:
    data = yaml.safe_load((ROOT / "contract" / "bindings.yaml").read_text(encoding="utf-8"))
    names = set(data["bindings"].keys())
    enum_values = {item.value for item in Binding}
    assert names == enum_values
