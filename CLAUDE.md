# CLAUDE.md

Guidance for Claude Code (and other AI agents) working IN this repository.
Humans: see CONTRIBUTING.md. The rules are the same.

## What this repo is

A Claude Code plugin, also usable as Hermes skills. It automates Improving admin chores:
- `skills/weekly-checkin`: weekly Workday timesheet + the weekly Engage "full week" activity
- `skills/engage-log`: ad-hoc Engage activities
- `src/improving_assistant`: stdlib-only Python CLI (`ia.py`) for week planning, holidays,
  reminder state, desktop notifications and OS scheduler install

Read `docs/architecture.md` before making structural changes.

## Development process: RED -> GREEN -> REFACTOR (mandatory)

Every change to behavior starts with a failing test. No exceptions without the maintainer's
explicit approval in the PR.

1. RED: write ONE small test for the next behavior. Run it and watch it fail for the
   expected reason (an assertion or NotImplementedError, not an ImportError or typo).
   If it passes right away, it isn't testing anything new, so fix the test.
2. GREEN: write the minimal code that makes it pass. Run the full suite.
3. REFACTOR: clean up with all tests green. Don't add behavior while refactoring.
4. Repeat, one vertical slice at a time. Don't write a pile of tests and then a pile of code.

Bug fixes follow the same process: first write a failing test that reproduces the bug.
If you realize you wrote code before its test, delete the code and start again from RED.

When reporting work, show the RED run (the failing output) and the GREEN run.

## Commands

    uv sync                         # set up dev environment (pytest)
    uv run pytest                   # full suite, must be green before every commit
    uv run pytest tests/test_x.py::test_name   # single test (RED/GREEN loop)
    python3 ia.py plan --config config.example.toml --week 2026-11-23
    claude plugin validate .        # validate plugin + marketplace manifests

## Before every push: secret and personal-data check (mandatory)

This repo is public. Before any `git push`, run:

    python3 scripts/check_secrets.py

and push only if it passes. It scans tracked files for credentials, private keys and
non-Improving email addresses, plus the terms in your local denylist (client names, colleague
names, anything personal), and runs gitleaks on the history when it's installed. Enable the hook
once per clone so it runs automatically:

    git config core.hooksPath .githooks

- Never bypass it with `--no-verify`. If it flags something, remove or generalize the content.
  If the leak is already in history, stop and tell the maintainer, since the history must be rewritten.
- Never commit the denylist (`.denylist` / `~/.improving-assistant/denylist.txt`). A list of
  sensitive names would itself leak them.
- Use neutral examples in docs and tests ("Acme: Software Development > Project > Time Entry"),
  never real client, project or colleague names, real screenshots, or real submissions.
- CI runs gitleaks on the full history for every push and PR.

## Rules and constraints

- Runtime code in `src/` uses only the Python standard library (3.11+). The scheduled job runs
  on teammates' machines with just a system Python. Dev-only tools can go in `[dependency-groups]`.
- Support Linux, macOS and Windows. Anything OS-specific goes through `notify.py` or `scheduler.py`,
  with a test for each OS.
- Tests never touch the real `~/.improving-assistant`. `tests/conftest.py` isolates it. Tests never
  hit Workday or Engage.
- Skills must confirm with the user before submitting anything to Workday or Engage.
- Never type, store or log passwords or MFA codes. Sign-in is always done by the human.
- Keep `version` in `.claude-plugin/plugin.json` and `pyproject.toml` in sync, and add a
  CHANGELOG entry.
- When the Workday or Engage UI changes, update `docs/workday.md` or `docs/engage.md` in the
  same PR as the skill change.
- Holiday data lives in `data/holidays/<calendar>-<year>.toml`. Improving Guatemala uses the
  `us` calendar.
- `tests/test_repo_contract.py` enforces the manifests, skill frontmatter and required docs.
  If you add a required doc, add it there too.
