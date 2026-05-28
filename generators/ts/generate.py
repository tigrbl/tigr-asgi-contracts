from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT0 = Path(__file__).resolve().parents[1]
if str(ROOT0) not in sys.path:
    sys.path.insert(0, str(ROOT0))

from common import contract_data, member_name

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages" / "contract-npm"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def emit_enum(path: Path, enum_name: str, values: list[str]) -> None:
    lines = [f"export enum {enum_name} {{"]
    for value in values:
        lines.append(f"  {member_name(value)} = {json.dumps(value)},")
    lines.append("}")
    lines.append("")
    write(path, "\n".join(lines))


def main() -> None:
    data = contract_data()
    src = OUT / "src"

    emit_enum(src / "scope_types.ts", "ScopeType", data["scope_types"])
    emit_enum(src / "channels.ts", "Channel", data["channels"])
    emit_enum(src / "directions.ts", "Direction", data["directions"])
    emit_enum(src / "framing.ts", "Framing", data["framings"])
    emit_enum(src / "bindings.ts", "Binding", list(data["bindings"].keys()))
    emit_enum(src / "protocols.ts", "Protocol", list(data["protocols"].keys()))
    emit_enum(src / "exchanges.ts", "Exchange", data["exchanges"])
    emit_enum(src / "families.ts", "Family", data["families"])
    emit_enum(src / "subevents.ts", "Subevent", data["all_subevents"])
    emit_enum(src / "frames.ts", "Frame", list(data["frames"].keys()))
    emit_enum(src / "completion.ts", "EmitCompletionLevel", list(data["completion"]["levels"].keys()))

    write(src / "capabilities.ts", """export interface FamilyCapabilities {
  request?: boolean;
  session?: boolean;
  message?: boolean;
  stream_in?: boolean;
  stream_out?: boolean;
  datagram?: boolean;
  lifespan?: boolean;
}
""")
    write(src / "compatibility.ts", """export interface Compatibility {
  contract_name: string;
  contract_version: string;
  serde_version: number;
  schema_draft: string;
  min_tigrcorn_version?: string | null;
  min_tigrbl_version?: string | null;
}
""")
    write(src / "ids.ts", """export interface UnitIds {
  unit_id?: string | null;
  parent_unit_id?: string | null;
  session_id?: string | null;
  stream_id?: number | null;
  datagram_id?: number | null;
  emit_id?: string | null;
}
""")
    write(src / "models.ts", """import type { FamilyCapabilities } from "./capabilities";

export interface TlsMetadata {
  version?: string | null;
  cipher?: string | null;
  verified: boolean;
  peer_identity?: string | null;
  peer_cert?: Record<string, unknown> | null;
}

export interface TransportMetadata {
  binding: string;
  network: string;
  secure: boolean;
  alpn?: string | null;
  tls?: TlsMetadata | null;
  framing?: string | null;
}

export interface WebSocketScopeExt {
  subprotocol?: string | null;
}

export interface SseScopeExt {
  retry_ms?: number | null;
  last_event_id?: string | null;
}

export interface WebTransportScopeExt {
  session_id?: string | null;
  supports_datagrams?: boolean;
  supports_bidi_streams?: boolean;
  supports_uni_streams?: boolean;
  max_datagram_size?: number | null;
}

export interface ScopeExt {
  transport: TransportMetadata;
  family_capabilities: FamilyCapabilities;
  websocket?: WebSocketScopeExt | null;
  sse?: SseScopeExt | null;
  webtransport?: WebTransportScopeExt | null;
}

export interface DerivedEvent {
  family: string;
  subevent: string;
  repeated?: boolean;
}

export interface EventClassification {
  event: string;
  channel: string;
  scope_type: string;
  binding: string;
  family: string;
  exchange: string;
  direction: string;
  allowed_framings: string[];
  required_scope_fields: string[];
  required_payload_fields: string[];
  capability_gates: string[];
  stream_direction?: string | null;
}
""")
    write(src / "scope.ts", """import type { ScopeExt } from "./models";

export interface ContractScope {
  type: string;
  asgi: Record<string, unknown>;
  scheme: string;
  http_version?: string | null;
  method?: string | null;
  path: string;
  query_string?: string;
  headers: [string, string][];
  client?: [string, number] | null;
  server?: [string, number] | null;
  ext: ScopeExt;
}
""")
    event_values = data["schemas"]["event.schema.json"]["properties"]["type"]["enum"]
    emit_enum(src / "events.ts", "TransportEventType", event_values)
    with open(src / "events.ts", "a", encoding="utf-8") as handle:
        handle.write("""export interface ContractEvent {
  type: TransportEventType;
  message?: string | null;
  payload?: Record<string, unknown>;
}
""")

    registry_parts = [
        ("BINDING_FAMILY_MATRIX", data["binding_family"]),
        ("FAMILY_SUBEVENT_MATRIX", data["family_subevent"]),
        ("BINDING_SUBEVENT_MATRIX", data["binding_subevent"]),
        ("PROTOCOLS", data["protocols"]),
        ("AUTOMATA", data["automata"]),
        ("FRAMES", data["frames"]),
        ("EXTENSIONS", data["extensions"]),
        ("CHANNELS", data["channels"]),
        ("DIRECTIONS", data["directions"]),
        ("FRAMINGS", data["framings"]),
        ("EVENT_CLASSIFICATIONS", data["event_classifications"]),
    ]
    write(
        src / "registry.ts",
        "\n\n".join(
            f"export const {name} = {json.dumps(value, indent=2)} as const;"
            for name, value in registry_parts
        )
        + "\n",
    )
    write(src / "validators.ts", 'import {\n  AUTOMATA,\n  BINDING_FAMILY_MATRIX,\n  FAMILY_SUBEVENT_MATRIX,\n  BINDING_SUBEVENT_MATRIX,\n  PROTOCOLS,\n  EVENT_CLASSIFICATIONS,\n  FRAMINGS,\n} from "./registry";\nimport type { EventClassification } from "./models";\n\ntype ScopeLike = { type?: string; ext?: Record<string, any> };\nexport const LEGALITY_CODES = ["R", "O", "D", "F"] as const;\nexport const LEGALITY_ALLOWED_CODES = ["R", "O", "D"] as const;\n\nfunction bindingFromScope(scope: ScopeLike): string | undefined {\n  return scope.ext?.transport?.binding;\n}\n\nfunction hasCapability(scope: ScopeLike, gate: string): boolean {\n  return Boolean(scope.ext?.webtransport?.[gate]);\n}\n\nexport function bindingSupportsFamily(binding: keyof typeof BINDING_FAMILY_MATRIX, family: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(bindingFamilyLegality(binding, family));\n}\n\nexport function familySupportsSubevent(family: keyof typeof FAMILY_SUBEVENT_MATRIX, subevent: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(familySubeventLegality(family, subevent));\n}\n\nexport function bindingSupportsSubevent(binding: keyof typeof BINDING_SUBEVENT_MATRIX, subevent: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(bindingSubeventLegality(binding, subevent));\n}\n\nexport function bindingFamilyLegality(binding: string, family: string): string {\n  return ((BINDING_FAMILY_MATRIX as any)[binding] ?? {})[family] ?? "F";\n}\n\nexport function familySubeventLegality(family: string, subevent: string): string {\n  return ((FAMILY_SUBEVENT_MATRIX as any)[family] ?? {})[subevent] ?? "F";\n}\n\nexport function bindingSubeventLegality(binding: string, subevent: string): string {\n  return ((BINDING_SUBEVENT_MATRIX as any)[binding] ?? {})[subevent] ?? "F";\n}\n\nexport function validateBindingFamily(binding: string, family: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(bindingFamilyLegality(binding, family));\n}\n\nexport function validateFamilySubevent(family: string, subevent: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(familySubeventLegality(family, subevent));\n}\n\nexport function validateBindingSubevent(binding: string, subevent: string): boolean {\n  return (LEGALITY_ALLOWED_CODES as readonly string[]).includes(bindingSubeventLegality(binding, subevent));\n}\n\nexport function legalityMatrixErrors(): string[] {\n  const errors: string[] = [];\n  const bindings = new Set(Object.keys(BINDING_FAMILY_MATRIX));\n  const families = new Set(Object.keys(FAMILY_SUBEVENT_MATRIX));\n  const subevents = new Set<string>();\n  for (const values of Object.values(FAMILY_SUBEVENT_MATRIX as Record<string, Record<string, string>>)) {\n    for (const subevent of Object.keys(values)) subevents.add(subevent);\n  }\n\n  for (const [binding, familyMap] of Object.entries(BINDING_FAMILY_MATRIX as Record<string, Record<string, string>>)) {\n    for (const family of families) {\n      if (!(family in familyMap)) errors.push(`binding_family_missing:${binding}:${family}`);\n    }\n    for (const [family, code] of Object.entries(familyMap)) {\n      if (!families.has(family)) errors.push(`binding_family_unknown:${binding}:${family}`);\n      if (!(LEGALITY_CODES as readonly string[]).includes(code)) {\n        errors.push(`binding_family_bad_code:${binding}:${family}:${code}`);\n      }\n    }\n  }\n\n  for (const [family, subeventMap] of Object.entries(FAMILY_SUBEVENT_MATRIX as Record<string, Record<string, string>>)) {\n    for (const [subevent, code] of Object.entries(subeventMap)) {\n      if (!(LEGALITY_CODES as readonly string[]).includes(code)) {\n        errors.push(`family_subevent_bad_code:${family}:${subevent}:${code}`);\n      }\n    }\n  }\n\n  for (const [binding, subeventMap] of Object.entries(BINDING_SUBEVENT_MATRIX as Record<string, Record<string, string>>)) {\n    if (!bindings.has(binding)) errors.push(`binding_subevent_unknown_binding:${binding}`);\n    for (const subevent of subevents) {\n      if (!(subevent in subeventMap)) errors.push(`binding_subevent_missing:${binding}:${subevent}`);\n    }\n    for (const [subevent, code] of Object.entries(subeventMap)) {\n      if (!subevents.has(subevent)) errors.push(`binding_subevent_unknown:${binding}:${subevent}`);\n      if (!(LEGALITY_CODES as readonly string[]).includes(code)) {\n        errors.push(`binding_subevent_bad_code:${binding}:${subevent}:${code}`);\n      }\n    }\n  }\n  return errors;\n}\n\nexport function validateLegalityMatrices(): boolean {\n  return legalityMatrixErrors().length === 0;\n}\n\nexport function protocolBinding(protocol: keyof typeof PROTOCOLS): string {\n  return (PROTOCOLS as any)[protocol].binding;\n}\n\nexport function eventClassificationCandidates(\n  scope: ScopeLike,\n  channel: string,\n  eventType: string,\n  payload: Record<string, unknown> = {},\n): EventClassification[] {\n  const binding = bindingFromScope(scope);\n  return (EVENT_CLASSIFICATIONS as readonly any[])\n    .filter((row) => row.event === eventType && row.channel === channel)\n    .filter((row) => row.scope_type === scope.type)\n    .filter((row) => binding === undefined || row.binding === binding)\n    .filter((row) => !row.stream_direction || payload.stream_direction === row.stream_direction)\n    .filter((row) => (row.capability_gates ?? []).every((gate: string) => hasCapability(scope, gate)))\n    .map((row) => ({\n      allowed_framings: [],\n      required_scope_fields: [],\n      required_payload_fields: [],\n      capability_gates: [],\n      ...row,\n    }));\n}\n\nexport function classifyEvent(\n  scope: ScopeLike,\n  channel: string,\n  eventType: string,\n  payload: Record<string, unknown> = {},\n): EventClassification {\n  const rows = eventClassificationCandidates(scope, channel, eventType, payload);\n  if (rows.length === 0) throw new Error(`No event classification for ${channel}:${eventType}`);\n  return rows[0];\n}\n\nexport function validateEventClassification(\n  scope: ScopeLike,\n  channel: string,\n  eventType: string,\n  payload: Record<string, unknown> = {},\n): boolean {\n  return eventClassificationCandidates(scope, channel, eventType, payload).length > 0;\n}\n\nexport function validateFramingForClassification(\n  framing: string | null | undefined,\n  classification: EventClassification,\n): boolean {\n  if (framing == null) return true;\n  if (!(FRAMINGS as readonly string[]).includes(framing)) return false;\n  return classification.allowed_framings.includes(framing);\n}\n\nexport function validateEventPayload(\n  eventType: string,\n  payload: Record<string, unknown>,\n  classification?: EventClassification,\n): boolean {\n  if (payload == null || typeof payload !== "object" || "subsurface" in payload) return false;\n  if (eventType === "http.response.pathsend" && typeof payload.path !== "string") return false;\n  if (eventType.includes(".stream.") && !("stream_id" in payload)) return false;\n  if (eventType.includes(".datagram.") && !("datagram_id" in payload)) return false;\n  if (classification) {\n    if (classification.required_payload_fields.some((field) => !(field in payload))) return false;\n    const framing = payload.framing;\n    if (typeof framing === "string" && !validateFramingForClassification(framing, classification)) return false;\n    if (framing === "jsonrpc" && payload.jsonrpc_complete !== true) return false;\n    if (framing === "ndjson" && payload.jsonrpc_complete === true) return false;\n  }\n  return true;\n}\n\nexport function validateAutomataSequence(family: keyof typeof AUTOMATA, subevents: string[]): boolean {\n  const automaton = (AUTOMATA as any)[family];\n  let state = automaton.initial;\n  const transitions = new Map<string, string>();\n  for (const row of automaton.transitions) {\n    transitions.set(`${row.from}\\u0000${row.event}`, row.to);\n  }\n  for (const subevent of subevents) {\n    const next = transitions.get(`${state}\\u0000${subevent}`);\n    if (!next) return false;\n    state = next;\n  }\n  return automaton.terminal.includes(state) || subevents.length > 0;\n}\n')
    write(src / "index.ts", """export * from "./scope_types";
export * from "./channels";
export * from "./directions";
export * from "./framing";
export * from "./bindings";
export * from "./protocols";
export * from "./exchanges";
export * from "./families";
export * from "./subevents";
export * from "./frames";
export * from "./completion";
export * from "./capabilities";
export * from "./compatibility";
export * from "./ids";
export * from "./models";
export * from "./scope";
export * from "./events";
export * from "./registry";
export * from "./validators";
""")
    write(OUT / "tsx" / "ScopeView.tsx", """import React from "react";
import type { ContractScope } from "../src/scope";

export interface ScopeViewProps {
  scope: ContractScope;
}

export const ScopeView: React.FC<ScopeViewProps> = ({ scope }) => {
  return <pre>{JSON.stringify(scope, null, 2)}</pre>;
};
""")
    write(OUT / "tsx" / "BindingBadge.tsx", """import React from "react";
import type { Binding } from "../src/bindings";

export interface BindingBadgeProps {
  binding: Binding;
}

export const BindingBadge: React.FC<BindingBadgeProps> = ({ binding }) => <span>{binding}</span>;
""")
    write(OUT / "tsx" / "FamilyBadge.tsx", """import React from "react";
import type { Family } from "../src/families";

export interface FamilyBadgeProps {
  family: Family;
}

export const FamilyBadge: React.FC<FamilyBadgeProps> = ({ family }) => <span>{family}</span>;
""")
    write(OUT / "tsx" / "SubeventBadge.tsx", """import React from "react";
import type { Subevent } from "../src/subevents";

export interface SubeventBadgeProps {
  subevent: Subevent;
}

export const SubeventBadge: React.FC<SubeventBadgeProps> = ({ subevent }) => <span>{subevent}</span>;
""")


if __name__ == "__main__":
    main()
