from __future__ import annotations

from typing import Any

from .registry import FRAMES


EVENT_PAYLOAD_SCHEMA_PATHS: dict[str, str] = {
    "http.disconnect": "contract/schemas/events/http.disconnect.schema.json",
    "http.request": "contract/schemas/events/http.request.schema.json",
    "http.response.body": "contract/schemas/events/http.response.body.schema.json",
    "http.response.pathsend": "contract/schemas/events/http.response.pathsend.schema.json",
    "http.response.start": "contract/schemas/events/http.response.start.schema.json",
    "lifespan.shutdown": "contract/schemas/events/lifespan.shutdown.schema.json",
    "lifespan.shutdown.complete": "contract/schemas/events/lifespan.shutdown.complete.schema.json",
    "lifespan.shutdown.failed": "contract/schemas/events/lifespan.shutdown.failed.schema.json",
    "lifespan.startup": "contract/schemas/events/lifespan.startup.schema.json",
    "lifespan.startup.complete": "contract/schemas/events/lifespan.startup.complete.schema.json",
    "lifespan.startup.failed": "contract/schemas/events/lifespan.startup.failed.schema.json",
    "transport.emit.complete": "contract/schemas/events/transport.emit.complete.schema.json",
    "transport.emit.failed": "contract/schemas/events/transport.emit.failed.schema.json",
    "websocket.accept": "contract/schemas/events/websocket.accept.schema.json",
    "websocket.close": "contract/schemas/events/websocket.close.schema.json",
    "websocket.connect": "contract/schemas/events/websocket.connect.schema.json",
    "websocket.disconnect": "contract/schemas/events/websocket.disconnect.schema.json",
    "websocket.receive": "contract/schemas/events/websocket.receive.schema.json",
    "websocket.send": "contract/schemas/events/websocket.send.schema.json",
    "webtransport.accept": "contract/schemas/events/webtransport.accept.schema.json",
    "webtransport.close": "contract/schemas/events/webtransport.close.schema.json",
    "webtransport.connect": "contract/schemas/events/webtransport.connect.schema.json",
    "webtransport.datagram.receive": "contract/schemas/events/webtransport.datagram.receive.schema.json",
    "webtransport.datagram.send": "contract/schemas/events/webtransport.datagram.send.schema.json",
    "webtransport.disconnect": "contract/schemas/events/webtransport.disconnect.schema.json",
    "webtransport.stream.close": "contract/schemas/events/webtransport.stream.close.schema.json",
    "webtransport.stream.receive": "contract/schemas/events/webtransport.stream.receive.schema.json",
    "webtransport.stream.reset": "contract/schemas/events/webtransport.stream.reset.schema.json",
    "webtransport.stream.send": "contract/schemas/events/webtransport.stream.send.schema.json",
    "webtransport.stream.stop_sending": "contract/schemas/events/webtransport.stream.stop_sending.schema.json",
}

FRAME_PAYLOAD_SCHEMA_PATHS: dict[str, str] = {
    frame: f"contract/schemas/frames/{frame}.schema.json" for frame in FRAMES
}

EVENT_SCHEMA_IDS = frozenset(EVENT_PAYLOAD_SCHEMA_PATHS)
FRAME_SCHEMA_IDS = frozenset(FRAME_PAYLOAD_SCHEMA_PATHS)

_FRAMINGS = frozenset({"json", "jsonrpc", "ndjson", "sse", "text", "bytes", "binary"})
_STREAM_DIRECTIONS = frozenset({"bidi", "client_to_server", "server_to_client"})


def event_payload_schema_path(event_type: str) -> str:
    try:
        return EVENT_PAYLOAD_SCHEMA_PATHS[event_type]
    except KeyError as exc:
        raise KeyError(f"unknown event payload schema: {event_type}") from exc


def frame_payload_schema_path(frame: str) -> str:
    try:
        return FRAME_PAYLOAD_SCHEMA_PATHS[frame]
    except KeyError as exc:
        raise KeyError(f"unknown frame payload schema: {frame}") from exc


def event_has_payload_schema(event_type: str) -> bool:
    return event_type in EVENT_PAYLOAD_SCHEMA_PATHS


def frame_has_payload_schema(frame: str) -> bool:
    return frame in FRAME_PAYLOAD_SCHEMA_PATHS


def _is_present_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _has_unit_id(value: Any) -> bool:
    return isinstance(value, int) or _is_present_string(value)


def validate_event_payload_schema(event_type: str, event: dict[str, Any]) -> bool:
    if event_type not in EVENT_PAYLOAD_SCHEMA_PATHS:
        return False
    if not isinstance(event, dict) or event.get("type") != event_type:
        return False
    if "subsurface" in event:
        return False
    framing = event.get("framing")
    if framing is not None and framing not in _FRAMINGS:
        return False
    if event_type == "http.response.start" and not isinstance(event.get("status"), int):
        return False
    if event_type == "http.response.pathsend" and not _is_present_string(event.get("path")):
        return False
    if event_type.endswith(".failed") or event_type == "transport.emit.failed":
        if not _is_present_string(event.get("message")):
            return False
    if ".stream." in event_type:
        if not _has_unit_id(event.get("stream_id")):
            return False
        if event_type in {"webtransport.stream.receive", "webtransport.stream.send"}:
            if event.get("stream_direction") not in _STREAM_DIRECTIONS:
                return False
    if ".datagram." in event_type and not _has_unit_id(event.get("datagram_id")):
        return False
    return True


def validate_frame_payload_schema(frame: str, payload: dict[str, Any]) -> bool:
    if frame not in FRAME_PAYLOAD_SCHEMA_PATHS:
        return False
    if not isinstance(payload, dict) or payload.get("frame") != frame:
        return False
    if "subsurface" in payload:
        return False
    if frame == "http-response-start-frame" and not isinstance(payload.get("status"), int):
        return False
    if frame == "asgi-pathsend-extension" and not _is_present_string(payload.get("path")):
        return False
    if frame in {"websocket-receive-text", "websocket-send-text"}:
        return _is_present_string(payload.get("text"))
    if frame in {"websocket-receive-bytes", "websocket-send-bytes"}:
        return "bytes" in payload
    if frame == "webtransport-stream-frame":
        return _has_unit_id(payload.get("stream_id")) and payload.get("stream_direction") in _STREAM_DIRECTIONS
    if frame == "webtransport-datagram-frame":
        return _has_unit_id(payload.get("datagram_id"))
    if frame.startswith("sse-") and frame.endswith("-field"):
        return "value" in payload
    return True
