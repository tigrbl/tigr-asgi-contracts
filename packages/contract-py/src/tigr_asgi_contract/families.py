from enum import StrEnum


class Family(StrEnum):
    REQUEST = 'request'
    SESSION = 'session'
    MESSAGE = 'message'
    STREAM = 'stream'
    DATAGRAM = 'datagram'
