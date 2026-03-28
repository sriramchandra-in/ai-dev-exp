"""Tests for skill registry and installation."""

from pathlib import Path

from ai_dev_exp.skills import AVAILABLE_SKILLS
from ai_dev_exp.skills.base import Skill


def test_all_skills_registered():
    assert "checkin" in AVAILABLE_SKILLS
    assert "github" in AVAILABLE_SKILLS
    assert "deployment" in AVAILABLE_SKILLS


def test_skills_are_skill_instances():
    for skill in AVAILABLE_SKILLS.values():
        assert isinstance(skill, Skill)


def test_skills_have_required_properties():
    for name, skill in AVAILABLE_SKILLS.items():
        assert skill.name == name
        assert len(skill.description) > 0
        assert len(skill.skill_markdown()) > 0


def test_skill_markdown_has_frontmatter():
    for skill in AVAILABLE_SKILLS.values():
        md = skill.skill_markdown()
        assert md.startswith("---"), f"{skill.name} SKILL.md missing frontmatter"
        assert "name:" in md
        assert "description:" in md


def test_install_creates_skill_file(tmp_path: Path):
    skill = AVAILABLE_SKILLS["checkin"]
    skill_file = skill.install(str(tmp_path))
    assert skill_file.exists()
    assert skill_file.name == "SKILL.md"
    assert "checkin" in skill_file.read_text()
