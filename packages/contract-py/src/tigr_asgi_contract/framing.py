from ._enum_compat import StrEnum


class Framing(StrEnum):
    JSON = 'json'
    JSONRPC = 'jsonrpc'
    NDJSON = 'ndjson'
    SSE = 'sse'
    TEXT = 'text'
    BYTES = 'bytes'
    BINARY = 'binary'
