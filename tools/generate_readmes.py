from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generators.common import contract_data

PACKAGES = ROOT / "packages"

LEGALITY_LABELS = {
    "R": "required",
    "O": "optional",
    "D": "derived",
    "F": "forbidden",
}

SCOPE_EVENT_MAP = {
    "http": [
        "http.request",
        "http.disconnect",
        "http.response.start",
        "http.response.body",
        "transport.emit.complete",
        "transport.emit.failed",
    ],
    "websocket": [
        "websocket.connect",
        "websocket.receive",
        "websocket.disconnect",
        "websocket.accept",
        "websocket.send",
        "websocket.close",
        "transport.emit.complete",
        "transport.emit.failed",
    ],
    "webtransport": [
        "webtransport.connect",
        "webtransport.accept",
        "webtransport.stream.receive",
        "webtransport.stream.send",
        "webtransport.stream.close",
        "webtransport.stream.reset",
        "webtransport.stream.stop_sending",
        "webtransport.datagram.receive",
        "webtransport.datagram.send",
        "webtransport.disconnect",
        "webtransport.close",
        "transport.emit.complete",
        "transport.emit.failed",
    ],
    "lifespan": [
        "lifespan.startup",
        "lifespan.startup.complete",
        "lifespan.startup.failed",
        "lifespan.shutdown",
        "lifespan.shutdown.complete",
        "lifespan.shutdown.failed",
    ],
}

SCOPE_EXT_FIELDS = {
    "http": ["transport", "family_capabilities"],
    "websocket": ["transport", "family_capabilities", "websocket"],
    "lifespan": ["transport", "family_capabilities"],
    "webtransport": ["transport", "family_capabilities", "webtransport"],
}

SSE_SCOPE_EXT_FIELDS = ["transport", "family_capabilities", "sse"]

SUBEVENT_EVENT_MAP = {
    "request.open": ["http.request"],
    "request.body_in": ["http.request"],
    "request.chunk_in": ["http.request"],
    "request.dispatch": [],
    "request.close": ["http.request"],
    "request.disconnect": ["http.disconnect"],
    "response.open": ["http.response.start"],
    "response.body_out": ["http.response.body"],
    "response.chunk_out": ["http.response.body"],
    "response.finalize": ["http.response.body"],
    "response.emit_complete": ["transport.emit.complete"],
    "session.open": ["websocket.connect", "webtransport.connect"],
    "session.accept": ["websocket.accept", "webtransport.accept"],
    "session.reject": ["websocket.close", "webtransport.close"],
    "session.ready": ["websocket.accept", "webtransport.accept"],
    "session.heartbeat": ["websocket.send", "webtransport.stream.send"],
    "session.sync": ["websocket.send", "webtransport.stream.send"],
    "session.close": ["websocket.close", "webtransport.close"],
    "session.disconnect": ["websocket.disconnect", "webtransport.disconnect"],
    "session.emit_complete": ["transport.emit.complete"],
    "message.in": ["websocket.receive", "webtransport.stream.receive", "webtransport.datagram.receive"],
    "message.decode": ["websocket.receive", "webtransport.stream.receive", "webtransport.datagram.receive"],
    "message.decode_failed": ["websocket.receive", "webtransport.stream.receive", "webtransport.datagram.receive"],
    "message.handle": ["websocket.receive", "webtransport.stream.receive", "webtransport.datagram.receive"],
    "message.handle_failed": ["websocket.receive", "webtransport.stream.receive", "webtransport.datagram.receive"],
    "message.out": ["websocket.send", "webtransport.stream.send", "http.response.body"],
    "message.replay": ["websocket.send", "webtransport.stream.send", "http.response.body"],
    "message.snapshot": ["websocket.send", "webtransport.stream.send", "http.response.body"],
    "message.emit_complete": ["transport.emit.complete"],
    "message.emit_failed": ["transport.emit.failed"],
    "stream.open": ["webtransport.stream.send", "http.response.start"],
    "stream.chunk_in": ["webtransport.stream.receive", "http.request"],
    "stream.chunk_out": ["webtransport.stream.send", "http.response.body"],
    "stream.flush": ["webtransport.stream.send", "http.response.body"],
    "stream.finalize": ["webtransport.stream.send", "http.response.body"],
    "stream.reset": ["webtransport.stream.reset", "http.disconnect"],
    "stream.stop_sending": ["webtransport.stream.stop_sending"],
    "stream.close": ["webtransport.stream.close", "http.response.body"],
    "stream.emit_complete": ["transport.emit.complete"],
    "datagram.in": ["webtransport.datagram.receive"],
    "datagram.handle": ["webtransport.datagram.receive"],
    "datagram.out": ["webtransport.datagram.send"],
    "datagram.emit_complete": ["transport.emit.complete"],
    "datagram.emit_failed": ["transport.emit.failed"],
    "lifespan.startup": ["lifespan.startup"],
    "lifespan.startup_complete": ["lifespan.startup.complete"],
    "lifespan.startup_failed": ["lifespan.startup.failed"],
    "lifespan.shutdown": ["lifespan.shutdown"],
    "lifespan.shutdown_complete": ["lifespan.shutdown.complete"],
    "lifespan.shutdown_failed": ["lifespan.shutdown.failed"],
}

