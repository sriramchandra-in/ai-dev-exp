"""Resolve bundled skill markdown (wheel) or repo-root `claude/` / `cursor/` (editable)."""

from pathlib import Path


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    """Project root when installed editable (`src/ai_dev_exp` → repo)."""
    return _package_dir().parent.parent


def skills_root(variant: str) -> Path:
    """Directory containing `<skill-name>/SKILL.md` for `claude` or `cursor`."""
    bundled = _package_dir() / "_bundled" / variant / "skills"
    if bundled.is_dir():
        return bundled
    return repo_root() / variant / "skills"


def skill_dir(variant: str, name: str) -> Path:
    return skills_root(variant) / name
