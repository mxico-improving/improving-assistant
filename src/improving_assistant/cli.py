"""Command line entry point used by the skills and the OS scheduler.

Subcommands:
  plan          Print this week's timesheet plan as JSON (holidays + PTO applied).
  mark-done     Record that the week's check-in was completed.
  remind-check  Exit 0 and print a reminder if the week is still pending, else exit 1.
  notify        Same check, but shows a desktop notification (what the scheduler runs).
  install-scheduler  Install the weekly reminder in the OS scheduler.
  setup         Write the user config (project, hours, PTO type, holiday calendar).
  doctor        Check config, holidays, reminder and fallback browser.
  browser       Drive your own visible Chrome (fallback when Claude in Chrome isn't available):
                start | tabs | eval TAB JS | click TAB TEXT | type TAB TEXT | shot TAB FILE
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

    st = sub.add_parser("setup", help="write your config file")
    st.add_argument("--config", help="config path (default: ~/.improving-assistant/config.toml)")
    st.add_argument("--project", required=True, help="your Workday project row, exactly as shown")
    st.add_argument("--hours-per-day", type=float, default=8)
    st.add_argument("--pto-type", default="Guatemala PTO")
    st.add_argument("--country", default="us", help="holiday calendar code (data/holidays/<code>-*.toml)")
    st.add_argument("--force", action="store_true", help="overwrite an existing config")

    doc = sub.add_parser("doctor", help="check that everything is set up")
    doc.add_argument("--config")
    doc.add_argument("--port", type=int, default=9333)

    br = sub.add_parser("browser", help="drive your visible Chrome over DevTools (fallback)")
    br.add_argument("--port", type=int, default=9333)
    bsub = br.add_subparsers(dest="bcmd", required=True)
    bsub.add_parser("start", help="launch Chrome with the dedicated profile, Engage + Workday tabs")
    bsub.add_parser("tabs", help="list open tabs as JSON")
    for name, arg, h in (("eval", "js", "evaluate JavaScript, print the JSON value"),
                         ("click", "text", "real mouse click on the element with this exact text"),
                         ("type", "text", "type text as real key events into the focused element"),
                         ("shot", "file", "save a PNG screenshot")):
        c = bsub.add_parser(name, help=h)
        c.add_argument("tab", help="substring of the tab URL or title, e.g. 'engage' or 'myworkday'")
        c.add_argument(arg)
        if name == "click":
            c.add_argument("--index", type=int, default=0, help="pick the Nth match (default 0)")
    return p


def _toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # JSON string escaping is valid TOML basic-string syntax


def _calendars() -> list[str]:
    return sorted({p.name.split("-", 1)[0] for p in HOLIDAYS_DIR.glob("*-*.toml")})


def _setup(args) -> int:
    from improving_assistant.config import default_config_path

    path = Path(args.config) if args.config else default_config_path()
    if args.country not in _calendars():
        print(f"Unknown holiday calendar {args.country!r}. Available: {', '.join(_calendars())}")
        return 1
    if path.exists() and not args.force:
        print(f"{path} already exists. Re-run with --force to overwrite it.")
        return 1
    hours = int(args.hours_per_day) if float(args.hours_per_day).is_integer() else args.hours_per_day
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# improving-assistant config (see config.example.toml)\n"
        f"project = {_toml_str(args.project)}\n"
        f"hours_per_day = {hours}\n"
        f"pto_type = {_toml_str(args.pto_type)}\n"
        f"country = {_toml_str(args.country)}\n", encoding="utf-8")
    print(f"wrote {path}")
    return 0


def _reminder_status() -> str:
    os_name = current_os()
    if os_name == "linux":
        f = Path.home() / ".config" / "systemd" / "user" / "improving-assistant.timer"
    elif os_name == "macos":
        f = Path.home() / "Library" / "LaunchAgents" / "com.improving.assistant.plist"
    else:
        f = home_dir() / "scheduler" / "improving-assistant.xml"
    return "installed" if f.exists() else "not installed (run: ia.py install-scheduler)"


def _doctor(args) -> int:
    from improving_assistant.cdp import list_targets

    ok = True
    try:
        cfg = load_config(args.config)
        print(f"config: ok (project: {cfg.project}, {cfg.hours_per_day}h/day, calendar: {cfg.country})")
        years = sorted({d.year for d in load_holidays(HOLIDAYS_DIR, cfg.country)})
        if date.today().year in years:
            print(f"holidays: ok ({cfg.country}: {', '.join(map(str, years))})")
        else:
            print(f"holidays: WARNING, no {cfg.country} calendar for {date.today().year} (see docs/holidays.md)")
    except ConfigError as e:
        print(f"config: MISSING ({e})")
        ok = False
    print(f"reminder: {_reminder_status()}")
    try:
        n = len(list_targets(args.port))
        print(f"fallback browser: running on port {args.port} ({n} tabs)")
    except OSError:
        print("fallback browser: not running (only needed without Claude in Chrome: ia.py browser start)")
    return 0 if ok else 1


def _browser(args) -> int:
    from improving_assistant import browser

    if args.bcmd == "start":
        exe = browser.find_chrome(current_os())
        if not exe:
            print("Google Chrome or Microsoft Edge not found. Install one and retry.")
            return 2
        browser.start(exe, home_dir() / "chrome-profile", args.port)
        print(f"Started Chrome (profile {home_dir() / 'chrome-profile'}). Sign in to Engage and Workday there.")
        return 0
    try:
        if args.bcmd == "tabs":
            tabs = browser.list_targets(args.port)
            print(json.dumps([{"title": t.get("title"), "url": t.get("url")} for t in tabs], indent=2))
        elif args.bcmd == "eval":
            print(json.dumps(browser.evaluate(args.port, args.tab, args.js), ensure_ascii=False))
        elif args.bcmd == "click":
            if not browser.click_text(args.port, args.tab, args.text, args.index):
                print(f"No visible element with text {args.text!r}")
                return 1
        elif args.bcmd == "type":
            browser.type_text(args.port, args.tab, args.text)
        elif args.bcmd == "shot":
            print(browser.screenshot(args.port, args.tab, Path(args.file)))
    except (OSError, ConnectionError) as e:
        print(f"Can't reach Chrome on port {args.port} ({e}). Run: ia.py browser start")
        return 2
    except LookupError as e:
        print(e)
        return 1
    return 0


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

    if args.cmd == "browser":
        return _browser(args)
    if args.cmd == "setup":
        return _setup(args)
    if args.cmd == "doctor":
        return _doctor(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
