from pydantic import BaseModel
from .models import ScopeExt


class ContractScope(BaseModel):
    type: str
    asgi: dict
    scheme: str
    http_version: str | None = None
    method: str | None = None
    path: str
    query_string: bytes = b""
    headers: list[tuple[bytes, bytes]]
    client: tuple[str, int] | None = None
    server: tuple[str, int] | None = None
    ext: ScopeExt
