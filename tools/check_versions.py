from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def load_pyproject_version(path: Path) -> str:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data["project"]["version"]


def load_package_json_version(path: Path) -> str:
    return json.loads(path.read_text(encoding="utf-8"))["version"]


def load_cargo_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not m:
        raise RuntimeError(f"could not find Cargo version in {path}")
    return m.group(1)


def main() -> None:
    expected = sys.argv[1] if len(sys.argv) > 1 else EXPECTED
    checks = {
        ROOT / "packages/artifacts-py/pyproject.toml": load_pyproject_version,
        ROOT / "packages/contract-py/pyproject.toml": load_pyproject_version,
        ROOT / "packages/artifacts-npm/package.json": load_package_json_version,
        ROOT / "packages/contract-npm/package.json": load_package_json_version,
        ROOT / "packages/artifacts-rs/Cargo.toml": load_cargo_version,
        ROOT / "packages/contract-rs/Cargo.toml": load_cargo_version,
    }
    errors: list[str] = []
    if EXPECTED != expected:
        errors.append(f"VERSION file {EXPECTED!r} != expected {expected!r}")
    for path, loader in checks.items():
        got = loader(path)
        if got != expected:
            errors.append(f"{path}: {got!r} != {expected!r}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"all package versions match {expected}")


if __name__ == "__main__":
    main()
