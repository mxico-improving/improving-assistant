"""Remembers which weeks have been completed, so reminders stop once done."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from improving_assistant.week import week_of


def _load(state_file: Path) -> dict:
    p = Path(state_file)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def is_week_done(state_file: str | Path, day: date) -> bool:
    return week_of(day)[0].isoformat() in _load(Path(state_file)).get("weeks_done", [])


def mark_week_done(state_file: str | Path, day: date) -> None:
    p = Path(state_file)
    data = _load(p)
    weeks = set(data.get("weeks_done", []))
    weeks.add(week_of(day)[0].isoformat())
    data["weeks_done"] = sorted(weeks)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def needs_reminder(state_file: str | Path, today: date) -> bool:
    return today.weekday() < 5 and not is_week_done(state_file, today)
