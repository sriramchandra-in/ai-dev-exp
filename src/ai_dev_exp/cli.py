"""CLI entry point for ai-dev-exp."""

import click

from ai_dev_exp import __version__
from ai_dev_exp.skills import AVAILABLE_SKILLS, CURSOR_SKILLS


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """AI developer experience skills for coding assistants."""


@main.command("list")
def list_skills() -> None:
    """List all available skills."""
    click.echo("Claude bundle → installs under .claude/skills/:\n")
    for name, skill in AVAILABLE_SKILLS.items():
        click.echo(f"  {name:20s} {skill.description}")
    click.echo("\nCursor bundle → installs under .cursor/skills/:\n")
    for name, skill in CURSOR_SKILLS.items():
        click.echo(f"  {name:20s} {skill.description}")


@main.command()
@click.argument("skill_name", required=False)
@click.option("--target", default=None, help="Target directory for skill installation")
@click.option(
    "--cursor",
    is_flag=True,
    help="Use the Cursor skill tree (installs under .cursor/skills/).",
)
def install(skill_name: str | None, target: str | None, cursor: bool) -> None:
    """Install skills into your AI coding assistant environment."""
    registry = CURSOR_SKILLS if cursor else AVAILABLE_SKILLS
    dest = target or "."

    if skill_name is None:
        for name, skill in registry.items():
            skill.install(target)
            click.echo(f"  Installed: {name}")
        click.echo(f"\n{len(registry)} skills installed to {dest}.")
        return

    if skill_name not in registry:
        if not cursor and skill_name in CURSOR_SKILLS:
            click.echo(
                f"Skill {skill_name!r} is in the Cursor bundle only. "
                f"Try: ai-dev-exp install {skill_name} --cursor",
                err=True,
            )
        else:
            click.echo(f"Unknown skill: {skill_name}", err=True)
            click.echo(f"Available: {', '.join(registry.keys())}", err=True)
        raise SystemExit(1)

    registry[skill_name].install(target)
    click.echo(f"Installed: {skill_name}")
