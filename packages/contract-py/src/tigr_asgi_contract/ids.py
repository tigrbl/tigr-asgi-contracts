from pydantic import BaseModel


class UnitIds(BaseModel):
    unit_id: str | None = None
    parent_unit_id: str | None = None
    session_id: str | None = None
    stream_id: int | None = None
    datagram_id: int | None = None
    emit_id: str | None = None
