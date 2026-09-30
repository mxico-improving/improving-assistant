"""Render OS-native scheduler definitions for the weekly reminder.

Each OS gets a job that fires Monday 09:00 and also shortly after login, so a
laptop that was off on Monday still gets reminded. The job runs
``improving-assistant notify``, which is silent once the week is marked done.
"""

from __future__ import annotations

import plistlib
import shlex
from xml.sax.saxutils import escape

LABEL = "com.improving.assistant"


def _linux(cmd: list[str]) -> dict[str, str]:
    service = (
        "[Unit]\nDescription=Improving Assistant weekly check-in reminder\n\n"
        "[Service]\nType=oneshot\n"
        f"ExecStart={shlex.join(cmd)}\n"
    )
    timer = (
        "[Unit]\nDescription=Improving Assistant weekly reminder timer\n\n"
        "[Timer]\n"
        "OnCalendar=Mon *-*-* 09:00:00\n"
        "Persistent=true\n"  # run a missed Monday as soon as the machine is up
        "OnStartupSec=5min\n"  # re-check after each login (silent if already done)
        "Unit=improving-assistant.service\n\n"
        "[Install]\nWantedBy=timers.target\n"
    )
    return {"improving-assistant.service": service, "improving-assistant.timer": timer}


def _macos(cmd: list[str]) -> dict[str, str]:
    plist = {
        "Label": LABEL,
        "ProgramArguments": cmd,
        "StartCalendarInterval": {"Weekday": 1, "Hour": 9, "Minute": 0},
        "RunAtLoad": True,
    }
    return {f"{LABEL}.plist": plistlib.dumps(plist).decode()}


def _windows(cmd: list[str]) -> dict[str, str]:
    exe, args = escape(cmd[0]), escape(" ".join(cmd[1:]))
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Improving Assistant weekly check-in reminder</Description></RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-05T09:00:00</StartBoundary>
      <ScheduleByWeek><DaysOfWeek><Monday /></DaysOfWeek><WeeksInterval>1</WeeksInterval></ScheduleByWeek>
    </CalendarTrigger>
    <LogonTrigger><Delay>PT5M</Delay></LogonTrigger>
  </Triggers>
  <Settings>
    <StartWhenAvailable>true</StartWhenAvailable>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
  </Settings>
  <Actions><Exec><Command>{exe}</Command><Arguments>{args}</Arguments></Exec></Actions>
</Task>
"""
    return {"improving-assistant.xml": xml}


_RENDERERS = {"linux": _linux, "macos": _macos, "windows": _windows}


def render(os_name: str, command: list[str]) -> dict[str, str]:
    """Return {filename: content} for *os_name* ('linux' | 'macos' | 'windows')."""
    try:
        return _RENDERERS[os_name](command)
    except KeyError:
        raise ValueError(f"Unsupported OS {os_name!r}; expected one of {sorted(_RENDERERS)}") from None
