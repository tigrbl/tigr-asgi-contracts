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
    write(src / "validators.ts", """import {
  AUTOMATA,
  BINDING_FAMILY_MATRIX,
  FAMILY_SUBEVENT_MATRIX,
  BINDING_SUBEVENT_MATRIX,
  PROTOCOLS,
  EVENT_CLASSIFICATIONS,
  FRAMINGS,
} from "./registry";
import type { EventClassification } from "./models";

type ScopeLike = { type?: string; ext?: Record<string, any> };

function bindingFromScope(scope: ScopeLike): string | undefined {
  return scope.ext?.transport?.binding;
}

function hasCapability(scope: ScopeLike, gate: string): boolean {
  return Boolean(scope.ext?.webtransport?.[gate]);
}

export function bindingSupportsFamily(binding: keyof typeof BINDING_FAMILY_MATRIX, family: string): boolean {
  return (BINDING_FAMILY_MATRIX as any)[binding][family] !== "F";
}

export function familySupportsSubevent(family: keyof typeof FAMILY_SUBEVENT_MATRIX, subevent: string): boolean {
  return ((FAMILY_SUBEVENT_MATRIX as any)[family] ?? {})[subevent] !== "F";
}

export function bindingSupportsSubevent(binding: keyof typeof BINDING_SUBEVENT_MATRIX, subevent: string): boolean {
  return ((BINDING_SUBEVENT_MATRIX as any)[binding] ?? {})[subevent] !== "F";
}

export function protocolBinding(protocol: keyof typeof PROTOCOLS): string {
  return (PROTOCOLS as any)[protocol].binding;
}

export function eventClassificationCandidates(
  scope: ScopeLike,
  channel: string,
  eventType: string,
  payload: Record<string, unknown> = {},
): EventClassification[] {
  const binding = bindingFromScope(scope);
  return (EVENT_CLASSIFICATIONS as readonly any[])
    .filter((row) => row.event === eventType && row.channel === channel)
    .filter((row) => row.scope_type === scope.type)
    .filter((row) => binding === undefined || row.binding === binding)
    .filter((row) => !row.stream_direction || payload.stream_direction === row.stream_direction)
    .filter((row) => (row.capability_gates ?? []).every((gate: string) => hasCapability(scope, gate)))
    .map((row) => ({
      allowed_framings: [],
      required_scope_fields: [],
      required_payload_fields: [],
      capability_gates: [],
      ...row,
    }));
}

export function classifyEvent(
  scope: ScopeLike,
  channel: string,
  eventType: string,
  payload: Record<string, unknown> = {},
): EventClassification {
  const rows = eventClassificationCandidates(scope, channel, eventType, payload);
  if (rows.length === 0) throw new Error(`No event classification for ${channel}:${eventType}`);
  return rows[0];
}

export function validateEventClassification(
  scope: ScopeLike,
  channel: string,
  eventType: string,
  payload: Record<string, unknown> = {},
): boolean {
  return eventClassificationCandidates(scope, channel, eventType, payload).length > 0;
}

export function validateFramingForClassification(
  framing: string | null | undefined,
  classification: EventClassification,
): boolean {
  if (framing == null) return true;
  if (!(FRAMINGS as readonly string[]).includes(framing)) return false;
  return classification.allowed_framings.includes(framing);
}

export function validateEventPayload(
  eventType: string,
  payload: Record<string, unknown>,
  classification?: EventClassification,
): boolean {
  if (payload == null || typeof payload !== "object" || "subsurface" in payload) return false;
  if (eventType === "http.response.pathsend" && typeof payload.path !== "string") return false;
  if (eventType.includes(".stream.") && !("stream_id" in payload)) return false;
  if (eventType.includes(".datagram.") && !("datagram_id" in payload)) return false;
  if (classification) {
    if (classification.required_payload_fields.some((field) => !(field in payload))) return false;
    const framing = payload.framing;
    if (typeof framing === "string" && !validateFramingForClassification(framing, classification)) return false;
    if (framing === "jsonrpc" && payload.jsonrpc_complete !== true) return false;
    if (framing === "ndjson" && payload.jsonrpc_complete === true) return false;
  }
  return true;
}

export function validateAutomataSequence(family: keyof typeof AUTOMATA, subevents: string[]): boolean {
  const automaton = (AUTOMATA as any)[family];
  let state = automaton.initial;
  const transitions = new Map<string, string>();
  for (const row of automaton.transitions) {
    transitions.set(`${row.from}\\u0000${row.event}`, row.to);
  }
  for (const subevent of subevents) {
    const next = transitions.get(`${state}\\u0000${subevent}`);
    if (!next) return false;
    state = next;
  }
  return automaton.terminal.includes(state) || subevents.length > 0;
}
""")
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
