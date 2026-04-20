from ._enum_compat import StrEnum


class Exchange(StrEnum):
    UNARY = 'unary'
    SERVER_STREAM = 'server_stream'
    DUPLEX = 'duplex'
