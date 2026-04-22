from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIRS = [
    ROOT / "packages" / "artifacts-py",
    ROOT / "packages" / "artifacts-npm",
    ROOT / "packages" / "artifacts-rs",
    ROOT / "packages" / "contract-py",
    ROOT / "packages" / "contract-npm",
    ROOT / "packages" / "contract-rs",
]


def test_package_license_files_match_root_license() -> None:
    license_bytes = (ROOT / "LICENSE").read_bytes()

    for package_dir in PACKAGE_DIRS:
        assert (package_dir / "LICENSE").read_bytes() == license_bytes


def test_package_manifest_license_metadata_is_apache_2() -> None:
    assert 'license = { text = "Apache-2.0" }' in (
        ROOT / "packages" / "artifacts-py" / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert 'license = { text = "Apache-2.0" }' in (
        ROOT / "packages" / "contract-py" / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert 'license = "Apache-2.0"' in (
        ROOT / "packages" / "artifacts-rs" / "Cargo.toml"
    ).read_text(encoding="utf-8")
    assert 'license = "Apache-2.0"' in (
        ROOT / "packages" / "contract-rs" / "Cargo.toml"
    ).read_text(encoding="utf-8")

    for package_json in [
        ROOT / "packages" / "artifacts-npm" / "package.json",
        ROOT / "packages" / "contract-npm" / "package.json",
    ]:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
        assert payload["license"] == "Apache-2.0"
        assert "LICENSE" in payload["files"]
