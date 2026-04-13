from __future__ import annotations
from pathlib import Path
import yaml
import json
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract"

def load_yaml(name: str) -> Any:
    return yaml.safe_load((CONTRACT / name).read_text(encoding="utf-8"))

def load_json(path: str) -> Any:
    return json.loads((CONTRACT / path).read_text(encoding="utf-8"))

def member_name(value: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", value).upper().strip("_")
    if not s or s[0].isdigit():
        s = "_" + s
    return s

def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^A-Za-z0-9]+", name) if part)

def camel(name: str) -> str:
    parts = [part for part in re.split(r"[^A-Za-z0-9]+", name) if part]
    if not parts:
        return name
    return parts[0].lower() + "".join(part.capitalize() for part in parts[1:])

def quote_list(values: list[str]) -> str:
    return ", ".join(repr(v) for v in values)

def contract_data() -> dict[str, Any]:
    subevents_map = load_yaml("subevents.yaml")["subevents"]
    all_subevents = [s for items in subevents_map.values() for s in items]
    return {
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "scope_types": load_yaml("scope_types.yaml")["scope_types"],
        "bindings": load_yaml("bindings.yaml")["bindings"],
        "exchanges": load_yaml("exchanges.yaml")["exchanges"],
        "families": load_yaml("families.yaml")["families"],
        "subevents_by_family": subevents_map,
        "all_subevents": all_subevents,
        "capabilities": load_yaml("capabilities.yaml")["fields"],
        "completion": load_yaml("completion.yaml"),
        "compatibility": load_yaml("compatibility.yaml"),
        "ids": load_yaml("ids.yaml")["fields"],
        "binding_family": load_yaml("legality/binding_family.yaml")["binding_family"],
        "family_subevent": load_yaml("legality/family_subevent.yaml")["family_subevent"],
        "binding_subevent": load_yaml("legality/binding_subevent.yaml")["binding_subevent"],
        "manifest": load_json("manifest.json"),
        "schemas": {
            p.name: json.loads(p.read_text(encoding="utf-8"))
            for p in (CONTRACT / "schemas").glob("*.json")
        },
    }
