"""CLI commands used by the OS scheduler: notify + install-scheduler."""

import shlex
import sys
from pathlib import Path

from improving_assistant import cli


def _exec_start(service_file: Path) -> list[str]:
    line = next(l for l in service_file.read_text().splitlines() if l.startswith("ExecStart="))
    return shlex.split(line.removeprefix("ExecStart="))


def test_notify_sends_desktop_notification_when_week_pending(tmp_path, monkeypatch):
    sent = []
    monkeypatch.setattr(cli, "send_notification", lambda title, msg: sent.append((title, msg)))

    rc = cli.main(["notify", "--state", str(tmp_path / "s.json"), "--today", "2026-09-28"])

    assert rc == 0
    assert len(sent) == 1 and "/weekly-checkin" in sent[0][1]


def test_notify_is_silent_when_week_already_done(tmp_path, monkeypatch):
    sent = []
    monkeypatch.setattr(cli, "send_notification", lambda title, msg: sent.append((title, msg)))
    state = tmp_path / "s.json"
    cli.main(["mark-done", "--state", str(state), "--week", "2026-09-28"])

    rc = cli.main(["notify", "--state", str(state), "--today", "2026-09-30"])

    assert rc == 0 and sent == []


def test_install_scheduler_writes_linux_units_to_dest(tmp_path):
    rc = cli.main(["install-scheduler", "--os", "linux", "--dest", str(tmp_path), "--no-activate"])

    assert rc == 0
    assert (tmp_path / "improving-assistant.timer").exists()
    argv = _exec_start(tmp_path / "improving-assistant.service")
    assert Path(argv[1]).name == "ia.py" and argv[2:] == ["notify"]


def test_install_scheduler_copies_app_to_stable_home_and_points_job_there(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("IMPROVING_ASSISTANT_HOME", str(home))

    cli.main(["install-scheduler", "--os", "linux", "--dest", str(tmp_path / "units"), "--no-activate"])

    runner = home / "app" / "ia.py"
    assert runner.exists()
    assert (home / "app" / "src" / "improving_assistant" / "cli.py").exists()
    assert (home / "app" / "data" / "holidays" / "us-2026.toml").exists()
    assert _exec_start(tmp_path / "units" / "improving-assistant.service") == [sys.executable, str(runner), "notify"]


def test_install_scheduler_writes_macos_plist_to_dest(tmp_path):
    cli.main(["install-scheduler", "--os", "macos", "--dest", str(tmp_path), "--no-activate"])

    assert (tmp_path / "com.improving.assistant.plist").exists()
