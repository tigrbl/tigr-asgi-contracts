#!/usr/bin/env python3
"""Build a normalized review workbook from feature matrix sources.

This script intentionally does not mutate the SSOT registry. It consolidates the
generated CSV/XLSX review artifacts into a deduped feature-candidate workbook
that can be reviewed before deciding whether any candidates are ready for SSOT.
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
OUTPUT_PATH = REPORTS / "normalized_master_feature_matrix.xlsx"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"main": MAIN_NS, "rel": REL_NS}


NORMALIZED_FEATURE_COLUMNS = [
    "candidate_feature_id",
    "feature_surface_key",
    "feature_kind",
    "title",
    "description",
    "implementation_status",
    "lifecycle_stage",
    "plan_horizon",
    "target_claim_tier",
    "target_lifecycle_stage",
    "existing_ssot_feature_id",
    "existing_ssot_match_kind",
    "source_count",
    "source_files",
    "source_sheets",
    "source_rows",
    "primary_source_file",
    "primary_source_row",
    "scope_type",
    "family",
    "subevent",
    "transport_event_type",
    "binding",
    "protocols",
    "schema_path",
    "frame_or_framing",
    "concern",
    "current_support",
    "current_status",
    "legality_rest",
    "legality_jsonrpc",
    "legality_http_stream",
    "legality_sse",
    "legality_websocket",
    "legality_webtransport",
    "dedupe_confidence",
    "review_status",
    "review_notes",
]

SOURCE_ROW_EXTRA_COLUMNS = [
    "feature_surface_key",
    "candidate_feature_id",
    "normalized_row_status",
    "dedupe_group_id",
]

DUPLICATE_GROUP_COLUMNS = [
    "dedupe_group_id",
    "feature_surface_key",
    "candidate_feature_id",
    "row_count",
    "source_files",
    "conflicting_values",
    "selected_title",
    "selected_description",
    "review_reason",
]

REJECTED_ROW_COLUMNS = [
    "source_file",
    "source_sheet",
    "source_row",
    "reason",
    "record_key",
]

COLUMN_DICTIONARY_COLUMNS = [
    "column_name",
    "sheet",
    "role",
    "source_columns",
    "description",
]

LEGACY_SCHEMA_PATHS = {
    "contract/schemas/ext/websocket.schema.json": "contract/schemas/websocket.schema.json",
    "contract/schemas/ext/sse.schema.json": "contract/schemas/sse.schema.json",
    "contract/schemas/ext/webtransport.schema.json": "contract/schemas/webtransport.schema.json",
}

IMPLEMENTED_SIGNALS = {
    "r",
    "exists",
    "implemented",
    "supported",
    "represented by events",
    "implicit",
}
PARTIAL_SIGNALS = {
    "o",
    "d",
    "partial",
    "partially implemented",
    "partially represented",
    "schema-hardening",
}
ABSENT_SIGNALS = {
    "f",
    "missing",
    "proposed",
    "candidate",
    "not supported",
    "not explicit",
    "not supported explicitly",
    "absent",
}


@dataclass
class SourceRecord:
    source_file: str
    source_sheet: str
    source_row: str
    source_type: str
    record_key: str
    data: dict[str, str]
    feature_surface_key: str = ""
    candidate_feature_id: str = ""
    dedupe_group_id: str = ""
    normalized_row_status: str = ""
    rejection_reason: str = ""


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def norm(token: str) -> str:
    """Match the repo's broad feature-id normalization convention."""
    token = token.strip().lower()
    token = token.replace(".schema", "-schema")
    token = re.sub(r"[^a-z0-9]+", "-", token)
    token = re.sub(r"-+", "-", token).strip("-")
    return token or "unnamed"


def schema_body(path: str) -> str:
    value = path.strip()
    if value.startswith("contract/"):
        value = value.removeprefix("contract/")
    value = value.removesuffix(".json")
    return norm(value)


