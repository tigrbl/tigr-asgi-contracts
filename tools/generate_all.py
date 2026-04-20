from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(path: str, *args: str) -> None:
    subprocess.run([sys.executable, str(ROOT / path), *args], check=True)

def main() -> None:
    run("tools/build_manifest.py")
    run("tools/build_checksums.py")
    run("generators/python/generate.py")
    run("generators/rust/generate.py")
    run("generators/ts/generate.py")
    run("tools/generate_readmes.py")
    run("tools/sync_ssot_registry.py")
    run("tools/ssot_release_lifecycle.py", "prepare")

if __name__ == "__main__":
    main()
