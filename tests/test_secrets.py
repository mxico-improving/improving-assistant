"""Secret / personal-data scanning: required before every push (see CLAUDE.md)."""

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCAN = REPO / "scripts" / "check_secrets.py"


def _scan(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCAN), "--paths", str(path)],
                          capture_output=True, text=True)


def test_pre_push_hook_exists_is_executable_and_runs_the_scan():
    hook = REPO / ".githooks" / "pre-push"
    assert hook.exists()
    if os.name != "nt":
        assert hook.stat().st_mode & stat.S_IXUSR
    assert "check_secrets.py" in hook.read_text()


def test_ci_runs_gitleaks_on_full_history():
    ci = (REPO / ".github" / "workflows" / "ci.yml").read_text()
    assert "gitleaks" in ci and "fetch-depth: 0" in ci


def test_claude_md_requires_secret_check_before_push():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8").lower()
    assert "check_secrets.py" in text and "before" in text and "push" in text


def test_scan_flags_personal_denylist_terms(tmp_path, monkeypatch):
    deny = tmp_path / "deny.txt"
    deny.write_text("# comment\nAcmeClientCorp\n")
    monkeypatch.setenv("IA_DENYLIST", str(deny))
    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").write_text("my project row is acmeclientcorp: Software Development\n")

    r = _scan(src)

    assert r.returncode == 1
    assert "doc.md" in r.stdout
    assert "acmeclientcorp" not in r.stdout.lower()  # never echo the sensitive term itself


def test_denylist_is_not_tracked_in_the_repo():
    assert not (REPO / "scripts" / "denylist.txt").exists()
    assert ".denylist" in (REPO / ".gitignore").read_text()


def test_scan_flags_non_improving_email(tmp_path):
    (tmp_path / "x.md").write_text("contact someone@gmail.com\n")

    assert _scan(tmp_path).returncode == 1


def test_scan_flags_private_key_and_token_like_strings(tmp_path):
    (tmp_path / "a.txt").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n")
    (tmp_path / "b.txt").write_text("token = ghp_" + "a" * 36 + "\n")

    r = _scan(tmp_path)

    assert r.returncode == 1 and "a.txt" in r.stdout and "b.txt" in r.stdout


def test_scan_passes_clean_content(tmp_path):
    (tmp_path / "ok.md").write_text("Project row: Acme: Software Development > Project > Time Entry\n"
                                    "maintainer: mynor.xico@improving.com\n")

    r = _scan(tmp_path)

    assert r.returncode == 0, r.stdout


def test_repository_itself_is_clean():
    r = subprocess.run([sys.executable, str(SCAN)], capture_output=True, text=True, cwd=REPO)

    assert r.returncode == 0, r.stdout
