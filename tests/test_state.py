from datetime import date

from improving_assistant.state import is_week_done, mark_week_done, needs_reminder


def test_week_not_done_when_no_state_file(tmp_path):
    assert is_week_done(tmp_path / "state.json", date(2026, 9, 28)) is False


def test_marking_done_is_remembered_for_that_week_only(tmp_path):
    s = tmp_path / "state.json"
    mark_week_done(s, date(2026, 9, 30))  # any day in the week

    assert is_week_done(s, date(2026, 9, 28)) is True
    assert is_week_done(s, date(2026, 10, 5)) is False


def test_reminder_needed_on_weekday_when_week_not_done(tmp_path):
    assert needs_reminder(tmp_path / "s.json", today=date(2026, 9, 28)) is True  # Monday


def test_no_reminder_once_week_is_done(tmp_path):
    s = tmp_path / "s.json"
    mark_week_done(s, date(2026, 9, 28))

    assert needs_reminder(s, today=date(2026, 10, 1)) is False


def test_no_reminder_on_weekends(tmp_path):
    assert needs_reminder(tmp_path / "s.json", today=date(2026, 10, 3)) is False  # Saturday
