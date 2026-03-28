"""Probe Anthropic Messages API rate-limit headers (API / BYOK), not Claude Pro 5h/7d windows."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_PROBE_MODEL = "claude-haiku-4-5"
MESSAGES_URL = "https://api.anthropic.com/v1/messages"

# Headers from https://docs.anthropic.com/en/api/rate-limits#response-headers
HDR_REQ_REM = "anthropic-ratelimit-requests-remaining"
HDR_REQ_LIM = "anthropic-ratelimit-requests-limit"
HDR_IN_REM = "anthropic-ratelimit-input-tokens-remaining"
HDR_IN_LIM = "anthropic-ratelimit-input-tokens-limit"
HDR_OUT_REM = "anthropic-ratelimit-output-tokens-remaining"
HDR_OUT_LIM = "anthropic-ratelimit-output-tokens-limit"


def _pct_consumed(remaining: str | None, limit: str | None) -> float | None:
    """Return approximate % of limit *consumed* (not remaining)."""
    if remaining is None or limit is None:
        return None
    try:
        r = float(remaining)
        lim = float(limit)
    except ValueError:
        return None
    if lim <= 0:
        return None
    used = lim - r
    return max(0.0, min(100.0, 100.0 * used / lim))


def probe_rate_headers(
    *,
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 30.0,
) -> tuple[dict[str, str], int]:
    """POST a minimal message; return (headers dict lowercased keys for lookup, status_code).

    On failure, headers may be empty; status_code is HTTP status or 0 for transport errors.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {}, 0

    mdl = model or os.environ.get("ANTHROPIC_USAGE_PROBE_MODEL", DEFAULT_PROBE_MODEL)

    body = {
        "model": mdl,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "."}],
    }
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        r = httpx.post(
            MESSAGES_URL,
            headers=headers,
            json=body,
            timeout=timeout,
        )
    except httpx.HTTPError:
        return {}, 0

    # httpx headers are case-insensitive; normalize to lowercase for lookup
    h = {k.lower(): v for k, v in r.headers.items()}
    return h, r.status_code


def build_snapshot(
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Structured result for JSON / tooling."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {
            "ok": False,
            "error": "ANTHROPIC_API_KEY is not set",
            "brief": "API: no ANTHROPIC_API_KEY",
        }

    h, status = probe_rate_headers(api_key=key, model=model)
    if status == 0:
        return {
            "ok": False,
            "error": "network or HTTP client failure",
            "brief": "API: request failed",
        }

    if status == 401:
        return {"ok": False, "error": "401 unauthorized", "brief": "API: auth failed"}

    req_pct = _pct_consumed(h.get(HDR_REQ_REM), h.get(HDR_REQ_LIM))
    in_pct = _pct_consumed(h.get(HDR_IN_REM), h.get(HDR_IN_LIM))
    out_pct = _pct_consumed(h.get(HDR_OUT_REM), h.get(HDR_OUT_LIM))

    parts: list[str] = ["API"]
    if req_pct is not None:
        parts.append(f"req~{req_pct:.0f}%")
    if in_pct is not None:
        parts.append(f"in~{in_pct:.0f}%")
    if out_pct is not None:
        parts.append(f"out~{out_pct:.0f}%")

    if len(parts) > 1:
        brief = " ".join(parts)
    elif status == 429:
        brief = "API: limited (429)"
    else:
        brief = f"API: HTTP {status}" if not h else "API: (no limit headers)"

    ok = 200 <= status < 300
    out: dict[str, Any] = {
        "ok": ok,
        "http_status": status,
        "brief": brief,
        "requests": {
            "remaining": h.get(HDR_REQ_REM),
            "limit": h.get(HDR_REQ_LIM),
            "reset": h.get("anthropic-ratelimit-requests-reset"),
            "used_pct": req_pct,
        },
        "input_tokens": {
            "remaining": h.get(HDR_IN_REM),
            "limit": h.get(HDR_IN_LIM),
            "reset": h.get("anthropic-ratelimit-input-tokens-reset"),
            "used_pct": in_pct,
        },
        "output_tokens": {
            "remaining": h.get(HDR_OUT_REM),
            "limit": h.get(HDR_OUT_LIM),
            "reset": h.get("anthropic-ratelimit-output-tokens-reset"),
            "used_pct": out_pct,
        },
    }
    if status == 429:
        out["warning"] = "429 on probe request"
    return out


def format_brief_line(snapshot: dict[str, Any]) -> str:
    return str(snapshot.get("brief") or "API: unknown")
