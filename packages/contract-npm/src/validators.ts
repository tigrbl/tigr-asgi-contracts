import { AUTOMATA, BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX, PROTOCOLS } from "./registry";

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

export function validateEventPayload(eventType: string, payload: Record<string, unknown>): boolean {
  if (eventType === "http.response.pathsend") {
    return typeof payload.path === "string" && payload.path.length > 0;
  }
  if (eventType.includes(".stream.")) return "stream_id" in payload;
  if (eventType.includes(".datagram.") || eventType.endsWith(".datagram")) return "datagram_id" in payload;
  return typeof payload === "object" && payload !== null;
}
