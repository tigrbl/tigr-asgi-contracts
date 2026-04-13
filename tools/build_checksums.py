from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def main() -> None:
    lines = []
    for path in sorted(CONTRACT.rglob("*")):
        if path.is_file() and path.name != "checksums.txt":
            lines.append(f"{sha256(path)}  {path.relative_to(CONTRACT).as_posix()}")
    (CONTRACT / "checksums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
