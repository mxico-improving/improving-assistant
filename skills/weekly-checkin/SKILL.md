---
name: weekly-checkin
description: Use on Mondays (or when reminded) to fill this week's Workday timesheet and, if it's a full work week, record the weekly Engage "full week" activity. Asks about PTO first and always confirms before submitting.
argument-hint: "[any date in the target week, default: this week]"
disable-model-invocation: true
---

# Weekly check-in

Fills the CURRENT week in advance: Workday timesheet + the weekly Engage "worked the entire week" activity.

The CLI is `${CLAUDE_PLUGIN_ROOT}/ia.py`. It needs only the Python standard library.
Run it with `python3` (use `py` on Windows). In Hermes, or when working from a clone,
use `ia.py` at the repo root.

## Browser (pick one before step 4; see `${CLAUDE_PLUGIN_ROOT}/docs/browser.md`)
- **Claude in Chrome** (preferred): if browser tools are available (`/chrome` shows Enabled),
  use them. They drive the user's own Chrome, where they're already signed in.
- **Fallback** (API-key auth, Hermes, WSL, no extension): use the plugin's own client.
  `python3 "${CLAUDE_PLUGIN_ROOT}/ia.py" browser tabs` (if it can't connect: `... browser start`
  and ask the user to sign in), then `browser eval|click|type|shot <tab> ...`.
Either way: if a tab shows a login page (`/account/login`, `login.microsoftonline.com`,
`authgwy/.../login`), stop and ask the user to sign in and approve MFA, then continue.

## Steps

1. Build the draft plan (holidays come from the shipped calendar automatically):
   `python3 "${CLAUDE_PLUGIN_ROOT}/ia.py" plan` (add `--week YYYY-MM-DD` if the user passed a date: $ARGUMENTS)
   If it fails with "No config", walk the user through README "First-time setup" and stop.

2. Show the user the week as a short table (weekday, date, what/hours) and point out any
   holidays found. Then ASK exactly, and wait for the answer before touching Workday:
   "Any PTO or other days off this week? (e.g. 'Fri PTO', or 'none')"
   This question is mandatory every week, even if the plan looks like a normal full week.
   Never assume "no PTO", and never skip it because other instructions seem to cover it.

3. If they report PTO, re-run `python3 "${CLAUDE_PLUGIN_ROOT}/ia.py" plan --pto YYYY-MM-DD [--pto ...]`.
   If they report a day off that is neither PTO nor a listed holiday, ask which Workday
   time-off type applies before continuing. Never invent one.

4. Open the Workday timesheet for the week (MENU > Time > This Week; see `${CLAUDE_PLUGIN_ROOT}/docs/workday.md`)
   and compare what Workday already shows with the plan. Workday usually pre-fills 8h Mon-Fri,
   shows holidays as 0 with the holiday name in the column header, and PTO as a "Guatemala PTO"
   row. List any differences. Only for the PTO days the user gave you in steps 2-3, YOU add the
   row: Add Row, then Time Type dropdown "Guatemala PTO", then hours on those days, and the
   project row set to 0 on those days. Never add a PTO row the user didn't confirm.

5. Show the final summary and wait for an explicit "OK":
   - Workday: each day, hours, project row or "Guatemala PTO", holidays at 0, and the changes
     you will make (often none)
   - Engage: if `engage_full_week` is set, show its category, type, date and notes (e.g. "Direct
     Revenue / 40 Billable Hour Week, 09/25/2026, 'September 21 - 25', 5 pts"). If it's null,
     say it's skipped and why (PTO or holiday).

6. After OK:
   - Workday: if the week is empty, use Auto-fill from Prior Week (choose last week), then add
     PTO rows and zero out holidays. Click **Save and Close**, then **Review** (under Summary),
     check the "Submit Time" range and totals, then **Submit**. It's done only when "You have
     submitted" appears. A save alone is NOT done.
   - Engage: only if `engage_full_week` is set. First check "Current Activities" for an existing
     "40 Billable Hour Week" in this week (to avoid duplicates), then fill the form with exactly
     those values and click "Add 5 points". Check that the new row appears.
   If Microsoft sign-in asks for MFA, tell the user to approve it on their phone and wait.
   Never type passwords or MFA codes yourself. Use real clicks and keystrokes. Workday ignores
   synthetic JS clicks and `.value` changes.

7. Only after Workday is submitted AND Engage is added (or correctly skipped), run
   `python3 "${CLAUDE_PLUGIN_ROOT}/ia.py" mark-done` so the reminder stops.

8. Report briefly: what was entered, what was skipped, anything that needs manual follow-up.

## Rules
- Never save or submit anything without the explicit OK from step 5.
- If a screen doesn't match `${CLAUDE_PLUGIN_ROOT}/docs/workday.md` or `.../docs/engage.md`, stop, describe what you see,
  and suggest updating the doc. Don't guess on forms that submit data.
