"""PostToolUse hook – logs tool calls to .claude/token-log.jsonl.

Entry point: ``token-log-hook`` (installed via pip).
Reads Claude Code hook JSON from **stdin**, extracts key fields,
estimates token sizes, and appends one JSONL line.

Designed to run with ``"async": true`` so it never blocks the session.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Rough token estimate: ~4 chars per token for English/code.
CHARS_PER_TOKEN = 4

# Tool name → category mapping.
CATEGORY_MAP: dict[str, str] = {
    "Read": "read",
    "Grep": "search",
    "Glob": "search",
    "Edit": "write",
    "Write": "write",
    "NotebookEdit": "write",
    "Bash": "execution",
    "Agent": "agent",
    "WebFetch": "web",
    "WebSearch": "web",
}


def _estimate_tokens(obj: object) -> int:
    """Rough token count from the JSON-serialised size of *obj*."""
    try:
        return max(1, len(json.dumps(obj, default=str)) // CHARS_PER_TOKEN)
    except (TypeError, ValueError):
        return 1


def _extract_read_meta(tool_input: dict) -> dict:
    """Pull offset/limit/file_path from a Read tool call."""
    return {
        "file_path": tool_input.get("file_path", ""),
        "offset": tool_input.get("offset"),
        "limit": tool_input.get("limit"),
    }


def _log_dir(cwd: str) -> Path:
    """Return the .claude/ directory inside the project *cwd*."""
    d = Path(cwd) / ".claude"
    d.mkdir(parents=True, exist_ok=True)
    return d


def process_event(event: dict) -> dict:
    """Transform a raw hook event into a compact log entry."""
    tool_name: str = event.get("tool_name", "unknown")
    tool_input = event.get("tool_input", {})
    tool_response = event.get("tool_response", {})

    input_tokens = _estimate_tokens(tool_input)
    output_tokens = _estimate_tokens(tool_response)

    entry: dict = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": event.get("session_id", ""),
        "tool": tool_name,
        "category": CATEGORY_MAP.get(tool_name, "other"),
        "in_tok": input_tokens,
        "out_tok": output_tokens,
    }

    # Extra metadata for reads (savings calculation).
    if tool_name == "Read":
        entry["meta"] = _extract_read_meta(tool_input if isinstance(tool_input, dict) else {})

    # Extra metadata for agent delegations.
    if tool_name == "Agent" and isinstance(tool_input, dict):
        entry["meta"] = {
            "subagent_type": tool_input.get("subagent_type", "general-purpose"),
            "description": tool_input.get("description", ""),
        }

    return entry


def main() -> None:
    """Entry point for the ``token-log-hook`` command."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        event = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return  # Silently skip malformed input; never block the session.

    entry = process_event(event)
    cwd = event.get("cwd", os.getcwd())
    log_file = _log_dir(cwd) / "token-log.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError:
        pass  # Best-effort; never crash the hook.


if __name__ == "__main__":
    main()
