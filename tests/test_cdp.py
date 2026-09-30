"""Stdlib CDP client: WebSocket framing + request/response over a fake DevTools endpoint."""

import io
import json

import pytest

from fake_cdp import FakeCDP
from improving_assistant.cdp import CDPConnection, decode_frame, encode_frame, list_targets


def test_client_frames_are_masked_text_frames():
    frame = encode_frame(b"hi", mask_key=b"\x01\x02\x03\x04")

    assert frame[0] == 0x81          # FIN + text
    assert frame[1] == 0x80 | 2      # masked, length 2
    assert frame[2:6] == b"\x01\x02\x03\x04"
    assert bytes(b ^ k for b, k in zip(frame[6:], b"\x01\x02")) == b"hi"


@pytest.mark.parametrize("size", [5, 300, 70_000])
def test_decode_handles_all_length_encodings(size):
    payload = b"x" * size
    head = bytes([0x81])
    if size < 126:
        head += bytes([size])
    elif size < 65536:
        head += bytes([126]) + size.to_bytes(2, "big")
    else:
        head += bytes([127]) + size.to_bytes(8, "big")
    buf = io.BytesIO(head + payload)

    assert decode_frame(buf.read) == (1, payload)


def test_list_targets_returns_pages_from_json_endpoint():
    srv = FakeCDP()
    try:
        tabs = list_targets(srv.port)
        assert [t["title"] for t in tabs] == ["Engage"]
    finally:
        srv.close()


def test_call_returns_matching_result_and_skips_events():
    srv = FakeCDP(responder=lambda m: {"echo": m["method"]})
    try:
        with CDPConnection(list_targets(srv.port)[0]["webSocketDebuggerUrl"]) as c:
            assert c.call("Runtime.evaluate", {"expression": "1"}) == {"echo": "Runtime.evaluate"}
            assert c.call("Page.enable") == {"echo": "Page.enable"}
        assert [m["method"] for m in srv.received] == ["Runtime.evaluate", "Page.enable"]
        assert srv.masked_ok
    finally:
        srv.close()


def test_call_raises_on_cdp_error():
    srv = FakeCDP()
    srv.error_for = {"Bad.method": {"code": -32601, "message": "'Bad.method' wasn't found"}}
    try:
        with CDPConnection(list_targets(srv.port)[0]["webSocketDebuggerUrl"]) as c:
            with pytest.raises(RuntimeError, match="wasn't found"):
                c.call("Bad.method")
    finally:
        srv.close()
