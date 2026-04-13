from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(path: str) -> None:
    subprocess.run([sys.executable, str(ROOT / path)], check=True)

def main() -> None:
    run("tools/build_manifest.py")
    run("tools/build_checksums.py")
    run("generators/python/generate.py")
    run("generators/rust/generate.py")
    run("generators/ts/generate.py")
    run("tools/generate_readmes.py")

if __name__ == "__main__":
    main()