def candidate_id_for(feature_surface_key: str) -> str:
    kind, _, value = feature_surface_key.partition(":")
    if kind == "schema":
        return f"feat:{schema_body(value)}"
    if kind == "event":
        if value.endswith(".schema.json") or "/" in value:
            return f"feat:event-{schema_body(value)}"
        return f"feat:event-{norm(value)}"
    if kind == "scope":
        parts = re.findall(r"(?:scope|family|subevent):([^|]+)", feature_surface_key)
        return f"feat:scope-{norm('-'.join(parts))}"
    if kind == "frame":
        return f"feat:frame-{norm(value)}"
    if kind == "concern":
        return f"feat:concern-{norm(value)}"
    if kind == "lifespan":
        return f"feat:{norm(value)}"
    return f"feat:{norm(value or feature_surface_key)}"


def title_for(feature_surface_key: str, row: dict[str, str]) -> str:
    kind, _, value = feature_surface_key.partition(":")
    if kind == "schema":
        return f"Schema: {value}"
    if kind == "event":
        return f"Event: {value}"
    if kind == "scope":
        return (
            "Scope subevent: "
            f"{row.get('scope_type') or row.get('scope_types')} / "
            f"{row.get('family')} / {row.get('subevent')}"
        )
    if kind == "frame":
        return f"Frame: {value}"
    if kind == "concern":
        return f"Transport concern: {value}"
    if kind == "lifespan":
        return f"Lifespan: {value}"
    return value


def description_for(feature_surface_key: str, rows: list[SourceRecord]) -> str:
    for record in rows:
        data = record.data
        for key in (
            "primary_purpose",
            "needed_for",
            "validation_policy_notes",
            "Notes",
            "gap",
            "current_behavior",
            "event_frame_impact",
        ):
            value = data.get(key, "").strip()
            if value:
                return value
    return f"Normalized feature candidate for {feature_surface_key}."


