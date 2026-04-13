from __future__ import annotations
from pathlib import Path
import json
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contract" / "schemas"

def main() -> None:
    for path in sorted(SCHEMAS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        validator_for(data).check_schema(data)
        print(f"OK {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
