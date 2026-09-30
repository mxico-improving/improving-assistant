"""The scheduler module renders OS-native job definitions; tests check their content
(the parts that matter for 'run weekly + catch up after the laptop was off')."""

import plistlib
import xml.etree.ElementTree as ET

import pytest

from improving_assistant.scheduler import render

CMD = ["/usr/bin/python3", "-m", "improving_assistant", "notify"]


def test_linux_timer_runs_monday_morning_and_catches_up_missed_runs():
    files = render("linux", CMD)

    timer = files["improving-assistant.timer"]
    assert "OnCalendar=Mon *-*-* 09:00:00" in timer
    assert "Persistent=true" in timer
    assert "OnStartupSec=" in timer  # also nudge after login on later weekdays


def test_linux_service_runs_the_command():
    service = render("linux", CMD)["improving-assistant.service"]

    assert "ExecStart=/usr/bin/python3 -m improving_assistant notify" in service
    assert "Type=oneshot" in service


def test_macos_launch_agent_runs_monday_and_at_load():
    plist = plistlib.loads(render("macos", CMD)["com.improving.assistant.plist"].encode())

    assert plist["ProgramArguments"] == CMD
    assert plist["StartCalendarInterval"] == {"Weekday": 1, "Hour": 9, "Minute": 0}
    assert plist["RunAtLoad"] is True  # catches the case where the Mac was off on Monday


def test_windows_task_is_weekly_and_starts_when_available():
    xml = render("windows", CMD)["improving-assistant.xml"]
    root = ET.fromstring(xml.encode("utf-16"))
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}

    assert root.find(".//t:Settings/t:StartWhenAvailable", ns).text == "true"
    assert root.find(".//t:CalendarTrigger/t:ScheduleByWeek/t:DaysOfWeek/t:Monday", ns) is not None
    assert root.find(".//t:LogonTrigger", ns) is not None
    assert root.find(".//t:Exec/t:Command", ns).text == "/usr/bin/python3"


def test_unknown_os_is_rejected():
    with pytest.raises(ValueError):
        render("beos", CMD)
