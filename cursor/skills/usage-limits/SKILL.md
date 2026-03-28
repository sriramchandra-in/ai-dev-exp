---
name: usage-limits
description: >-
  Explains Claude Code vs Cursor usage reporting: Claude Code 5h/7d statusline
  JSON, Anthropic API rate headers for BYOK, Cursor subscription UI, and the
  ai-dev-exp anthropic-rate-brief CLI plus optional Cursor status-bar add-on.
---

# Usage limits (Claude Code vs Cursor)

## What differs

| Source | Session / weekly style limits | Where it shows |
|--------|-------------------------------|----------------|
| **Claude Code** | `rate_limits.five_hour` and `seven_day` (`used_percentage`) | Piped into `~/.claude/statusline-command.py` as JSON on stdin |
| **Anthropic API** (direct / BYOK) | RPM / tokens-per-minute buckets (headers on each response) | `ai-dev-exp anthropic-rate-brief` or Cursor extension `editors/cursor-anthropic-rate` |
| **Cursor subscription** | Composer / plan quotas | Cursor **Settings →** usage / billing UI — **not** exposed to this CLI |

Cursor **cannot** receive the same statusline JSON as Claude Code unless Anthropic/Cursor add a hook.

## Cursor workflow (API key in env)

1. Ensure **`ANTHROPIC_API_KEY`** is visible to the environment that runs the CLI (terminal, or **launch Cursor from a shell** that exports it, if the extension should see it).
2. **One line (terminal or automation):**
   ```bash
   ai-dev-exp anthropic-rate-brief
   ```
3. **JSON:**
   ```bash
   ai-dev-exp anthropic-rate-brief --format json
   ```
4. **Cursor status bar (optional):** Install the add-on from **`ai-dev-exp/editors/cursor-anthropic-rate/`** using **Cursor → Extensions → Install from Folder** (Cursor uses the same extension format as VS Code; you do **not** need to use the VS Code app). If the user avoids extensions entirely, use only the CLI / Tasks / shell alias—same numbers, no status bar.

**Cost:** Each probe sends one minimal Messages API request (Haiku by default). Increase the add-on’s refresh interval if that matters.

## Claude Code workflow (unchanged)

Keep **`~/.claude/settings.json`** pointing at **`statusline-command.py`**. That script already reads **`rate_limits`** from Claude Code’s JSON — no replacement by this skill.

## Alignment with “session / weekly” wording

- **5h / 7d** percentages are **Claude Code product** signals, not returned by the public Messages API headers.
- **`anthropic-rate-brief`** reports **API rate-limit bucket utilization** (approximate % consumed from remaining/limit headers). Treat it as **“how hot the API pipe is”**, not as “weekly Pro quota.”

## When the user asks for parity in Cursor

- If they use **Cursor without BYOK:** point them to **Cursor’s usage UI**; the extension/CLI cannot read subscription internals.
- If they use **BYOK / API:** use **`anthropic-rate-brief`** + extension.
- If they also use **Claude Code:** remind them the **5h/7d** line is **only** in Claude’s statusline unless Cursor adds an equivalent feed.
