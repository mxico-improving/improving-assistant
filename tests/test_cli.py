import json
from pathlib import Path

from improving_assistant.cli import main

REPO = Path(__file__).resolve().parents[1]


def _cfg(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('project = "Acme - Dev"\n')
    return f


def test_plan_prints_json_with_holiday_and_pto(tmp_path, capsys):
    rc = main(["plan", "--config", str(_cfg(tmp_path)), "--week", "2026-11-23", "--pto", "2026-11-23"])

    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["full_week"] is False
    assert [e["kind"] for e in out["entries"]] == ["pto", "project", "project", "holiday", "holiday"]


def test_plan_includes_engage_entry_only_for_full_weeks(tmp_path, capsys):
    main(["plan", "--config", str(_cfg(tmp_path)), "--week", "2026-09-21"])
    full = json.loads(capsys.readouterr().out)
    main(["plan", "--config", str(_cfg(tmp_path)), "--week", "2026-09-07"])  # Labor Day week
    partial = json.loads(capsys.readouterr().out)

    assert full["engage_full_week"]["notes"] == "September 21 - 25"
    assert partial["engage_full_week"] is None


def test_plan_defaults_to_current_week(tmp_path, capsys):
    main(["plan", "--config", str(_cfg(tmp_path)), "--today", "2026-10-01"])

    assert json.loads(capsys.readouterr().out)["week_start"] == "2026-09-28"


def test_mark_done_then_remind_check_reports_nothing_to_do(tmp_path, capsys):
    state = tmp_path / "state.json"
    main(["mark-done", "--state", str(state), "--week", "2026-09-28"])
    capsys.readouterr()

    rc = main(["remind-check", "--state", str(state), "--today", "2026-09-29"])

    assert rc == 1  # 1 = nothing to remind about
    assert capsys.readouterr().out.strip() == ""


def test_remind_check_prints_message_when_pending(tmp_path, capsys):
    rc = main(["remind-check", "--state", str(tmp_path / "s.json"), "--today", "2026-11-23",
               "--config", str(_cfg(tmp_path))])

    out = capsys.readouterr().out
    assert rc == 0
    assert "/weekly-checkin" in out
    assert "Thanksgiving Day" in out
