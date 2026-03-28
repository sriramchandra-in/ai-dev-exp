"""Skill registry."""

from ai_dev_exp.skills.base import FileBackedSkill, Skill

AVAILABLE_SKILLS: dict[str, Skill] = {
    "checkin": FileBackedSkill(
        "checkin",
        "Load codex-tree knowledge into AI sessions (Claude + Cursor digests, intent).",
    ),
    "github": FileBackedSkill(
        "github",
        "GitHub PR management, issue tracking, and code review workflows.",
    ),
    "deployment": FileBackedSkill(
        "deployment",
        "Deployment orchestration: CI/CD, environments, health checks, rollback.",
    ),
}

CURSOR_SKILLS: dict[str, Skill] = {
    "checkin": FileBackedSkill(
        "checkin",
        "Load codex-tree knowledge (Cursor-first; Claude digest fallback).",
        variant="cursor",
    ),
    "github": FileBackedSkill(
        "github",
        "GitHub workflows using Cursor terminal and project rules when present.",
        variant="cursor",
    ),
    "deployment": FileBackedSkill(
        "deployment",
        "Deployment orchestration from Cursor terminal; confirm risky steps in chat.",
        variant="cursor",
    ),
    "token-optimization": FileBackedSkill(
        "token-optimization",
        "Cursor token discipline: compaction, cursor/ digests, terminal ai-dev-exp reports.",
        variant="cursor",
    ),
    "usage-limits": FileBackedSkill(
        "usage-limits",
        "Cursor: terminal reports (cursor-context); plan limits in Cursor Settings.",
        variant="cursor",
    ),
}

__all__ = ["AVAILABLE_SKILLS", "CURSOR_SKILLS", "Skill"]
