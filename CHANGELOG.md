# Changelog

All notable changes are listed here. Versions follow SemVer, and the version in
`.claude-plugin/plugin.json` and `pyproject.toml` must match.

## [Unreleased]

## [0.2.0] - 2026-09-30
### Added
- `/improving-setup` skill, plus `ia.py setup` (writes the config) and `ia.py doctor` (health check).
- Browser access: Claude in Chrome (preferred), or a stdlib DevTools fallback `ia.py browser
  start|tabs|eval|click|type|shot` that drives a visible Chrome with a dedicated profile (docs/browser.md).
- Secret and personal-data scan (`scripts/check_secrets.py`, pre-push hook, gitleaks in CI) and a
  CLAUDE.md rule to run it before every push. Local-only denylist for sensitive names.
### Changed
- Skills pick the browser automatically and reference docs via `${CLAUDE_PLUGIN_ROOT}`.
### Added
- Engage full-week entry (`Direct Revenue / 40 Billable Hour Week`, dated Friday, notes like
  "September 21 - 25"), included in `ia.py plan` output as `engage_full_week` (null if not a full week).
- Live screen maps for Workday and Engage: all 17 Engage categories, 100 types and their points.
### Changed
- weekly-checkin now compares against Workday's pre-filled timesheet, and requires Save **and** Submit.

## [0.1.0] - 2026-09-29
### Added
- Week planner: Mon-Fri plan with project hours, PTO ("Guatemala PTO") and holidays, plus the
  `full_week` flag (false if any PTO or holiday).
- Improving US holiday calendar for 2026 (`data/holidays/us-2026.toml`).
- Stdlib-only CLI `ia.py` with the commands `plan`, `mark-done`, `remind-check`, `notify` and
  `install-scheduler`.
- Weekly reminder via systemd (Linux), launchd (macOS) and Task Scheduler (Windows), with catch-up
  after missed runs.
- Skills: `weekly-checkin`, `engage-log`.
- Contributor docs, CLAUDE.md, ADRs, and CI on all three OSes.
