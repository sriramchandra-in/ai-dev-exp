"""Token usage report generator.

Reads ``.claude/token-log.jsonl`` produced by the ``token-log-hook`` and
generates per-category breakdowns with efficiency metrics.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CategoryStats:
    calls: int = 0
    in_tokens: int = 0
    out_tokens: int = 0
    # Read-specific: count of calls that used offset/limit.
    partial_reads: int = 0
    total_reads: int = 0
    # Estimated tokens saved by partial reads (requires file size on disk).
    saved_tokens: int = 0


@dataclass
class SessionReport:
    session_id: str
    categories: dict[str, CategoryStats] = field(default_factory=dict)
    total_calls: int = 0
    total_tokens: int = 0
    agent_delegations: int = 0
    entries: list[dict] = field(default_factory=list)


# Display order and labels.
CATEGORY_LABELS: dict[str, str] = {
    "read": "Read",
    "search": "Search (Grep/Glob)",
    "write": "Edit / Write",
    "execution": "Bash",
    "agent": "Agent",
    "web": "Web",
    "other": "Other",
}

CHARS_PER_TOKEN = 4
DEFAULT_LINES_PER_FILE = 500  # Fallback when we can't stat the file.


def _estimate_full_file_tokens(file_path: str) -> int | None:
    """Estimate how many tokens the full file would cost to read."""
    try:
        size = os.path.getsize(file_path)
        return max(1, size // CHARS_PER_TOKEN)
    except OSError:
        return None


def load_entries(log_path: Path) -> list[dict]:
    """Load all JSONL entries from *log_path*."""
    if not log_path.is_file():
        return []
    entries: list[dict] = []
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def build_report(entries: list[dict], session_id: str | None = None) -> SessionReport:
    """Build a :class:`SessionReport` from log entries.

    If *session_id* is ``None``, uses the most recent session found.
    """
    if not entries:
        return SessionReport(session_id=session_id or "")

    # Determine session.
    if session_id is None:
        session_id = entries[-1].get("session", "")

    filtered = [e for e in entries if e.get("session") == session_id]
    if not filtered:
        filtered = entries  # Fallback: show everything.

    cats: dict[str, CategoryStats] = defaultdict(CategoryStats)
    agent_delegations = 0

    for e in filtered:
        cat = e.get("category", "other")
        s = cats[cat]
        s.calls += 1
        s.in_tokens += e.get("in_tok", 0)
        s.out_tokens += e.get("out_tok", 0)

        # Read savings.
        if cat == "read":
            s.total_reads += 1
            meta = e.get("meta", {})
            if meta.get("offset") is not None or meta.get("limit") is not None:
                s.partial_reads += 1
                file_path = meta.get("file_path", "")
                full_tokens = _estimate_full_file_tokens(file_path)
                if full_tokens is not None:
                    actual = e.get("out_tok", 0)
                    if full_tokens > actual:
                        s.saved_tokens += full_tokens - actual

        if cat == "agent":
            agent_delegations += 1

    total_calls = sum(s.calls for s in cats.values())
    total_tokens = sum(s.in_tokens + s.out_tokens for s in cats.values())

    return SessionReport(
        session_id=session_id,
        categories=dict(cats),
        total_calls=total_calls,
        total_tokens=total_tokens,
        agent_delegations=agent_delegations,
        entries=filtered,
    )


def format_report_text(report: SessionReport) -> str:
    """Human-readable multi-line report."""
    lines: list[str] = []
    sid = report.session_id[:12] if report.session_id else "all"
    lines.append(f"Token Usage Report — session {sid}")
    lines.append("=" * 56)
    lines.append("")

    # Category table.
    lines.append(f"{'Category':<22s} {'Calls':>6s} {'Est. Tokens':>12s} {'%':>6s}")
    lines.append("-" * 56)

    for cat_key in CATEGORY_LABELS:
        s = report.categories.get(cat_key)
        if s is None:
            continue
        tok = s.in_tokens + s.out_tokens
        pct = (tok / report.total_tokens * 100) if report.total_tokens else 0
        label = CATEGORY_LABELS[cat_key]
        lines.append(f"{label:<22s} {s.calls:>6d} {tok:>12,d} {pct:>5.0f}%")

    lines.append("-" * 56)
    lines.append(f"{'Total':<22s} {report.total_calls:>6d} {report.total_tokens:>12,d}")
    lines.append("")

    # Efficiency metrics.
    lines.append("Efficiency Metrics")
    lines.append("-" * 56)

    read_stats = report.categories.get("read")
    if read_stats and read_stats.total_reads > 0:
        ratio = read_stats.partial_reads / read_stats.total_reads
        lines.append(
            f"Reads with offset/limit:  "
            f"{read_stats.partial_reads}/{read_stats.total_reads} ({ratio:.0%})"
        )
        if read_stats.saved_tokens > 0:
            lines.append(f"Est. saved by partial reads: ~{read_stats.saved_tokens:,d} tokens")

    if report.agent_delegations:
        lines.append(f"Agent delegations:        {report.agent_delegations}")

    lines.append("")
    return "\n".join(lines)


def format_brief(report: SessionReport) -> str:
    """One-line summary."""
    read_stats = report.categories.get("read")
    partial = ""
    if read_stats and read_stats.total_reads > 0:
        pct = read_stats.partial_reads / read_stats.total_reads * 100
        partial = f" | partial reads {pct:.0f}%"
        if read_stats.saved_tokens > 0:
            partial += f" (~{read_stats.saved_tokens:,d} saved)"

    agents = ""
    if report.agent_delegations:
        agents = f" | {report.agent_delegations} delegations"

    return (
        f"session {report.session_id[:8]} | "
        f"{report.total_calls} calls | "
        f"~{report.total_tokens:,d} est. tokens"
        f"{partial}{agents}"
    )


def format_json(report: SessionReport) -> dict:
    """Machine-readable report dict."""
    cats = {}
    for key, s in report.categories.items():
        cats[key] = {
            "label": CATEGORY_LABELS.get(key, key),
            "calls": s.calls,
            "in_tokens": s.in_tokens,
            "out_tokens": s.out_tokens,
            "total_tokens": s.in_tokens + s.out_tokens,
        }
        if key == "read":
            cats[key]["partial_reads"] = s.partial_reads
            cats[key]["total_reads"] = s.total_reads
            cats[key]["saved_tokens"] = s.saved_tokens

    return {
        "session_id": report.session_id,
        "total_calls": report.total_calls,
        "total_tokens": report.total_tokens,
        "agent_delegations": report.agent_delegations,
        "categories": cats,
    }
