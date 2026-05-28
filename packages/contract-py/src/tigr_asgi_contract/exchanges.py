from ._enum_compat import StrEnum


class Exchange(StrEnum):
    UNARY = 'unary'
    CLIENT_STREAM = 'client_stream'
    SERVER_STREAM = 'server_stream'
    DUPLEX = 'duplex'
