from enum import StrEnum


class EmitCompletionLevel(StrEnum):
    ACCEPTED_BY_RUNTIME = 'accepted_by_runtime'
    FLUSHED_TO_TRANSPORT = 'flushed_to_transport'
