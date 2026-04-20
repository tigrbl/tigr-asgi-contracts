from __future__ import annotations

from tigr_asgi_contract import (
    binding_family_legality,
    binding_subevent_legality,
    binding_supports_family,
    binding_supports_subevent,
)


def assert_optional_family(binding: str, family: str) -> None:
    assert binding_family_legality(binding, family) == "O"
    assert binding_supports_family(binding, family) is True


def assert_optional_subevents(binding: str, subevents: list[str]) -> None:
    for subevent in subevents:
        assert binding_subevent_legality(binding, subevent) == "O"
        assert binding_supports_subevent(binding, subevent) is True


def test_optional_binding_families_are_supported() -> None:
    assert_optional_family("jsonrpc", "stream")
    assert_optional_family("rest", "stream")
    assert_optional_family("webtransport", "message")


def test_http_stream_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "http.stream",
        [
            "request.accept",
            "request.body_in",
            "request.disconnect",
            "response.body_out",
            "response.close",
            "stream.abort",
            "stream.flush",
        ],
    )


def test_jsonrpc_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "jsonrpc",
        [
            "request.accept",
            "request.disconnect",
            "response.close",
            "stream.chunk_in",
            "stream.chunk_out",
            "stream.close",
            "stream.emit_complete",
            "stream.finalize",
            "stream.open",
        ],
    )


def test_rest_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "rest",
        [
            "request.accept",
            "request.disconnect",
            "response.close",
            "stream.chunk_in",
            "stream.chunk_out",
            "stream.close",
            "stream.emit_complete",
            "stream.finalize",
            "stream.open",
        ],
    )


def test_websocket_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "websocket",
        [
            "message.ack",
            "message.decode",
            "message.nack",
            "message.replay",
            "message.snapshot",
            "session.disconnect",
            "session.emit_complete",
            "session.heartbeat",
            "session.sync",
        ],
    )


def test_sse_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "sse",
        [
            "request.accept",
            "request.body_in",
            "request.disconnect",
            "response.open",
            "response.close",
            "session.disconnect",
            "session.emit_complete",
            "session.heartbeat",
            "session.sync",
            "message.replay",
            "message.snapshot",
            "stream.abort",
            "stream.finalize",
            "stream.flush",
        ],
    )


def test_webtransport_optional_subevents_are_supported() -> None:
    assert_optional_subevents(
        "webtransport",
        [
            "session.heartbeat",
            "session.sync",
            "session.disconnect",
            "session.emit_complete",
            "message.in",
            "message.decode",
            "message.handle",
            "message.out",
            "message.ack",
            "message.nack",
            "message.replay",
            "message.snapshot",
            "message.emit_complete",
            "stream.flush",
            "stream.abort",
            "datagram.ack",
        ],
    )
