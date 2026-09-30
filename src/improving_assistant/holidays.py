"""Holiday calendars stored as TOML files named ``<country>-<year>.toml``."""

from __future__ import annotations

import tomllib
from datetime import date
from pathlib import Path


def load_holidays(directory: str | Path, country: str) -> dict[date, str]:
    """Return {date: name} for every ``<country>-*.toml`` file in *directory*."""
    holidays: dict[date, str] = {}
    for path in sorted(Path(directory).glob(f"{country.lower()}-*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for item in data.get("holiday", []):
            holidays[item["date"]] = item["name"]
    return holidays
