"""Per-user configuration (project name, hours, PTO type, holiday calendar)."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    project: str
    hours_per_day: float = 8
    pto_type: str = "Guatemala PTO"
    country: str = "us"  # holiday calendar: data/holidays/<country>-<year>.toml


def home_dir() -> Path:
    """Where user config and state live. Override with IMPROVING_ASSISTANT_HOME."""
    override = os.environ.get("IMPROVING_ASSISTANT_HOME")
    return Path(override) if override else Path.home() / ".improving-assistant"


def default_config_path() -> Path:
    return home_dir() / "config.toml"


def load_config(path: str | Path | None = None) -> Config:
    path = Path(path) if path else default_config_path()
    if not path.exists():
        raise ConfigError(f"No config at {path}. Copy config.example.toml there and edit it.")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if not data.get("project"):
        raise ConfigError(f"{path}: 'project' is required (your Workday project line).")
    known = {k: data[k] for k in ("project", "hours_per_day", "pto_type", "country") if k in data}
    return Config(**known)
