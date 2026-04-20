from ._enum_compat import StrEnum


class ScopeType(StrEnum):
    HTTP = 'http'
    WEBSOCKET = 'websocket'
    LIFESPAN = 'lifespan'
    WEBTRANSPORT = 'webtransport'
