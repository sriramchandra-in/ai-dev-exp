"""Base skill interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

from ai_dev_exp.paths import skill_dir

Variant = Literal["claude", "cursor"]


class Skill(ABC):
    """Each skill provides SKILL.md (and optional reference.md) for an AI assistant."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what the skill does."""

    @property
    def variant(self) -> Variant:
        """Which bundled tree (`claude/` or `cursor/`) this skill reads from."""
        return "claude"

    @abstractmethod
    def skill_markdown(self) -> str:
        """Return the SKILL.md content that defines this skill's behavior."""

    def skill_source_path(self) -> Path:
        return skill_dir(self.variant, self.name)

    def install(self, target: str | None = None) -> Path:
        """Copy SKILL.md (and reference.md if present) into the assistant layout."""
        dest_base = Path(target) if target else Path.cwd()
        if self.variant == "cursor":
            out_dir = dest_base / ".cursor" / "skills" / self.name
        else:
            out_dir = dest_base / ".claude" / "skills" / self.name

        out_dir.mkdir(parents=True, exist_ok=True)
        src = self.skill_source_path()
        skill_file = out_dir / "SKILL.md"
        skill_file.write_text(self.skill_markdown(), encoding="utf-8")
        ref = src / "reference.md"
        if ref.is_file():
            (out_dir / "reference.md").write_text(ref.read_text(encoding="utf-8"), encoding="utf-8")
        return skill_file


class FileBackedSkill(Skill):
    """Skill whose body lives in `claude/skills/<name>/` or `cursor/skills/<name>/`."""

    def __init__(self, name: str, description: str, *, variant: Variant = "claude") -> None:
        self._name = name
        self._description = description
        self._variant: Variant = variant

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def variant(self) -> Variant:
        return self._variant

    def skill_markdown(self) -> str:
        path = self.skill_source_path() / "SKILL.md"
        if not path.is_file():
            msg = f"Missing skill file: {path}"
            raise FileNotFoundError(msg)
        return path.read_text(encoding="utf-8")
