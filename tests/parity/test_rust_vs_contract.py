from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

def test_rust_registry_exists() -> None:
    assert (ROOT / "packages" / "contract-rs" / "src" / "registry.rs").exists()


def test_rust_exports_classification_surfaces() -> None:
    registry = (ROOT / "packages" / "contract-rs" / "src" / "registry.rs").read_text(encoding="utf-8")
    lib = (ROOT / "packages" / "contract-rs" / "src" / "lib.rs").read_text(encoding="utf-8")
    framings = yaml.safe_load((ROOT / "contract" / "framing.yaml").read_text(encoding="utf-8"))["framings"]

    assert "pub const CHANNELS" in registry
    assert "pub const DIRECTIONS" in registry
    assert "pub const FRAMINGS" in registry
    assert "pub const EVENT_CLASSIFICATIONS_JSON" in registry
    assert "pub mod channels;" in lib
    assert "pub mod directions;" in lib
    assert "pub mod framing;" in lib
    for framing in framings:
        assert f'"{framing}"' in registry