def read_csv_records(path: Path) -> tuple[list[SourceRecord], list[str]]:
    records: list[SourceRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        for row_num, row in enumerate(reader, start=2):
            data = {header: row.get(header, "") for header in headers}
            source_file = rel(path)
            records.append(
                SourceRecord(
                    source_file=source_file,
                    source_sheet="",
                    source_row=str(row_num),
                    source_type="csv",
                    record_key=f"{source_file}#{row_num}",
                    data=data,
                )
            )
    return records, headers


def cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find("main:is", NS)
        return (
            "".join((node.text or "") for node in inline.iter() if node.tag.endswith("}t"))
            if inline is not None
            else ""
        )
    value = cell.find("main:v", NS)
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        index = int(value.text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return value.text


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall("main:si", NS):
        strings.append("".join((node.text or "") for node in item.iter() if node.tag.endswith("}t")))
    return strings


def read_xlsx_records(path: Path) -> tuple[list[SourceRecord], list[str]]:
    records: list[SourceRecord] = []
    all_headers: list[str] = []
    with zipfile.ZipFile(path) as archive:
        shared_strings = load_shared_strings(archive)
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap = {}
        for relationship in rels:
            target = relationship.attrib["Target"].lstrip("/")
            if not target.startswith("xl/"):
                target = f"xl/{target}"
            relmap[relationship.attrib["Id"]] = target
        sheets = workbook.find("main:sheets", NS)
        for sheet in list(sheets) if sheets is not None else []:
            sheet_name = sheet.attrib["name"]
            rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
            worksheet = ET.fromstring(archive.read(relmap[rel_id]))
            xml_rows = worksheet.find("main:sheetData", NS).findall("main:row", NS)
            matrix: list[tuple[int, list[str]]] = []
            for xml_row in xml_rows:
                values: list[str] = []
                for cell in xml_row.findall("main:c", NS):
                    ref = cell.attrib.get("r", "")
                    match = re.match(r"([A-Z]+)", ref)
                    if match:
                        col = 0
                        for char in match.group(1):
                            col = col * 26 + (ord(char) - 64)
                        while len(values) < col - 1:
                            values.append("")
                    values.append(cell_text(cell, shared_strings))
                matrix.append((int(xml_row.attrib.get("r", len(matrix) + 1)), values))
            if not matrix:
                continue
            headers = matrix[0][1]
            for header in headers:
                if header and header not in all_headers:
                    all_headers.append(header)
            for row_num, values in matrix[1:]:
                data = {header: values[index] if index < len(values) else "" for index, header in enumerate(headers)}
                source_file = rel(path)
                records.append(
                    SourceRecord(
                        source_file=source_file,
                        source_sheet=sheet_name,
                        source_row=str(row_num),
                        source_type="xlsx",
                        record_key=f"{source_file}::{sheet_name}#{row_num}",
                        data=data,
                    )
                )
    return records, all_headers


def discover_sources() -> list[Path]:
    paths: list[Path] = []
    for base in (DOCS, REPORTS):
        if not base.exists():
            continue
        paths.extend(base.rglob("*.csv"))
        paths.extend(base.rglob("*.xlsx"))
    excluded = {
        "reports/normalized_master_feature_matrix.xlsx",
    }
    return sorted(path for path in paths if rel(path) not in excluded)


def load_source_records() -> tuple[list[SourceRecord], list[str]]:
    records: list[SourceRecord] = []
    source_headers: list[str] = []
    for path in discover_sources():
        if path.suffix.lower() == ".csv":
            loaded, headers = read_csv_records(path)
        elif path.suffix.lower() == ".xlsx":
            loaded, headers = read_xlsx_records(path)
        else:
            continue
        records.extend(loaded)
        for header in headers:
            if header and header not in source_headers:
                source_headers.append(header)
    return records, source_headers


def existing_features() -> tuple[set[str], dict[str, str]]:
    if not REGISTRY_PATH.exists():
        return set(), {}
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    titles: dict[str, str] = {}
    for feature in registry.get("features", []):
        feature_id = feature.get("id")
        if not feature_id:
            continue
        ids.add(feature_id)
        title = feature.get("title")
        if title:
            titles[title.strip().lower()] = feature_id
    return ids, titles


def frame_name(data: dict[str, str]) -> str:
    return (
        data.get("Frame / Framing")
        or data.get("Proposed Contract Frame/Profile")
        or data.get("Framing")
        or ""
    ).strip()


def event_type_from_schema_path(schema_path: str) -> str:
    filename = Path(schema_path).name
    if not filename.endswith(".schema.json"):
        return ""
    stem = filename[: -len(".schema.json")]
    event_prefixes = (
        "http-",
        "websocket-",
        "lifespan-",
        "webtransport-",
    )
    if not any(stem.startswith(prefix) for prefix in event_prefixes):
        return ""
    return stem.replace("-", ".")


def is_lifespan_row(record: SourceRecord) -> bool:
    subevent = record.data.get("subevent", "")
    return record.source_file.endswith("lifespan_subevent_matrix.csv") or subevent.startswith("lifespan.")


def surface_key(record: SourceRecord) -> str:
    data = record.data
    source_file = record.source_file
    category = data.get("category", "")
    schema_path = data.get("schema_path", "").strip()
    transport_event = data.get("transport_event_type", "").strip()
    scope_type = data.get("scope_type", "").strip()
    scope_types = data.get("scope_types", "").strip()
    family = data.get("family", "").strip()
    subevent = data.get("subevent", "").strip()
    concern = data.get("concern", "").strip()
    framing = frame_name(data)

    if schema_path:
        event_type = event_type_from_schema_path(schema_path)
        if event_type:
            return f"event:{event_type}"
        if category == "event" or "/events/" in schema_path:
            return f"event:{schema_path}"
        return f"schema:{schema_path}"
    if transport_event:
        return f"event:{transport_event}"
    if scope_type and family and subevent:
        return f"scope:scope:{scope_type}|family:{family}|subevent:{subevent}"
    if framing:
        return f"frame:{framing}"
    if concern:
        return f"concern:{concern}"
    if is_lifespan_row(record) and subevent:
        return f"lifespan:{subevent}"
    if scope_types and family and subevent:
        return f"scope:scope:{scope_types}|family:{family}|subevent:{subevent}"
    if source_file.endswith("subevent_scope_matrix.csv") and family and subevent:
        return f"scope:scope:{scope_types or 'unspecified'}|family:{family}|subevent:{subevent}"
    return ""


def rejection_reason(record: SourceRecord) -> str:
    data = record.data
    if data.get("valid_scope_subevent_event") == "no":
        return "invalid cartesian scope/event/subevent permutation"
    if data.get("scope_supported") == "no" and not any(
        [
            data.get("schema_path"),
            data.get("concern"),
            frame_name(data),
            is_lifespan_row(record),
        ]
    ):
        return "unsupported scope/subevent combination without planned surface"
    if not surface_key(record):
        return "no governed feature surface key could be derived"
    return ""


def classify_kind(feature_surface_key: str) -> str:
    return feature_surface_key.partition(":")[0] or "unknown"


def value_set(rows: Iterable[SourceRecord], key: str) -> list[str]:
    values = sorted({row.data.get(key, "").strip() for row in rows if row.data.get(key, "").strip()})
    return values


def first_value(rows: Iterable[SourceRecord], *keys: str) -> str:
    for row in rows:
        for key in keys:
            value = row.data.get(key, "").strip()
            if value:
                return value
    return ""


def status_from_value(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return ""
    if normalized in IMPLEMENTED_SIGNALS:
        return "implemented"
    if normalized in PARTIAL_SIGNALS:
        return "partial"
    if normalized in ABSENT_SIGNALS:
        return "absent"
    return ""


def implementation_status(rows: list[SourceRecord]) -> str:
    statuses: list[str] = []
    for row in rows:
        data = row.data
        for key in (
            "current_status",
            "current_support",
            "status",
            "Current contract support",
            "Recommended support level",
        ):
            status = status_from_value(data.get(key, ""))
            if status:
                statuses.append(status)
        for key in ("rest", "jsonrpc", "http.stream", "sse", "websocket", "webtransport"):
            status = status_from_value(data.get(key, ""))
            if status:
                statuses.append(status)
    if "implemented" in statuses:
        return "implemented"
    if "partial" in statuses:
        return "partial"
    return "absent"


def forbidden_only(rows: list[SourceRecord]) -> bool:
    saw_legality = False
    saw_non_forbidden = False
    for row in rows:
        for key in ("rest", "jsonrpc", "http.stream", "sse", "websocket", "webtransport"):
            value = row.data.get(key, "").strip()
            if not value:
                continue
            saw_legality = True
            if value != "F":
                saw_non_forbidden = True
    return saw_legality and not saw_non_forbidden


def plan_horizon(status: str, rows: list[SourceRecord]) -> str:
    if forbidden_only(rows):
        return "out_of_bounds"
    if status in {"implemented", "partial"}:
        return "current"
    return "future"


def join_values(rows: Iterable[SourceRecord], attr: str) -> str:
    values = sorted({getattr(row, attr).strip() for row in rows if getattr(row, attr).strip()})
    return "; ".join(values)


def join_data_values(rows: Iterable[SourceRecord], key: str) -> str:
    return "; ".join(value_set(rows, key))


def binding_summary(rows: list[SourceRecord]) -> str:
    bindings = []
    for key in ("rest", "jsonrpc", "http.stream", "sse", "websocket", "webtransport"):
        if any(row.data.get(key, "").strip() not in {"", "F"} for row in rows):
            bindings.append(key)
    return "; ".join(bindings)


def aggregate_legality(rows: list[SourceRecord], key: str) -> str:
    values = value_set(rows, key)
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return "; ".join(values)


def conflict_summary(rows: list[SourceRecord]) -> str:
    interesting = [
        "current_status",
        "current_support",
        "status",
        "Current contract support",
        "Recommended support level",
        "scope_type",
        "family",
        "subevent",
        "transport_event_type",
        "schema_path",
        "concern",
    ]
    conflicts = []
    for key in interesting:
        values = value_set(rows, key)
        if len(values) > 1:
            conflicts.append(f"{key}={','.join(values)}")
    return " | ".join(conflicts)


def dedupe_confidence(rows: list[SourceRecord]) -> str:
    conflicts = conflict_summary(rows)
    if not conflicts and len(rows) > 1:
        return "high"
    if conflicts:
        return "medium"
    return "high"


def review_reason(rows: list[SourceRecord]) -> str:
    if len(rows) == 1:
        return "single source row"
    conflicts = conflict_summary(rows)
    if conflicts:
        return f"deduped with conflicting source values: {conflicts}"
    return "deduped equivalent source rows"


def group_records(records: list[SourceRecord]) -> tuple[dict[str, list[SourceRecord]], list[SourceRecord]]:
    groups: dict[str, list[SourceRecord]] = defaultdict(list)
    rejected: list[SourceRecord] = []
    group_index: dict[str, str] = {}
    next_group = 1
    for record in records:
        reason = rejection_reason(record)
        key = surface_key(record)
        record.feature_surface_key = key
        if key:
            record.candidate_feature_id = candidate_id_for(key)
        if reason:
            record.normalized_row_status = "rejected"
            record.rejection_reason = reason
            rejected.append(record)
            continue
        if key not in group_index:
            group_index[key] = f"grp:{next_group:05d}"
            next_group += 1
        record.dedupe_group_id = group_index[key]
        record.normalized_row_status = "promoted"
        groups[key].append(record)
    return dict(groups), rejected


def primary_row(rows: list[SourceRecord]) -> SourceRecord:
    def score(row: SourceRecord) -> tuple[int, int]:
        source = row.source_file
        preferred = 0
        if source.endswith("proposed_schema_matrix.csv"):
            preferred = 5
        elif source.endswith("transport_adjacency_matrix.csv"):
            preferred = 4
        elif source.endswith("framing_multiplex_matrix.xlsx"):
            preferred = 3
        elif source.startswith("docs/"):
            preferred = 2
        elif source.endswith("master_feature_matrix.xlsx"):
            preferred = 1
        filled = sum(1 for value in row.data.values() if value.strip())
        return preferred, filled

    return max(rows, key=score)


def normalized_rows(groups: dict[str, list[SourceRecord]]) -> list[dict[str, str]]:
    existing_ids, title_matches = existing_features()
    rows: list[dict[str, str]] = []
    for key in sorted(groups):
        grouped = groups[key]
        primary = primary_row(grouped)
        candidate_id = candidate_id_for(key)
        title = title_for(key, primary.data)
        status = implementation_status(grouped)
        exact_match = candidate_id if candidate_id in existing_ids else ""
        weak_match = ""
        if not exact_match:
            weak_match = title_matches.get(title.strip().lower(), "")
        rows.append(
            {
                "candidate_feature_id": candidate_id,
                "feature_surface_key": key,
                "feature_kind": classify_kind(key),
                "title": title,
                "description": description_for(key, grouped),
                "implementation_status": status,
                "lifecycle_stage": "active",
                "plan_horizon": plan_horizon(status, grouped),
                "target_claim_tier": "T2",
                "target_lifecycle_stage": "active",
                "existing_ssot_feature_id": exact_match or weak_match,
                "existing_ssot_match_kind": "exact" if exact_match else "weak_title" if weak_match else "",
                "source_count": str(len(grouped)),
                "source_files": join_values(grouped, "source_file"),
                "source_sheets": join_values(grouped, "source_sheet"),
                "source_rows": "; ".join(f"{row.source_file}:{row.source_row}" for row in grouped),
                "primary_source_file": primary.source_file,
                "primary_source_row": primary.source_row,
                "scope_type": first_value(grouped, "scope_type", "scope_types"),
                "family": first_value(grouped, "family"),
                "subevent": first_value(grouped, "subevent"),
                "transport_event_type": first_value(grouped, "transport_event_type"),
                "binding": binding_summary(grouped),
                "protocols": first_value(grouped, "protocols_when_non_forbidden", "Supported bindings", "Current binding(s)"),
                "schema_path": first_value(grouped, "schema_path"),
                "frame_or_framing": frame_name(primary.data),
                "concern": first_value(grouped, "concern"),
                "current_support": first_value(grouped, "current_support", "Current contract support"),
                "current_status": first_value(grouped, "current_status", "status", "Recommended support level"),
                "legality_rest": aggregate_legality(grouped, "rest"),
                "legality_jsonrpc": aggregate_legality(grouped, "jsonrpc"),
                "legality_http_stream": aggregate_legality(grouped, "http.stream"),
                "legality_sse": aggregate_legality(grouped, "sse"),
                "legality_websocket": aggregate_legality(grouped, "websocket"),
                "legality_webtransport": aggregate_legality(grouped, "webtransport"),
                "dedupe_confidence": dedupe_confidence(grouped),
                "review_status": "needs_review",
                "review_notes": "",
            }
        )
    return rows


def duplicate_group_rows(groups: dict[str, list[SourceRecord]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, key in enumerate(sorted(groups), start=1):
        grouped = groups[key]
        primary = primary_row(grouped)
        title = title_for(key, primary.data)
        rows.append(
            {
                "dedupe_group_id": grouped[0].dedupe_group_id or f"grp:{index:05d}",
                "feature_surface_key": key,
                "candidate_feature_id": candidate_id_for(key),
                "row_count": str(len(grouped)),
                "source_files": join_values(grouped, "source_file"),
                "conflicting_values": conflict_summary(grouped),
                "selected_title": title,
                "selected_description": description_for(key, grouped),
                "review_reason": review_reason(grouped),
            }
        )
    return rows


def source_row_dicts(records: list[SourceRecord], source_headers: list[str]) -> list[dict[str, str]]:
    columns = provenance_columns() + SOURCE_ROW_EXTRA_COLUMNS + source_headers
    rows: list[dict[str, str]] = []
    for record in records:
        row = {
            "_source_file": record.source_file,
            "_source_sheet": record.source_sheet,
            "_source_row": record.source_row,
            "_source_type": record.source_type,
            "_record_key": record.record_key,
            "feature_surface_key": record.feature_surface_key,
            "candidate_feature_id": record.candidate_feature_id,
            "normalized_row_status": record.normalized_row_status,
            "dedupe_group_id": record.dedupe_group_id,
        }
        for header in source_headers:
            row[header] = record.data.get(header, "")
        rows.append({column: row.get(column, "") for column in columns})
    return rows


def rejected_row_dicts(rejected: list[SourceRecord]) -> list[dict[str, str]]:
    return [
        {
            "source_file": record.source_file,
            "source_sheet": record.source_sheet,
            "source_row": record.source_row,
            "reason": record.rejection_reason,
            "record_key": record.record_key,
        }
        for record in rejected
    ]


def provenance_columns() -> list[str]:
    return ["_source_file", "_source_sheet", "_source_row", "_source_type", "_record_key"]


def column_dictionary(source_headers: list[str]) -> list[dict[str, str]]:
    descriptions = {
        "candidate_feature_id": "Review-only candidate SSOT feature id.",
        "feature_surface_key": "Canonical dedupe key for the governed surface.",
        "feature_kind": "Surface category such as schema, event, scope, frame, concern, or lifespan.",
        "title": "Candidate SSOT feature title.",
        "description": "Candidate SSOT feature description.",
        "implementation_status": "Candidate absent/partial/implemented status.",
        "lifecycle_stage": "Candidate lifecycle stage defaulted for review.",
        "plan_horizon": "Candidate planning horizon defaulted from status.",
        "target_claim_tier": "Review default target claim tier.",
        "target_lifecycle_stage": "Review default lifecycle target.",
        "existing_ssot_feature_id": "Matched existing SSOT feature id, if any.",
        "existing_ssot_match_kind": "Exact or weak match marker.",
        "source_count": "Number of source rows in the dedupe group.",
        "source_files": "Source files represented in the dedupe group.",
        "source_sheets": "Source workbook sheets represented in the dedupe group.",
        "source_rows": "Source file and row provenance.",
        "primary_source_file": "Selected source for title/description defaults.",
        "primary_source_row": "Selected source row for title/description defaults.",
        "scope_type": "Scope type associated with the feature candidate.",
        "family": "Contract family associated with the feature candidate.",
        "subevent": "Contract subevent associated with the feature candidate.",
        "transport_event_type": "Transport event associated with the feature candidate.",
        "binding": "Bindings where the candidate is non-forbidden.",
        "protocols": "Protocols where the candidate is non-forbidden.",
        "schema_path": "Schema path associated with the feature candidate.",
        "frame_or_framing": "Frame or framing name associated with the feature candidate.",
        "concern": "Transport adjacency concern associated with the candidate.",
        "current_support": "Current support field preserved from source data.",
        "current_status": "Current status field preserved from source data.",
        "dedupe_confidence": "High/medium confidence based on source conflicts.",
        "review_status": "Manual review state.",
        "review_notes": "Manual review notes.",
    }
    rows: list[dict[str, str]] = []
    for column in NORMALIZED_FEATURE_COLUMNS:
        rows.append(
            {
                "column_name": column,
                "sheet": "Normalized Features",
                "role": "SSOT-ready" if column in {"candidate_feature_id", "title", "description", "implementation_status", "lifecycle_stage", "plan_horizon", "target_claim_tier", "target_lifecycle_stage"} else "review-only",
                "source_columns": source_columns_for(column),
                "description": descriptions.get(column, "Normalized review column."),
            }
        )
    for column in provenance_columns() + SOURCE_ROW_EXTRA_COLUMNS:
        rows.append(
            {
                "column_name": column,
                "sheet": "Source Rows",
                "role": "provenance-only",
                "source_columns": column,
                "description": "Preserves source row provenance and normalization linkage.",
            }
        )
    for column in source_headers:
        rows.append(
            {
                "column_name": column,
                "sheet": "Source Rows",
                "role": "provenance-only",
                "source_columns": column,
                "description": "Original source column preserved without transformation.",
            }
        )
    return rows


def source_columns_for(column: str) -> str:
    mapping = {
        "scope_type": "scope_type; scope_types",
        "transport_event_type": "transport_event_type",
        "schema_path": "schema_path",
        "frame_or_framing": "Frame / Framing; Proposed Contract Frame/Profile; Framing",
        "concern": "concern",
        "current_support": "current_support; Current contract support",
        "current_status": "current_status; status; Recommended support level",
        "protocols": "protocols_when_non_forbidden; Supported bindings; Current binding(s)",
        "binding": "rest; jsonrpc; http.stream; sse; websocket; webtransport",
    }
    if column.startswith("legality_"):
        return column.removeprefix("legality_").replace("_", ".")
    return mapping.get(column, "derived")


def col_letter(number: int) -> str:
    letters = ""
    while number:
        number, rem = divmod(number - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def cell_xml(row_number: int, col_number: int, value: object) -> str:
    text = "" if value is None else str(value)
    return (
        f'<c r="{col_letter(col_number)}{row_number}" t="inlineStr">'
        f"<is><t>{html.escape(text)}</t></is></c>"
    )


def worksheet_xml(headers: list[str], rows: list[dict[str, str]]) -> bytes:
    row_count = len(rows) + 1
    col_count = max(len(headers), 1)
    last_cell = f"{col_letter(col_count)}{row_count}"
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{MAIN_NS}" xmlns:r="{REL_NS}">',
        f'<dimension ref="A1:{last_cell}"/>',
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
        'activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" '
        'activeCell="A2" sqref="A2"/></sheetView></sheetViews>',
        '<sheetFormatPr defaultRowHeight="15"/>',
        "<sheetData>",
        '<row r="1">' + "".join(cell_xml(1, index, header) for index, header in enumerate(headers, 1)) + "</row>",
    ]
    for row_number, row in enumerate(rows, start=2):
        parts.append(
            f'<row r="{row_number}">'
            + "".join(cell_xml(row_number, index, row.get(header, "")) for index, header in enumerate(headers, 1))
            + "</row>"
        )
    parts.extend(["</sheetData>", f'<autoFilter ref="A1:{last_cell}"/>', "</worksheet>"])
    return "".join(parts).encode("utf-8")


def workbook_xml(sheet_names: list[str]) -> bytes:
    sheets = "".join(
        f'<sheet name="{html.escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<workbook xmlns="{MAIN_NS}" xmlns:r="{REL_NS}"><sheets>{sheets}</sheets></workbook>'
    ).encode("utf-8")


def workbook_rels_xml(sheet_count: int) -> bytes:
    rels = [
        f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        for index in range(1, sheet_count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{sheet_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{PKG_REL_NS}">{"".join(rels)}</Relationships>'
    ).encode("utf-8")


def content_types_xml(sheet_count: int) -> bytes:
    overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'{"".join(overrides)}</Types>'
    ).encode("utf-8")


def root_rels_xml() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{PKG_REL_NS}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    ).encode("utf-8")


def styles_xml() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<styleSheet xmlns="{MAIN_NS}">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        "</styleSheet>"
    ).encode("utf-8")


def app_xml() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        "<Application>Codex</Application></Properties>"
    ).encode("utf-8")


def core_xml() -> bytes:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
        "</cp:coreProperties>"
    ).encode("utf-8")


def write_workbook(sheets: list[tuple[str, list[str], list[dict[str, str]]]]) -> None:
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml([name for name, _, _ in sheets]))
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheets)))
        archive.writestr("xl/styles.xml", styles_xml())
        archive.writestr("docProps/app.xml", app_xml())
        archive.writestr("docProps/core.xml", core_xml())
        for index, (_, headers, rows) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", worksheet_xml(headers, rows))


