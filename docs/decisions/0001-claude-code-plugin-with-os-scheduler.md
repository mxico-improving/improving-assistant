# ADR 0001: Claude Code plugin + OS-native scheduler

Status: accepted (2026-09-29)

## Context
Recurring chores: the Workday timesheet (weekly, filled on Monday for the current week), the
weekly Engage "full week" activity, and ad-hoc Engage activities. Both sites use Microsoft SSO
with MFA. Most of the team uses Claude Code, on Linux, macOS and Windows. Everything should run
locally, with no third-party messaging apps. Laptops may be off at the scheduled time.

## Options considered
- Hermes built-in cron: native scheduling, but it requires every teammate to install and keep
  running Hermes, and a scheduled job can't ask interactive questions in a terminal-only setup.
- Claude Code `/loop` or CronCreate: session-scoped, expires after 7 days, doesn't catch up.
- Claude Code Desktop scheduled tasks: catch up on wake, but need the Desktop app open. A catch-up
  run happens without the user present, and the check-in needs the user's answers.
- Cloud routines: can't reach a user's signed-in browser session, and SSO/MFA must be done by the user.
- OS scheduler + interactive skill (chosen).

## Decision
Ship a Claude Code plugin (skills plus a stdlib-only CLI). The skills are plain SKILL.md files,
so Hermes can use them too. The weekly trigger is the OS scheduler (systemd, launchd or Task
Scheduler), which shows a notification. The work itself happens interactively via /weekly-checkin.

## Consequences
- No dependency on any AI tool being open for the reminder. Missed runs are caught up.
- The user still starts the check-in, which is desirable: PTO questions and the OK before submit.
- Three scheduler backends to maintain, each covered by tests.
