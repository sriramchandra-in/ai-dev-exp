"""Tests for cursor-context snapshot formatting."""

from pathlib import Path

from ai_dev_exp.cursor_context import format_brief, format_report_text, gather_snapshot


def test_format_brief_with_data():
    snap = {
        "path": "/tmp/proj",
        "codex_tree_cli": True,
        "has_dot_codex_tree": True,
        "errors": [],
        "check": {
            "is_stale": False,
            "clean_files": 10,
            "stale_files": [],
        },
        "report": {
            "token_estimate": {
                "raw_source_tokens": 100_000,
                "savings_tree_plus_cursor": 0.55,
                "cursor_digest_used": "cursor/l2.md",
            },
        },
    }
    line = format_brief(snap)
    assert "clean" in line
    assert "10 indexed" in line
    assert "55%" in line or "Cursor ctx" in line
    assert "cursor/l2.md" in line


def test_format_brief_stale():
    snap = {
        "path": "/p",
        "codex_tree_cli": True,
        "has_dot_codex_tree": True,
        "errors": [],
        "check": {
            "is_stale": True,
            "clean_files": 2,
            "stale_files": [{"path": "a.py", "reason": "modified"}],
        },
        "report": None,
    }
    assert "stale 1" in format_brief(snap)


def test_format_brief_no_cli():
    snap = {
        "path": "/p",
        "codex_tree_cli": False,
        "has_dot_codex_tree": False,
        "errors": ["codex-tree CLI not on PATH; install codex-tree to use this command."],
        "check": None,
        "report": None,
    }
    b = format_brief(snap)
    assert "unavailable" in b


def test_format_report_text_includes_sections():
    snap = {
        "path": "/repo",
        "codex_tree_cli": True,
        "has_dot_codex_tree": True,
        "errors": [],
        "check": {
            "tree_version": "1.0",
            "is_stale": False,
            "clean_files": 5,
            "stale_files": [],
        },
        "report": {
            "token_estimate": {
                "raw_source_tokens": 1000,
                "just_tree_tokens": 400,
                "savings_just_tree": 0.6,
                "tree_plus_cursor_tokens": 300,
                "savings_tree_plus_cursor": 0.7,
                "cursor_digest_used": "cursor/l2.md",
                "tree_plus_claude_tokens": 320,
                "savings_tree_plus_claude": 0.68,
                "claude_digest_used": "claude/l2.md",
            },
            "stats": {
                "total_files": 20,
                "total_symbols": 100,
                "total_lines_of_code": 500,
                "languages": ["Python"],
            },
        },
    }
    text = format_report_text(snap)
    assert "Staleness" in text
    assert "Token estimates" in text
    assert "60%" in text
    assert "70%" in text


def test_gather_snapshot_no_codex_tree_dir(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("ai_dev_exp.cursor_context.find_codex_tree_bin", lambda: None)
    snap = gather_snapshot(tmp_path)
    assert snap["has_dot_codex_tree"] is False
    assert snap["codex_tree_cli"] is False
    assert snap["errors"]
