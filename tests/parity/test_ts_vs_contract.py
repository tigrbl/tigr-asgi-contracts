from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

def test_ts_registry_exists() -> None:
    assert (ROOT / "packages" / "contract-npm" / "src" / "registry.ts").exists()


def test_ts_exports_classification_surfaces() -> None:
    registry = (ROOT / "packages" / "contract-npm" / "src" / "registry.ts").read_text(encoding="utf-8")
    index = (ROOT / "packages" / "contract-npm" / "src" / "index.ts").read_text(encoding="utf-8")
    framings = yaml.safe_load((ROOT / "contract" / "framing.yaml").read_text(encoding="utf-8"))["framings"]

    assert "export const CHANNELS" in registry
    assert "export const DIRECTIONS" in registry
    assert "export const FRAMINGS" in registry
    assert "export const EVENT_CLASSIFICATIONS" in registry
    assert 'export * from "./channels";' in index
    assert 'export * from "./directions";' in index
    assert 'export * from "./framing";' in index
    for framing in framings:
        assert f'"{framing}"' in registry
