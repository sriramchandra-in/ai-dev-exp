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
   SHA-256 content hashes per file, and classifies each as:
   - `Modified` — content hash mismatch (file changed since tree was generated)
   - `Untracked` — file exists on disk but has no module index
   - `Deleted` — module index exists but file is gone
   The JSON output includes `commits_behind`, `stale_files`, `clean_files`, and `is_stale`.
   - If stale: suggest `codex-tree update` to refresh incrementally.
   - Note stale files for lazy raw-source exploration.

3. **Load context** — Read the appropriate detail level based on the task and model:
   - Quick tasks / Haiku: load `.codex-tree/claude/l1.md` (~500 tokens)
   - Implementation / Sonnet: load `.codex-tree/claude/l2.md` (~2,000 tokens)
   - Architecture / Opus: load `.codex-tree/claude/l3.md` (full detail)
   - If `claude/` layer doesn't exist (generated with `--no-claude`), fall back to
     `tree.json` for the overview + key `modules/{path}/index.json` files for detail.

4. **Load intent** — If `.codex-tree/intent/` exists, read it for deeper understanding:
   - `intent/decisions.json` — design decisions anchored to specific files/symbols,
     with confidence scores (0.0–1.0) and provenance markers.
   - `intent/patterns.json` — cross-cutting design patterns observed across the codebase.
   - **Confidence guide:**
     - 0.7–1.0: trust directly (extracted from docs or high-certainty inference)
     - 0.4–0.6: plausible but verify against source before acting on it
     - 0.1–0.3: speculative — treat as a hypothesis, not a fact
   - **Provenance types:** `extracted_from_docs`, `extracted_from_commit`,
     `inferred_from_code`, `human_annotated`
   - Intent results are cached by content hash — re-running with unchanged files is free.
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
| `codex-tree regen` | Full rebuild (new generation, increments counter) |
| `codex-tree check` | Staleness report (clean vs stale files) |
| `codex-tree report` | Token savings and tree statistics |

### Flags by command

**init / regen:**
- `--no-intent` — skip AI intent layer (no API key needed)
- `--no-claude` — skip Claude optimization layer
- `--languages <list>` — comma-separated languages to parse (default: all supported)
- `--dry-run` — show what would be generated without writing (init only)

**update:**
- `--no-intent` — skip AI intent analysis for changed files
- `--no-claude` — skip Claude layer regeneration
- `--no-compact` — skip auto-compaction even if thresholds are met

**check:**
- `--format json` — machine-readable output
- `--fail-if-stale` — exit code 1 if any files are stale (useful in CI)

**report:**
- `--format json` — machine-readable output

**Global:** `--path <dir>` (default: `.`), `-v/--verbose`, `-q/--quiet`

### Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | For intent layer | — | Claude API authentication |
| `CODEX_TREE_MODEL` | No | `claude-sonnet-4-20250514` | Model for intent analysis |
| `CODEX_TREE_BUDGET` | No | Unlimited | Max tokens for intent API calls |

Without `ANTHROPIC_API_KEY`, intent/claude layers are skipped with a warning (not an error).

## Tree structure reference

```
.codex-tree/
  version.json          # Tree version (generation.delta_count), stats, source_commit
  tree.json             # Top-level structure map (files + directories with aggregate counts)
  modules/{path}/       # Per-file structural detail
    index.json          #   symbols, imports, exports, content_hash (SHA-256)
  intent/               # AI-generated semantic layer (optional, needs API key)
    decisions.json      #   design decisions with confidence + provenance
    patterns.json       #   cross-cutting patterns
    .cache/             #   content-hash-based cache (avoids redundant API calls)
  claude/               # Claude-optimized summaries (optional, generated locally)
    l1.md               #   ~500 tokens — stats, architecture, entry points, key types
    l2.md               #   ~2K tokens  — L1 + per-module symbols, dependency graph, patterns
    l3.md               #   full detail — L2 + all symbols, full decisions, import/export manifests
  deltas/               # Incremental updates (auto-compacted at 10 deltas or 100KB)
```

### Compaction

Deltas are auto-compacted when either threshold is met:
- **10 deltas** accumulated, OR
- **100 KB** total delta size

Compaction folds all deltas into the base tree and resets the counter.
Use `--no-compact` on `update` to defer compaction (e.g., during rapid iteration).

### Excluded directories

`init` and `regen` skip: `.git`, `target`, `.codex-tree`, `node_modules`,
`__pycache__`, `.venv`, `vendor`, `dist`, `build`.

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
