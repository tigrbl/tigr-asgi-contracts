from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = []
    for path in sorted(CONTRACT.rglob("*")):
        if path.is_file() and path.name not in {"manifest.json", "checksums.txt"}:
            files.append({
                "path": path.relative_to(CONTRACT).as_posix(),
                "sha256": sha256(path),
            })
    manifest = {
        "name": "tigr-asgi-contract",
        "contract_version": version,
        "artifact_version": version,
        "serde_version": 1,
        "schema_draft": "2020-12",
        "files": files,
    }
    (CONTRACT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
