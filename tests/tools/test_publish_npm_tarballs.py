from __future__ import annotations

import importlib.util
import io
import json
import sys
import tarfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "publish_npm_tarballs.py"
SPEC = importlib.util.spec_from_file_location("publish_npm_tarballs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_tarball(root: Path, filename: str, *, package_name: str, version: str) -> Path:
    path = root / filename
    payload = json.dumps({"name": package_name, "version": version}).encode("utf-8")
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo("package/package.json")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))
    return path


def test_parse_version_orders_prereleases_before_stable() -> None:
    assert MODULE.parse_version("0.1.0-dev2") < MODULE.parse_version("0.1.0")
    assert MODULE.parse_version("0.1.0") < MODULE.parse_version("0.2.0-dev1")


def test_read_tarball_metadata(tmp_path: Path) -> None:
    tarball = write_tarball(
        tmp_path,
        "tigrbljs-tigr-asgi-contract-0.1.1-dev1.tgz",
        package_name="@tigrbljs/tigr-asgi-contract",
        version="0.1.1-dev1",
    )

    metadata = MODULE.read_tarball_metadata(tarball)

    assert metadata.package_name == "@tigrbljs/tigr-asgi-contract"
    assert metadata.version == "0.1.1-dev1"


def test_tarball_sorting_prefers_older_versions_first(tmp_path: Path) -> None:
    stable = write_tarball(
        tmp_path,
        "tigrbljs-tigr-asgi-contract-0.1.1.tgz",
        package_name="@tigrbljs/tigr-asgi-contract",
        version="0.1.1",
    )
    prerelease = write_tarball(
        tmp_path,
        "tigrbljs-tigr-asgi-contract-0.1.1-dev2.tgz",
        package_name="@tigrbljs/tigr-asgi-contract",
        version="0.1.1-dev2",
    )

    tarballs = [MODULE.read_tarball_metadata(stable), MODULE.read_tarball_metadata(prerelease)]
    ordered = sorted(tarballs, key=lambda item: (MODULE.parse_version(item.version), item.package_name))

    assert [item.path.name for item in ordered] == [
        "tigrbljs-tigr-asgi-contract-0.1.1-dev2.tgz",
        "tigrbljs-tigr-asgi-contract-0.1.1.tgz",
    ]
