---
name: usage-limits
description: >-
  Cursor usage reporting via terminal: ai-dev-exp cursor-context (codex-tree) from
  Cursor or PyCharm terminal; Cursor plan limits only in Cursor Settings.
---

# Usage limits (Cursor + terminal)

## Terminal (Cursor or PyCharm)

| Report | Command | Needs |
|--------|---------|--------|
| **Repo context vs raw** | `ai-dev-exp cursor-context` / `--brief` / `--format json` | `codex-tree` on `PATH`, `.codex-tree/` |

Run from **Cursor’s integrated terminal** or **PyCharm’s terminal** with working directory = git root.

**PyCharm External Tools:** Program `ai-dev-exp`, arguments e.g. `cursor-context --brief`.

## Cursor plan / Composer

**Subscription and quota** are only in **Cursor Settings** (billing / usage). No CLI in this bundle reads them.

## When the user asks for numbers

- **Cursor billing** → Cursor Settings.
- **Repo context strategy** → `cursor-context` in terminal.
