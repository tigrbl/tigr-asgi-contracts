#!/usr/bin/env python3
"""Summarize SSOT registry feature availability and implementation status."""

from __future__ import annotations

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

IMPLEMENTED_CODES = {"R", "O", "D"}
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "packages/contract-py/src/tigr_asgi_contract/registry.py"


def load_registry_matrix() -> dict[str, dict[str, str]]:
    spec = spec_from_file_location("tigr_registry", REGISTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load registry file at {REGISTRY_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.BINDING_SUBEVENT_MATRIX


def build_rows(binding_subevent_matrix: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for binding, features in sorted(binding_subevent_matrix.items()):
        counts = Counter(features.values())
        total = len(features)
        implemented = sum(counts[c] for c in IMPLEMENTED_CODES)
        rows.append(
            {
                "binding": binding,
                "total_features": total,
                "implemented_features": implemented,
                "not_implemented_features": counts.get("F", 0),
                "required_R": counts.get("R", 0),
                "optional_O": counts.get("O", 0),
                "derived_D": counts.get("D", 0),
                "implementation_pct": round(implemented * 100 / total, 1) if total else 0.0,
            }
        )
    return rows


def render_table(rows: list[dict[str, object]]) -> str:
    headers = list(rows[0].keys())
    widths = [max(len(str(h)), *(len(str(r[h])) for r in rows)) for h in headers]

    def fmt_row(row: dict[str, object]) -> str:
        return " | ".join(str(row[h]).ljust(widths[i]) for i, h in enumerate(headers))

    divider = "-+-".join("-" * w for w in widths)
    out = [fmt_row({h: h for h in headers}), divider]
    out.extend(fmt_row(r) for r in rows)
    return "\n".join(out)


def main() -> None:
    rows = build_rows(load_registry_matrix())
    print(render_table(rows))


if __name__ == "__main__":
    main()
