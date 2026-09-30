from datetime import date

from improving_assistant.engage import full_week_entry


def test_full_week_entry_uses_direct_revenue_40_billable_hour_week():
    e = full_week_entry(date(2026, 9, 21))

    assert (e["category"], e["type"], e["quantity"]) == ("Direct Revenue", "40 Billable Hour Week", 1)


def test_full_week_entry_is_dated_friday_in_engage_format():
    assert full_week_entry(date(2026, 9, 23))["date"] == "09/25/2026"  # any day of the week


def test_notes_are_week_range_within_one_month():
    assert full_week_entry(date(2026, 9, 21))["notes"] == "September 21 - 25"


def test_notes_span_two_months_when_week_crosses_month_end():
    assert full_week_entry(date(2026, 9, 28))["notes"] == "September 28 - October 2"
