---
name: usage-limits
description: >-
  Cursor-focused usage reporting: run ai-dev-exp in the terminal (Cursor or
  PyCharm) for codex-tree context and optional API rate headers; Cursor plan
  quotas stay in Settings. Optional editor status-bar add-on for those who want it.
---

# Usage limits (Cursor + terminal)

## What you can print in the terminal

| Report | Command | Needs |
|--------|---------|--------|
| **Repo context vs raw** (codex-tree) | `ai-dev-exp cursor-context` / `--brief` / `--format json` | `codex-tree` on `PATH`, `.codex-tree/` |
| **API rate buckets** (BYOK) | `ai-dev-exp anthropic-rate-brief` / `--format json` | `ANTHROPIC_API_KEY` in the shell |

Run these from **Cursor’s integrated terminal** or **PyCharm’s terminal** (same commands). For PyCharm **External Tools**, set the program to `ai-dev-exp` and arguments to `cursor-context --brief` or `anthropic-rate-brief`, with working directory = git root and env vars as needed.

## What you cannot get from the CLI

- **Cursor subscription / Composer / plan usage** — only **Cursor Settings →** billing or usage UI.
- **Exact chat token counts** per message — not exposed for terminal scripts.

## Optional: status bar (Cursor or VS Code)

Folder **`editors/cursor-anthropic-rate/`** polls **`anthropic-rate-brief`** on a timer. **Skip** if you only want **terminal** output.

## Notes on `anthropic-rate-brief`

- Shows **Messages API** rate-limit headers (approx. % of bucket used), **not** “weekly Pro” style product windows.
- Each run sends one **small** API probe (default Haiku-class model; override with **`ANTHROPIC_USAGE_PROBE_MODEL`**).

## When the user asks for numbers

- **Cursor-only billing** → Settings UI.
- **Repo context strategy** → `cursor-context`.
- **BYOK API pressure** → `anthropic-rate-brief` in terminal.
