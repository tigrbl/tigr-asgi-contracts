#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-dev(?P<dev>0|[1-9]\d*))?$"
)


@dataclass(frozen=True)
class NpmTarball:
    path: Path
    package_name: str
    version: str


def parse_version(version: str) -> tuple[int, int, int, int, int]:
    match = VERSION_RE.match(version)
    if match is None:
        raise ValueError(f"Unsupported npm version format: {version!r}")
    dev = match.group("dev")
    prerelease_flag = 0 if dev is None else -1
    dev_number = 0 if dev is None else int(dev)
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease_flag,
        dev_number,
    )


def read_tarball_metadata(path: Path) -> NpmTarball:
    with tarfile.open(path, "r:gz") as archive:
        member = archive.getmember("package/package.json")
        payload = json.load(archive.extractfile(member))
    return NpmTarball(path=path, package_name=payload["name"], version=payload["version"])


def npm_version_exists(package_name: str, version: str) -> bool:
    result = subprocess.run(
        ["npm", "view", f"{package_name}@{version}", "version", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() not in {"", "null"}


def build_npm_env() -> dict[str, str]:
    env = os.environ.copy()
    token = env.get("NODE_AUTH_TOKEN") or env.get("NPM_TOKEN")
    if token:
        npmrc = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".npmrc")
        npmrc.write("registry=https://registry.npmjs.org/\n")
        npmrc.write(f"//registry.npmjs.org/:_authToken={token}\n")
        npmrc.write("always-auth=true\n")
        npmrc.flush()
        npmrc.close()
        env["NPM_CONFIG_USERCONFIG"] = npmrc.name
        return env

    username = env.get("NPM_USERNAME")
    password = env.get("NPM_PASSWORD")
    email = env.get("NPM_EMAIL")
    if username and password and email:
        login = subprocess.run(
            ["npm", "adduser", "--registry", "https://registry.npmjs.org", "--auth-type=legacy"],
            input=f"{username}\n{password}\n{email}\n",
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        if login.returncode != 0:
            raise RuntimeError(
                "npm authentication failed via NPM_USERNAME/NPM_PASSWORD/NPM_EMAIL.\n"
                f"stdout:\n{login.stdout}\n\nstderr:\n{login.stderr}"
            )
        return env

    raise RuntimeError(
        "Missing npm credentials. Provide NODE_AUTH_TOKEN or NPM_TOKEN, "
        "or set NPM_USERNAME, NPM_PASSWORD, and NPM_EMAIL."
    )


def publish_tarball(tarball: NpmTarball, env: dict[str, str]) -> None:
    if npm_version_exists(tarball.package_name, tarball.version):
        print(f"skip existing {tarball.package_name}@{tarball.version}")
        return
    subprocess.run(["npm", "publish", str(tarball.path), "--access", "public"], check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish npm tarballs from downloaded release bundles.")
    parser.add_argument("--root", type=Path, required=True, help="Root directory containing downloaded *.tgz files.")
    args = parser.parse_args()

    env = build_npm_env()
    tarballs = [read_tarball_metadata(path) for path in sorted(args.root.rglob("*.tgz"))]
    for tarball in sorted(tarballs, key=lambda item: (parse_version(item.version), item.package_name)):
        publish_tarball(tarball, env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
