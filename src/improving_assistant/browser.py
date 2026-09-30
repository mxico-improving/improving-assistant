"""Drive the user's own visible Chrome over CDP (the fallback when Claude in Chrome isn't available).

The user signs in (SSO + MFA) in this window themselves. It uses a dedicated profile at
``~/.improving-assistant/chrome-profile`` so sessions persist and the personal profile isn't touched.
It must NOT be headless: Engage's Cloudflare check blocks headless and automated browsers.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
from pathlib import Path

from improving_assistant.cdp import CDPConnection, list_targets

DEFAULT_PORT = 9333
START_URLS = ["https://engage.improving.com", "https://workday.improving.com"]

_CANDIDATES = {
    "linux": ["google-chrome", "google-chrome-stable", "microsoft-edge", "chromium", "chromium-browser"],
    "macos": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
    "windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"],
}


def find_chrome(os_name: str) -> str | None:
    for c in _CANDIDATES.get(os_name, []):
        if Path(c).exists():
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def chrome_command(exe: str, profile: Path, port: int, urls: list[str]) -> list[str]:
    return [exe, f"--user-data-dir={profile}", f"--remote-debugging-port={port}",
            "--remote-debugging-address=127.0.0.1", "--no-first-run", "--no-default-browser-check", *urls]


def start(exe: str, profile: Path, port: int = DEFAULT_PORT, urls: list[str] | None = None) -> None:
    profile.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(chrome_command(exe, profile, port, urls or START_URLS),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def _tab(port: int, match: str) -> dict:
    tabs = list_targets(port)
    for t in tabs:
        if match.lower() in t.get("url", "").lower() or match.lower() in t.get("title", "").lower():
            return t
    raise LookupError(f"no tab matching {match!r}; open tabs: {[t.get('url') for t in tabs]}")


def evaluate(port: int, match: str, expression: str):
    with CDPConnection(_tab(port, match)["webSocketDebuggerUrl"]) as c:
        r = c.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
    if "exceptionDetails" in r:
        raise RuntimeError(r["exceptionDetails"].get("text", "JavaScript error"))
    return r.get("result", {}).get("value")


# Center of the smallest visible element whose trimmed text equals the label
# (buttons first, then any element). Workday ignores synthetic .click(), so we use real mouse events.
_FIND = """(() => {{
  const t = {label};
  const vis = e => e.offsetParent !== null && e.getClientRects().length;
  let els = [...document.querySelectorAll('button,[role=button],a,[role=link],[role=menuitem],[role=option]')]
      .filter(e => vis(e) && (e.innerText || e.getAttribute('aria-label') || '').trim() === t);
  if (!els.length) els = [...document.querySelectorAll('div,span,li,td')]
      .filter(e => vis(e) && (e.innerText || '').trim() === t);
  if (!els.length) return null;
  const e = els.sort((a, b) => a.innerText.length - b.innerText.length)[{index}];
  e.scrollIntoView({{block: 'center'}});
  const r = e.getBoundingClientRect();
  return [r.x + r.width / 2, r.y + r.height / 2];
}})()"""


def click_text(port: int, match: str, label: str, index: int = 0) -> bool:
    with CDPConnection(_tab(port, match)["webSocketDebuggerUrl"]) as c:
        r = c.call("Runtime.evaluate", {"expression": _FIND.format(label=json.dumps(label), index=index),
                                        "returnByValue": True})
        box = r.get("result", {}).get("value")
        if not box:
            return False
        x, y = box
        for kind in ("mouseMoved", "mousePressed", "mouseReleased"):
            ev = {"type": kind, "x": x, "y": y}
            if kind != "mouseMoved":
                ev.update(button="left", clickCount=1)
            c.call("Input.dispatchMouseEvent", ev)
    return True


def type_text(port: int, match: str, text: str) -> None:
    """Real key events into the focused element (Workday date fields ignore .value / insertText)."""
    with CDPConnection(_tab(port, match)["webSocketDebuggerUrl"]) as c:
        for ch in text:
            c.call("Input.dispatchKeyEvent", {"type": "keyDown", "text": ch, "key": ch})
            c.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": ch})


def screenshot(port: int, match: str, path: Path) -> Path:
    with CDPConnection(_tab(port, match)["webSocketDebuggerUrl"]) as c:
        c.call("Page.bringToFront")  # background tabs don't render, so capture would hang
        data = c.call("Page.captureScreenshot", {"format": "png"})["data"]
    path.write_bytes(base64.b64decode(data))
    return path
