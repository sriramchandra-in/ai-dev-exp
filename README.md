# ai-dev-exp

AI developer experience skills for coding assistants.

## Skills

- **checkin** — Load a codex-tree knowledge tree into an AI session (Cursor and Claude digest layers, optional intent)
- **github** — GitHub operations: PR management, issue tracking, code review workflows
- **deployment** — Deployment orchestration: CI triggers, environment management, rollback

## Installation

```bash
pip install ai-dev-exp
```

## Usage

```bash
# Install skills into your Claude Code environment
ai-dev-exp install

# List available skills
ai-dev-exp list

# Install a specific skill
ai-dev-exp install checkin
```

## Development

```bash
git clone https://github.com/sriramchandra-in/ai-dev-exp.git
cd ai-dev-exp
pip install -e ".[dev]"
pytest
```

## License

MIT — Institute of Sri Ramchandra Consciousness
