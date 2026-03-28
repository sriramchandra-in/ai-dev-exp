"""Skill registry."""

from ai_dev_exp.skills.base import Skill
from ai_dev_exp.skills.checkin import CheckinSkill
from ai_dev_exp.skills.github import GitHubSkill
from ai_dev_exp.skills.deployment import DeploymentSkill

AVAILABLE_SKILLS: dict[str, Skill] = {
    "checkin": CheckinSkill(),
    "github": GitHubSkill(),
    "deployment": DeploymentSkill(),
}

__all__ = ["AVAILABLE_SKILLS", "Skill"]
