#!/usr/bin/env python3
"""Pre-push secret and personal-data scan (stdlib only). REQUIRED before every push.

    python3 scripts/check_secrets.py              # scan files tracked by git (+ gitleaks history)
    python3 scripts/check_secrets.py --paths DIR  # scan specific files or dirs

It fails (exit 1) on anything that looks like a credential or private key, a non-Improving email
address, or a term from your LOCAL denylist (client names, colleague names, anything personal).

The denylist is never committed, because a list of sensitive names would itself leak them. The
scan reads every one of these that exists:
  - $IA_DENYLIST (a file path)
  - ./.denylist                          (repo root, gitignored)
  - ~/.improving-assistant/denylist.txt
Format: one term per line, case-insensitive, `#` for comments.

When `gitleaks` is installed, it also scans the full git history.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}"),
    "AWS key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Anthropic/OpenAI key": re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}"),
    "Slack token": re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "password assignment": re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key)\s*[:=]\s*['\"][^'\"\s]{6,}['\"]"),
}
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
ALLOWED_EMAIL_DOMAINS = {"improving.com", "example.com", "users.noreply.github.com"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".lock", ".pyc"}
SKIP_NAMES = {"check_secrets.py", "test_secrets.py"}  # contain example patterns on purpose


def denylist_files() -> list[Path]:
    cands = [os.environ.get("IA_DENYLIST"), ".denylist",
             str(Path.home() / ".improving-assistant" / "denylist.txt")]
    return [Path(c) for c in cands if c and Path(c).is_file()]


def load_denylist() -> list[str]:
    terms: list[str] = []
    for f in denylist_files():
        terms += [l.strip() for l in f.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.lstrip().startswith("#")]
    return terms


def scan_text(name: str, text: str, deny: list[str]) -> list[str]:
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in PATTERNS.items():
            if rx.search(line):
                findings.append(f"{name}:{lineno}: {label}")
        for m in EMAIL.finditer(line):
            domain = m.group(1).lower()
            if not any(domain == d or domain.endswith("." + d) for d in ALLOWED_EMAIL_DOMAINS):
                findings.append(f"{name}:{lineno}: non-Improving email address")
        low = line.lower()
        for i, term in enumerate(deny, 1):
            if term.lower() in low:
                findings.append(f"{name}:{lineno}: denylisted term #{i}")  # never print the term
    return findings


def files_to_scan(paths: list[str] | None) -> list[Path]:
    if paths:
        out: list[Path] = []
        for p in map(Path, paths):
            out.extend([f for f in p.rglob("*") if f.is_file()] if p.is_dir() else [p])
        return out
    tracked = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout
    return [Path(f) for f in tracked.split("\0") if f]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Secret / personal-data scan")
    ap.add_argument("--paths", nargs="*", help="scan these files/dirs instead of git-tracked files")
    args = ap.parse_args(argv)

    deny = load_denylist()
    findings: list[str] = []
    for f in files_to_scan(args.paths):
        if f.name in SKIP_NAMES or f.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        findings += scan_text(str(f), text, deny)

    if not args.paths and shutil.which("gitleaks"):
        r = subprocess.run(["gitleaks", "git", "--redact", "--no-banner", "."], capture_output=True, text=True)
        if r.returncode != 0:
            findings.append("gitleaks: leaks found in git history (run `gitleaks git -v --redact .`)")

    if findings:
        print("Secret / personal-data check FAILED. Fix these before pushing:")
        print("\n".join(f"  {x}" for x in findings))
        return 1
    print(f"Secret / personal-data check passed ({len(deny)} denylist terms).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