EVENT_NOTES = {
    "http.request": "Inbound HTTP request unit",
    "http.disconnect": "HTTP connection closed by peer or server",
    "http.response.start": "HTTP response metadata start",
    "http.response.body": "HTTP response body frame",
    "websocket.connect": "WebSocket connection open event",
    "websocket.receive": "Inbound WebSocket frame",
    "websocket.disconnect": "WebSocket disconnect signal",
    "websocket.accept": "WebSocket accept handshake response",
    "websocket.send": "Outbound WebSocket frame",
    "websocket.close": "WebSocket close frame",
    "webtransport.connect": "WebTransport session connect event",
    "webtransport.accept": "WebTransport accept event",
    "webtransport.stream.receive": "Inbound WebTransport stream frame",
    "webtransport.stream.send": "Outbound WebTransport stream frame",
    "webtransport.stream.close": "Per-stream WebTransport close or FIN",
    "webtransport.stream.reset": "Per-stream WebTransport reset",
    "webtransport.stream.stop_sending": "Per-stream WebTransport stop-sending signal",
    "webtransport.datagram.receive": "Inbound WebTransport datagram",
    "webtransport.datagram.send": "Outbound WebTransport datagram",
    "webtransport.disconnect": "WebTransport disconnect signal",
    "webtransport.close": "WebTransport session close event",
    "lifespan.startup": "ASGI lifespan startup receive event",
    "lifespan.startup.complete": "ASGI lifespan startup completion send event",
    "lifespan.startup.failed": "ASGI lifespan startup failure send event",
    "lifespan.shutdown": "ASGI lifespan shutdown receive event",
    "lifespan.shutdown.complete": "ASGI lifespan shutdown completion send event",
    "lifespan.shutdown.failed": "ASGI lifespan shutdown failure send event",
    "transport.emit.complete": "Completion emission event",
    "transport.emit.failed": "Failed emission event",
}


