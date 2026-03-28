"""Base skill interface."""

from abc import ABC, abstractmethod
from pathlib import Path


class Skill(ABC):
    """Base class for all AI developer experience skills.

    Each skill provides a SKILL.md that defines behavior for an AI assistant,
    plus optional tooling for installation and configuration.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what the skill does."""

    @abstractmethod
    def skill_markdown(self) -> str:
        """Return the SKILL.md content that defines this skill's behavior."""

    def install(self, target: str | None = None) -> Path:
        """Install the skill's SKILL.md to the target directory.

        Default target: .claude/skills/{name}/SKILL.md (project-level)
        """
        if target is None:
            target_dir = Path.cwd() / ".claude" / "skills" / self.name
        else:
            target_dir = Path(target) / ".claude" / "skills" / self.name

        target_dir.mkdir(parents=True, exist_ok=True)
        skill_file = target_dir / "SKILL.md"
        skill_file.write_text(self.skill_markdown())
        return skill_file
