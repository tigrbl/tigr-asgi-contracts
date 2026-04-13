import type { FamilyCapabilities } from "./capabilities";

export interface TlsMetadata {
  version?: string | null;
  cipher?: string | null;
  verified: boolean;
  peer_identity?: string | null;
  peer_cert?: Record<string, unknown> | null;
}

export interface TransportMetadata {
  binding: string;
  network: string;
  secure: boolean;
  alpn?: string | null;
  tls?: TlsMetadata | null;
  framing?: string | null;
}

export interface WebSocketScopeExt {
  subprotocol?: string | null;
}

export interface SseScopeExt {
  retry_ms?: number | null;
  last_event_id?: string | null;
}

export interface WebTransportScopeExt {
  session_id?: string | null;
  supports_datagrams?: boolean;
  supports_bidi_streams?: boolean;
  supports_uni_streams?: boolean;
  max_datagram_size?: number | null;
}

export interface ScopeExt {
  transport: TransportMetadata;
  family_capabilities: FamilyCapabilities;
  websocket?: WebSocketScopeExt | null;
  sse?: SseScopeExt | null;
  webtransport?: WebTransportScopeExt | null;
}

export interface DerivedEvent {
  family: string;
  subevent: string;
  repeated?: boolean;
}
