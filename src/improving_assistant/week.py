"""Plan a work week: which days are project work, PTO or holidays."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass(frozen=True)
class DayEntry:
    day: date
    kind: str  # "project" | "pto" | "holiday"
    hours: float
    project: str | None = None
    label: str | None = None

    def to_dict(self) -> dict:
        return {
            "day": self.day.isoformat(),
            "weekday": WEEKDAYS[self.day.weekday()],
            "kind": self.kind,
            "hours": self.hours,
            "project": self.project,
            "label": self.label,
        }


@dataclass(frozen=True)
class WeekPlan:
    week_start: date
    entries: list[DayEntry]

    @property
    def full_week(self) -> bool:
        """True only when every weekday is project work (no PTO, no holiday)."""
        return all(e.kind == "project" for e in self.entries)

    def to_dict(self) -> dict:
        return {
            "week_start": self.week_start.isoformat(),
            "full_week": self.full_week,
            "entries": [e.to_dict() for e in self.entries],
        }


def week_of(day: date) -> list[date]:
    """Monday..Friday of the ISO week containing *day*."""
    monday = day - timedelta(days=day.weekday())
    return [monday + timedelta(days=i) for i in range(5)]


def plan_week(
    week_start: date,
    project: str,
    holidays: dict[date, str],
    pto_days: Iterable[date] = (),
    pto_type: str = "Guatemala PTO",
    hours_per_day: float = 8,
) -> WeekPlan:
    days = week_of(week_start)
    pto = set(pto_days)
    outside = pto - set(days)
    if outside:
        raise ValueError(f"PTO days not in the week of {days[0]}: {sorted(outside)}")

    entries = []
    for d in days:
        if d in holidays:
            entries.append(DayEntry(d, "holiday", 0, label=holidays[d]))
        elif d in pto:
            entries.append(DayEntry(d, "pto", hours_per_day, label=pto_type))
        else:
            entries.append(DayEntry(d, "project", hours_per_day, project=project))
    return WeekPlan(days[0], entries)