def load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def render_markdown(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(line[8:] if line.startswith("        ") else line for line in lines).strip()


def fmt_code(value: str) -> str:
    return f"`{value}`"


def comma_code(values: list[str]) -> str:
    if not values:
        return "-"
    return ", ".join(fmt_code(value) for value in values)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def legality_label(code: str) -> str:
    return f"{fmt_code(code)} {LEGALITY_LABELS[code]}"


def package_metadata() -> dict[str, dict]:
    return {
        "artifacts": {
            "python": load_toml(PACKAGES / "artifacts-py" / "pyproject.toml")["project"],
            "npm": json.loads((PACKAGES / "artifacts-npm" / "package.json").read_text(encoding="utf-8")),
            "rust": load_toml(PACKAGES / "artifacts-rs" / "Cargo.toml")["package"],
        },
        "contracts": {
            "python": load_toml(PACKAGES / "contract-py" / "pyproject.toml")["project"],
            "npm": json.loads((PACKAGES / "contract-npm" / "package.json").read_text(encoding="utf-8")),
            "rust": load_toml(PACKAGES / "contract-rs" / "Cargo.toml")["package"],
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
            "rust": sorted(path.stem for path in (PACKAGES / "artifacts-rs" / "src").glob("*.rs") if path.stem != "lib"),
        },
        "contracts": {
            "python": sorted(
                path.stem
                for path in (PACKAGES / "contract-py" / "src" / "tigr_asgi_contract").glob("*.py")
                if path.stem != "__init__"
            ),
            "npm": sorted(path.stem for path in (PACKAGES / "contract-npm" / "src").glob("*.ts") if path.stem != "index")
            + [f"tsx/{path.stem}" for path in sorted((PACKAGES / "contract-npm" / "tsx").glob("*.tsx"))],
            "rust": sorted(path.stem for path in (PACKAGES / "contract-rs" / "src").glob("*.rs") if path.stem != "lib"),
        },
    }


def binding_family_sets(data: dict, binding: str) -> tuple[list[str], list[str]]:
    family_states = data["binding_family"][binding]
    required = [family for family, state in family_states.items() if state == "R"]
    optional = [family for family, state in family_states.items() if state == "O"]
    return required, optional


def family_for_subevent(data: dict, subevent: str) -> str:
    for family, subevents in data["subevents_by_family"].items():
        if subevent in subevents:
            return family
    raise KeyError(subevent)


def scope_ext_fields_for_binding(binding: str, scope_type: str) -> list[str]:
    if binding == "sse":
        return SSE_SCOPE_EXT_FIELDS
    return SCOPE_EXT_FIELDS[scope_type]


def compatibility_rows(data: dict) -> list[list[str]]:
    compatibility = data["compatibility"]
    descriptions = {
        "contract_name": "Canonical contract identifier",
        "contract_version": "Published contract version",
        "serde_version": "Serialization surface version",
        "schema_draft": "JSON Schema draft level",
    }
    return [
        [fmt_code(key), fmt_code(str(value)), descriptions.get(key, "Compatibility field"), fmt_code("contract/compatibility.yaml")]
        for key, value in compatibility.items()
    ]


def completion_rows(data: dict) -> list[list[str]]:
    completion = data["completion"]
    rows = []
    for level, meaning in completion["levels"].items():
        rows.append(
            [
                fmt_code(level),
                meaning,
                "yes" if completion["default"] == level else "no",
                fmt_code("contract/completion.yaml"),
            ]
        )
    return rows


def capability_rows(data: dict) -> list[list[str]]:
    family_map = {
        "request": ["request"],
        "session": ["session"],
        "message": ["message"],
        "stream_in": ["stream"],
        "stream_out": ["stream"],
        "datagram": ["datagram"],
        "lifespan": ["lifespan"],
    }
    rows = []
    for field, meaning in data["capabilities"].items():
        rows.append(
            [
                fmt_code(field),
                comma_code(family_map.get(field, [])),
                meaning,
                fmt_code("transport.schema.json#/$defs/familyCapabilities"),
            ]
        )
    return rows


def family_rows(data: dict) -> list[list[str]]:
    rows = []
    for family in data["families"]:
        subevents = data["subevents_by_family"][family]
        supported_bindings = []
        optional_bindings = []
        for binding in data["bindings"]:
            state = data["binding_family"][binding][family]
            if state == "R":
                supported_bindings.append(binding)
            elif state == "O":
                optional_bindings.append(binding)
        rows.append(
            [
                fmt_code(family),
                str(len(subevents)),
                comma_code(supported_bindings),
                comma_code(optional_bindings),
                comma_code(subevents),
            ]
        )
    return rows


def subevent_rows(data: dict) -> list[list[str]]:
    rows = []
    for family in data["families"]:
        for subevent in data["subevents_by_family"][family]:
            supporting = []
            optional = []
            derived = []
            for binding in data["bindings"]:
                state = data["binding_subevent"][binding][subevent]
                if state == "R":
                    supporting.append(binding)
                elif state == "O":
                    optional.append(binding)
                elif state == "D":
                    derived.append(binding)
            rows.append(
                [
                    fmt_code(subevent),
                    fmt_code(family),
                    legality_label(data["family_subevent"][family][subevent]),
                    comma_code(supporting),
                    comma_code(optional),
                    comma_code(derived),
                    comma_code(SUBEVENT_EVENT_MAP.get(subevent, [])),
                ]
            )
    return rows


def scope_rows() -> list[list[str]]:
    rows = []
    for scope_type, events in SCOPE_EVENT_MAP.items():
        scope_ext_fields = SCOPE_EXT_FIELDS.get(scope_type, ["transport", "family_capabilities"])
        rows.append(
            [
                fmt_code(scope_type),
                comma_code(scope_ext_fields),
                comma_code(events),
                fmt_code("scope.schema.json"),
            ]
        )
    return rows


def event_rows(data: dict) -> list[list[str]]:
    event_values = data["schemas"]["event.schema.json"]["properties"]["type"]["enum"]
    rows = []
    for event in event_values:
        if event.startswith("http."):
            scope_type = "http"
        elif event.startswith("websocket."):
            scope_type = "websocket"
        elif event.startswith("webtransport."):
            scope_type = "webtransport"
        elif event.startswith("lifespan."):
            scope_type = "lifespan"
        else:
            scope_type = "http, websocket, webtransport"

        related_subevents = sorted([subevent for subevent, events in SUBEVENT_EVENT_MAP.items() if event in events])
        bindings = sorted(
            [
                binding
                for binding, binding_info in data["bindings"].items()
                if (
                    (scope_type == "http" and binding_info["scope_type"] == "http")
                    or (scope_type == "websocket" and binding_info["scope_type"] == "websocket")
                    or (scope_type == "webtransport" and binding_info["scope_type"] == "webtransport")
                    or event == "transport.emit.complete"
                )
            ]
        )

        rows.append(
            [
                fmt_code(event),
                fmt_code(scope_type),
                comma_code(bindings),
                comma_code(related_subevents),
                EVENT_NOTES.get(event, ""),
            ]
        )
    return rows


def binding_subevent_rows(data: dict) -> list[list[str]]:
    rows = []
    for binding, binding_info in data["bindings"].items():
        required_families, optional_families = binding_family_sets(data, binding)
        scope_type = binding_info["scope_type"]
        scope_events = SCOPE_EVENT_MAP[scope_type]
        if binding == "sse":
            scope_events = sorted(set(scope_events + ["transport.emit.complete"]))
        scope_ext_fields = scope_ext_fields_for_binding(binding, scope_type)

        for family in data["families"]:
            for subevent in data["subevents_by_family"][family]:
                rows.append(
                    [
                        fmt_code(binding),
                        comma_code(binding_info["protocols"]),
                        fmt_code(binding_info["exchange"]),
                        fmt_code(scope_type),
                        comma_code(scope_ext_fields),
                        comma_code(scope_events),
                        comma_code(required_families),
                        comma_code(optional_families),
                        fmt_code(subevent),
                        fmt_code(family),
                        legality_label(data["family_subevent"][family][subevent]),
                        legality_label(data["binding_subevent"][binding][subevent]),
                        comma_code(SUBEVENT_EVENT_MAP.get(subevent, [])),
                    ]
                )
    return rows


def package_rows(meta: dict[str, dict], modules: dict[str, list[str]], family: str, current: str | None = None) -> list[list[str]]:
    paths = {
        "artifacts": {
            "python": "packages/artifacts-py",
            "npm": "packages/artifacts-npm",
            "rust": "packages/artifacts-rs",
        },
        "contracts": {
            "python": "packages/contract-py",
            "npm": "packages/contract-npm",
            "rust": "packages/contract-rs",
        },
    }
    notes = {
        "artifacts": {
            "python": "Vendored file accessors",
            "npm": "Packaged artifact exports",
            "rust": "Embedded artifact accessors",
        },
        "contracts": {
            "python": "Enums, models, validators",
            "npm": "TypeScript and TSX surfaces",
            "rust": "Serde-friendly contract surfaces",
        },
    }
    rows = []
    for ecosystem in ("python", "npm", "rust"):
        package_name = fmt_code(meta[ecosystem]["name"])
        if ecosystem == current:
            package_name = f"**{package_name}**"
        rows.append(
            [
                ecosystem,
                package_name,
                fmt_code(meta[ecosystem]["version"]),
                fmt_code(paths[family][ecosystem]),
                str(len(modules[ecosystem])),
                notes[family][ecosystem],
            ]
        )
    return rows


def artifact_inventory_rows(data: dict) -> list[list[str]]:
    rows = []
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
        rows.append([fmt_code(path), category, fmt_code(file_info["sha256"][:12])])
    return rows


def contract_surface_rows(modules: dict[str, list[str]], ecosystem: str) -> list[list[str]]:
    rows = []
    for module_name in modules[ecosystem]:
        if ecosystem == "python":
            export_surface = f"tigr_asgi_contract/{module_name}.py"
        elif ecosystem == "npm":
            export_surface = module_name if module_name.startswith("tsx/") else f"src/{module_name}.ts"
        else:
            export_surface = f"src/{module_name}.rs"
        rows.append([fmt_code(module_name), fmt_code(export_surface)])
    return rows


def shared_contract_matrices(data: dict) -> str:
    manifest = data["manifest"]
    return render_markdown(
        f"""\
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
                ["Subevents", str(len(data["all_subevents"]))],
                ["Scope types", str(len(data["scope_types"]))],
                ["Event types", str(len(data["schemas"]["event.schema.json"]["properties"]["type"]["enum"]))],
            ],
        )}

        ## Scope Type Matrix

        {md_table(["ASGI3 scope type", "Scope ext fields", "Scope event types", "Source"], scope_rows())}

        ## Capability Matrix

        {md_table(["Capability field", "Family alignment", "Meaning", "Schema source"], capability_rows(data))}

        ## Compatibility Matrix

        {md_table(["Compatibility field", "Value", "Meaning", "Source"], compatibility_rows(data))}

        ## Completion Matrix

        {md_table(["Completion level", "Meaning", "Default", "Source"], completion_rows(data))}

        ## Event Matrix

        {md_table(["Transport event", "ASGI3 scope type", "Bindings", "Related subevents", "Meaning"], event_rows(data))}

        ## Family Matrix

        {md_table(["Family", "Subevent count", "Required bindings", "Optional bindings", "Subevents"], family_rows(data))}

        ## Subevent Matrix

        {md_table(["Subevent", "Family", "Family legality", "Required bindings", "Optional bindings", "Derived bindings", "Related transport events"], subevent_rows(data))}

        ## Binding Subevent Matrix

        Every row is a concrete `binding x subevent` record sourced from the legality registries.

        {md_table(
            [
                "Binding",
                "Protocols",
                "Exchange",
                "ASGI3 scope type",
                "Scope ext fields",
                "Scope event types",
                "Required families",
                "Optional families",
                "Subevent",
                "Family",
                "Family legality",
                "Binding legality",
                "Related transport events",
            ],
            binding_subevent_rows(data),
        )}
        """
    )


def render_root_readme(data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    return render_markdown(
        f"""\
        # tigr-asgi-contracts

        `contract/` is the canonical source of truth for the Tigr ASGI contract. This repository publishes canonical artifacts plus generated downstream contract packages for Python, npm, and Rust.

        ## Artifact Package Matrix

        {md_table(["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"], package_rows(meta["artifacts"], modules["artifacts"], "artifacts"))}

        ## Contract Package Matrix

        {md_table(["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"], package_rows(meta["contracts"], modules["contracts"], "contracts"))}

        {shared_contract_matrices(data)}

        ## Repository Layout

        ```text
        contract/                 # canonical registries, schemas, manifest, checksums, legality matrices
        generators/               # language generators used for downstream packages
        packages/artifacts-*      # artifact distributions
        packages/contract-*       # generated downstream contract distributions
        tools/                    # validation, packaging, checksum, manifest, README generation
        tests/                    # contract, codegen, and parity coverage
        ```

        ## Authoring Workflow

        1. Edit files under `contract/`.
        2. Rebuild generated artifacts, packages, and READMEs.
        3. Run validation and tests.
        4. Commit source and generated outputs together.

        ```bash
        uv sync --frozen
        uv run --frozen python tools/validate_yaml.py
        uv run --frozen python tools/validate_jsonschema.py
        uv run --frozen python tools/generate_all.py
        uv run --frozen python tools/check_versions.py
        uv run --frozen python -m pytest -q
        ```

        Do not hand-edit generated outputs under `packages/contract-*`, `contract/manifest.json`, `contract/checksums.txt`, or these generated README files.
        """
    )


def render_artifact_readme(ecosystem: str, data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    names = {
        "python": meta["artifacts"]["python"]["name"],
        "npm": meta["artifacts"]["npm"]["name"],
        "rust": meta["artifacts"]["rust"]["name"],
    }
    intros = {
        "python": "Canonical Python artifact package for the Tigr ASGI contract.",
        "npm": "Canonical npm artifact package for the Tigr ASGI contract.",
        "rust": "Canonical Rust artifact crate for the Tigr ASGI contract.",
    }
    return render_markdown(
        f"""\
        # {names[ecosystem]}

        {intros[ecosystem]} This package ships the source artifacts that drive the downstream contract packages.

        ## Artifact Package Matrix

        {md_table(["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"], package_rows(meta["artifacts"], modules["artifacts"], "artifacts", current=ecosystem))}

        ## Artifact Inventory Matrix

        {md_table(["Artifact path", "Category", "SHA-256"], artifact_inventory_rows(data))}

        {shared_contract_matrices(data)}
        """
    )


def render_contract_readme(ecosystem: str, data: dict, meta: dict[str, dict], modules: dict[str, dict[str, list[str]]]) -> str:
    names = {
        "python": meta["contracts"]["python"]["name"],
        "npm": meta["contracts"]["npm"]["name"],
        "rust": meta["contracts"]["rust"]["name"],
    }
    intros = {
        "python": "Generated Python contract package for the Tigr ASGI contract.",
        "npm": "Generated TypeScript and TSX contract package for the Tigr ASGI contract.",
        "rust": "Generated Rust contract crate for the Tigr ASGI contract.",
    }
    return render_markdown(
        f"""\
        # {names[ecosystem]}

        {intros[ecosystem]} It is generated from the canonical `contract/` directory and mirrors the legality and schema artifacts.

        ## Contract Package Matrix

        {md_table(["Ecosystem", "Package", "Version", "Path", "Surface files", "Notes"], package_rows(meta["contracts"], modules["contracts"], "contracts", current=ecosystem))}

        ## Generated Surface Matrix

        {md_table(["Module", "Export surface"], contract_surface_rows(modules["contracts"], ecosystem))}

        {shared_contract_matrices(data)}
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
