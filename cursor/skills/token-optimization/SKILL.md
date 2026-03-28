---
name: token-optimization
description: >-
  Reduces tokens and API cost via shallow context, context-window compaction,
  codex-tree digests, prompt caching patterns, model tiering, batch vs sync
  calls, output caps, semantic cache discipline, and request aggregation. Use
  when the user mentions tokens, context limits, compaction, budget, cost,
  caching, batch API, model choice, or keeping sessions small; or before pulling
  huge transcripts, files, or redundant text into context.
---

# Token optimization

## Portability

This skill is **host-agnostic**: it applies to any coding agent with repo access and tools or APIs. Instructions refer to repository paths and optional `.codex-tree/` artifacts, not to a specific editor or vendor UI.

**Packaging:** Maintained in **ai-dev-exp** at `cursor/skills/token-optimization/`. Install into a target repo with `ai-dev-exp install --cursor` (all Cursor skills) or `ai-dev-exp install token-optimization --cursor`, or copy this directory into that project’s `.cursor/skills/token-optimization/`. Keep the **workspace root** on the codebase you are editing so paths and `.codex-tree/` resolve correctly.

**Measuring context strategy (not chat tokens):** With **codex-tree** on `PATH`, run `ai-dev-exp cursor-context` (full summary), `ai-dev-exp cursor-context --brief` (one line), or `--format json` from the repo root for staleness + estimated savings vs raw source.

## Cursor

Use Cursor’s **native code citations** (path + line range) when quoting existing code. Run terminal commands from the integrated terminal when the workflow below references the shell.

## When to apply

- User asks to save tokens, stay under limits, lower cost, or keep replies compact.
- Topics: prompt caching, batch API, model tiering, semantic cache, aggregation, output limits.
- Session is long, or many large files are in scope.
- You are about to read, paste, or repeat large blobs without a clear need.
- Context feels full, repetitive, or dominated by already-resolved work.

## Context window compaction

**When appropriate**, shrink what stays in the active window—do not wait for the user to hit a hard limit.

- **Proactively offer** compaction when: many turns of settled decisions, huge logs or diffs still in thread, a **topic pivot**, or the next step only needs a short **handoff** (open tasks, key paths, last commands).
- **Summarize** into a tight block: current goal, constraints, files touched, unresolved questions. Drop obsolete tool output and duplicate code pastes from the narrative (keep citations to paths, not full re-quotes).
- **Host affordances:** If the product exposes **compact** / **summarize thread** / **clear** (e.g. Claude Code-style compaction), **suggest using it** at natural breakpoints; then continue from the summary only.
- **New scope → new chat** when the old thread is mostly unrelated; carry over only a one-paragraph brief.
- After compaction, **avoid re-ingesting** the same large blobs unless the task requires it.

## Defaults (in order)

1. **Assume competence** — Do not explain basics the user did not ask for. Prefer short plans and direct edits.

2. **Progressive disclosure** — Start with structure or search hits; open full files only for the exact symbols or regions you will change. Use `offset`/`limit` on large files.

3. **Search before read** — Use repo search or semantic search to locate symbols; then read narrow ranges. Avoid serial full-file reads across a directory “to understand.”

4. **One-shot tool batches** — Combine independent lookups in parallel instead of chatty back-and-forth (see **API aggregation** in reference).

5. **Compact outputs** — Summarize in prose; cite code by path and line range (Cursor citation blocks when available) instead of pasting whole files. Truncate long excerpts with `...` when unavoidable. Prefer **output limits** (max tokens / concise formats) when you control generation settings.

6. **No noise** — Skip lockfiles, minified assets, generated trees, `node_modules`, and huge binaries unless the task explicitly requires them.

## API and orchestration (patterns)

Use these when building or configuring **integrations** (scripts, services, CI), not when the host hides the API entirely. Exact parameters are **provider-specific**—follow the project’s SDK docs; this skill states intent only.

| Pattern | Intent |
|--------|--------|
| **Prompt caching** | Keep a **stable prefix** (system rules, long instructions, tool schemas, static docs) and append **volatile** content (user message, timestamps, one-off blobs) **after** the stable block so caches can hit across requests. |
| **Model tiering** | Use smaller/cheaper models for narrow, deterministic work; escalate to larger models for ambiguous reasoning, security-sensitive review, or cross-cutting design. Match tier to task, not ego. |
| **Batch API** | Use **batch** for many **independent**, latency-tolerant jobs (bulk labeling, extraction). Use **synchronous** calls for interactive loops needing fast feedback. |
| **Output limits** | Set conservative **max output** tokens where supported; ask for structured short answers first; expand only on request. |
| **Semantic caching** | Cache **responses or retrieved chunks** keyed by embedding similarity (and scope), not only exact string match. **Invalidate** when source content or policy-relevant context changes. |
| **API aggregation** | Combine related operations into **fewer round-trips** (batch fields in one request, merge tool reads) without losing necessary separation of secrets or tenants. |

**Safety:** Do not share cache keys, batch queues, or aggregated requests across **different users, secrets, or trust boundaries** unless the architecture explicitly allows it.

## Codex-tree projects (`.codex-tree/`)

Optional integration when another repository uses the **codex-tree** tool: prefer **tiered markdown digests** over raw source until depth is needed.

- Under `.codex-tree/`, **`claude/l*.md`** and **`cursor/l*.md`** are **parallel** digest families with the **same l1→l2→l3 structure** (only the opening usage notes differ). In Cursor, prefer `.codex-tree/cursor/l*.md` when present; otherwise use `claude/l*.md`.
- **Tier ladder:** l1 = orientation / tiny edits; l2 = feature work and APIs; l3 = refactors and full import/architecture detail.

For stale files from `codex-tree check`, read **raw source** for those paths. For heuristic token comparisons, use `codex-tree report` (optional `--format json`). Full checkin workflow: see the **checkin** skill in the same Cursor bundle or repo.

## Before a large read

- Can grep or one function-sized block answer the question?
- If the file is huge, locate symbols first, then read a small window around known line numbers.

## Checklist (quick)

- [ ] Compaction or handoff summary offered when the thread is long or pivoting?
- [ ] Smallest digest or search path tried first?
- [ ] Stable-vs-volatile prompt layout respects caching if API calls are in play?
- [ ] Model tier matches task risk and ambiguity?
- [ ] Batch vs sync choice matches latency and interactivity?
- [ ] Outputs capped or summarized; no redundant huge paste?
- [ ] Semantic cache entries scoped and invalidation considered?
- [ ] Aggregated calls do not mix incompatible contexts?

## Anti-patterns

- Dumping entire directories or “read everything in `src/`.”
- Repeating long logs or configs already in the thread.
- Quoting rules or skills verbatim when a short pointer suffices.
- Caching or batching **personalized or secret-bearing** outputs without explicit policy.

## Additional resources

For tool habits, subagents, codex-tree CLI reminders, and provider-agnostic detail on each pattern, see [reference.md](reference.md).
