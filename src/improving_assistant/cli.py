"""Command line entry point used by the skills and the OS scheduler.

Subcommands:
  plan          Print this week's timesheet plan as JSON (holidays + PTO applied).
  mark-done     Record that the week's check-in was completed.
  remind-check  Exit 0 and print a reminder if the week is still pending, else exit 1.
  notify        Same check, but shows a desktop notification (what the scheduler runs).
  install-scheduler  Install the weekly reminder in the OS scheduler.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from improving_assistant.config import ConfigError, home_dir, load_config
from improving_assistant.engage import full_week_entry
from improving_assistant.holidays import load_holidays
from improving_assistant.notify import current_os
from improving_assistant.notify import send as send_notification
from improving_assistant.scheduler import render
from improving_assistant.state import mark_week_done, needs_reminder
from improving_assistant.week import plan_week, week_of

HOLIDAYS_DIR = Path(__file__).resolve().parents[2] / "data" / "holidays"


def _date(s: str) -> date:
    return date.fromisoformat(s)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="improving-assistant")
    sub = p.add_subparsers(dest="cmd", required=True)

    plan = sub.add_parser("plan", help="print the week's timesheet plan as JSON")
    plan.add_argument("--config")
    plan.add_argument("--week", type=_date, help="any day in the target week (default: current week)")
    plan.add_argument("--today", type=_date, default=None, help=argparse.SUPPRESS)
    plan.add_argument("--pto", type=_date, action="append", default=[], help="PTO day (repeatable)")

    done = sub.add_parser("mark-done", help="record the week as completed")
    done.add_argument("--state")
    done.add_argument("--week", type=_date, default=None)

    for name in ("remind-check", "notify"):
        rem = sub.add_parser(name, help=f"{name}: remind if the week's check-in is pending")
        rem.add_argument("--state")
        rem.add_argument("--config")
        rem.add_argument("--today", type=_date, default=None)

    ins = sub.add_parser("install-scheduler", help="install the weekly reminder for this OS")
    ins.add_argument("--os", choices=["linux", "macos", "windows"], default=None)
    ins.add_argument("--dest", help="directory to write files to (default: the OS location)")
    ins.add_argument("--no-activate", action="store_true", help="write files only, don't enable")
    return p


def _reminder_message(args, today: date) -> str:
    msg = f"Weekly check-in pending for week of {week_of(today)[0]}. Run /weekly-checkin in Claude Code."
    try:
        hols = load_holidays(HOLIDAYS_DIR, load_config(args.config).country)
        names = [f"{d:%a %b %d} {hols[d]}" for d in week_of(today) if d in hols]
        if names:
            msg += " Holidays this week: " + ", ".join(names) + "."
    except ConfigError:
        msg += " (No config yet: see README setup.)"
    return msg


def _default_dest(os_name: str) -> Path:
    if os_name == "linux":
        return Path.home() / ".config" / "systemd" / "user"
    if os_name == "macos":
        return Path.home() / "Library" / "LaunchAgents"
    return home_dir() / "scheduler"


def _copy_app_to_home() -> Path:
    """Copy the stdlib-only app to ~/.improving-assistant/app so the scheduled job
    keeps working when the Claude Code plugin cache moves on update."""
    import shutil

    repo = Path(__file__).resolve().parents[2]
    app = home_dir() / "app"
    for sub in ("src", "data"):
        shutil.copytree(repo / sub, app / sub, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(repo / "ia.py", app / "ia.py")
    return app / "ia.py"


def _install_scheduler(args) -> int:
    os_name = args.os or current_os()
    dest = Path(args.dest) if args.dest else _default_dest(os_name)
    dest.mkdir(parents=True, exist_ok=True)
    runner = _copy_app_to_home()
    command = [sys.executable, str(runner), "notify"]
    written = []
    for name, content in render(os_name, command).items():
        path = dest / name
        path.write_text(content, encoding="utf-16" if name.endswith(".xml") else "utf-8")
        written.append(path)
        print(f"wrote {path}")
    if args.no_activate:
        return 0
    if os_name == "linux":
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "--now", "improving-assistant.timer"], check=True)
    elif os_name == "macos":
        plist = written[0]
        subprocess.run(["launchctl", "unload", str(plist)], check=False)
        subprocess.run(["launchctl", "load", str(plist)], check=True)
    else:
        subprocess.run(["schtasks", "/Create", "/F", "/TN", "ImprovingAssistant", "/XML", str(written[0])], check=True)
    print("Weekly reminder installed.")
    return 0


def _state_path(arg: str | None) -> Path:
    return Path(arg) if arg else home_dir() / "state.json"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    today = getattr(args, "today", None) or date.today()

    if args.cmd == "plan":
        cfg = load_config(args.config)
        plan = plan_week(args.week or today, project=cfg.project,
                         holidays=load_holidays(HOLIDAYS_DIR, cfg.country),
                         pto_days=args.pto, pto_type=cfg.pto_type, hours_per_day=cfg.hours_per_day)
        out = plan.to_dict()
        out["engage_full_week"] = full_week_entry(plan.week_start) if plan.full_week else None
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "mark-done":
        mark_week_done(_state_path(args.state), args.week or date.today())
        return 0

    if args.cmd == "remind-check":
        if not needs_reminder(_state_path(args.state), today):
            return 1
        print(_reminder_message(args, today))
        return 0

    if args.cmd == "notify":
        if needs_reminder(_state_path(args.state), today):
            send_notification("Improving Assistant", _reminder_message(args, today))
        return 0

    if args.cmd == "install-scheduler":
        return _install_scheduler(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
