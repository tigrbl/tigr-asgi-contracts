from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generators.common import contract_data
PACKAGES = ROOT / "packages"


def load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def fmt_code(value: str) -> str:
    return f"`{value}`"


def comma_code(values: list[str]) -> str:
    return ", ".join(fmt_code(value) for value in values)


def short_sha(value: str) -> str:
    return fmt_code(value[:12])


def render_markdown(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(line[8:] if line.startswith("        ") else line for line in lines).strip()


def current_version(data: dict) -> str:
    return data["manifest"]["contract_version"]


def package_metadata() -> dict[str, dict]:
    artifact_py = load_toml(PACKAGES / "artifacts-py" / "pyproject.toml")["project"]
    artifact_npm = json.loads((PACKAGES / "artifacts-npm" / "package.json").read_text(encoding="utf-8"))
    artifact_rs = load_toml(PACKAGES / "artifacts-rs" / "Cargo.toml")["package"]

    contract_py = load_toml(PACKAGES / "contract-py" / "pyproject.toml")["project"]
    contract_npm = json.loads((PACKAGES / "contract-npm" / "package.json").read_text(encoding="utf-8"))
    contract_rs = load_toml(PACKAGES / "contract-rs" / "Cargo.toml")["package"]

    return {
        "artifacts": {
            "python": artifact_py,
            "npm": artifact_npm,
            "rust": artifact_rs,
        },
        "contracts": {
            "python": contract_py,
            "npm": contract_npm,
            "rust": contract_rs,
        },
    }


def module_inventory() -> dict[str, dict[str, list[str]]]:
    return {
        "artifacts": {
            "python": sorted(
                path.stem
                for path in (PACKAGES / "artifacts-py" / "src" / "tigr_contract_artifacts").glob("*.py")
                if path.stem != "__init__"
            ),
            "npm": sorted(json.loads((PACKAGES / "artifacts-npm" / "package.json").read_text(encoding="utf-8"))["exports"].keys()),
            "rust": sorted(
                path.stem for path in (PACKAGES / "artifacts-rs" / "src").glob("*.rs") if path.stem != "lib"
            ),
        },
        "contracts": {
            "python": sorted(
                path.stem
                for path in (PACKAGES / "contract-py" / "src" / "tigr_asgi_contract").glob("*.py")
                if path.stem != "__init__"
            ),
            "npm": sorted(
                path.stem for path in (PACKAGES / "contract-npm" / "src").glob("*.ts") if path.stem != "index"
            )
            + [f"tsx/{path.stem}" for path in sorted((PACKAGES / "contract-npm" / "tsx").glob("*.tsx"))],
            "rust": sorted(path.stem for path in (PACKAGES / "contract-rs" / "src").glob("*.rs") if path.stem != "lib"),
        },
    }


def binding_rows(data: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for binding, binding_info in data["bindings"].items():
        family_states = data["binding_family"][binding]
        required_families = [family for family, state in family_states.items() if state == "R"]
        optional_families = [family for family, state in family_states.items() if state == "O"]
        subevent_states = data["binding_subevent"][binding].values()
        required_count = sum(1 for state in subevent_states if state == "R")
        optional_count = sum(1 for state in subevent_states if state == "O")
        derived_count = sum(1 for state in subevent_states if state == "D")
        rows.append(
            [
                fmt_code(binding),
                fmt_code(binding_info["scope_type"]),
                fmt_code(binding_info["exchange"]),
                comma_code(binding_info["protocols"]),
                comma_code(required_families) if required_families else "-",
                comma_code(optional_families) if optional_families else "-",
                str(required_count),
                str(optional_count),
                str(derived_count),
                comma_code(binding_info["framing"]),
            ]
        )
    return rows


def family_rows(data: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for family in data["families"]:
        subevents = data["subevents_by_family"][family]
        rows.append(
            [
                fmt_code(family),
                str(len(subevents)),
                comma_code(subevents[:4]) + (" ..." if len(subevents) > 4 else ""),
            ]
        )
    return rows


def contract_package_rows(meta: dict[str, dict], modules: dict[str, list[str]], current: str | None = None) -> list[list[str]]:
    package_paths = {
        "python": "packages/contract-py",
        "npm": "packages/contract-npm",
        "rust": "packages/contract-rs",
    }
    notes = {
        "python": "Pydantic models plus validator helpers",
        "npm": "TypeScript surface plus TSX badges/views",
        "rust": "Serde-friendly enums, models, validators",
    }
    rows: list[list[str]] = []
    for ecosystem in ("python", "npm", "rust"):
        package_name = meta[ecosystem]["name"]
        row_name = f"**{fmt_code(package_name)}**" if ecosystem == current else fmt_code(package_name)
        rows.append(
            [
                ecosystem,
                row_name,
                fmt_code(meta[ecosystem]["version"]),
                fmt_code(package_paths[ecosystem]),
                str(len(modules[ecosystem])),
                notes[ecosystem],
            ]
        )
    return rows


def artifact_package_rows(meta: dict[str, dict], modules: dict[str, list[str]], current: str | None = None) -> list[list[str]]:
    package_paths = {
        "python": "packages/artifacts-py",
        "npm": "packages/artifacts-npm",
        "rust": "packages/artifacts-rs",
    }
    notes = {
        "python": "Filesystem access helpers over vendored artifacts",
        "npm": "Package exports over vendored artifact files",
        "rust": "Embedded accessors for YAML, JSON, manifest, checksums",
    }
    rows: list[list[str]] = []
    for ecosystem in ("python", "npm", "rust"):
        package_name = meta[ecosystem]["name"]
        row_name = f"**{fmt_code(package_name)}**" if ecosystem == current else fmt_code(package_name)
        rows.append(
            [
                ecosystem,
                row_name,
                fmt_code(meta[ecosystem]["version"]),
                fmt_code(package_paths[ecosystem]),
                str(len(modules[ecosystem])),
                notes[ecosystem],
            ]
        )
    return rows


def artifact_inventory_rows(data: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for file_info in data["manifest"]["files"]:
        path = file_info["path"]
        if path.startswith("schemas/"):
            category = "schema"
        elif path.startswith("legality/"):
            category = "legality"
        elif path.endswith(".json"):
            category = "metadata"
        else:
            category = "registry"
        rows.append([fmt_code(path), category, short_sha(file_info["sha256"])])
    return rows


def render_root_readme(data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    manifest = data["manifest"]
    schema_count = sum(1 for file_info in manifest["files"] if file_info["path"].startswith("schemas/"))
    legality_count = sum(1 for file_info in manifest["files"] if file_info["path"].startswith("legality/"))

    return render_markdown(
        f"""\
        # tigr-asgi-contracts

        `contract/` is the canonical source of truth for the Tigr ASGI contract. This repository publishes canonical artifacts plus generated downstream contract packages for Python, npm, and Rust.

        ## Release Matrix

        {md_table(
            ["Field", "Value"],
            [
                ["Contract name", fmt_code(manifest["name"])],
                ["Contract version", fmt_code(manifest["contract_version"])],
                ["Artifact version", fmt_code(manifest["artifact_version"])],
                ["Serde version", fmt_code(str(manifest["serde_version"]))],
                ["Schema draft", fmt_code(manifest["schema_draft"])],
                ["Bindings", str(len(data["bindings"]))],
                ["Families", str(len(data["families"]))],
                ["Scope types", str(len(data["scope_types"]))],
                ["Schemas", str(schema_count)],
                ["Legality matrices", str(legality_count)],
                ["Tracked artifact files", str(len(manifest["files"]))],
            ],
        )}

        ## Binding Matrix

        Status counts derive from `contract/legality/binding_family.yaml` and `contract/legality/binding_subevent.yaml`.

        {md_table(
            ["Binding", "Scope", "Exchange", "Protocols", "Required families", "Optional families", "Required subevents", "Optional subevents", "Derived subevents", "Framing"],
            binding_rows(data),
        )}

        ## Family Matrix

        {md_table(["Family", "Subevents", "Examples"], family_rows(data))}

        ## Artifact Packages

        {md_table(
            ["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"],
            artifact_package_rows(meta["artifacts"], modules["artifacts"]),
        )}

        ## Contract Packages

        {md_table(
            ["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"],
            contract_package_rows(meta["contracts"], modules["contracts"]),
        )}

        ## Repository Layout

        ```text
        contract/                 # canonical registries, schemas, manifest, checksums
        generators/               # language generators used for downstream packages
        packages/artifacts-*      # artifact distributions
        packages/contract-*       # generated downstream contract distributions
        tools/                    # validation, packaging, checksum, manifest, README generation
        tests/                    # contract, codegen, and parity coverage
        ```

        ## Authoring Workflow

        1. Edit files under `contract/`.
        2. Rebuild generated artifacts and READMEs.
        3. Run validation and tests.
        4. Commit source and generated outputs together.

        ```bash
        python tools/validate_yaml.py
        python tools/validate_jsonschema.py
        python tools/generate_all.py
        python tools/check_versions.py
        pytest -q
        ```

        Do not hand-edit generated outputs under `packages/contract-*`, `contract/manifest.json`, `contract/checksums.txt`, or these generated README files. Regenerate them from source.

        ## Additional Docs

        - [docs/publishing.md](docs/publishing.md)
        - [docs/versioning.md](docs/versioning.md)
        - [docs/conformance.md](docs/conformance.md)
        - [docs/contract-governance.md](docs/contract-governance.md)
        """
    )


def render_artifact_readme(ecosystem: str, data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    names = {
        "python": meta["artifacts"]["python"]["name"],
        "npm": meta["artifacts"]["npm"]["name"],
        "rust": meta["artifacts"]["rust"]["name"],
    }
    descriptions = {
        "python": "Canonical Python artifact package for the Tigr ASGI contract.",
        "npm": "Canonical npm artifact package for the Tigr ASGI contract.",
        "rust": "Canonical Rust artifact crate for the Tigr ASGI contract.",
    }
    package_specific = {
        "python": "Python consumers get direct filesystem access to vendored YAML, JSON Schema, manifest, and checksum artifacts.",
        "npm": "npm consumers get vendored artifact files plus package exports for the manifest and schema paths.",
        "rust": "Rust consumers get embedded artifact accessors without needing runtime filesystem lookups.",
    }

    return render_markdown(
        f"""\
        # {names[ecosystem]}

        {descriptions[ecosystem]} Generated from the canonical `contract/` directory in this repository.

        {package_specific[ecosystem]}

        ## Artifact Package Matrix

        {md_table(
            ["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"],
            artifact_package_rows(meta["artifacts"], modules["artifacts"], current=ecosystem),
        )}

        ## Artifact Inventory Matrix

        {md_table(["Artifact path", "Category", "SHA-256"], artifact_inventory_rows(data))}

        ## Contract Coverage Matrix

        {md_table(
            ["Field", "Value"],
            [
                ["Contract version", fmt_code(current_version(data))],
                ["Bindings", str(len(data["bindings"]))],
                ["Families", str(len(data["families"]))],
                ["Scope types", str(len(data["scope_types"]))],
                ["Schemas", str(sum(1 for file_info in data["manifest"]["files"] if file_info["path"].startswith("schemas/")))],
                ["Legality matrices", str(sum(1 for file_info in data["manifest"]["files"] if file_info["path"].startswith("legality/")))],
            ],
        )}

        See the repository-level README for the cross-ecosystem contract and package overview.
        """
    )


def render_contract_readme(ecosystem: str, data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    names = {
        "python": meta["contracts"]["python"]["name"],
        "npm": meta["contracts"]["npm"]["name"],
        "rust": meta["contracts"]["rust"]["name"],
    }
    descriptions = {
        "python": "Generated Python enums, models, and validators for the Tigr ASGI contract.",
        "npm": "Generated TypeScript and TSX contract surfaces for the Tigr ASGI contract.",
        "rust": "Generated Rust enums, models, and validators for the Tigr ASGI contract.",
    }
    package_specific = {
        "python": "The Python package exposes enum-like values, Pydantic models, registry helpers, and validators.",
        "npm": "The npm package exposes TypeScript registries and validators plus TSX helpers for UI-facing contract rendering.",
        "rust": "The Rust crate exposes serde-friendly enums, models, registries, and validator helpers.",
    }

    module_rows = []
    for module_name in modules["contracts"][ecosystem]:
        if ecosystem == "npm" and module_name.startswith("tsx/"):
            export_surface = fmt_code(module_name)
        elif ecosystem == "npm":
            export_surface = fmt_code(f"src/{module_name}.ts")
        elif ecosystem == "python":
            export_surface = fmt_code(f"tigr_asgi_contract/{module_name}.py")
        else:
            export_surface = fmt_code(f"src/{module_name}.rs")
        module_rows.append([fmt_code(module_name), export_surface])

    return render_markdown(
        f"""\
        # {names[ecosystem]}

        {descriptions[ecosystem]} Generated from the canonical `contract/` directory in this repository.

        {package_specific[ecosystem]}

        ## Contract Package Matrix

        {md_table(
            ["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"],
            contract_package_rows(meta["contracts"], modules["contracts"], current=ecosystem),
        )}

        ## Generated Surface Matrix

        {md_table(["Module", "Export surface"], module_rows)}

        ## Binding Support Matrix

        {md_table(
            ["Binding", "Exchange", "Required families", "Optional families", "Required subevents", "Optional subevents", "Derived subevents"],
            [
                [row[0], row[2], row[4], row[5], row[6], row[7], row[8]]
                for row in binding_rows(data)
            ],
        )}

        See the repository-level README for authoring workflow, release sequencing, and cross-ecosystem package context.
        """
    )


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    data = contract_data()
    meta = package_metadata()
    modules = module_inventory()

    write(ROOT / "README.md", render_root_readme(data, meta, modules))
    write(PACKAGES / "artifacts-py" / "README.md", render_artifact_readme("python", data, meta, modules))
    write(PACKAGES / "artifacts-npm" / "README.md", render_artifact_readme("npm", data, meta, modules))
    write(PACKAGES / "artifacts-rs" / "README.md", render_artifact_readme("rust", data, meta, modules))
    write(PACKAGES / "contract-py" / "README.md", render_contract_readme("python", data, meta, modules))
    write(PACKAGES / "contract-npm" / "README.md", render_contract_readme("npm", data, meta, modules))
    write(PACKAGES / "contract-rs" / "README.md", render_contract_readme("rust", data, meta, modules))


if __name__ == "__main__":
    main()
