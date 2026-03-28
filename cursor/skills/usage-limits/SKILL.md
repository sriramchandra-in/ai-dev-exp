---
name: usage-limits
description: >-
  Explains Claude Code vs API vs Cursor usage: 5h/7d statusline JSON,
  anthropic-rate-brief for terminal/PyCharm, optional Cursor/VS Code status-bar
  add-on, and Cursor subscription UI limits.
---

# Usage limits (Claude Code vs API vs editors)

## What differs

| Source | Session / weekly style limits | Where it shows |
|--------|-------------------------------|----------------|
| **Claude Code** | `rate_limits.five_hour` and `seven_day` (`used_percentage`) | Piped into `~/.claude/statusline-command.py` as JSON on stdin |
| **Anthropic API** (direct / BYOK) | RPM / tokens-per-minute buckets (response headers) | **`ai-dev-exp anthropic-rate-brief`** in any terminal, PyCharm External Tool, etc. |
| **Cursor subscription** | Composer / plan quotas | Cursor **Settings →** usage / billing — **not** exposed to this CLI |
| **VS Code / Cursor extension** | Same as API line above | Optional add-on `editors/cursor-anthropic-rate/` (polls the CLI) |

Claude Code **cannot** feed its statusline JSON into PyCharm or a plain terminal; use **`anthropic-rate-brief`** for API bucket utilization instead.

## Terminal + PyCharm (recommended for non-Cursor workflows)

1. Export **`ANTHROPIC_API_KEY`** in the shell (or in PyCharm **Run configuration → Environment** / **External Tool → Environment**).
2. Run:
   ```bash
   ai-dev-exp anthropic-rate-brief
   ai-dev-exp anthropic-rate-brief --format json
   ```
3. **PyCharm External Tool** example: Program `ai-dev-exp`, Arguments `anthropic-rate-brief`, working directory optional.

**Cost:** Each run sends one minimal Messages request (default model **`claude-haiku-4-5`**, overridable with **`ANTHROPIC_USAGE_PROBE_MODEL`**).

## Optional: Cursor or VS Code status bar

Install **`ai-dev-exp/editors/cursor-anthropic-rate/`** via **Install from Folder** or a **`.vsix`** (VS Code-compatible manifest; works in **Cursor** too). Same data as the CLI, refreshed on a timer. Skip entirely if you only use **terminal + PyCharm**.

## Claude Code workflow (unchanged)

Keep **`~/.claude/settings.json`** pointing at **`statusline-command.py`**. That script reads **`rate_limits`** from Claude Code’s JSON.

## Alignment with “session / weekly” wording

- **5h / 7d** are **Claude Code product** signals, not returned by public Messages API headers.
- **`anthropic-rate-brief`** is **API rate-limit bucket utilization** (approx. % consumed from remaining vs limit). Not “weekly Pro quota.”

## When the user asks for parity

- **PyCharm / terminal only:** **`anthropic-rate-brief`** + explain 5h/7d stay in Claude Code.
- **Cursor without BYOK:** Cursor’s own usage UI; this CLI cannot read it.
- **BYOK / API:** CLI (and optional editor add-on).
