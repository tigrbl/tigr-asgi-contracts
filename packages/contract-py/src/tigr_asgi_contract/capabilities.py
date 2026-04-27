from pydantic import BaseModel


class FamilyCapabilities(BaseModel):
    request: bool = False
    session: bool = False
    message: bool = False
    stream_in: bool = False
    stream_out: bool = False
    datagram: bool = False
    lifespan: bool = False
