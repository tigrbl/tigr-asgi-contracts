from ._enum_compat import StrEnum


class Channel(StrEnum):
    RECEIVE = 'receive'
    SEND = 'send'
