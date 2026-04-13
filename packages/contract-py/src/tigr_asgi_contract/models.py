from pydantic import BaseModel
from .capabilities import FamilyCapabilities


class TlsMetadata(BaseModel):
    version: str | None = None
    cipher: str | None = None
    verified: bool = False
    peer_identity: str | None = None
    peer_cert: dict | None = None


class TransportMetadata(BaseModel):
    binding: str
    network: str
    secure: bool
    alpn: str | None = None
    tls: TlsMetadata | None = None
    framing: str | None = None


class WebSocketScopeExt(BaseModel):
    subprotocol: str | None = None


class SseScopeExt(BaseModel):
    retry_ms: int | None = None
    last_event_id: str | None = None


class WebTransportScopeExt(BaseModel):
    session_id: str | None = None
    supports_datagrams: bool = False
    supports_bidi_streams: bool = False
    supports_uni_streams: bool = False
    max_datagram_size: int | None = None


class ScopeExt(BaseModel):
    transport: TransportMetadata
    family_capabilities: FamilyCapabilities
    websocket: WebSocketScopeExt | None = None
    sse: SseScopeExt | None = None
    webtransport: WebTransportScopeExt | None = None


class DerivedEvent(BaseModel):
    family: str
    subevent: str
    repeated: bool = False
