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

2. **Check staleness** — Run `codex-tree check --format json` for a machine-readable
   staleness report. This compares `version.json` source_commit against HEAD, verifies
   content hashes per file, and reports which files are clean vs stale vs untracked.
   - If stale files exist, suggest `codex-tree update` to refresh.
   - Note stale files for lazy raw-source exploration.

3. **Load context** — Read the appropriate detail level based on the task and model:
   - Quick tasks / Haiku: load `.codex-tree/claude/l1.md` (~500 tokens)
   - Implementation / Sonnet: load `.codex-tree/claude/l2.md` (~2,000 tokens)
   - Architecture / Opus: load `.codex-tree/claude/l3.md` (full detail)
   - If `claude/` layer doesn't exist (generated with `--no-claude`), fall back to
     `tree.json` for the overview + key `modules/{path}/index.json` files for detail.

4. **Load intent** — If `.codex-tree/intent/` exists, read it for deeper understanding:
   - `intent/decisions.json` — design decisions anchored to specific files/symbols,
     with confidence scores (0.0–1.0) and provenance (inferred_from_code, extracted_from_docs, etc.)
   - `intent/patterns.json` — cross-cutting design patterns observed across the codebase.
   - Trust decisions with confidence >= 0.7. For lower confidence, verify against source.
   - If intent layer doesn't exist (generated with `--no-intent`), rely on AST layer only.

5. **Establish understanding** — Summarize what you know about the project in 2-3 sentences.
   Store this understanding for the duration of the session.

6. **Flag gaps** — For stale or missing files, note that you'll explore the raw source
   when those areas become relevant.

## Lazy exploration

The knowledge tree is a starting point, not a complete picture. When working on a specific
module:
- Load its `modules/{path}/index.json` for detailed symbols, imports, and exports
- If the file is flagged stale by `codex-tree check`, read the raw source instead
- If the intent layer exists, consult `decisions.json` for *why* things are structured
  the way they are — but always verify low-confidence insights against the code

## CLI commands reference

These commands are available when `codex-tree` is installed:

| Command | Purpose |
|---------|---------|
| `codex-tree init` | Generate `.codex-tree/` from scratch |
| `codex-tree update` | Incremental delta from git changes |
| `codex-tree regen` | Full rebuild (new generation) |
| `codex-tree check` | Staleness report (clean vs stale files) |
| `codex-tree report` | Token savings and tree statistics |

Key flags:
- `--no-intent` — skip AI intent layer (no API key needed)
- `--no-claude` — skip Claude optimization layer
- `--format json` — machine-readable output (check, report)
- `--fail-if-stale` — exit code 1 if stale (useful in CI)

## Tree structure reference

```
.codex-tree/
  version.json          # Tree version (generation.delta_count), stats
  tree.json             # Top-level structure map (files + directories)
  modules/{path}/       # Per-file structural detail
    index.json          #   symbols, imports, exports, content_hash
  intent/               # AI-generated semantic layer (optional)
    decisions.json      #   design decisions with confidence + provenance
    patterns.json       #   cross-cutting patterns
  claude/               # Claude-optimized summaries (optional)
    l1.md               #   ~500 tokens — project overview
    l2.md               #   ~2,000 tokens — module detail
    l3.md               #   full detail
  deltas/               # Incremental updates (auto-compacted)
```

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
