# Changelog

All notable changes are listed here. Versions follow SemVer, and the version in
`.claude-plugin/plugin.json` and `pyproject.toml` must match.

## [Unreleased]
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
