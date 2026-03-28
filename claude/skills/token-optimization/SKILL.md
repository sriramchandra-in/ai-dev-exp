---
name: token-optimization
description: >-
  Optimizes Claude Code sessions: shallow context, compaction, codex-tree
  `.codex-tree/claude/` digests, subagent delegation, and terminal reports via
  ai-dev-exp. Use when the user mentions tokens, context limits, compaction,
  cost, or keeping sessions lean; or before huge reads and redundant paste.
---

# Token optimization (Claude Code)

## Who this is for

You are assisting someone working in **Claude Code** (CLI, desktop, or IDE extension). **Terminal reports** for this repo use **`ai-dev-exp`** via the **Bash tool**.

**Packaging:** **ai-dev-exp** -> `claude/skills/token-optimization/`. Install with `ai-dev-exp install token-optimization`. Keep the **working directory** on the repo being edited.

## Terminal reports

Run via Bash tool from the **project git root**:

```bash
# Repo context strategy (needs codex-tree + .codex-tree/)
ai-dev-exp cursor-context            # works for any host; reports tree + digest stats
ai-dev-exp cursor-context --brief
ai-dev-exp cursor-context --format json

# Anthropic API rate-limit snapshot (needs ANTHROPIC_API_KEY)
ai-dev-exp anthropic-rate-brief
ai-dev-exp anthropic-rate-brief --format json
```

## Claude Code habits

- **Batch reads, sequential writes** -- parallel tool calls for independent reads (Grep, Glob, Read); sequence writes/edits that depend on each other.
- **Explore agent for cross-cutting searches; direct Grep/Glob for known paths** -- if you know the file or symbol name, go direct. If the search spans multiple modules or naming is unclear, delegate to an Explore agent to keep the main context clean.
- **Read with `offset`/`limit` for files over ~200 lines** -- Grep to find the line number first, then Read a 50-100 line window around it. Small files are fine to read whole.
- **Suggest `/compact` at milestones, don't force** -- after completing a feature or fix, mention compaction if context is heavy. Let the user decide; don't auto-trigger.
- **Short paste (< 10 lines) inline; cite `file:line` for everything else** -- keep diffs and small snippets visible; point to the file for longer references.

## When to apply

- User asks to save tokens, compact context, lower cost, or keep replies small.
- Session is long, many large files, or the thread is noisy with resolved work.

## Context window compaction

**When appropriate**, shrink active context before limits bite.

- Offer a **short handoff**: goal, constraints, files touched, open questions; drop stale tool dumps.
- Claude Code **auto-compresses** prior messages as the context window fills. Before that point, suggest `/compact` to proactively summarize.
- **New scope -> new session** when history is unrelated; carry one short paragraph forward only.
- After compaction, **don't re-paste** large blobs unless needed.

## Defaults (in order)

1. **Assume competence** -- Short plans, direct edits.

2. **Progressive disclosure** -- Search hits first; narrow `Read` with `offset`/`limit` on large files.

3. **Search before read** -- Use Grep/Glob to locate symbols; then Read narrow ranges. Avoid serial full-file reads "to understand."

4. **One-shot tool batches** -- Parallel independent tool calls in a single response (see **API aggregation** in reference).

5. **Compact outputs** -- Summarize; cite by path and line range instead of pasting whole files.

6. **No noise** -- Skip lockfiles, `node_modules`, minified bundles, unless required.

## Subagent delegation

- Delegate broad exploration to the **Explore agent** instead of issuing many sequential Grep/Read calls in the main context.
- When delegating: provide minimal specs; require **summarized** returns, not raw dumps.
- Use background agents for independent work that doesn't block the current task.

## API and orchestration (patterns)

For **scripts and services** you integrate (not the host's billing). Provider-specific details: project SDK docs.

| Pattern | Intent |
|--------|--------|
| **Prompt caching** | Stable prefix first; volatile user content after. |
| **Model tiering** | Cheaper models for mechanical work; stronger for ambiguous or high-risk tasks. |
| **Batch API** | Many independent, latency-tolerant jobs -> batch; tight loops -> sync. |
| **Output limits** | Cap max output; structured short answers first. |
| **Semantic caching** | Cache by meaning + scope; invalidate on source or policy change. |
| **API aggregation** | Fewer round-trips without mixing tenants/secrets. |

## Codex-tree in Claude Code

If **`.codex-tree/`** exists, prefer **`.codex-tree/claude/l1.md` -> l2 -> l3** over raw source until depth demands it. If `claude/` is missing, use the only other digest `l*.md` set under `.codex-tree/` if present (same tiering).

**Staleness:** `codex-tree check --format json`. **Estimates:** `codex-tree report` or **`ai-dev-exp cursor-context`**.

**Checkin workflow:** see **`checkin`** in this Claude bundle.

## Checklist

- [ ] Compaction or handoff when the thread is long or pivoting?
- [ ] Smallest digest / search path first?
- [ ] Outputs small; no redundant huge paste?
- [ ] Subagent delegation for broad exploration instead of main-context tool chains?

## Anti-patterns

- Dumping whole trees; repeating logs already in thread; quoting long rules verbatim.
- Sequential full-file reads across a directory when Grep + targeted Read would suffice.

## Additional resources

See [reference.md](reference.md).
