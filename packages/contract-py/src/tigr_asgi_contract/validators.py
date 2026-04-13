from __future__ import annotations
from .registry import BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX


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
