from __future__ import annotations
from .registry import AUTOMATA, BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX, PROTOCOLS


def binding_supports_family(binding: str, family: str) -> bool:
    return BINDING_FAMILY_MATRIX[binding][family] != "F"


def family_supports_subevent(family: str, subevent: str) -> bool:
    return FAMILY_SUBEVENT_MATRIX[family].get(subevent) != "F"


def binding_supports_subevent(binding: str, subevent: str) -> bool:
    return BINDING_SUBEVENT_MATRIX[binding].get(subevent) != "F"


def binding_family_legality(binding: str, family: str) -> str:
    return BINDING_FAMILY_MATRIX[binding][family]


def binding_subevent_legality(binding: str, subevent: str) -> str:
    return BINDING_SUBEVENT_MATRIX[binding][subevent]


def protocol_binding(protocol: str) -> str:
    return PROTOCOLS[protocol]["binding"]


def validate_automata_sequence(family: str, subevents: list[str]) -> bool:
    automaton = AUTOMATA[family]
    state = automaton["initial"]
    transitions = {(row["from"], row["event"]): row["to"] for row in automaton["transitions"]}
    for subevent in subevents:
        next_state = transitions.get((state, subevent))
        if next_state is None:
            return False
        state = next_state
    return state in set(automaton["terminal"]) or bool(subevents)


def validate_event_payload(event_type: str, payload: dict) -> bool:
    if event_type == "http.response.pathsend":
        return isinstance(payload.get("path"), str) and bool(payload["path"])
    if ".stream." in event_type:
        return "stream_id" in payload
    if ".datagram." in event_type or event_type.endswith(".datagram"):
        return "datagram_id" in payload
    return isinstance(payload, dict)
