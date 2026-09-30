"""`ia.py setup`: create or update the user's config non-interactively (the skill asks the questions)."""

import tomllib

from improving_assistant import cli


def test_setup_writes_config_with_project_and_defaults(tmp_path):
    cfg = tmp_path / "config.toml"

    rc = cli.main(["setup", "--config", str(cfg), "--project", "Acme: Software Development > Project > Time Entry"])

    data = tomllib.loads(cfg.read_text())
    assert rc == 0
    assert data == {"project": "Acme: Software Development > Project > Time Entry",
                    "hours_per_day": 8, "pto_type": "Guatemala PTO", "country": "us"}


def test_setup_accepts_overrides(tmp_path):
    cfg = tmp_path / "config.toml"

    cli.main(["setup", "--config", str(cfg), "--project", "P", "--hours-per-day", "6",
              "--pto-type", "Other PTO", "--country", "us"])

    assert tomllib.loads(cfg.read_text())["hours_per_day"] == 6
    assert tomllib.loads(cfg.read_text())["pto_type"] == "Other PTO"


def test_setup_refuses_to_overwrite_without_force(tmp_path, capsys):
    cfg = tmp_path / "config.toml"
    cfg.write_text('project = "Old"\n')

    rc = cli.main(["setup", "--config", str(cfg), "--project", "New"])

    assert rc == 1
    assert "Old" in cfg.read_text()
    assert "--force" in capsys.readouterr().out


def test_setup_force_overwrites(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text('project = "Old"\n')

    cli.main(["setup", "--config", str(cfg), "--project", "New", "--force"])

    assert tomllib.loads(cfg.read_text())["project"] == "New"


def test_setup_escapes_quotes_in_project_name(tmp_path):
    cfg = tmp_path / "config.toml"

    cli.main(["setup", "--config", str(cfg), "--project", 'Acme "Beta" > Time Entry'])

    assert tomllib.loads(cfg.read_text())["project"] == 'Acme "Beta" > Time Entry'


def test_setup_rejects_unknown_holiday_calendar(tmp_path, capsys):
    rc = cli.main(["setup", "--config", str(tmp_path / "c.toml"), "--project", "P", "--country", "zz"])

    assert rc == 1
    assert "us" in capsys.readouterr().out  # lists available calendars


def test_setup_defaults_to_user_home_config(isolated_home):
    cli.main(["setup", "--project", "P"])

    assert (isolated_home / "config.toml").exists()


def test_doctor_reports_each_check(tmp_path, capsys):
    cfg = tmp_path / "config.toml"
    cli.main(["setup", "--config", str(cfg), "--project", "P"])
    capsys.readouterr()

    rc = cli.main(["doctor", "--config", str(cfg), "--port", "1"])

    out = capsys.readouterr().out
    assert "config: ok" in out
    assert "holidays: ok" in out
    assert "reminder:" in out
    assert "fallback browser: not running" in out
    assert rc == 0  # a missing fallback browser is informational, not an error


def test_doctor_fails_without_config(tmp_path, capsys):
    rc = cli.main(["doctor", "--config", str(tmp_path / "missing.toml"), "--port", "1"])

    assert rc == 1
    assert "config: MISSING" in capsys.readouterr().out
