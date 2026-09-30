# improving-assistant

A Claude Code plugin that handles recurring Improving admin chores for you:

- /weekly-checkin: fills this week's Workday timesheet in advance (8h/day on your project,
  with PTO and Improving holidays applied). If you work the full week, it also records the
  weekly Engage "full week" activity. It asks about PTO first and always shows a summary
  and waits for your OK before submitting.
- /improving-setup: one-time guided setup (browser, config, reminder).
- /engage-log: records any Engage activity from a plain description, e.g.
  `/engage-log mentored Ana for 1h yesterday`.
- A weekly desktop reminder: Monday 09:00, or at your next login if the laptop was off. It
  goes quiet once the week is done. It uses your OS's own scheduler, so no extra apps are needed.

Everything runs on your laptop. You sign in to Microsoft yourself, and MFA is always approved
by you on your phone.

## Requirements

- Claude Code (or Hermes, see below)
- Python 3.11+ (`python3 --version`; on Windows, `py --version`)
- Google Chrome or Microsoft Edge
- An Improving Microsoft account with access to Workday and engage.improving.com
- Recommended: a Claude Pro/Max/Team/Enterprise plan, which enables Claude in Chrome. Without it
  (e.g. API-key auth), the plugin uses its own built-in browser fallback. See docs/browser.md.

## Install (Claude Code)

In Claude Code:

    /plugin marketplace add mxico-improving/improving-assistant
    /plugin install improving-assistant@improving-assistant

## First-time setup

Optional but recommended: install the Claude in Chrome extension and start Claude Code with
`claude --chrome` (docs/browser.md). Then run:

    /improving-setup

It checks Python, sets up browser access (you sign in to Engage and Workday yourself), reads your
Workday project row, writes `~/.improving-assistant/config.toml`, installs the Monday reminder
(systemd on Linux, launchd on macOS, Task Scheduler on Windows) and runs a check.

Manual alternative (`<plugin-dir>` is shown in `/plugin`; from a clone, it's the repo root):

    python3 <plugin-dir>/ia.py setup --project "Acme: Software Development > Project > Time Entry"
    python3 <plugin-dir>/ia.py install-scheduler
    python3 <plugin-dir>/ia.py doctor

Re-run `install-scheduler` after updating the plugin. See docs/scheduler.md to remove the reminder.

## Use

- Monday reminder: run `/weekly-checkin` in Claude Code.
- Anytime: `/engage-log <what you did and when>`.

## Hermes

Hermes reads the same `skills/*/SKILL.md` files. Clone the repo and point Hermes at `skills/`
(or copy the skill folders into `~/.hermes/skills/improving/`). In Hermes, `ia.py` is at the repo
root, and browser access uses the built-in fallback (`ia.py browser`).

## Contributing

Anyone at Improving is welcome to contribute. Start with CONTRIBUTING.md and CLAUDE.md.
This project uses strict RED -> GREEN test-driven development.

## Docs

- docs/architecture.md: how the pieces fit together
- docs/development.md: dev setup, tests, releases
- docs/adding-a-skill.md: add a new automation
- docs/browser.md: Claude in Chrome vs the built-in browser fallback
- docs/workday.md, docs/engage.md: screen maps for the two sites
- docs/scheduler.md: the weekly reminder on each OS
- docs/holidays.md: holiday calendars
- docs/decisions/: why things are the way they are
