"""Repository contract: plugin manifests, skills and required docs stay valid.

These run in CI so a contributor can't accidentally break installation."""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILLS = sorted(p for p in (REPO / "skills").iterdir() if p.is_dir()) if (REPO / "skills").exists() else []


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path} must start with YAML frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def test_plugin_manifest_is_valid():
    m = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    assert m["name"] == "improving-assistant"
    assert re.fullmatch(r"\d+\.\d+\.\d+", m["version"])


def test_marketplace_lists_this_plugin_from_repo_root():
    mk = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    assert mk["owner"]["name"]
    entry = next(p for p in mk["plugins"] if p["name"] == "improving-assistant")
    assert entry["source"] == "./"


def test_plugin_and_pyproject_versions_match():
    m = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    py = (REPO / "pyproject.toml").read_text()
    assert f'version = "{m["version"]}"' in py


def test_expected_skills_exist():
    assert {p.name for p in SKILLS} >= {"weekly-checkin", "engage-log"}


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_has_name_matching_folder_and_description(skill):
    fm = _frontmatter(skill / "SKILL.md")
    assert fm.get("name") == skill.name
    assert len(fm.get("description", "")) >= 20


@pytest.mark.parametrize("doc", [
    "README.md", "CLAUDE.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE",
    "docs/architecture.md", "docs/development.md", "docs/adding-a-skill.md",
    "docs/workday.md", "docs/engage.md", "docs/scheduler.md", "docs/holidays.md",
    "docs/decisions/0001-claude-code-plugin-with-os-scheduler.md",
    "docs/decisions/0002-red-green-tdd.md",
])
def test_required_docs_exist_and_are_not_empty(doc):
    p = REPO / doc
    assert p.exists(), f"missing {doc}"
    assert len(p.read_text(encoding="utf-8").strip()) > 100, f"{doc} is too short"


def test_claude_md_mandates_red_green():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8").lower()
    assert "red" in text and "green" in text and "failing test" in text
