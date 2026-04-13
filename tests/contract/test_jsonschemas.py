from __future__ import annotations
import json
from pathlib import Path
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "contract" / "schemas"

def test_all_schemas_are_valid() -> None:
    for path in SCHEMAS.glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        validator_for(schema).check_schema(schema)
