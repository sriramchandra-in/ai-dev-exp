---
name: checkin
description: >-
  Load the codex-tree knowledge tree into the AI session for instant codebase
  context (Cursor primary; Claude digest equivalent). Use at the start of every
  conversation or when switching projects.
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

3. **Load context** — Pick the digest path for the environment, then the depth tier:

   **In Cursor (Chat / Composer / Agent)** — prefer `.codex-tree/cursor/`:
   - Quick orientation / small edits: `.codex-tree/cursor/l1.md` (~500 tokens of structure + Cursor preamble)
   - Feature work (public APIs, imports, intent patterns in L2): `cursor/l2.md` (~2,000 tokens)
   - Refactors / architecture (all symbols, decisions, import/export detail): `cursor/l3.md`
   - These files mirror the **same structural body** as `claude/l*.md`; only the opening
     **Cursor usage guide** differs (e.g. `@` file attachment, `.cursor/rules`, when to escalate).
   - If `cursor/` is missing (e.g. tree built with `--no-cursor`) but `claude/` exists, use
     `.codex-tree/claude/l1.md` / `l2.md` / `l3.md` instead — content is aligned.

   **In Claude Code / Anthropic clients** — prefer `.codex-tree/claude/`:
   - Quick tasks / Haiku: `claude/l1.md`
   - Implementation / Sonnet: `claude/l2.md`
   - Architecture / Opus: `claude/l3.md`
   - If `claude/` is missing but `cursor/` exists, use `cursor/l*.md` (skip the preamble if you want only structure).

   **If neither digest exists** — fall back to `tree.json` for overview + key
   `modules/{path}/index.json` files for detail.

   **No extra API key** is required to read or generate `cursor/` or `claude/`; both are produced
   locally from the AST tree plus optional cached intent JSON.

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
| `codex-tree report` | Estimated tokens: raw vs tree vs tree+cursor digest |

### `codex-tree report` output

Text mode prints **context strategies** (heuristic token estimates vs reading all indexed source):

- **Nothing (raw source only)** — baseline; no codex-tree context.
- **Tree only** — `tree.json` + all `modules/**/index.json`.
- **Tree + Claude** — tree plus `claude/l2.md` (or `l1.md` if L2 missing).
- **Tree + Cursor** — tree plus `cursor/l2.md` (or `l1.md` if L2 missing).

Each line includes **% vs raw** (savings vs baseline). JSON (`--format json`) exposes
`token_estimate.just_tree_tokens`, `tree_plus_claude_tokens`, `claude_digest_used`,
`tree_plus_cursor_tokens`, `cursor_digest_used`,
`savings_just_tree`, `savings_tree_plus_claude`, `savings_tree_plus_cursor`,
plus legacy module-only fields.

### Flags by command

**init / regen:**
- `--no-intent` — skip AI intent layer (no `ANTHROPIC_API_KEY` needed for AST-only trees)
- `--no-claude` — skip Claude digest layer (`claude/l1.md`–`l3.md`)
- `--no-cursor` — skip Cursor digest layer (`cursor/l1.md`–`l3.md`; same structure as Claude + Cursor preamble)
- `--languages <list>` — comma-separated languages to parse (default: all supported)
- `--dry-run` — show what would be generated without writing (init only)

**update:**
- `--no-intent` — skip AI intent analysis for changed files
- `--no-claude` — skip Claude layer regeneration
- `--no-cursor` — skip Cursor layer regeneration
- `--no-compact` — skip auto-compaction even if thresholds are met

**check:**
- `--format json` — machine-readable output
- `--fail-if-stale` — exit code 1 if any files are stale (useful in CI)

**report:**
- `--format json` — machine-readable output (includes multi-strategy `token_estimate`)
- `-q/--quiet` — suppresses report text (useful when only exit status matters)

**Global:** `--path <dir>` (default: `.`), `-v/--verbose`, `-q/--quiet`

### Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | For intent layer only | — | Claude API authentication (intent JSON). Not used for `claude/` or `cursor/` markdown. |
| `CODEX_TREE_MODEL` | No | `claude-sonnet-4-20250514` | Model for intent analysis |
| `CODEX_TREE_BUDGET` | No | Unlimited | Max tokens for intent API calls |

There is **no codex-tree integration with a “Cursor API key”** — Cursor digest files are built on disk like Claude’s. Using Cursor’s own in-editor AI is separate (Cursor account / optional BYOK in app settings).

Without `ANTHROPIC_API_KEY`, the **intent** layer is skipped with a warning (not an error).
`claude/` and `cursor/` still generate without any API key.

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
  claude/               # Claude-oriented digest (optional, generated locally, no API)
    l1.md               #   ~500 tokens — stats, architecture, entry points, key types
    l2.md               #   ~2K tokens  — L1 + per-module symbols, dependency graph, patterns
    l3.md               #   full detail — L2 + all symbols, full decisions, import/export manifests
  cursor/               # Same structural digest + Cursor usage preamble (optional, local, no API)
    l1.md               #   align with claude/l1.md body; front matter + Cursor how-to
    l2.md               #   align with claude/l2.md
    l3.md               #   align with claude/l3.md
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
