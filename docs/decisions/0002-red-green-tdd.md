# ADR 0002: Strict RED -> GREEN -> REFACTOR development

Status: accepted (2026-09-29)

## Context
This tool submits data about people's work hours and attendance under their identity. Mistakes
such as wrong hours, a missed holiday, or a full-week entry during PTO have real consequences.
The contributors are many, occasional, and often AI agents.

## Decision
All behavior changes follow test-driven development:
1. RED: write one failing test and confirm it fails for the expected reason.
2. GREEN: write the minimal code to pass it, and keep the whole suite green.
3. REFACTOR: clean up without changing behavior.

Bug fixes start with a test that reproduces the bug. Rules live in tested Python (`src/`), not
in skill prompts. `tests/test_repo_contract.py` guards the manifests, skills and required docs.
CLAUDE.md states the same rule for AI agents.

## Consequences
- Slightly slower first commits, but reliable behavior for every teammate, every week.
- Browser steps can't be unit-tested, so they are kept thin and documented in screen maps.
