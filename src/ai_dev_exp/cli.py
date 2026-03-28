"""CLI entry point for ai-dev-exp."""

import click

from ai_dev_exp import __version__
from ai_dev_exp.skills import AVAILABLE_SKILLS


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """AI developer experience skills for coding assistants."""


@main.command()
def list() -> None:
    """List all available skills."""
    click.echo("Available skills:\n")
    for name, skill in AVAILABLE_SKILLS.items():
        click.echo(f"  {name:15s} {skill.description}")


@main.command()
@click.argument("skill_name", required=False)
@click.option("--target", default=None, help="Target directory for skill installation")
def install(skill_name: str | None, target: str | None) -> None:
    """Install skills into your AI coding assistant environment."""
    if skill_name is None:
        # Install all skills
        for name, skill in AVAILABLE_SKILLS.items():
            skill.install(target)
            click.echo(f"  Installed: {name}")
        click.echo(f"\n{len(AVAILABLE_SKILLS)} skills installed.")
    else:
        if skill_name not in AVAILABLE_SKILLS:
            click.echo(f"Unknown skill: {skill_name}", err=True)
            click.echo(f"Available: {', '.join(AVAILABLE_SKILLS.keys())}", err=True)
            raise SystemExit(1)
        AVAILABLE_SKILLS[skill_name].install(target)
        click.echo(f"Installed: {skill_name}")


if __name__ == "__main__":
    main()
