---
name: improving-setup
description: Use when setting up improving-assistant for the first time, or when /weekly-checkin says there's no config. Checks prerequisites, sets up browser access, reads the user's Workday project row, writes the config, installs the weekly reminder, and runs a check.
disable-model-invocation: true
---

# Improving assistant setup

Takes a new user from install to a working /weekly-checkin. The CLI is
`python3 "${CLAUDE_PLUGIN_ROOT}/ia.py"` (use `py` on Windows; in Hermes or a clone, `ia.py` at the
repo root). Called `IA` below.

## Steps

1. **Python**: run `python3 --version` (Windows: `py --version`). It must be 3.11+. If it's older
   or missing, tell the user how to install it for their OS and stop.

2. **Current state**: run `IA doctor`. If config, reminder and browser are all ok already, say so
   and ask whether they want to redo anything.

3. **Browser access** (read `${CLAUDE_PLUGIN_ROOT}/docs/browser.md`):
   - If Claude in Chrome browser tools are available in this session, use them.
   - Otherwise explain the two options briefly: Claude in Chrome needs a Pro/Max/Team/Enterprise
     plan signed in with /login (not an API key), Chrome or Edge, and the extension, then
     `claude --chrome`. The fallback works for everyone: `IA browser start`. Let the user pick.
     If they aren't sure about their plan, use the fallback.
   - Either way, ask the user to sign in to https://engage.improving.com and
     https://workday.improving.com in that browser, approve MFA, and tell you when both home
     pages show. Never type passwords or codes.

4. **Find the Workday project row**: in Workday, open MENU > Time > Last Week (read only, don't
   save). Read the Time Type of the project row(s), e.g.
   "Acme: Software Development > Project > Time Entry". If there are several, list them and ask
   which one is their main project. If the week is empty, ask the user to type the row name
   exactly as Workday shows it. Close the grid without saving (click X, then "Discard" if asked).

5. **Confirm and write the config**: show project, hours per day (default 8), PTO type (default
   "Guatemala PTO") and holiday calendar (default `us`, the Improving US calendar that Improving
   Guatemala follows). Ask for changes, then run:
   `IA setup --project "<row>" [--hours-per-day N] [--pto-type "..."] [--country us]`
   If the config exists, ask before adding `--force`.

6. **Weekly reminder**: explain that it pops up a desktop notification on Monday 09:00, and at the
   next login if the laptop was off, until the week is done. Ask whether to install it. If yes:
   `IA install-scheduler`. On Linux, `notify-send` must exist (package `libnotify-bin` or
   `libnotify`). Offer to install it if it's missing.

7. **Verify**: run `IA doctor` and `IA plan`. Show the plan for this week as a short table.

8. **Finish**: tell them:
   - Run `/weekly-checkin` on Mondays (or when the reminder appears). It asks about PTO and waits
     for their OK before submitting.
   - Use `/engage-log <what and when>` for other Engage activities.
   - After updating the plugin, re-run `IA install-scheduler`.

## Rules
- Never save anything in Workday or Engage during setup. It's read-only.
- Never handle passwords or MFA codes.
