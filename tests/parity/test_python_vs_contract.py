from __future__ import annotations
import yaml
from pathlib import Path
from tigr_asgi_contract import Binding, Channel, Direction, Framing

ROOT = Path(__file__).resolve().parents[2]

def test_python_bindings_match_contract() -> None:
    data = yaml.safe_load((ROOT / "contract" / "bindings.yaml").read_text(encoding="utf-8"))
    names = set(data["bindings"].keys())
    enum_values = {item.value for item in Binding}
    assert names == enum_values


def test_python_classification_enums_match_contract() -> None:
    channels = yaml.safe_load((ROOT / "contract" / "channels.yaml").read_text(encoding="utf-8"))
    directions = yaml.safe_load((ROOT / "contract" / "directions.yaml").read_text(encoding="utf-8"))
    framings = yaml.safe_load((ROOT / "contract" / "framing.yaml").read_text(encoding="utf-8"))

    assert {item.value for item in Channel} == set(channels["channels"])
    assert {item.value for item in Direction} == set(directions["directions"])
    assert {item.value for item in Framing} == set(framings["framings"])
