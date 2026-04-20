from ._enum_compat import StrEnum


class Family(StrEnum):
    REQUEST = 'request'
    SESSION = 'session'
    MESSAGE = 'message'
    STREAM = 'stream'
    DATAGRAM = 'datagram'
