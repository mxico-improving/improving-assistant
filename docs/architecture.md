# Architecture

    ┌─────────────── Claude Code / Hermes (interactive) ───────────────┐
    │  skills/weekly-checkin      skills/engage-log                    │
    │     │  asks PTO, shows summary, waits for OK                     │
    │     │  drives the browser (Workday, Engage), human does MFA      │
    │     ▼                                                            │
    │  ia.py plan / mark-done   ◄── deterministic logic, unit-tested   │
    └──────────────────────────────────────────────────────────────────┘
                 ▲                              │
                 │ reads                        │ writes
      data/holidays/*.toml             ~/.improving-assistant/
      ~/.improving-assistant/config.toml     state.json (weeks done)
                 ▲
                 │ runs `ia.py notify`
    ┌──── OS scheduler (no AI) ────┐
    │ systemd timer / launchd /    │ ── desktop notification:
    │ Task Scheduler, Mon 09:00 +  │    "run /weekly-checkin"
    │ catch-up at login            │
    └──────────────────────────────┘

## Components

- `src/improving_assistant/week.py` builds the Mon-Fri plan. A day is a holiday, PTO or
  project work. `full_week` is true only if all five days are project work.
- `holidays.py` loads `data/holidays/<calendar>-<year>.toml`.
- `config.py` holds per-user settings (project, hours, PTO type, calendar). Override the
  location with `IMPROVING_ASSISTANT_HOME`.
- `state.py` records which weeks are done, so the reminder stops.
- `notify.py` sends native notifications (notify-send, osascript, PowerShell toast).
- `scheduler.py` renders the OS job definitions. `cli.py install-scheduler` copies the app to
  `~/.improving-assistant/app/` (a stable path that survives plugin updates) and registers the job.
- `skills/` holds the conversational parts: judgment, confirmation and browser work.

## Why this split

- Business rules (hours, PTO, holidays, the full-week rule) live in plain tested Python, not in
  prompts, so they behave the same way every week and for every teammate.
- The scheduler has no AI in it. It works even if Claude Code isn't open, and catches up after the
  laptop was off. A scheduled job can't ask you questions, so it only reminds you and the rest
  happens interactively. See ADR 0001.
- Browser steps are guided by the screen maps in docs/workday.md and docs/engage.md. When the
  sites change, updating those docs is usually all that's needed.

## Security

- The human always signs in and approves MFA. Nothing stores credentials.
- Every submission needs an explicit OK from the user.
