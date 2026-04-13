from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract"

def main() -> None:
    for path in sorted(CONTRACT.rglob("*.yaml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))
        print(f"OK {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
