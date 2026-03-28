---
name: checkin
description: >-
  Load the codex-tree knowledge tree for Cursor (Chat / Composer / Agent) using
  `.codex-tree/cursor/` digests. Use at the start of every session or when
  switching projects.
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

3. **Load context** — In **Cursor**, use **`.codex-tree/cursor/`** and pick the depth tier:

   - Quick orientation / small edits: `.codex-tree/cursor/l1.md`
   - Feature work (APIs, imports, patterns in L2): `.codex-tree/cursor/l2.md`
   - Refactors / architecture (full symbols, imports/exports): `.codex-tree/cursor/l3.md`

   Use **`@`** to attach files, respect **`.cursor/rules`**, and escalate digest tier when the task needs more structure.

   If **`cursor/`** is missing (e.g. tree built with `--no-cursor`) but another digest directory exists under `.codex-tree/`, use its **`l1.md` / `l2.md` / `l3.md`** for the same tier (structure matches; preambles differ).

   **If neither digest exists** — fall back to `tree.json` plus key `modules/{path}/index.json` files.

   Reading or generating these digests needs **no API key** (intent layer is separate).

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

Heuristic token estimates vs reading all indexed source. In Cursor, prioritize **Tree + Cursor** (digest `cursor/l2.md` or `l1.md`).

- **Nothing (raw source only)** — baseline.
- **Tree only** — `tree.json` + all `modules/**/index.json`.
- **Tree + Cursor** — tree plus `cursor/l2.md` (or `l1.md` if L2 missing).

JSON (`--format json`) includes multiple strategies; for Cursor automation use **`tree_plus_cursor_tokens`**, **`cursor_digest_used`**, **`savings_tree_plus_cursor`** (e.g. `ai-dev-exp cursor-context`).

### Flags by command

**init / regen:**
- `--no-intent` — skip optional semantic intent layer (AST-only trees need no remote analysis key)
- `--no-claude` — skip non-Cursor digest export (codex-tree flag; directory name is tool-defined)
- `--no-cursor` — skip `.codex-tree/cursor/` digest layer
- `--languages <list>` — comma-separated languages to parse (default: all supported)
- `--dry-run` — show what would be generated without writing (init only)

**update:**
- `--no-intent` — skip intent analysis for changed files
- `--no-claude` — skip non-Cursor digest regeneration
- `--no-cursor` — skip Cursor digest regeneration
- `--no-compact` — skip auto-compaction even if thresholds are met

**check:**
- `--format json` — machine-readable output
- `--fail-if-stale` — exit code 1 if any files are stale (useful in CI)

**report:**
- `--format json` — machine-readable output (includes multi-strategy `token_estimate`)
- `-q/--quiet` — suppresses report text (useful when only exit status matters)

**Global:** `--path <dir>` (default: `.`), `-v/--verbose`, `-q/--quiet`

### Environment variables (optional intent layer)

| Variable | Required | Purpose |
|----------|----------|---------|
| See **codex-tree** docs | — | Optional keys / model / budget **only** if you generate the **intent** layer. Not used for markdown digests under `cursor/`. |

Markdown digests under **`.codex-tree/cursor/`** are built **locally** without those keys. **Cursor billing** for in-editor AI is separate (Cursor account / settings).

## Tree structure reference

```
.codex-tree/
  version.json          # Tree version (generation.delta_count), stats, source_commit
  tree.json             # Top-level structure map (files + directories with aggregate counts)
  modules/{path}/       # Per-file structural detail
    index.json          #   symbols, imports, exports, content_hash (SHA-256)
  intent/               # Optional semantic layer (see codex-tree docs)
    decisions.json
    patterns.json
    .cache/
  cursor/               # Cursor digest (local markdown, no editor API)
    l1.md
    l2.md
    l3.md
  …                     # Other generator outputs may exist; prefer cursor/ in Cursor
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
