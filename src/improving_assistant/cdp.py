"""Minimal Chrome DevTools Protocol client using only the standard library.

Used by ``ia.py browser`` to drive the user's own, visible Chrome window. That's the fallback
for people who can't use the Claude in Chrome extension (e.g. API-key auth or Hermes users).
"""

from __future__ import annotations

import base64
import json
import os
import socket
import struct
import urllib.request
from urllib.parse import urlparse


def encode_frame(payload: bytes, opcode: int = 1, mask_key: bytes | None = None) -> bytes:
    """Client-to-server frames must be masked (RFC 6455 5.3)."""
    key = mask_key or os.urandom(4)
    n = len(payload)
    head = bytes([0x80 | opcode])
    if n < 126:
        head += bytes([0x80 | n])
    elif n < 65536:
        head += bytes([0x80 | 126]) + struct.pack(">H", n)
    else:
        head += bytes([0x80 | 127]) + struct.pack(">Q", n)
    return head + key + bytes(b ^ key[i % 4] for i, b in enumerate(payload))


def decode_frame(read) -> tuple[int, bytes]:
    """Read one (unmasked, server-to-client) frame via ``read(n)``; return (opcode, payload)."""
    b1, b2 = read(2)
    opcode, length = b1 & 0x0F, b2 & 0x7F
    if length == 126:
        length = struct.unpack(">H", read(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", read(8))[0]
    key = read(4) if b2 & 0x80 else None
    data = read(length) if length else b""
    if key:
        data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
    return opcode, data


def list_targets(port: int, host: str = "127.0.0.1") -> list[dict]:
    with urllib.request.urlopen(f"http://{host}:{port}/json/list", timeout=5) as r:
        return [t for t in json.load(r) if t.get("type") == "page"]


class CDPConnection:
    """``with CDPConnection(ws_url) as c: c.call("Runtime.evaluate", {...})``"""

    def __init__(self, ws_url: str, timeout: float = 30):
        u = urlparse(ws_url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n"
                           "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("DevTools closed the connection during handshake")
            resp += chunk
        status_line = resp.split(b"\r\n", 1)[0]
        if b" 101 " not in status_line:
            raise ConnectionError(f"WebSocket handshake failed: {status_line!r}")
        self._buf = resp.split(b"\r\n\r\n", 1)[1]
        self._next_id = 0

    def _read(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self.sock.recv(max(65536, n))
            if not chunk:
                raise ConnectionError("DevTools connection closed")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def _recv_message(self) -> dict:
        parts = b""
        while True:
            opcode, data = decode_frame(self._read)
            if opcode == 9:  # ping -> pong
                self.sock.sendall(encode_frame(data, opcode=10))
                continue
            if opcode == 8:
                raise ConnectionError("DevTools closed the connection")
            parts += data
            if opcode in (1, 0):
                return json.loads(parts)

    def call(self, method: str, params: dict | None = None) -> dict:
        self._next_id += 1
        mid = self._next_id
        self.sock.sendall(encode_frame(json.dumps({"id": mid, "method": method, "params": params or {}}).encode()))
        while True:
            msg = self._recv_message()
            if msg.get("id") != mid:
                continue  # an event, or a reply to someone else
            if "error" in msg:
                raise RuntimeError(f"{method}: {msg['error'].get('message')}")
            return msg.get("result", {})

    def close(self):
        try:
            self.sock.sendall(encode_frame(b"", opcode=8))
        except OSError:
            pass
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
