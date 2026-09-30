# Development

## Setup

    git clone https://github.com/mxico-improving/improving-assistant.git
    cd improving-assistant
    uv sync            # installs pytest into .venv (install uv: https://docs.astral.sh/uv/)
    uv run pytest

Without uv: `python3 -m venv .venv && . .venv/bin/activate && pip install pytest && pytest`.

## RED -> GREEN -> REFACTOR

This is the only accepted way to change behavior here (see ADR 0002).

    # 1. RED: add one test and watch it fail for the right reason
    uv run pytest tests/test_week_plan.py::test_new_behavior
    #    If it fails on ImportError or NameError, add a stub that raises NotImplementedError
    #    so it fails on behavior instead.

    # 2. GREEN: write the minimal code, then run everything
    uv run pytest

    # 3. REFACTOR with the suite green, then commit

Tips:
- Test behavior through public functions or the CLI (`cli.main([...])`), not internals.
- Use `tmp_path` for files. `conftest.py` already redirects `IMPROVING_ASSISTANT_HOME`.
- OS-specific code: test the generated command or file content for each OS. Don't actually run
  `systemctl`, `launchctl` or `schtasks` in tests (use `--no-activate`).
- Skills and browser flows aren't unit-testable. Keep logic out of them and put it in `src/`
  where it can be tested. `tests/test_repo_contract.py` checks their structure.

## Try the plugin locally

    claude --plugin-dir .          # load this checkout as a plugin in Claude Code
    claude plugin validate .       # check manifests

## Releasing

1. Bump `version` in both `.claude-plugin/plugin.json` and `pyproject.toml` (a test enforces this).
2. Move the CHANGELOG "Unreleased" entries under the new version.
3. Merge to `main` and tag `vX.Y.Z`. Users get it with `/plugin marketplace update`.
