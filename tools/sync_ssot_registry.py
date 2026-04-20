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


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contract"
TESTS_ROOT = ROOT / "tests"
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
LOCAL_SSOT_SITE = ROOT / ".tmp" / "ssot_registry_pkg"
CONTRACT_REGISTRY_PATH = ROOT / "packages" / "contract-py" / "src" / "tigr_asgi_contract" / "registry.py"
VERSION_PATH = ROOT / "VERSION"
EXPECTED_SSOT_VERSION = "0.2.10"

CODE_TO_STATUS = {
    "R": "implemented",
    "D": "implemented",
    "O": "implemented",
    "F": "absent",
}

CODE_LABEL = {
    "R": "required",
    "D": "derived",
    "O": "optional",
    "F": "forbidden",
}


@dataclass
class FeatureSpec:
    entity_id: str
    title: str
    description: str
    implementation_status: str = "implemented"
    claim_ids: set[str] = field(default_factory=set)
    test_ids: set[str] = field(default_factory=set)


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


def require_ssot_version() -> None:
    added_path = False
    if LOCAL_SSOT_SITE.exists():
        sys.path.insert(0, str(LOCAL_SSOT_SITE))
        added_path = True
    try:
        import ssot_registry  # type: ignore
    finally:
        if added_path:
            sys.path.pop(0)
    version = getattr(ssot_registry, "__version__", None)
    if version != EXPECTED_SSOT_VERSION:
        raise RuntimeError(
            f"Expected ssot-registry {EXPECTED_SSOT_VERSION}, found {version or 'unknown'}."
        )


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
    require_ssot_version()
    repo_id = norm(ROOT.name)
    repo_name = ROOT.name
    version = VERSION_PATH.read_text(encoding="utf-8").strip() if VERSION_PATH.exists() else "0.1.0"
    if REGISTRY_PATH.exists():
        try:
            run_ssot("upgrade", ".", "--sync-docs", "--write-report")
        except RuntimeError as exc:
            print(f"warning: ssot upgrade skipped: {exc}", file=sys.stderr)
    else:
        run_ssot("init", ".", "--repo-id", repo_id, "--repo-name", repo_name, "--version", version)
        run_ssot("upgrade", ".", "--sync-docs", "--write-report")


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
        rel = rel_posix(path)
        if not rel.startswith(("tests/codegen/", "tests/contract/", "tests/parity/")):
            continue
        module = ast.parse(path.read_text(encoding="utf-8"))
        case_names = [
            node.name
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        cases[rel] = case_names
    return cases


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
    optional_binding_family_ids: set[str] = set()
    optional_binding_subevent_ids: set[str] = set()
    implemented_binding_family_ids: set[str] = set()
    implemented_family_subevent_ids: set[str] = set()
    implemented_binding_subevent_ids: set[str] = set()
    for binding, families in sorted(contract_registry.BINDING_FAMILY_MATRIX.items()):
        for family, code in sorted(families.items()):
            feat_id = f"feat:binding-family-{norm(binding)}-{norm(family)}"
            binding_family_ids.add(feat_id)
            if code == "O":
                optional_binding_family_ids.add(feat_id)
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
            if code == "O":
                optional_binding_subevent_ids.add(feat_id)
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
        "tests/contract/test_optional_features.py",
        feature_ids=set(optional_binding_family_ids | optional_binding_subevent_ids),
        claim_ids={
            "clm:bindings",
            "clm:families",
            "clm:subevents",
            "clm:legality-binding-family",
            "clm:legality-binding-subevent",
        },
    )
    register_file_test(
        "tests/contract/test_manifest.py",
        feature_ids={"feat:manifest"},
        claim_ids={"clm:manifest"},
    )
    register_file_test(
        "tests/contract/test_ssot_certification.py",
        feature_ids=set(features.keys()),
        claim_ids=set(claims.keys()),
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
        ("tests/contract/test_optional_features.py", "test_optional_binding_families_are_supported"): (
            set(optional_binding_family_ids),
            {"clm:bindings", "clm:families", "clm:legality-binding-family"},
        ),
        ("tests/contract/test_optional_features.py", "test_http_stream_optional_subevents_are_supported"): (
            {
                "feat:binding-subevent-http-stream-request-accept",
                "feat:binding-subevent-http-stream-request-body-in",
                "feat:binding-subevent-http-stream-request-disconnect",
                "feat:binding-subevent-http-stream-response-body-out",
                "feat:binding-subevent-http-stream-response-close",
                "feat:binding-subevent-http-stream-stream-abort",
                "feat:binding-subevent-http-stream-stream-flush",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_optional_features.py", "test_jsonrpc_optional_subevents_are_supported"): (
            {
                "feat:binding-subevent-jsonrpc-request-accept",
                "feat:binding-subevent-jsonrpc-request-disconnect",
                "feat:binding-subevent-jsonrpc-response-close",
                "feat:binding-subevent-jsonrpc-stream-chunk-in",
                "feat:binding-subevent-jsonrpc-stream-chunk-out",
                "feat:binding-subevent-jsonrpc-stream-close",
                "feat:binding-subevent-jsonrpc-stream-emit-complete",
                "feat:binding-subevent-jsonrpc-stream-finalize",
                "feat:binding-subevent-jsonrpc-stream-open",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_optional_features.py", "test_rest_optional_subevents_are_supported"): (
            {
                "feat:binding-subevent-rest-request-accept",
                "feat:binding-subevent-rest-request-disconnect",
                "feat:binding-subevent-rest-response-close",
                "feat:binding-subevent-rest-stream-chunk-in",
                "feat:binding-subevent-rest-stream-chunk-out",
                "feat:binding-subevent-rest-stream-close",
                "feat:binding-subevent-rest-stream-emit-complete",
                "feat:binding-subevent-rest-stream-finalize",
                "feat:binding-subevent-rest-stream-open",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_optional_features.py", "test_websocket_optional_subevents_are_supported"): (
            {
                "feat:binding-subevent-websocket-message-ack",
                "feat:binding-subevent-websocket-message-decode",
                "feat:binding-subevent-websocket-message-nack",
                "feat:binding-subevent-websocket-message-replay",
                "feat:binding-subevent-websocket-message-snapshot",
                "feat:binding-subevent-websocket-session-disconnect",
                "feat:binding-subevent-websocket-session-emit-complete",
                "feat:binding-subevent-websocket-session-heartbeat",
                "feat:binding-subevent-websocket-session-sync",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_optional_features.py", "test_sse_optional_subevents_are_supported"): (
            {
                "feat:binding-subevent-sse-request-accept",
                "feat:binding-subevent-sse-request-body-in",
                "feat:binding-subevent-sse-request-disconnect",
                "feat:binding-subevent-sse-response-open",
                "feat:binding-subevent-sse-response-close",
                "feat:binding-subevent-sse-session-disconnect",
                "feat:binding-subevent-sse-session-emit-complete",
                "feat:binding-subevent-sse-session-heartbeat",
                "feat:binding-subevent-sse-session-sync",
                "feat:binding-subevent-sse-message-replay",
                "feat:binding-subevent-sse-message-snapshot",
                "feat:binding-subevent-sse-stream-abort",
                "feat:binding-subevent-sse-stream-finalize",
                "feat:binding-subevent-sse-stream-flush",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_optional_features.py", "test_webtransport_optional_subevents_are_supported"): (
            {
                "feat:binding-family-webtransport-message",
                "feat:binding-subevent-webtransport-datagram-ack",
                "feat:binding-subevent-webtransport-session-disconnect",
                "feat:binding-subevent-webtransport-session-emit-complete",
                "feat:binding-subevent-webtransport-session-heartbeat",
                "feat:binding-subevent-webtransport-session-sync",
                "feat:binding-subevent-webtransport-message-ack",
                "feat:binding-subevent-webtransport-message-decode",
                "feat:binding-subevent-webtransport-message-emit-complete",
                "feat:binding-subevent-webtransport-message-handle",
                "feat:binding-subevent-webtransport-message-in",
                "feat:binding-subevent-webtransport-message-nack",
                "feat:binding-subevent-webtransport-message-out",
                "feat:binding-subevent-webtransport-message-replay",
                "feat:binding-subevent-webtransport-message-snapshot",
                "feat:binding-subevent-webtransport-stream-abort",
                "feat:binding-subevent-webtransport-stream-flush",
            },
            {"clm:bindings", "clm:subevents", "clm:legality-binding-family", "clm:legality-binding-subevent"},
        ),
        ("tests/contract/test_manifest.py", "test_manifest_exists"): (
            {"feat:manifest"},
            {"clm:manifest"},
        ),
        ("tests/contract/test_ssot_certification.py", "test_all_features_are_claim_covered_and_complete"): (
            set(features.keys()),
            set(claims.keys()),
        ),
        ("tests/contract/test_ssot_certification.py", "test_current_release_matches_repo_version"): (
            set(features.keys()),
            set(claims.keys()),
        ),
        ("tests/contract/test_ssot_certification.py", "test_validation_report_is_green_and_blockers_are_empty"): (
            set(features.keys()),
            set(claims.keys()),
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
                    "horizon": "current",
                    "slot": None,
                    "target_claim_tier": "T2",
                    "target_lifecycle_stage": "active",
                },
                "claim_ids": sorted(spec.claim_ids),
                "test_ids": sorted(spec.test_ids),
                "requires": [],
            }
            rows.append(row)
            lookup[spec.entity_id] = row
            created_or_updated += 1
            links_added += len(spec.claim_ids) + len(spec.test_ids)
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
        desired_plan = {
            "horizon": "current" if spec.implementation_status == "implemented" else "out_of_bounds",
            "slot": None,
            "target_claim_tier": "T2",
            "target_lifecycle_stage": "active",
        }
        if row.get("plan") != desired_plan:
            row["plan"] = desired_plan
            changed = True
        desired_claim_ids = sorted(spec.claim_ids)
        desired_test_ids = sorted(spec.test_ids)
        if row.get("claim_ids") != desired_claim_ids:
            row["claim_ids"] = desired_claim_ids
            changed = True
        if row.get("test_ids") != desired_test_ids:
            row["test_ids"] = desired_test_ids
            changed = True
        links_added += len(desired_claim_ids) + len(desired_test_ids)
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
    registry.setdefault("repo", {})["version"] = VERSION_PATH.read_text(encoding="utf-8").strip()
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
