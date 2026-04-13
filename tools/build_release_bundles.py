from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "release"
PYPI_DIST = DIST / "pypi"
NPM_DIST = DIST / "npm"
CRATES_DIST = DIST / "crates"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def clean() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    PYPI_DIST.mkdir(parents=True, exist_ok=True)
    NPM_DIST.mkdir(parents=True, exist_ok=True)
    CRATES_DIST.mkdir(parents=True, exist_ok=True)


def build_python() -> None:
    run([sys.executable, "-m", "build", "packages/artifacts-py", "--sdist", "--wheel", "-o", str(PYPI_DIST)], cwd=ROOT)
    run([sys.executable, "-m", "build", "packages/contract-py", "--sdist", "--wheel", "-o", str(PYPI_DIST)], cwd=ROOT)


def build_npm() -> None:
    run(["npm", "pack", "--pack-destination", str(NPM_DIST)], cwd=ROOT / "packages/artifacts-npm")
    run(["npm", "pack", "--pack-destination", str(NPM_DIST)], cwd=ROOT / "packages/contract-npm")


def build_crates() -> None:
    vendor_script = ROOT / "packages/artifacts-rs/scripts/vendor_contract.py"
    vendor_dst = ROOT / "packages/artifacts-rs/contract"
    try:
        run([sys.executable, str(vendor_script)], cwd=ROOT)
        run(["cargo", "package", "--manifest-path", str(ROOT / "packages/artifacts-rs/Cargo.toml"), "--allow-dirty", "--no-verify"], cwd=ROOT)
        run(["cargo", "package", "--manifest-path", str(ROOT / "packages/contract-rs/Cargo.toml"), "--allow-dirty", "--no-verify"], cwd=ROOT)
        target_pkg = ROOT / "target/package"
        for crate in sorted(target_pkg.glob("*.crate")):
            shutil.copy2(crate, CRATES_DIST / crate.name)
    finally:
        if vendor_dst.exists():
            shutil.rmtree(vendor_dst)


def copy_metadata() -> None:
    shutil.copy2(ROOT / "contract/manifest.json", DIST / "manifest.json")
    shutil.copy2(ROOT / "contract/checksums.txt", DIST / "checksums.txt")
    shutil.copy2(ROOT / "VERSION", DIST / "VERSION")


def main() -> None:
    clean()
    build_python()
    build_npm()
    build_crates()
    copy_metadata()
    print(f"release bundles written to {DIST}")


if __name__ == "__main__":
    main()
