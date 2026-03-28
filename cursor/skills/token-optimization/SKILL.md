---
name: token-optimization
description: >-
  Optimizes Cursor sessions: shallow context, compaction, codex-tree
  `.codex-tree/cursor/` digests, and terminal reports via ai-dev-exp. Use when
  the user mentions tokens, context limits, compaction, cost, or keeping Cursor
  chats lean; or before huge reads and redundant paste.
---

# Token optimization (Cursor)

## Who this is for

You are assisting someone working in **Cursor** (Chat / Composer / Agent). **Terminal reports** for this repo use **`ai-dev-exp`** from the **Cursor integrated terminal** or **PyCharm’s terminal** (same shell commands).

**Packaging:** **ai-dev-exp** → `cursor/skills/token-optimization/`. Install with `ai-dev-exp install --cursor`. Keep the **workspace root** on the repo being edited.

## Terminal reports (no Cursor UI API)

Run from the **project git root**:

```bash
# Repo context strategy (needs codex-tree + .codex-tree/)
ai-dev-exp cursor-context
ai-dev-exp cursor-context --brief
ai-dev-exp cursor-context --format json
```

**Cursor subscription / Composer quotas** are only in **Cursor Settings**; this bundle does not add other usage CLIs.

## Cursor editor habits

- Use **native code citations** (path + line range).
- Prefer **Cursor’s terminal** (or PyCharm terminal with the same env) for the commands above.

## When to apply

- User asks to save tokens, compact context, lower cost, or keep replies small.
- Session is long, many large files, or the thread is noisy with resolved work.

## Context window compaction

**When appropriate**, shrink active context before limits bite.

- Offer a **short handoff**: goal, constraints, files touched, open questions; drop stale tool dumps.
- Suggest **Cursor’s** compact / clear / new-chat flows when the product provides them; then continue from the summary.
- **New scope → new chat** when history is unrelated; carry one short paragraph forward only.
- After compaction, **don’t re-paste** large blobs unless needed.

## Defaults (in order)

1. **Assume competence** — Short plans, direct edits.

2. **Progressive disclosure** — Search hits first; narrow `read` windows on large files.

3. **Search before read** — Avoid serial full-file reads “to understand.”

4. **One-shot tool batches** — Parallel independent lookups (see **API aggregation** in reference).

5. **Compact outputs** — Summarize; cite instead of pasting whole files.

6. **No noise** — Skip lockfiles, `node_modules`, minified bundles, unless required.

## API and orchestration (patterns)

For **scripts and services** you integrate (not Cursor’s hidden billing). Provider-specific details: project SDK docs.

| Pattern | Intent |
|--------|--------|
| **Prompt caching** | Stable prefix first; volatile user content after. |
| **Model tiering** | Cheaper models for mechanical work; stronger for ambiguous or high-risk tasks. |
| **Batch API** | Many independent, latency-tolerant jobs → batch; tight loops → sync. |
| **Output limits** | Cap max output; structured short answers first. |
| **Semantic caching** | Cache by meaning + scope; invalidate on source or policy change. |
| **API aggregation** | Fewer round-trips without mixing tenants/secrets. |

## Codex-tree in Cursor

If **`.codex-tree/`** exists, prefer **`.codex-tree/cursor/l1.md` → l2 → l3** over raw source until depth demands it. If `cursor/` is missing, use the only other digest `l*.md` set under `.codex-tree/` if present (same tiering).

**Staleness:** `codex-tree check --format json`. **Estimates:** `codex-tree report` or **`ai-dev-exp cursor-context`**.

**Checkin workflow:** see **`checkin`** in this Cursor bundle.

## Checklist

- [ ] Compaction or handoff when the thread is long or pivoting?
- [ ] Smallest digest / search path first?
- [ ] Outputs small; no redundant huge paste?

## Anti-patterns

- Dumping whole trees; repeating logs already in thread; quoting long rules verbatim.

## Additional resources

See [reference.md](reference.md).
