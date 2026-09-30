# Contributing

Thanks for helping. Anyone at Improving can contribute: bug reports, holiday updates,
screen-map fixes when Workday or Engage change, and new automations.

## Ground rules

1. Development is RED -> GREEN -> REFACTOR, always. Write a failing test first, watch it
   fail, write the minimum code to pass, then clean up. This also applies to bug fixes: first
   a test that reproduces the bug. PRs that add behavior without a test that drove it will be
   asked to redo it. Details: docs/development.md and docs/decisions/0002-red-green-tdd.md.
2. Nothing submits to Workday or Engage without the user's explicit confirmation.
3. Never handle passwords or MFA codes in code, skills, logs or docs.
4. Runtime Python uses the standard library only, and must work on Linux, macOS and Windows.
5. AI agents working here follow CLAUDE.md. It has the same rules, written for agents.
6. This repo is public. Run `python3 scripts/check_secrets.py` before every push, and enable the
   hook once with `git config core.hooksPath .githooks`. Keep your own list of sensitive terms
   (client or colleague names) in `~/.improving-assistant/denylist.txt`, and never commit it. Use
   neutral examples like "Acme" in docs and tests.

## Workflow

1. Open an issue (or comment on one) describing the change.
2. Create a branch: `feat/...`, `fix/...`, `docs/...` or `holidays/...`.
3. Loop: RED (failing test) -> GREEN -> REFACTOR. Commit at green. It's good practice to show
   the RED step in the history, e.g. `test: ...` then `feat: ...`.
4. `uv run pytest` must be green. `claude plugin validate .` must pass if you touched the manifests.
5. Update docs in the same PR (README, docs/*, CHANGELOG.md).
6. Open a PR using the template. CI runs the test suite on Linux, macOS and Windows.

## Common contributions

- New year of holidays: docs/holidays.md
- Workday or Engage UI changed: update docs/workday.md or docs/engage.md, then the skill
- New automation: docs/adding-a-skill.md
- A significant design choice: add a short ADR in docs/decisions/

## Commit messages

Conventional-ish: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
