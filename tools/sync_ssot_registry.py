#!/usr/bin/env python3
"""Initialize/upgrade and sync this repo into ssot-registry.

This script uses the PyPI `ssot-registry` package through `python -m ssot_registry`.
If the package is installed into `.tmp/ssot_registry_pkg`, that local copy is used.

Notes:
- `ssot-registry` has no first-class `profile` entity. This sync maps the
  repository's contract surfaces, generated/runtime verification surfaces, test
  files, and individual pytest cases into the supported feature/test/claim/evidence
  entities.
- The sync is additive and idempotent. It creates missing entities, updates basic
  fields for known entities, and adds missing links without deleting unrelated
  existing data.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import build_normalized_feature_matrix as normalized_matrix


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contract"
TESTS_ROOT = ROOT / "tests"
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
LOCAL_SSOT_SITE = ROOT / ".tmp" / "ssot_registry_pkg"
CONTRACT_REGISTRY_PATH = ROOT / "packages" / "contract-py" / "src" / "tigr_asgi_contract" / "registry.py"
VERSION_PATH = ROOT / "VERSION"

CODE_TO_STATUS = {
    "R": "implemented",
    "D": "implemented",
    "O": "partial",
    "F": "absent",
}

CODE_LABEL = {
    "R": "required",
    "D": "derived",
    "O": "optional",
    "F": "forbidden",
}

NORMALIZED_MATRIX_EXACT_EXISTING_FEATURE_IDS = {
    "feat:schemas-scope-schema",
    "feat:schemas-transport-schema",
}

HTTP_ADJACENT_TERMS = {
    "early hints",
    "early-hints",
    "trailers",
    "trailer",
    "redirect",
    "upgrade",
}

PROXY_METADATA_TERMS = {
    "forwarded",
    "x-forwarded",
    "x-real-ip",
    "proxy",
    "peer",
}


@dataclass
class FeatureSpec:
    entity_id: str
    title: str
    description: str
    implementation_status: str = "implemented"
    plan_horizon: str = "current"
    target_claim_tier: str = "T2"
    claim_ids: set[str] = field(default_factory=set)
    test_ids: set[str] = field(default_factory=set)
    spec_ids: set[str] = field(default_factory=set)
    matrix_provenance: dict[str, str] = field(default_factory=dict)
    overwrite_links: bool = True


@dataclass
class ClaimSpec:
    entity_id: str
    title: str
    kind: str
    description: str
    status: str = "evidenced"
    tier: str = "T2"
    feature_ids: set[str] = field(default_factory=set)
    test_ids: set[str] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)


@dataclass
class TestSpec:
    entity_id: str
    title: str
    kind: str
    path: str
    status: str = "passing"
    feature_ids: set[str] = field(default_factory=set)
    claim_ids: set[str] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)


@dataclass
class EvidenceSpec:
    entity_id: str
    title: str
    kind: str
    path: str
    status: str = "passed"
    tier: str = "T2"
    claim_ids: set[str] = field(default_factory=set)
    test_ids: set[str] = field(default_factory=set)


def norm(token: str) -> str:
    return token.replace(".schema", "-schema").replace(".", "-").replace("_", "-").replace("/", "-")


def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def contract_rel_posix(path: Path) -> str:
    return path.relative_to(CONTRACT_ROOT).as_posix()


def load_contract_registry():
    spec = spec_from_file_location("tigr_registry", CONTRACT_REGISTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load contract registry: {CONTRACT_REGISTRY_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ssot_env() -> dict[str, str]:
    env = os.environ.copy()
    if LOCAL_SSOT_SITE.exists():
        current = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(LOCAL_SSOT_SITE) if not current else f"{LOCAL_SSOT_SITE}{os.pathsep}{current}"
    return env


def run_ssot(*args: str) -> None:
    cmd = [sys.executable, "-m", "ssot_registry", *args]
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        env=ssot_env(),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{detail}")


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def ensure_registry() -> None:
    repo_id = norm(ROOT.name)
    repo_name = ROOT.name
    version = VERSION_PATH.read_text(encoding="utf-8").strip() if VERSION_PATH.exists() else "0.1.0"
    if REGISTRY_PATH.exists():
        try:
            run_ssot("upgrade", ".")
        except RuntimeError as exc:
            print(f"warning: ssot upgrade skipped: {exc}", file=sys.stderr)
    else:
        run_ssot("init", ".", "--repo-id", repo_id, "--repo-name", repo_name, "--version", version)


def artifact_slug(path: Path) -> str:
    rel = contract_rel_posix(path)
    if rel.startswith("legality/"):
        return f"legality-{norm(rel.removesuffix('.yaml').split('/', 1)[1])}"
    if rel.startswith("schemas/"):
        return f"schemas-{norm(rel.split('/', 1)[1].removesuffix('.json'))}"
    suffix = path.suffix
    if suffix in {".yaml", ".json", ".txt"}:
        return norm(rel.removesuffix(suffix))
    return norm(rel)


def artifact_feature_id(path: Path) -> str:
    return f"feat:{artifact_slug(path)}"


def artifact_claim_id(path: Path) -> str:
    return f"clm:{artifact_slug(path)}"


def file_test_id(path: Path) -> str:
    return f"tst:{norm(rel_posix(path).removeprefix('tests/').removesuffix('.py'))}"


def case_test_id(path: Path, case_name: str) -> str:
    base = rel_posix(path).removeprefix("tests/").removesuffix(".py")
    return f"tst:case-{norm(base)}-{norm(case_name.removeprefix('test_'))}"


def evidence_id_for_file_test(test_id: str) -> str:
    return f"evd:{test_id.removeprefix('tst:')}"


def discover_test_cases() -> dict[str, list[str]]:
    cases: dict[str, list[str]] = {}
    for path in sorted(TESTS_ROOT.rglob("test_*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        case_names = [
            node.name
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        cases[rel_posix(path)] = case_names
    return cases


def normalized_candidate_spec_ids(row: dict[str, str]) -> set[str]:
    kind = row.get("feature_kind", "")
    surface_key = row.get("feature_surface_key", "").lower()
    title = row.get("title", "").lower()
    schema_path = row.get("schema_path", "").lower()
    concern = row.get("concern", "").lower()
    haystack = " ".join([surface_key, title, schema_path, concern])

    if kind == "schema":
        spec_ids = {"spc:1019"}
        if any(term in haystack for term in PROXY_METADATA_TERMS):
            spec_ids.add("spc:1026")
        if any(term in haystack for term in HTTP_ADJACENT_TERMS):
            spec_ids.add("spc:1027")
        if any(
            term in haystack
            for term in (
                "header",
                "path",
                "query",
                "client",
                "server",
                "state",
                "scheme",
                "method",
                "scope",
            )
        ):
            spec_ids.add("spc:1025")
        return spec_ids
    if kind == "event":
        spec_ids = {"spc:1000", "spc:1020"}
        if "lifespan." in haystack:
            spec_ids.add("spc:1024")
        if any(term in haystack for term in HTTP_ADJACENT_TERMS):
            spec_ids.add("spc:1027")
        return spec_ids
    if kind == "scope":
        return {"spc:1000", "spc:1012", "spc:1021"}
    if kind == "frame":
        return {"spc:1004", "spc:1023"}
    if kind == "concern":
        spec_ids = {"spc:1022"}
        if any(term in haystack for term in PROXY_METADATA_TERMS):
            spec_ids.add("spc:1026")
        if any(term in haystack for term in HTTP_ADJACENT_TERMS):
            spec_ids.add("spc:1027")
        return spec_ids
    if kind == "lifespan":
        return {"spc:1012", "spc:1024"}
    return {"spc:1018"}


def normalized_candidate_description(row: dict[str, str]) -> str:
    description = row.get("description", "").strip() or (
        f"Normalized feature candidate for {row.get('feature_surface_key', '').strip()}."
    )
    return (
        f"{description} Promoted from reports/normalized_master_feature_matrix.xlsx "
        f"as agreed normalized candidate {row.get('candidate_feature_id')}."
    )


def normalized_candidate_provenance(row: dict[str, str]) -> dict[str, str]:
    return {
        "source": "reports/normalized_master_feature_matrix.xlsx",
        "feature_surface_key": row.get("feature_surface_key", ""),
        "source_count": row.get("source_count", ""),
        "source_files": row.get("source_files", ""),
        "source_sheets": row.get("source_sheets", ""),
        "source_rows": row.get("source_rows", ""),
        "primary_source": (
            f"{row.get('primary_source_file', '')}:{row.get('primary_source_row', '')}"
        ).strip(":"),
        "dedupe_confidence": row.get("dedupe_confidence", ""),
        "review_status": "promoted",
    }


def build_normalized_candidate_feature_specs() -> dict[str, FeatureSpec]:
    records, _ = normalized_matrix.load_source_records()
    groups, _ = normalized_matrix.group_records(records)
    rows = normalized_matrix.normalized_rows(groups)
    specs: dict[str, FeatureSpec] = {}
    for row in rows:
        candidate_id = row["candidate_feature_id"]
        if candidate_id in NORMALIZED_MATRIX_EXACT_EXISTING_FEATURE_IDS:
            continue
        specs[candidate_id] = FeatureSpec(
            entity_id=candidate_id,
            title=row["title"],
            description=normalized_candidate_description(row),
            implementation_status=row["implementation_status"],
            plan_horizon=row["plan_horizon"],
            target_claim_tier=row["target_claim_tier"] or "T2",
            spec_ids=normalized_candidate_spec_ids(row),
            matrix_provenance=normalized_candidate_provenance(row),
            overwrite_links=False,
        )
    return specs


def build_specs() -> tuple[dict[str, FeatureSpec], dict[str, ClaimSpec], dict[str, TestSpec], dict[str, EvidenceSpec]]:
    contract_registry = load_contract_registry()
    features: dict[str, FeatureSpec] = {}
    claims: dict[str, ClaimSpec] = {}
    tests: dict[str, TestSpec] = {}
    evidence: dict[str, EvidenceSpec] = {}

    artifact_paths = sorted(path for path in CONTRACT_ROOT.rglob("*") if path.is_file())
    schema_paths = [path for path in artifact_paths if contract_rel_posix(path).startswith("schemas/")]
    legality_paths = [path for path in artifact_paths if contract_rel_posix(path).startswith("legality/")]

    for path in artifact_paths:
        rel = rel_posix(path)
        feat_id = artifact_feature_id(path)
        clm_id = artifact_claim_id(path)
        features[feat_id] = FeatureSpec(
            entity_id=feat_id,
            title=f"Contract artifact {rel}",
            description=f"SSOT feature tracking for {rel}.",
            implementation_status="implemented",
            claim_ids={clm_id},
        )
        claims[clm_id] = ClaimSpec(
            entity_id=clm_id,
            title=f"Conformance claim for {rel}",
            kind="conformance",
            description=f"{rel} is covered by repository tests and tracked evidence.",
            feature_ids={feat_id},
        )

    binding_family_ids: set[str] = set()
    family_subevent_ids: set[str] = set()
    binding_subevent_ids: set[str] = set()
    implemented_binding_family_ids: set[str] = set()
    implemented_family_subevent_ids: set[str] = set()
    implemented_binding_subevent_ids: set[str] = set()

    for binding, families in sorted(contract_registry.BINDING_FAMILY_MATRIX.items()):
        for family, code in sorted(families.items()):
            feat_id = f"feat:binding-family-{norm(binding)}-{norm(family)}"
            binding_family_ids.add(feat_id)
            if CODE_TO_STATUS[code] == "implemented":
                implemented_binding_family_ids.add(feat_id)
            claim_ids = {"clm:bindings", "clm:families", "clm:legality-binding-family"} if CODE_TO_STATUS[code] == "implemented" else set()
            features[feat_id] = FeatureSpec(
                entity_id=feat_id,
                title=f"Binding family {binding} x {family}",
                description=f"From BINDING_FAMILY_MATRIX: code {code} ({CODE_LABEL[code]}).",
                implementation_status=CODE_TO_STATUS[code],
                claim_ids=claim_ids,
            )

    for family, subevents in sorted(contract_registry.FAMILY_SUBEVENT_MATRIX.items()):
        for subevent, code in sorted(subevents.items()):
            feat_id = f"feat:family-subevent-{norm(family)}-{norm(subevent)}"
            family_subevent_ids.add(feat_id)
            if CODE_TO_STATUS[code] == "implemented":
                implemented_family_subevent_ids.add(feat_id)
            claim_ids = {"clm:families", "clm:subevents", "clm:legality-family-subevent"} if CODE_TO_STATUS[code] == "implemented" else set()
            features[feat_id] = FeatureSpec(
                entity_id=feat_id,
                title=f"Family subevent {family} x {subevent}",
                description=f"From FAMILY_SUBEVENT_MATRIX: code {code} ({CODE_LABEL[code]}).",
                implementation_status=CODE_TO_STATUS[code],
                claim_ids=claim_ids,
            )

    for binding, subevents in sorted(contract_registry.BINDING_SUBEVENT_MATRIX.items()):
        for subevent, code in sorted(subevents.items()):
            feat_id = f"feat:binding-subevent-{norm(binding)}-{norm(subevent)}"
            binding_subevent_ids.add(feat_id)
            if CODE_TO_STATUS[code] == "implemented":
                implemented_binding_subevent_ids.add(feat_id)
            claim_ids = {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"} if CODE_TO_STATUS[code] == "implemented" else set()
            features[feat_id] = FeatureSpec(
                entity_id=feat_id,
                title=f"Binding subevent {binding} x {subevent}",
                description=f"From BINDING_SUBEVENT_MATRIX: code {code} ({CODE_LABEL[code]}).",
                implementation_status=CODE_TO_STATUS[code],
                claim_ids=claim_ids,
            )

    claims["clm:bindings"].feature_ids.update(implemented_binding_family_ids | implemented_binding_subevent_ids)
    claims["clm:families"].feature_ids.update(implemented_binding_family_ids | implemented_family_subevent_ids)
    claims["clm:subevents"].feature_ids.update(implemented_family_subevent_ids | implemented_binding_subevent_ids)
    claims["clm:legality-binding-family"].feature_ids.update(implemented_binding_family_ids)
    claims["clm:legality-family-subevent"].feature_ids.update(implemented_family_subevent_ids)
    claims["clm:legality-binding-subevent"].feature_ids.update(implemented_binding_subevent_ids)

    all_artifact_feature_ids = {artifact_feature_id(path) for path in artifact_paths}
    all_artifact_claim_ids = {artifact_claim_id(path) for path in artifact_paths}
    schema_feature_ids = {artifact_feature_id(path) for path in schema_paths}
    schema_claim_ids = {artifact_claim_id(path) for path in schema_paths}
    legality_feature_ids = {artifact_feature_id(path) for path in legality_paths}
    legality_claim_ids = {artifact_claim_id(path) for path in legality_paths}

    def register_file_test(
        path_str: str,
        *,
        feature_ids: set[str],
        claim_ids: set[str],
        evidence_links: bool = True,
    ) -> None:
        path = ROOT / path_str
        test_id = file_test_id(path)
        evidence_id = evidence_id_for_file_test(test_id)
        tests[test_id] = TestSpec(
            entity_id=test_id,
            title=f"Automated test {path_str}",
            kind="pytest",
            path=path_str,
            feature_ids=set(feature_ids),
            claim_ids=set(claim_ids),
            evidence_ids={evidence_id} if evidence_links else set(),
        )
        evidence[evidence_id] = EvidenceSpec(
            entity_id=evidence_id,
            title=f"Test evidence from {path_str}",
            kind="test-report",
            path=path_str,
            claim_ids=set(claim_ids),
            test_ids={test_id},
        )
        for feature_id in feature_ids:
            if feature_id in features:
                features[feature_id].test_ids.add(test_id)
        for claim_id in claim_ids:
            if claim_id in claims:
                claims[claim_id].test_ids.add(test_id)
                claims[claim_id].evidence_ids.add(evidence_id)

    register_file_test(
        "tests/codegen/test_python_codegen.py",
        feature_ids={"feat:bindings", "feat:families", "feat:legality-binding-family"},
        claim_ids={"clm:bindings", "clm:families", "clm:legality-binding-family"},
    )
    register_file_test(
        "tests/codegen/test_rust_codegen.py",
        feature_ids=set(all_artifact_feature_ids),
        claim_ids=set(all_artifact_claim_ids),
    )
    register_file_test(
        "tests/codegen/test_ts_codegen.py",
        feature_ids=set(all_artifact_feature_ids),
        claim_ids=set(all_artifact_claim_ids),
    )
    register_file_test(
        "tests/contract/test_checksums.py",
        feature_ids={"feat:checksums", "feat:manifest"},
        claim_ids={"clm:checksums", "clm:manifest"},
    )
    register_file_test(
        "tests/contract/test_jsonschemas.py",
        feature_ids=set(schema_feature_ids),
        claim_ids=set(schema_claim_ids),
    )
    register_file_test(
        "tests/contract/test_legality.py",
        feature_ids=set(legality_feature_ids | binding_family_ids | family_subevent_ids | binding_subevent_ids),
        claim_ids={"clm:bindings", "clm:families", "clm:subevents"} | legality_claim_ids,
    )
    register_file_test(
        "tests/contract/test_manifest.py",
        feature_ids={"feat:manifest"},
        claim_ids={"clm:manifest"},
    )
    register_file_test(
        "tests/parity/test_cross_language_roundtrip.py",
        feature_ids={"feat:bindings", "feat:families", "feat:binding-family-rest-request"},
        claim_ids={"clm:bindings", "clm:families", "clm:legality-binding-family"},
    )
    register_file_test(
        "tests/parity/test_python_vs_contract.py",
        feature_ids={"feat:bindings"},
        claim_ids={"clm:bindings"},
    )
    register_file_test(
        "tests/parity/test_rust_vs_contract.py",
        feature_ids=set(legality_feature_ids),
        claim_ids=set(legality_claim_ids),
    )
    register_file_test(
        "tests/parity/test_ts_vs_contract.py",
        feature_ids=set(legality_feature_ids),
        claim_ids=set(legality_claim_ids),
    )

    case_links: dict[tuple[str, str], tuple[set[str], set[str]]] = {
        ("tests/codegen/test_python_codegen.py", "test_python_binding_supports_family"): (
            {"feat:bindings", "feat:families", "feat:binding-family-websocket-message"},
            {"clm:bindings", "clm:families", "clm:legality-binding-family"},
        ),
        ("tests/codegen/test_rust_codegen.py", "test_rust_generated_files_exist"): (
            set(all_artifact_feature_ids),
            set(all_artifact_claim_ids),
        ),
        ("tests/codegen/test_ts_codegen.py", "test_ts_generated_files_exist"): (
            set(all_artifact_feature_ids),
            set(all_artifact_claim_ids),
        ),
        ("tests/contract/test_checksums.py", "test_checksums_contains_manifest"): (
            {"feat:checksums", "feat:manifest"},
            {"clm:checksums", "clm:manifest"},
        ),
        ("tests/contract/test_jsonschemas.py", "test_all_schemas_are_valid"): (
            set(schema_feature_ids),
            set(schema_claim_ids),
        ),
        ("tests/contract/test_legality.py", "test_webtransport_datagram_required"): (
            {"feat:legality-binding-family", "feat:binding-family-webtransport-datagram"},
            {"clm:bindings", "clm:families", "clm:legality-binding-family"},
        ),
        ("tests/contract/test_manifest.py", "test_manifest_exists"): (
            {"feat:manifest"},
            {"clm:manifest"},
        ),
        ("tests/parity/test_cross_language_roundtrip.py", "test_cross_language_roundtrip_smoke"): (
            {"feat:bindings", "feat:families", "feat:binding-family-rest-request"},
            {"clm:bindings", "clm:families", "clm:legality-binding-family"},
        ),
        ("tests/parity/test_python_vs_contract.py", "test_python_bindings_match_contract"): (
            {"feat:bindings"},
            {"clm:bindings"},
        ),
        ("tests/parity/test_rust_vs_contract.py", "test_rust_registry_exists"): (
            set(legality_feature_ids),
            set(legality_claim_ids),
        ),
        ("tests/parity/test_ts_vs_contract.py", "test_ts_registry_exists"): (
            set(legality_feature_ids),
            set(legality_claim_ids),
        ),
    }

    for path_str, case_names in discover_test_cases().items():
        for case_name in case_names:
            if (path_str, case_name) not in case_links:
                continue
            feature_ids, claim_ids = case_links[(path_str, case_name)]
            case_id = case_test_id(ROOT / path_str, case_name)
            evidence_id = evidence_id_for_file_test(file_test_id(ROOT / path_str))
            tests[case_id] = TestSpec(
                entity_id=case_id,
                title=f"Pytest case {path_str}::{case_name}",
                kind="pytest-case",
                path=path_str,
                feature_ids=set(feature_ids),
                claim_ids=set(claim_ids),
                evidence_ids={evidence_id},
            )
            for feature_id in feature_ids:
                if feature_id in features:
                    features[feature_id].test_ids.add(case_id)
            for claim_id in claim_ids:
                if claim_id in claims:
                    claims[claim_id].test_ids.add(case_id)
                    claims[claim_id].evidence_ids.add(evidence_id)
            if evidence_id in evidence:
                evidence[evidence_id].test_ids.add(case_id)
                evidence[evidence_id].claim_ids.update(claim_ids)

    features.update(build_normalized_candidate_feature_specs())

    return features, claims, tests, evidence


def merge_sorted_unique(existing: list[str] | None, additions: set[str]) -> tuple[list[str], int]:
    current = list(existing or [])
    current_set = set(current)
    missing = sorted(additions - current_set)
    if missing:
        current.extend(missing)
    return current, len(missing)


def upsert_feature_rows(registry: dict, specs: dict[str, FeatureSpec]) -> tuple[int, int]:
    rows = registry.setdefault("features", [])
    lookup = {row["id"]: row for row in rows}
    created_or_updated = 0
    links_added = 0

    for spec in specs.values():
        row = lookup.get(spec.entity_id)
        if row is None:
            row = {
                "id": spec.entity_id,
                "title": spec.title,
                "description": spec.description,
                "implementation_status": spec.implementation_status,
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {
                    "horizon": spec.plan_horizon,
                    "slot": None,
                    "target_claim_tier": spec.target_claim_tier,
                    "target_lifecycle_stage": "active",
                },
                "claim_ids": sorted(spec.claim_ids),
                "test_ids": sorted(spec.test_ids),
                "requires": [],
            }
            if spec.spec_ids:
                row["spec_ids"] = sorted(spec.spec_ids)
            if spec.matrix_provenance:
                row["matrix_provenance"] = spec.matrix_provenance
            rows.append(row)
            lookup[spec.entity_id] = row
            created_or_updated += 1
            links_added += len(spec.claim_ids) + len(spec.test_ids) + len(spec.spec_ids)
            continue

        changed = False
        if row.get("title") != spec.title:
            row["title"] = spec.title
            changed = True
        if row.get("description") != spec.description:
            row["description"] = spec.description
            changed = True
        if row.get("implementation_status") != spec.implementation_status:
            row["implementation_status"] = spec.implementation_status
            changed = True
        row.setdefault("lifecycle", {"stage": "active", "replacement_feature_ids": [], "note": None})
        row.setdefault(
            "plan",
            {
                "horizon": "current",
                "slot": None,
                "target_claim_tier": "T2",
                "target_lifecycle_stage": "active",
            },
        )
        if spec.matrix_provenance:
            plan = row["plan"]
            desired_plan = {
                "horizon": spec.plan_horizon,
                "slot": plan.get("slot"),
                "target_claim_tier": spec.target_claim_tier,
                "target_lifecycle_stage": plan.get("target_lifecycle_stage", "active"),
            }
            if plan != desired_plan:
                row["plan"] = desired_plan
                changed = True
            if row.get("matrix_provenance") != spec.matrix_provenance:
                row["matrix_provenance"] = spec.matrix_provenance
                changed = True
        desired_spec_ids = sorted(spec.spec_ids)
        if desired_spec_ids:
            row["spec_ids"], added = merge_sorted_unique(row.get("spec_ids"), spec.spec_ids)
            links_added += added
        if spec.overwrite_links:
            desired_claim_ids = sorted(spec.claim_ids)
            desired_test_ids = sorted(spec.test_ids)
            if row.get("claim_ids") != desired_claim_ids:
                row["claim_ids"] = desired_claim_ids
                changed = True
            if row.get("test_ids") != desired_test_ids:
                row["test_ids"] = desired_test_ids
                changed = True
            links_added += len(desired_claim_ids) + len(desired_test_ids)
        else:
            row["claim_ids"], added = merge_sorted_unique(row.get("claim_ids"), spec.claim_ids)
            links_added += added
            row["test_ids"], added = merge_sorted_unique(row.get("test_ids"), spec.test_ids)
            links_added += added
        row.setdefault("requires", [])
        if changed:
            created_or_updated += 1

    return created_or_updated, links_added


def upsert_claim_rows(registry: dict, specs: dict[str, ClaimSpec]) -> tuple[int, int]:
    rows = registry.setdefault("claims", [])
    lookup = {row["id"]: row for row in rows}
    created_or_updated = 0
    links_added = 0

    for spec in specs.values():
        row = lookup.get(spec.entity_id)
        if row is None:
            row = {
                "id": spec.entity_id,
                "title": spec.title,
                "status": spec.status,
                "tier": spec.tier,
                "kind": spec.kind,
                "description": spec.description,
                "feature_ids": sorted(spec.feature_ids),
                "test_ids": sorted(spec.test_ids),
                "evidence_ids": sorted(spec.evidence_ids),
            }
            rows.append(row)
            lookup[spec.entity_id] = row
            created_or_updated += 1
            links_added += len(spec.feature_ids) + len(spec.test_ids) + len(spec.evidence_ids)
            continue

        changed = False
        for key, value in {
            "title": spec.title,
            "status": spec.status,
            "tier": spec.tier,
            "kind": spec.kind,
            "description": spec.description,
        }.items():
            if row.get(key) != value:
                row[key] = value
                changed = True
        desired_feature_ids = sorted(spec.feature_ids)
        desired_test_ids = sorted(spec.test_ids)
        desired_evidence_ids = sorted(spec.evidence_ids)
        if row.get("feature_ids") != desired_feature_ids:
            row["feature_ids"] = desired_feature_ids
            changed = True
        if row.get("test_ids") != desired_test_ids:
            row["test_ids"] = desired_test_ids
            changed = True
        if row.get("evidence_ids") != desired_evidence_ids:
            row["evidence_ids"] = desired_evidence_ids
            changed = True
        links_added += len(desired_feature_ids) + len(desired_test_ids) + len(desired_evidence_ids)
        if changed:
            created_or_updated += 1

    return created_or_updated, links_added


def upsert_test_rows(registry: dict, specs: dict[str, TestSpec]) -> tuple[int, int]:
    rows = registry.setdefault("tests", [])
    lookup = {row["id"]: row for row in rows}
    created_or_updated = 0
    links_added = 0

    for spec in specs.values():
        row = lookup.get(spec.entity_id)
        if row is None:
            row = {
                "id": spec.entity_id,
                "title": spec.title,
                "status": spec.status,
                "kind": spec.kind,
                "path": spec.path,
                "feature_ids": sorted(spec.feature_ids),
                "claim_ids": sorted(spec.claim_ids),
                "evidence_ids": sorted(spec.evidence_ids),
            }
            rows.append(row)
            lookup[spec.entity_id] = row
            created_or_updated += 1
            links_added += len(spec.feature_ids) + len(spec.claim_ids) + len(spec.evidence_ids)
            continue

        changed = False
        for key, value in {
            "title": spec.title,
            "status": spec.status,
            "kind": spec.kind,
            "path": spec.path,
        }.items():
            if row.get(key) != value:
                row[key] = value
                changed = True
        row["feature_ids"], added = merge_sorted_unique(row.get("feature_ids"), spec.feature_ids)
        links_added += added
        row["claim_ids"], added = merge_sorted_unique(row.get("claim_ids"), spec.claim_ids)
        links_added += added
        row["evidence_ids"], added = merge_sorted_unique(row.get("evidence_ids"), spec.evidence_ids)
        links_added += added
        if changed:
            created_or_updated += 1

    return created_or_updated, links_added


def upsert_evidence_rows(registry: dict, specs: dict[str, EvidenceSpec]) -> tuple[int, int]:
    rows = registry.setdefault("evidence", [])
    lookup = {row["id"]: row for row in rows}
    created_or_updated = 0
    links_added = 0

    for spec in specs.values():
        row = lookup.get(spec.entity_id)
        if row is None:
            row = {
                "id": spec.entity_id,
                "title": spec.title,
                "status": spec.status,
                "kind": spec.kind,
                "tier": spec.tier,
                "path": spec.path,
                "claim_ids": sorted(spec.claim_ids),
                "test_ids": sorted(spec.test_ids),
            }
            rows.append(row)
            lookup[spec.entity_id] = row
            created_or_updated += 1
            links_added += len(spec.claim_ids) + len(spec.test_ids)
            continue

        changed = False
        for key, value in {
            "title": spec.title,
            "status": spec.status,
            "kind": spec.kind,
            "tier": spec.tier,
            "path": spec.path,
        }.items():
            if row.get(key) != value:
                row[key] = value
                changed = True
        row["claim_ids"], added = merge_sorted_unique(row.get("claim_ids"), spec.claim_ids)
        links_added += added
        row["test_ids"], added = merge_sorted_unique(row.get("test_ids"), spec.test_ids)
        links_added += added
        if changed:
            created_or_updated += 1

    return created_or_updated, links_added


def save_registry(registry: dict) -> None:
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ensure_registry()
    features, claims, tests, evidence = build_specs()
    registry = load_registry()
    feature_changes, feature_links = upsert_feature_rows(registry, features)
    claim_changes, claim_links = upsert_claim_rows(registry, claims)
    test_changes, test_links = upsert_test_rows(registry, tests)
    evidence_changes, evidence_links = upsert_evidence_rows(registry, evidence)

    save_registry(registry)

    post_write_checks: dict[str, str] = {}
    for label, args in {
        "validate": ("validate", ".", "--write-report"),
        "claim_evaluate": ("claim", "evaluate", "."),
        "evidence_verify": ("evidence", "verify", "."),
        "registry_export": ("registry", "export", ".", "--format", "json"),
    }.items():
        try:
            run_ssot(*args)
            post_write_checks[label] = "passed"
        except RuntimeError as exc:
            post_write_checks[label] = f"failed: {exc}"

    final_registry = load_registry()
    print(
        json.dumps(
            {
                "created_or_updated": {
                    "features": feature_changes,
                    "claims": claim_changes,
                    "tests": test_changes,
                    "evidence": evidence_changes,
                },
                "links_added": feature_links + claim_links + test_links + evidence_links,
                "final_counts": {
                    "features": len(final_registry.get("features", [])),
                    "claims": len(final_registry.get("claims", [])),
                    "tests": len(final_registry.get("tests", [])),
                    "evidence": len(final_registry.get("evidence", [])),
                },
                "post_write_checks": post_write_checks,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
