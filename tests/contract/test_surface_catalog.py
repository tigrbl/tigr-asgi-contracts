from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ssot" / "registry.json"
SURFACES = ROOT / "contract" / "surfaces.yaml"


def test_surface_catalog_matches_declared_boundary() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    catalog = yaml.safe_load(SURFACES.read_text(encoding="utf-8"))["surface_catalog"]
    boundary = next(row for row in registry["boundaries"] if row["id"] == catalog["boundary_id"])

    catalog_ids = {
        row["id"]
        for rows in catalog["families"].values()
        for row in rows
    }
    boundary_ids = set(boundary["feature_ids"])
    features = {row["id"]: row for row in registry["features"]}

    assert catalog["target_claim_tier"] == "T2"
    assert catalog_ids == boundary_ids
    assert all(features[feature_id]["plan"]["horizon"] != "out_of_bounds" for feature_id in catalog_ids)
    assert all(features[feature_id]["implementation_status"] == "implemented" for feature_id in catalog_ids)
    assert all(features[feature_id]["plan"]["target_claim_tier"] == "T2" for feature_id in catalog_ids)


def test_surface_catalog_excludes_out_of_bounds_features() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    catalog = yaml.safe_load(SURFACES.read_text(encoding="utf-8"))["surface_catalog"]

    catalog_ids = {
        row["id"]
        for rows in catalog["families"].values()
        for row in rows
    }
    out_of_bounds_ids = {
        row["id"]
        for row in registry["features"]
        if row["plan"]["horizon"] == "out_of_bounds"
    }

    assert catalog_ids.isdisjoint(out_of_bounds_ids)
    assert out_of_bounds_ids
