"""A tiny scripted Chrome DevTools endpoint for tests (HTTP /json/* + one WebSocket).

It records every CDP message the client sends and answers from a responder function,
so tests can check exactly which commands the browser helpers issue.
"""

from __future__ import annotations

import base64
import hashlib
import json
import socket
import struct
import threading

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError
        buf += chunk
    return buf


def server_read_frame(conn):
    b1, b2 = _recv_exact(conn, 2)
    opcode, masked, length = b1 & 0x0F, b2 & 0x80, b2 & 0x7F
    if length == 126:
        length = struct.unpack(">H", _recv_exact(conn, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _recv_exact(conn, 8))[0]
    key = _recv_exact(conn, 4) if masked else b"\0\0\0\0"
    data = bytes(b ^ key[i % 4] for i, b in enumerate(_recv_exact(conn, length)))
    return opcode, data, bool(masked)


def server_send_frame(conn, payload: bytes, opcode=1):
    head = bytes([0x80 | opcode])
    n = len(payload)
    if n < 126:
        head += bytes([n])
    elif n < 65536:
        head += bytes([126]) + struct.pack(">H", n)
    else:
        head += bytes([127]) + struct.pack(">Q", n)
    conn.sendall(head + payload)


class FakeCDP:
    def __init__(self, targets=None, responder=None):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.port = self.sock.getsockname()[1]
        self.targets = targets if targets is not None else [
            {"id": "T1", "type": "page", "title": "Engage", "url": "https://engage.example.com/app",
             "webSocketDebuggerUrl": f"ws://127.0.0.1:{self.port}/devtools/page/T1"}]
        self.responder = responder or (lambda msg: {})
        self.received: list[dict] = []
        self.error_for: dict[str, dict] = {}
        self.masked_ok = True
        self._t = threading.Thread(target=self._serve, daemon=True)
        self._t.start()

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn):
        req = b""
        while b"\r\n\r\n" not in req:
            req += conn.recv(4096)
        head = req.decode()
        path = head.split(" ")[1]
        if "upgrade: websocket" not in head.lower():
            body = json.dumps(self.targets if path.startswith("/json/list") else {"Browser": "Fake/1"}).encode()
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
                         + str(len(body)).encode() + b"\r\n\r\n" + body)
            conn.close()
            return
        key = next(l.split(":", 1)[1].strip() for l in head.split("\r\n") if l.lower().startswith("sec-websocket-key"))
        accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
        conn.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                      f"Sec-WebSocket-Accept: {accept}\r\n\r\n").encode())
        try:
            while True:
                opcode, data, masked = server_read_frame(conn)
                self.masked_ok &= masked
                if opcode == 8:
                    return
                msg = json.loads(data)
                self.received.append(msg)
                server_send_frame(conn, json.dumps({"method": "Page.frameNavigated", "params": {}}).encode())
                if msg["method"] in self.error_for:
                    reply = {"id": msg["id"], "error": self.error_for[msg["method"]]}
                else:
                    reply = {"id": msg["id"], "result": self.responder(msg)}
                server_send_frame(conn, json.dumps(reply).encode())
        except (ConnectionError, OSError):
            return
        finally:
            conn.close()

    def close(self):
        self.sock.close()
