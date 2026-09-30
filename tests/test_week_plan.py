from datetime import date

from improving_assistant.week import plan_week, week_of

PROJECT = "Acme - Development"
HOLIDAYS = {date(2026, 9, 7): "Labor Day"}


def test_week_of_returns_monday_to_friday_for_any_day():
    assert week_of(date(2026, 10, 1)) == [date(2026, 9, 28) + _d(i) for i in range(5)]  # a Thursday
    assert week_of(date(2026, 10, 4)) == week_of(date(2026, 9, 28))  # Sunday belongs to same week


def test_normal_week_is_five_project_days_and_counts_as_full_week():
    plan = plan_week(date(2026, 9, 28), project=PROJECT, holidays=HOLIDAYS)

    assert [(e.day, e.kind, e.hours) for e in plan.entries] == [
        (date(2026, 9, 28) + _d(i), "project", 8) for i in range(5)
    ]
    assert all(e.project == PROJECT for e in plan.entries)
    assert plan.full_week is True


def test_holiday_is_marked_and_breaks_full_week():
    plan = plan_week(date(2026, 9, 7), project=PROJECT, holidays=HOLIDAYS)

    mon = plan.entries[0]
    assert (mon.day, mon.kind, mon.hours, mon.label) == (date(2026, 9, 7), "holiday", 0, "Labor Day")
    assert plan.full_week is False


def test_pto_day_is_logged_as_pto_type_and_breaks_full_week():
    plan = plan_week(date(2026, 10, 5), project=PROJECT, holidays=HOLIDAYS,
                     pto_days=[date(2026, 10, 9)], pto_type="Guatemala PTO")

    fri = plan.entries[4]
    assert (fri.kind, fri.hours, fri.label) == ("pto", 8, "Guatemala PTO")
    assert plan.full_week is False


def test_custom_daily_hours_are_respected():
    plan = plan_week(date(2026, 9, 28), project=PROJECT, holidays={}, hours_per_day=6)

    assert {e.hours for e in plan.entries} == {6}


def test_pto_outside_the_week_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="not in the week"):
        plan_week(date(2026, 9, 28), project=PROJECT, holidays={}, pto_days=[date(2026, 10, 5)])


def test_plan_serializes_to_json_friendly_dict():
    d = plan_week(date(2026, 9, 7), project=PROJECT, holidays=HOLIDAYS).to_dict()

    assert d["week_start"] == "2026-09-07"
    assert d["full_week"] is False
    assert d["entries"][0] == {"day": "2026-09-07", "weekday": "Mon", "kind": "holiday",
                               "hours": 0, "project": None, "label": "Labor Day"}


def _d(n):
    from datetime import timedelta
    return timedelta(days=n)
