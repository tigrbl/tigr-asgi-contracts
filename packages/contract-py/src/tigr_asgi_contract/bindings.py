from enum import StrEnum


class Binding(StrEnum):
    REST = 'rest'
    JSONRPC = 'jsonrpc'
    HTTP_STREAM = 'http.stream'
    SSE = 'sse'
    WEBSOCKET = 'websocket'
    WEBTRANSPORT = 'webtransport'
