"""`ia.py browser ...`: drive the user's own visible Chrome (fallback when Claude in Chrome
isn't available). Tests run against a fake DevTools endpoint and never launch a real browser."""

import json
from pathlib import Path

from fake_cdp import FakeCDP
from improving_assistant import browser, cli


def test_chrome_command_uses_dedicated_profile_and_local_debug_port(tmp_path):
    cmd = browser.chrome_command("/usr/bin/google-chrome", tmp_path / "profile", 9333, ["https://a", "https://b"])

    assert cmd[0] == "/usr/bin/google-chrome"
    assert f"--user-data-dir={tmp_path / 'profile'}" in cmd
    assert "--remote-debugging-port=9333" in cmd
    assert "--remote-debugging-address=127.0.0.1" in cmd
    assert not any("headless" in a for a in cmd)  # Engage's Cloudflare check blocks headless
    assert cmd[-2:] == ["https://a", "https://b"]


def test_find_chrome_prefers_known_install_locations(monkeypatch):
    monkeypatch.setattr(browser.shutil, "which", lambda n: "/opt/bin/" + n if n == "microsoft-edge" else None)
    monkeypatch.setattr(browser.Path, "exists", lambda self: False)

    assert browser.find_chrome("linux") == "/opt/bin/microsoft-edge"


def test_browser_tabs_lists_pages(capsys):
    srv = FakeCDP()
    try:
        rc = cli.main(["browser", "--port", str(srv.port), "tabs"])
        out = json.loads(capsys.readouterr().out)
        assert rc == 0 and out[0]["url"] == "https://engage.example.com/app"
    finally:
        srv.close()


def test_browser_eval_runs_js_in_matching_tab_and_prints_value(capsys):
    srv = FakeCDP(responder=lambda m: {"result": {"type": "string", "value": "Engage"}})
    try:
        cli.main(["browser", "--port", str(srv.port), "eval", "engage", "document.title"])
        assert capsys.readouterr().out.strip() == '"Engage"'
        sent = srv.received[-1]
        assert sent["method"] == "Runtime.evaluate" and sent["params"]["expression"] == "document.title"
        assert sent["params"]["returnByValue"] is True
    finally:
        srv.close()


def test_browser_click_text_sends_real_mouse_events_at_element_center():
    def responder(m):
        if m["method"] == "Runtime.evaluate":
            return {"result": {"type": "object", "value": [100, 50]}}
        return {}
    srv = FakeCDP(responder=responder)
    try:
        rc = cli.main(["browser", "--port", str(srv.port), "click", "engage", "Save"])
        kinds = [m["params"].get("type") for m in srv.received if m["method"] == "Input.dispatchMouseEvent"]
        assert rc == 0
        assert kinds == ["mouseMoved", "mousePressed", "mouseReleased"]
        press = next(m for m in srv.received if m["params"].get("type") == "mousePressed")
        assert (press["params"]["x"], press["params"]["y"]) == (100, 50)
    finally:
        srv.close()


def test_browser_click_reports_missing_element():
    srv = FakeCDP(responder=lambda m: {"result": {"type": "object", "subtype": "null", "value": None}})
    try:
        assert cli.main(["browser", "--port", str(srv.port), "click", "engage", "Nope"]) == 1
    finally:
        srv.close()


def test_browser_type_sends_one_key_event_pair_per_character():
    srv = FakeCDP()
    try:
        cli.main(["browser", "--port", str(srv.port), "type", "engage", "10/05"])
        downs = [m["params"]["text"] for m in srv.received
                 if m["method"] == "Input.dispatchKeyEvent" and m["params"]["type"] == "keyDown"]
        assert downs == list("10/05")
    finally:
        srv.close()


def test_browser_shot_writes_png(tmp_path):
    import base64
    srv = FakeCDP(responder=lambda m: {"data": base64.b64encode(b"\x89PNG fake").decode()})
    try:
        out = tmp_path / "s.png"
        cli.main(["browser", "--port", str(srv.port), "shot", "engage", str(out)])
        assert out.read_bytes().startswith(b"\x89PNG")
        methods = [m["method"] for m in srv.received]
        assert methods.index("Page.bringToFront") < methods.index("Page.captureScreenshot")
    finally:
        srv.close()


def test_browser_reports_when_chrome_is_not_running(capsys):
    rc = cli.main(["browser", "--port", "1", "tabs"])

    assert rc == 2
    assert "browser start" in capsys.readouterr().out
