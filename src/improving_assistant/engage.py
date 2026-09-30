"""Engage (engage.improving.com) entries derived from the week plan. See docs/engage.md."""

from __future__ import annotations

from datetime import date

from improving_assistant.week import week_of

FULL_WEEK_CATEGORY = "Direct Revenue"
FULL_WEEK_TYPE = "40 Billable Hour Week"


def full_week_entry(any_day: date) -> dict:
    """The weekly 'full week' activity: dated Friday, notes = 'September 21 - 25'."""
    mon, fri = week_of(any_day)[0], week_of(any_day)[-1]
    end = f"{fri.day}" if fri.month == mon.month else f"{fri:%B} {fri.day}"
    return {
        "category": FULL_WEEK_CATEGORY,
        "type": FULL_WEEK_TYPE,
        "date": f"{fri:%m/%d/%Y}",
        "quantity": 1,
        "notes": f"{mon:%B} {mon.day} - {end}",
    }
