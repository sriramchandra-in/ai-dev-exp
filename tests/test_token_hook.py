"""Tests for token_hook and token_report modules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_dev_exp.token_hook import CATEGORY_MAP, process_event
from ai_dev_exp.token_report import (
    build_report,
    format_brief,
    format_json,
    format_report_text,
    load_entries,
)


# ---------- token_hook.process_event ----------


def _make_event(tool_name: str = "Read", tool_input: dict | None = None) -> dict:
    return {
        "session_id": "sess-1",
        "tool_name": tool_name,
        "tool_input": tool_input or {},
        "tool_response": {"ok": True},
        "cwd": "/tmp/proj",
    }


def test_process_event_basic():
    entry = process_event(_make_event("Bash", {"command": "ls"}))
    assert entry["tool"] == "Bash"
    assert entry["category"] == "execution"
    assert entry["session"] == "sess-1"
    assert entry["in_tok"] > 0
    assert entry["out_tok"] > 0


def test_process_event_read_meta():
    entry = process_event(
        _make_event("Read", {"file_path": "/tmp/foo.py", "offset": 10, "limit": 50})
    )
    assert entry["category"] == "read"
    assert entry["meta"]["file_path"] == "/tmp/foo.py"
    assert entry["meta"]["offset"] == 10
    assert entry["meta"]["limit"] == 50


def test_process_event_agent_meta():
    entry = process_event(
        _make_event(
            "Agent",
            {"subagent_type": "Explore", "description": "find auth code", "prompt": "..."},
        )
    )
    assert entry["category"] == "agent"
    assert entry["meta"]["subagent_type"] == "Explore"


def test_process_event_unknown_tool():
    entry = process_event(_make_event("CustomMcpTool"))
    assert entry["category"] == "other"


def test_all_known_tools_categorised():
    for tool in CATEGORY_MAP:
        assert CATEGORY_MAP[tool] in {
            "read",
            "search",
            "write",
            "execution",
            "agent",
            "web",
            "other",
        }


# ---------- token_report ----------


def _write_log(tmp_path: Path, entries: list[dict]) -> Path:
    log = tmp_path / ".claude" / "token-log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return log


SAMPLE_ENTRIES = [
    {
        "ts": "2026-03-28T10:00:00Z",
        "session": "s1",
        "tool": "Read",
        "category": "read",
        "in_tok": 20,
        "out_tok": 500,
        "meta": {"file_path": "/tmp/big.py", "offset": 10, "limit": 50},
    },
    {
        "ts": "2026-03-28T10:00:01Z",
        "session": "s1",
        "tool": "Grep",
        "category": "search",
        "in_tok": 15,
        "out_tok": 80,
    },
    {
        "ts": "2026-03-28T10:00:02Z",
        "session": "s1",
        "tool": "Edit",
        "category": "write",
        "in_tok": 100,
        "out_tok": 30,
    },
    {
        "ts": "2026-03-28T10:00:03Z",
        "session": "s1",
        "tool": "Agent",
        "category": "agent",
        "in_tok": 50,
        "out_tok": 200,
    },
    {
        "ts": "2026-03-28T10:00:04Z",
        "session": "s1",
        "tool": "Read",
        "category": "read",
        "in_tok": 20,
        "out_tok": 800,
    },
]


def test_load_entries(tmp_path: Path):
    log = _write_log(tmp_path, SAMPLE_ENTRIES)
    entries = load_entries(log)
    assert len(entries) == 5


def test_load_entries_missing_file(tmp_path: Path):
    entries = load_entries(tmp_path / "nope.jsonl")
    assert entries == []


def test_build_report_categories():
    report = build_report(SAMPLE_ENTRIES, session_id="s1")
    assert report.total_calls == 5
    assert "read" in report.categories
    assert report.categories["read"].calls == 2
    assert report.categories["search"].calls == 1
    assert report.agent_delegations == 1


def test_build_report_partial_reads():
    report = build_report(SAMPLE_ENTRIES, session_id="s1")
    read_stats = report.categories["read"]
    assert read_stats.partial_reads == 1  # Only first Read had offset/limit.
    assert read_stats.total_reads == 2


def test_build_report_latest_session():
    """With session_id=None, picks the last entry's session."""
    report = build_report(SAMPLE_ENTRIES)
    assert report.session_id == "s1"


def test_build_report_empty():
    report = build_report([])
    assert report.total_calls == 0
    assert report.total_tokens == 0


def test_format_report_text():
    report = build_report(SAMPLE_ENTRIES, session_id="s1")
    text = format_report_text(report)
    assert "Read" in text
    assert "Search" in text
    assert "Agent" in text
    assert "Total" in text


def test_format_brief():
    report = build_report(SAMPLE_ENTRIES, session_id="s1")
    line = format_brief(report)
    assert "5 calls" in line
    assert "1 delegations" in line


def test_format_json():
    report = build_report(SAMPLE_ENTRIES, session_id="s1")
    data = format_json(report)
    assert data["total_calls"] == 5
    assert "read" in data["categories"]
    assert data["categories"]["read"]["partial_reads"] == 1
