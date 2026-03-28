# ai-dev-exp

AI developer experience skills for coding assistants.

## Layout

Canonical skill markdown lives in two trees at the **repository root** (not only under `.claude/` or `.cursor/`):

- **`claude/skills/<name>/SKILL.md`** — Claude Code / Anthropic-oriented copy (e.g. codex-tree **claude/** digest first in checkin).
- **`cursor/skills/<name>/SKILL.md`** — Cursor-oriented copy (e.g. codex-tree **cursor/** digest first; extra host notes where useful).

The **`token-optimization`** skill exists **only** under `cursor/skills/` (installs with `--cursor`).

For convenience in this repo, **`.claude/skills/`** and **`.cursor/skills/`** are **symlinks** into those trees so Claude Code and Cursor can discover skills without duplication.

## Skills

| Skill | Claude tree | Cursor tree |
|-------|-------------|-------------|
| **checkin** | yes | yes |
| **github** | yes | yes |
| **deployment** | yes | yes |
| **token-optimization** | — | yes |
| **usage-limits** | — | yes |

## Installation

```bash
pip install ai-dev-exp
```

## Usage

```bash
# List Claude and Cursor bundles
ai-dev-exp list

# Install Claude bundle into ./.claude/skills/ (default)
ai-dev-exp install

# Install Cursor bundle into ./.cursor/skills/ (includes token-optimization)
ai-dev-exp install --cursor

# One skill
ai-dev-exp install checkin
ai-dev-exp install token-optimization --cursor
```

### Cursor context snapshot (codex-tree)

For repos that use **codex-tree**, you can print **measurable** context-strategy numbers (tree vs raw vs Cursor digest). This does **not** read Cursor chat token usage; it runs `codex-tree check` and `codex-tree report`.

```bash
cd /path/to/your/repo   # git root with .codex-tree/

# End-of-session or checkpoint (multi-line, paste into notes or chat)
ai-dev-exp cursor-context

# One line — quick check, log line, or manual status-bar text in Cursor
ai-dev-exp cursor-context --brief

# JSON for scripts or dashboards
ai-dev-exp cursor-context --format json

# Another project root
ai-dev-exp cursor-context --path ~/projects/my-app --brief
```

Requires **`codex-tree` on `PATH`** and a **`.codex-tree/`** directory (see the **checkin** skill).

Cursor does not expose chat token metrics to extensions; **`--brief`** is meant to be run from the integrated terminal (or a Task) and pasted or glanced at—there is no automatic status-bar hook from this package alone.

### Anthropic API rate line (BYOK / API key)

Claude Code’s **5h / 7d** percentages come from **Claude Code’s** statusline JSON, not from the public API. This package can print **Messages API rate-limit headers** from any shell (**not** Cursor subscription usage):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
ai-dev-exp anthropic-rate-brief
ai-dev-exp anthropic-rate-brief --format json
```

**Terminal (default):** use your system terminal, **PyCharm’s terminal**, a shell alias, `cron`, or CI—whatever runs `ai-dev-exp` with the key in the environment.

**PyCharm:** **Settings → Tools → External Tools** (or a **Run/Debug** configuration) can run the same command; ensure **`ANTHROPIC_API_KEY`** is set in the tool env or in the IDE’s environment.

**Optional editor status bar (Cursor or VS Code):** load `editors/cursor-anthropic-rate/` via **Install from Folder** / `.vsix` if you use those editors; it polls the same CLI on an interval.

See the **`usage-limits`** skill for Claude vs API vs Cursor billing.

## Development

```bash
git clone https://github.com/sriramchandra-in/ai-dev-exp.git
cd ai-dev-exp
pip install -e ".[dev]"
pytest
```

CI (same shape as **isrc-modern**’s test job: Python 3.12 on Ubuntu) runs on push and pull requests to `main`: **ruff**, **mypy**, **pytest**, and a **wheel** build. See `.github/workflows/ci.yml`.

Editable installs read skills from repo-root `claude/` and `cursor/`. Wheels ship a copy under `ai_dev_exp/_bundled/` so `pip install` works without the git tree.

## License

MIT — Institute of Sri Ramchandra Consciousness
