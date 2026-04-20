#!/usr/bin/env python3
"""Manage the version-aligned SSOT boundary/release lifecycle for this repo."""

from __future__ import annotations

import argparse
import json

from sync_ssot_registry import REGISTRY_PATH, VERSION_PATH, load_registry, require_ssot_version, run_ssot


ADVANCED_RELEASE_STATUSES = {"certified", "promoted", "published"}


def current_version() -> str:
    return VERSION_PATH.read_text(encoding="utf-8").strip()


def current_boundary_id(version: str) -> str:
    return f"bnd:{version}"


def current_release_id(version: str) -> str:
    return f"rel:{version}"


def save_registry(registry: dict) -> None:
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def prepare() -> str:
    require_ssot_version()
    registry = load_registry()
    version = current_version()
    boundary_id = current_boundary_id(version)
    release_id = current_release_id(version)
    feature_ids = sorted(
        row["id"] for row in registry.get("features", []) if row.get("implementation_status") == "implemented"
    )
    claim_ids = sorted(row["id"] for row in registry.get("claims", []))
    evidence_ids = sorted(row["id"] for row in registry.get("evidence", []))

    boundary_rows = registry.setdefault("boundaries", [])
    release_rows = registry.setdefault("releases", [])
    registry.setdefault("repo", {})["version"] = version
    registry.setdefault("program", {})["active_boundary_id"] = boundary_id
    registry.setdefault("program", {})["active_release_id"] = release_id

    boundary = next((row for row in boundary_rows if row["id"] == boundary_id), None)
    if boundary is None:
        boundary = {
            "id": boundary_id,
            "title": f"Certification boundary for {version}",
            "status": "active",
            "frozen": False,
            "feature_ids": feature_ids,
            "profile_ids": [],
        }
        boundary_rows.append(boundary)
    else:
        if boundary.get("frozen", False) and sorted(boundary.get("feature_ids", [])) != feature_ids:
            raise RuntimeError(
                f"{boundary_id} is frozen but its feature set no longer matches the current repo state. Bump VERSION before changing certified scope."
            )
        boundary["title"] = f"Certification boundary for {version}"
        boundary["status"] = "frozen" if boundary.get("frozen", False) else "active"
        boundary["feature_ids"] = feature_ids
        boundary.setdefault("profile_ids", [])

    release = next((row for row in release_rows if row["id"] == release_id), None)
    if release is None:
        release = {
            "id": release_id,
            "version": version,
            "status": "candidate",
            "boundary_id": boundary_id,
            "claim_ids": claim_ids,
            "evidence_ids": evidence_ids,
        }
        release_rows.append(release)
    else:
        current_claim_ids = sorted(release.get("claim_ids", []))
        current_evidence_ids = sorted(release.get("evidence_ids", []))
        if release.get("status") in ADVANCED_RELEASE_STATUSES and (
            current_claim_ids != claim_ids or current_evidence_ids != evidence_ids
        ):
            raise RuntimeError(
                f"{release_id} is already advanced beyond candidate but its claim/evidence set no longer matches the current repo state. Bump VERSION before changing certified scope."
            )
        release["version"] = version
        release["boundary_id"] = boundary_id
        release["status"] = release.get("status") if release.get("status") in ADVANCED_RELEASE_STATUSES else "candidate"
        release["claim_ids"] = claim_ids
        release["evidence_ids"] = evidence_ids

    boundary_rows[:] = [
        row
        for row in boundary_rows
        if row["id"] == boundary_id or row.get("status") not in {"draft", "retired"}
    ]

    release_rows[:] = [
        row
        for row in release_rows
        if row["id"] == release_id or row.get("status") not in {"draft", "revoked"}
    ]

    save_registry(registry)
    run_ssot("validate", ".", "--write-report")
    run_ssot("claim", "evaluate", ".")
    run_ssot("evidence", "verify", ".")
    return release_id


def certify_promote() -> str:
    release_id = prepare()
    version = current_version()
    run_ssot("boundary", "freeze", ".", "--boundary-id", current_boundary_id(version))
    run_ssot("release", "certify", ".", "--release-id", release_id, "--write-report")
    run_ssot("release", "promote", ".", "--release-id", release_id)
    return release_id


def publish_release() -> str:
    release_id = certify_promote()
    run_ssot("release", "publish", ".", "--release-id", release_id)
    return release_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["prepare", "certify-promote", "publish"],
        help="Lifecycle action to run for the current VERSION.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "prepare":
        release_id = prepare()
    elif args.command == "certify-promote":
        release_id = certify_promote()
    else:
        release_id = publish_release()
    print(release_id)


if __name__ == "__main__":
    main()
