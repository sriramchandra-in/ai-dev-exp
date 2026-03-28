"""Checkin skill — loads codex-tree knowledge into AI sessions."""

from pathlib import Path

from ai_dev_exp.skills.base import Skill

SKILL_MD = """\
---
name: checkin
description: >-
  Load the codex-tree knowledge tree into the AI session for instant codebase
  context. Use at the start of every conversation or when switching projects.
---

# Checkin

## When to apply

At the start of any coding session, or when the user switches to a new project directory.

## Workflow

1. **Detect tree** — Check if `.codex-tree/` exists in the project root.
   - If missing: inform the user and suggest `codex-tree init`.
   - If present: proceed to step 2.

2. **Check staleness** — Compare `.codex-tree/version.json` source_commit against current HEAD.
   - Run `git status --porcelain` to detect uncommitted changes.
   - If stale files exist, note them for lazy exploration.

3. **Load context** — Read the appropriate detail level based on the task:
   - Quick tasks / Haiku: load `.codex-tree/claude/l1.md` (~500 tokens)
   - Implementation / Sonnet: load `.codex-tree/claude/l2.md` (~2,000 tokens)
   - Architecture / Opus: load `.codex-tree/claude/l3.md` (full detail)
   - If claude/ layer doesn't exist, fall back to `tree.json` + key module indexes.

4. **Establish understanding** — Summarize what you know about the project in 2-3 sentences.
   Store this understanding for the duration of the session.

5. **Flag gaps** — For stale or missing files, note that you'll explore the raw source
   when those areas become relevant.

## Lazy exploration

The knowledge tree is a starting point, not a complete picture. When working on a specific
module:
- Load its `modules/{path}/index.json` for detailed symbols
- If the file is flagged stale, read the raw source instead
- If the intent layer exists, use it for understanding *why* things are structured the way they are

## Output

After checkin, briefly confirm:
```
Loaded codex-tree (v{version}): {file_count} files, {symbol_count} symbols.
{stale_count} files changed since tree was generated — will explore those on demand.
```
"""


class CheckinSkill(Skill):
    @property
    def name(self) -> str:
        return "checkin"

    @property
    def description(self) -> str:
        return "Load codex-tree knowledge into AI sessions for instant codebase context"

    def skill_markdown(self) -> str:
        return SKILL_MD
