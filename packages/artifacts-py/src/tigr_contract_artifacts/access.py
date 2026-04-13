from __future__ import annotations
from importlib.resources import files
from pathlib import Path
import json
import yaml

def _packaged_root() -> Path:
    return files("tigr_contract_artifacts") / "_contract"

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4] / "contract"

def contract_root() -> Path:
    packaged = Path(_packaged_root())
    if packaged.exists():
        return packaged
    return _repo_root()

def load_yaml(relpath: str):
    return yaml.safe_load((contract_root() / relpath).read_text(encoding="utf-8"))

def load_json(relpath: str):
    return json.loads((contract_root() / relpath).read_text(encoding="utf-8"))

def manifest():
    return load_json("manifest.json")

def checksums() -> str:
    return (contract_root() / "checksums.txt").read_text(encoding="utf-8")
