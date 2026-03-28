# Token optimization — reference

Bundled with **ai-dev-exp** at `cursor/skills/token-optimization/`. Optional depth; read when implementing APIs, automation, or when the user wants explicit cost/context discipline.

## Reply and log shape

- Lead with the decision or change; evidence second.
- Prefer one tight code reference (path + line range) over multiple large duplicates.
- Logs: last ~30 lines plus error header, or the single stack frame that matters.

## Tool habits (repo work)

- **Grep**: exact strings, filenames, fast counts.
- **Semantic search**: behavior questions where naming is unclear.
- **Read**: after you know *which* path and roughly *where* in the file.

## Multi-step work

- Re-read only what drifted; do not re-ingest unchanged files between turns.
- When delegating to subagents or subprocesses: minimal specs; require **summarized** returns, not raw dumps.

## Skills and rules

- Load skills that match the task; avoid unrelated skill text.
- When authoring skills: keep `SKILL.md` short; push detail to linked files **one level deep**.

---

## Prompt caching (integration detail)

**Goal:** Reuse computation for repeated long prefixes across requests.

**Practice:**

- Order content so **stable** blocks (system prompt, tool definitions, organization policies, large static references) come **first**.
- Place **changing** content (user turn, current date if needed, one-off file bodies) **after** the stable prefix.
- Avoid tiny cosmetic changes in the stable block (whitespace, reordering) if they bust the cache.

**Caveats:** Minimum lengths, TTL, pricing, and “what counts as cacheable” vary by provider and SDK. Read current vendor documentation for the stack in use; do not hardcode magic numbers in skills.

---

## Model tiering (integration detail)

**Goal:** Pay for capability only where it matters.

**Heuristic:**

| Class of work | Tier tendency |
|---------------|----------------|
| Formatting, lint fixes, mechanical edits | Smaller / faster |
| Single-file implementation with clear spec | Mid |
| Architecture, threat modeling, unclear requirements | Larger / more capable |

Align with any **project routing rules** (e.g. separate docs for which model handles planning vs coding). **Do not** embed dated model IDs in shared skills—use role names and let repos map to current SKUs.

---

## Batch API (integration detail)

**Batch** suits:

- Large sets of **independent** items (e.g. classify 10k snippets).
- **Hours-level** latency is acceptable.

**Avoid batch** for:

- Tight human-in-the-loop edits.
- Single low-latency queries.
- Jobs where **ordering and retries** need immediate visibility.

Batch is a **latency tradeoff**, not a universal win.

---

## Output limits (integration detail)

- Set **max output tokens** (or equivalent) in API calls when exposing open-ended generation.
- Prefer **structured** outputs (JSON, bullet fields) so the model stops early.
- In chat without API control, still **self-limit**: short answer first, offer detail on request.

---

## Semantic caching (integration detail)

**Distinction from prompt caching:** Prompt caching reuses **prefix** computation for identical leading text. **Semantic** caching reuses **results** when a *new* prompt is **close in meaning** (embeddings + threshold).

**Practice:**

- Key cache entries by **scope**: repo revision, tenant, user, or environment as appropriate.
- Store **metadata**: model, temperature, and content hash of sources used.
- **Invalidate** when underlying documents change or when policy requires (security, compliance).

**Do not** semantically cache:

- Outputs that must reflect **live** secrets or **real-time** data unless TTL and scope are explicit.
- Cross-tenant answers without hard isolation.

---

## API aggregation (integration detail)

**Goal:** Fewer round-trips without losing correctness.

Examples:

- One request with multiple structured fields instead of five micro-prompts.
- Batching **read** tool calls in parallel in a single assistant turn (when the host allows).
- Grouping **homogeneous** batch API jobs in one submission.

**Contrast with Batch API:** Aggregation is often **synchronous** grouping; **Batch API** is typically **async** bulk processing. Choose based on latency and independence of tasks.

---

## Codex-tree CLI (reminder)

Used only in repositories where the **codex-tree** tool generated `.codex-tree/`:

- `codex-tree check --format json` — staleness; do not trust digests for paths reported stale without reading source.
- `codex-tree report` — heuristic token estimates (raw vs tree vs tree + digest markdown).

Digest **folder names** (`claude/` vs `cursor/`) reflect generator output layout, not a mandate to use a particular IDE—they are two equivalent tiered views of the same tree.
