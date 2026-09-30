# improving-assistant

A Claude Code plugin that handles recurring Improving admin chores for you:

- /weekly-checkin: fills this week's Workday timesheet in advance (8h/day on your project,
  with PTO and Improving holidays applied). If you work the full week, it also records the
  weekly Engage "full week" activity. It asks about PTO first and always shows a summary
  and waits for your OK before submitting.
- /engage-log: records any Engage activity from a plain description, e.g.
  `/engage-log mentored Ana for 1h yesterday`.
- A weekly desktop reminder: Monday 09:00, or at your next login if the laptop was off. It
  goes quiet once the week is done. It uses your OS's own scheduler, so no extra apps are needed.

Everything runs on your laptop. You sign in to Microsoft yourself, and MFA is always approved
by you on your phone.

## Requirements

- Claude Code (or Hermes, see below)
- Python 3.11+ (`python3 --version`; on Windows, `py --version`)
- An Improving Microsoft account with access to Workday and engage.improving.com

## Install (Claude Code)

In Claude Code:

    /plugin marketplace add mxico-improving/improving-assistant
    /plugin install improving-assistant@improving-assistant

## First-time setup

1. Create your config file:
   - macOS/Linux: `~/.improving-assistant/config.toml`
   - Windows: `%USERPROFILE%\.improving-assistant\config.toml`

   Copy `config.example.toml` and set `project` to your Workday project line exactly as
   it appears in Workday.

2. Check it:

       python3 <plugin-dir>/ia.py plan

   `<plugin-dir>` is shown in `/plugin`. From a clone, it's the repo root.

3. Install the weekly reminder (Linux: systemd user timer, macOS: launchd, Windows: Task Scheduler):

       python3 <plugin-dir>/ia.py install-scheduler

   Re-run this after updating the plugin so the reminder uses the new version.
   See docs/scheduler.md for how it works and how to remove it.

## Use

- Monday reminder: run `/weekly-checkin` in Claude Code.
- Anytime: `/engage-log <what you did and when>`.

## Hermes

Hermes reads the same `skills/*/SKILL.md` files. Clone the repo and point Hermes at `skills/`
(or copy the two folders into `~/.hermes/skills/improving/`). In Hermes, `ia.py` is at the repo root.

## Contributing

Anyone at Improving is welcome to contribute. Start with CONTRIBUTING.md and CLAUDE.md.
This project uses strict RED -> GREEN test-driven development.

## Docs

- docs/architecture.md: how the pieces fit together
- docs/development.md: dev setup, tests, releases
- docs/adding-a-skill.md: add a new automation
- docs/workday.md, docs/engage.md: screen maps for the two sites
- docs/scheduler.md: the weekly reminder on each OS
- docs/holidays.md: holiday calendars
- docs/decisions/: why things are the way they are
