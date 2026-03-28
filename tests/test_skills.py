"""Tests for skill registry and installation."""

from pathlib import Path

import pytest

from ai_dev_exp.skills import AVAILABLE_SKILLS, CURSOR_SKILLS
from ai_dev_exp.skills.base import Skill


def test_all_skills_registered():
    assert "checkin" in AVAILABLE_SKILLS
    assert "github" in AVAILABLE_SKILLS
    assert "deployment" in AVAILABLE_SKILLS


def test_cursor_skills_registered():
    assert "checkin" in CURSOR_SKILLS
    assert "github" in CURSOR_SKILLS
    assert "deployment" in CURSOR_SKILLS
    assert "token-optimization" in CURSOR_SKILLS


def test_skills_are_skill_instances():
    for skill in AVAILABLE_SKILLS.values():
        assert isinstance(skill, Skill)
    for skill in CURSOR_SKILLS.values():
        assert isinstance(skill, Skill)


def test_skills_have_required_properties():
    for name, skill in AVAILABLE_SKILLS.items():
        assert skill.name == name
        assert len(skill.description) > 0
        assert len(skill.skill_markdown()) > 0
        assert skill.variant == "claude"
    for name, skill in CURSOR_SKILLS.items():
        assert skill.name == name
        assert len(skill.description) > 0
        assert len(skill.skill_markdown()) > 0
        assert skill.variant == "cursor"


def test_skill_markdown_has_frontmatter():
    for skill in list(AVAILABLE_SKILLS.values()) + list(CURSOR_SKILLS.values()):
        md = skill.skill_markdown()
        assert md.startswith("---"), f"{skill.name} SKILL.md missing frontmatter"
        assert "name:" in md
        assert "description:" in md


def test_install_creates_skill_file(tmp_path: Path):
    skill = AVAILABLE_SKILLS["checkin"]
    skill_file = skill.install(str(tmp_path))
    assert skill_file.exists()
    assert skill_file.name == "SKILL.md"
    assert "checkin" in skill_file.read_text(encoding="utf-8")
    out = tmp_path / ".claude" / "skills" / "checkin" / "SKILL.md"
    assert out == skill_file


def test_install_cursor_writes_dot_cursor(tmp_path: Path):
    skill = CURSOR_SKILLS["token-optimization"]
    skill_file = skill.install(str(tmp_path))
    assert skill_file.exists()
    assert (tmp_path / ".cursor" / "skills" / "token-optimization" / "reference.md").is_file()


@pytest.mark.parametrize("name", ["checkin", "github", "deployment", "token-optimization"])
def test_cursor_skill_install_roundtrip(tmp_path: Path, name: str):
    skill = CURSOR_SKILLS[name]
    skill.install(str(tmp_path))
    md = (tmp_path / ".cursor" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    assert len(md) > 50