def validate_workbook(
    records: list[SourceRecord],
    normalized: list[dict[str, str]],
    groups: dict[str, list[SourceRecord]],
    rejected: list[SourceRecord],
) -> None:
    if not OUTPUT_PATH.exists():
        raise AssertionError(f"output workbook was not created: {OUTPUT_PATH}")
    with zipfile.ZipFile(OUTPUT_PATH) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise AssertionError(f"workbook zip integrity failed at {bad}")
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find("main:sheets", NS)
        sheet_names = [sheet.attrib["name"] for sheet in (list(sheets) if sheets is not None else [])]
    expected = ["Normalized Features", "Source Rows", "Duplicate Groups", "Rejected Rows", "Column Dictionary"]
    if sheet_names != expected:
        raise AssertionError(f"unexpected sheets: {sheet_names}")
    if len({row["candidate_feature_id"] for row in normalized}) != len(normalized):
        raise AssertionError("candidate_feature_id values are not unique")
    group_ids = {rows[0].dedupe_group_id for rows in groups.values() if rows}
    for record in records:
        if record.normalized_row_status == "promoted" and record.dedupe_group_id not in group_ids:
            raise AssertionError(f"missing duplicate group for {record.record_key}")
    represented = sum(1 for record in records if record.normalized_row_status in {"promoted", "rejected"})
    if represented != len(records):
        raise AssertionError("not all source rows were represented")
    if len(rejected) != sum(1 for record in records if record.normalized_row_status == "rejected"):
        raise AssertionError("rejected row accounting mismatch")
    spot_checks = {
        "schema:contract/schemas/scope.schema.json": "feat:schemas-scope-schema",
        "event:http.response.trailers": "feat:event-http-response-trailers",
        "lifespan:lifespan.startup": "feat:lifespan-startup",
        "concern:Alt-Svc": "feat:concern-alt-svc",
        "concern:SVCB": "feat:concern-svcb",
        "concern:HTTPS DNS record": "feat:concern-https-dns-record",
        "concern:ALPN": "feat:concern-alpn",
        "concern:ECH": "feat:concern-ech",
        "concern:mTLS": "feat:concern-mtls",
    }
    normalized_by_key = {row["feature_surface_key"]: row for row in normalized}
    for key, candidate_id in spot_checks.items():
        row = normalized_by_key.get(key)
        if row is None:
            raise AssertionError(f"missing spot-check surface {key}")
        if row["candidate_feature_id"] != candidate_id:
            raise AssertionError(f"unexpected candidate id for {key}: {row['candidate_feature_id']}")


