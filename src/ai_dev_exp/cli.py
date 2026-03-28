"""CLI entry point for ai-dev-exp."""

import json
from pathlib import Path

import click

from ai_dev_exp import __version__
from ai_dev_exp.anthropic_rate import build_snapshot, format_brief_line
from ai_dev_exp.cursor_context import format_brief, format_report_text, gather_snapshot
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


@main.command("cursor-context")
@click.option(
    "--path",
    "project_path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("."),
    help="Git project root (contains .codex-tree when using codex-tree).",
)
@click.option(
    "--format",
    "out_fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="text: human summary; json: machine-readable snapshot.",
)
@click.option(
    "--brief",
    is_flag=True,
    help="One line only (terminal status, Cursor status bar text, quick paste).",
)
def cursor_context(project_path: Path, out_fmt: str, brief: bool) -> None:
    """Print codex-tree staleness + token estimates to stdout.

    For Cursor’s terminal or PyCharm’s terminal. Measures repo context strategy
    (tree vs cursor digest vs raw), not Cursor subscription usage.
    Requires `codex-tree` on PATH and `.codex-tree/`.
    """
    snap = gather_snapshot(project_path)
    if out_fmt == "json":
        click.echo(json.dumps(snap, indent=2))
        return
    if brief:
        click.echo(format_brief(snap))
        return
    click.echo(format_report_text(snap))


@main.command("anthropic-rate-brief")
@click.option(
    "--format",
    "out_fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def anthropic_rate_brief(out_fmt: str) -> None:
    """Print Anthropic API rate-limit header summary to stdout (BYOK / API key).

    Run in Cursor’s terminal or PyCharm’s terminal. Not Cursor plan/billing usage.
    Sends a minimal Messages request (default Haiku). Requires ANTHROPIC_API_KEY.
    """
    snap = build_snapshot()
    if out_fmt == "json":
        click.echo(json.dumps(snap, indent=2))
        return
    click.echo(format_brief_line(snap))
