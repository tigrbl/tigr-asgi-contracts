from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_rust_generated_files_exist() -> None:
    assert (ROOT / "packages" / "contract-rs" / "src" / "bindings.rs").exists()
    assert (ROOT / "packages" / "contract-rs" / "src" / "models.rs").exists()


def test_rust_events_match_event_schema() -> None:
    schema = json.loads((ROOT / "contract" / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
    expected = {f'#[serde(rename = "{value}")]' for value in schema["properties"]["type"]["enum"]}
    events_rs = (ROOT / "packages" / "contract-rs" / "src" / "events.rs").read_text(encoding="utf-8")

    assert expected <= {line.strip() for line in events_rs.splitlines()}
    assert "pub message: Option<String>," in events_rs
