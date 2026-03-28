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

## Development

```bash
git clone https://github.com/sriramchandra-in/ai-dev-exp.git
cd ai-dev-exp
pip install -e ".[dev]"
pytest
```

Editable installs read skills from repo-root `claude/` and `cursor/`. Wheels ship a copy under `ai_dev_exp/_bundled/` so `pip install` works without the git tree.

## License

MIT — Institute of Sri Ramchandra Consciousness