def main() -> int:
    records, source_headers = load_source_records()
    groups, rejected = group_records(records)
    normalized = normalized_rows(groups)
    duplicate_groups = duplicate_group_rows(groups)
    source_rows = source_row_dicts(records, source_headers)
    rejected_rows = rejected_row_dicts(rejected)
    dictionary_rows = column_dictionary(source_headers)

    source_headers_full = provenance_columns() + SOURCE_ROW_EXTRA_COLUMNS + source_headers
    sheets = [
        ("Normalized Features", NORMALIZED_FEATURE_COLUMNS, normalized),
        ("Source Rows", source_headers_full, source_rows),
        ("Duplicate Groups", DUPLICATE_GROUP_COLUMNS, duplicate_groups),
        ("Rejected Rows", REJECTED_ROW_COLUMNS, rejected_rows),
        ("Column Dictionary", COLUMN_DICTIONARY_COLUMNS, dictionary_rows),
    ]
    write_workbook(sheets)
    validate_workbook(records, normalized, groups, rejected)

    exact_matches = sum(1 for row in normalized if row["existing_ssot_match_kind"] == "exact")
    print(f"output: {OUTPUT_PATH}")
    print(f"source row count: {len(records)}")
    print(f"normalized feature count: {len(normalized)}")
    print(f"duplicate group count: {len(duplicate_groups)}")
    print(f"rejected row count: {len(rejected_rows)}")
    print(f"exact existing SSOT feature matches: {exact_matches}")
    print("workbook zip integrity: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
