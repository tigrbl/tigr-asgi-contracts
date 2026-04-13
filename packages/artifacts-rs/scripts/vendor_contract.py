from __future__ import annotations
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "contract"
DST = ROOT / "packages" / "artifacts-rs" / "contract"

def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)

if __name__ == "__main__":
    main()
