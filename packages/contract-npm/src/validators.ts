import {
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
    transitions.set(`${row.from}\u0000${row.event}`, row.to);
  }
  for (const subevent of subevents) {
    const next = transitions.get(`${state}\u0000${subevent}`);
    if (!next) return false;
    state = next;
  }
  return automaton.terminal.includes(state) || subevents.length > 0;
}
