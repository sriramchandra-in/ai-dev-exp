"""Tests for Anthropic rate-limit probe (mocked HTTP)."""

from unittest.mock import MagicMock, patch

import httpx

from ai_dev_exp.anthropic_rate import _pct_consumed, build_snapshot, format_brief_line


def test_pct_consumed():
    assert _pct_consumed("50", "100") == 50.0
    assert _pct_consumed("100", "100") == 0.0
    assert _pct_consumed(None, "10") is None


def test_build_snapshot_no_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = build_snapshot()
    assert s["ok"] is False
    assert "no ANTHROPIC_API_KEY" in s["brief"]


@patch("ai_dev_exp.anthropic_rate.httpx.post")
def test_build_snapshot_parses_headers(mock_post: MagicMock, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = httpx.Headers(
        {
            "anthropic-ratelimit-requests-remaining": "40",
            "anthropic-ratelimit-requests-limit": "50",
            "anthropic-ratelimit-input-tokens-remaining": "900000",
            "anthropic-ratelimit-input-tokens-limit": "1000000",
        },
    )
    mock_post.return_value = resp

    s = build_snapshot()
    assert s["ok"] is True
    assert s["http_status"] == 200
    assert "req~20%" in s["brief"] or "req~20" in s["brief"]
    assert format_brief_line(s) == s["brief"]


@patch("ai_dev_exp.anthropic_rate.httpx.post")
def test_build_snapshot_401(mock_post: MagicMock, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-bad")
    resp = MagicMock()
    resp.status_code = 401
    resp.headers = httpx.Headers({})
    mock_post.return_value = resp
    s = build_snapshot()
    assert s["ok"] is False
    assert "auth" in s["brief"].lower()
