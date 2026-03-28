"""Cursor-focused context snapshot from codex-tree (check + report).

Measures **repo context strategy** (tree vs raw vs digest), not Cursor chat tokens.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CodexTreeResult:
    """Result of invoking `codex-tree` with JSON output."""

    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    data: dict[str, Any] | None


def find_codex_tree_bin() -> str | None:
    return shutil.which("codex-tree")


def _run_json(path: Path, subcommand: str) -> CodexTreeResult:
    """Run `codex-tree <subcommand> --path <path> --format json`."""
    bin_name = find_codex_tree_bin()
    if not bin_name:
        return CodexTreeResult(
            ok=False,
            exit_code=127,
            stdout="",
            stderr="codex-tree not found on PATH",
            data=None,
        )

    cmd = [bin_name, subcommand, "--path", str(path), "--format", "json"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return CodexTreeResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            data=None,
        )

    out = proc.stdout or ""
    err = proc.stderr or ""
    data: dict[str, Any] | None = None
    if proc.returncode == 0 and out.strip():
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            data = None

    return CodexTreeResult(
        ok=proc.returncode == 0 and data is not None,
        exit_code=proc.returncode,
        stdout=out,
        stderr=err,
        data=data,
    )


def gather_snapshot(project_path: Path) -> dict[str, Any]:
    """Run check + report and return a merged structure for CLI / JSON."""
    path = project_path.resolve()
    errors: list[str] = []

    if not find_codex_tree_bin():
        errors.append("codex-tree CLI not on PATH; install codex-tree to use this command.")

    tree_dir = path / ".codex-tree"
    if not tree_dir.is_dir():
        errors.append(f"No .codex-tree/ at {path} (run codex-tree init in the repo root).")

    check_r = _run_json(path, "check")
    report_r = _run_json(path, "report")

    if not check_r.ok:
        if check_r.stderr:
            errors.append(f"codex-tree check: {check_r.stderr.strip()}")
        elif check_r.exit_code != 0:
            errors.append(f"codex-tree check failed (exit {check_r.exit_code}).")

    if not report_r.ok:
        if report_r.stderr:
            errors.append(f"codex-tree report: {report_r.stderr.strip()}")
        elif report_r.exit_code != 0:
            errors.append(f"codex-tree report failed (exit {report_r.exit_code}).")

    return {
        "path": str(path),
        "codex_tree_cli": find_codex_tree_bin() is not None,
        "has_dot_codex_tree": tree_dir.is_dir(),
        "check": check_r.data,
        "report": report_r.data,
        "errors": errors,
    }


def _pct(x: float) -> int:
    return int(round(100 * x))


def format_brief(snapshot: dict[str, Any]) -> str:
    """One line for terminals, logs, or editor status text (~100 chars)."""
    errs = snapshot.get("errors") or []
    if errs and not snapshot.get("check") and not snapshot.get("report"):
        msg = str(errs[0])[:60]
        return f"codex-tree: unavailable ({msg})"

    parts: list[str] = ["codex-tree"]

    chk = snapshot.get("check") or {}
    if chk:
        stale_n = len(chk.get("stale_files") or [])
        clean_n = chk.get("clean_files")
        if chk.get("is_stale"):
            parts.append(f"stale {stale_n}")
        else:
            parts.append("clean")
        if isinstance(clean_n, int):
            parts.append(f"{clean_n} indexed")

    rep = snapshot.get("report") or {}
    te = rep.get("token_estimate") or {}
    if te:
        raw = te.get("raw_source_tokens") or 0
        cur_sv = te.get("savings_tree_plus_cursor")
        digest = te.get("cursor_digest_used")
        if raw and isinstance(cur_sv, (int, float)):
            parts.append(f"Cursor ctx ~{_pct(float(cur_sv))}% vs raw")
        if digest:
            parts.append(str(digest))

    if snapshot["errors"]:
        parts.append("(see full report for warnings)")

    return " | ".join(parts)


def format_report_text(snapshot: dict[str, Any]) -> str:
    """Multi-line summary for end-of-session or checkpoint paste."""
    lines: list[str] = [
        "codex-tree context report (repo strategy, not Cursor plan usage) — stdout / terminal",
        f"Path: {snapshot['path']}",
        "",
    ]

    for e in snapshot["errors"]:
        lines.append(f"! {e}")
    if snapshot["errors"]:
        lines.append("")

    chk = snapshot.get("check")
    if chk:
        lines.append("## Staleness (check)")
        lines.append(f"  Tree version: {chk.get('tree_version', '?')}")
        stale_flag = chk.get("is_stale", False)
        clean_n = chk.get("clean_files", "?")
        lines.append(f"  Stale: {stale_flag}  |  clean files: {clean_n}")
        stale = chk.get("stale_files") or []
        lines.append(f"  Stale file count: {len(stale)}")
        if stale[:15]:
            lines.append("  Sample stale paths:")
            for s in stale[:15]:
                p = s.get("path", "?")
                r = s.get("reason", "?")
                lines.append(f"    - {p} ({r})")
            if len(stale) > 15:
                lines.append(f"    … and {len(stale) - 15} more")
        lines.append("")

    rep = snapshot.get("report")
    if rep:
        lines.append("## Token estimates (report)")
        te = rep.get("token_estimate") or {}
        lines.append(f"  Raw source (baseline): ~{te.get('raw_source_tokens', '?')} tokens")
        jt = te.get("just_tree_tokens")
        sj = te.get("savings_just_tree")
        if isinstance(sj, (int, float)):
            lines.append(f"  Tree only: ~{jt} tokens  (~{_pct(float(sj))}% vs raw)")
        else:
            lines.append(f"  Tree only: ~{jt} tokens")
        if isinstance(te.get("savings_tree_plus_cursor"), (int, float)):
            lines.append(
                f"  Tree + Cursor digest ({te.get('cursor_digest_used', '?')}): "
                f"~{te.get('tree_plus_cursor_tokens', '?')} tokens  "
                f"(~{_pct(float(te['savings_tree_plus_cursor']))}% vs raw)"
            )
        if isinstance(te.get("savings_tree_plus_claude"), (int, float)):
            lines.append(
                f"  Tree + Claude digest ({te.get('claude_digest_used', '?')}): "
                f"~{te.get('tree_plus_claude_tokens', '?')} tokens  "
                f"(~{_pct(float(te['savings_tree_plus_claude']))}% vs raw)"
            )
        st = rep.get("stats") or {}
        lines.append("")
        lines.append("## Tree stats")
        tf, ts = st.get("total_files", "?"), st.get("total_symbols", "?")
        lines.append(f"  Files: {tf}  |  symbols: {ts}")
        loc, langs = st.get("total_lines_of_code", "?"), st.get("languages", [])
        lines.append(f"  LoC: {loc}  |  languages: {langs}")

    if not chk and not rep:
        lines.append("(No check/report data; fix errors above.)")

    lines.append("")
    lines.append("Tip: run again after `codex-tree update` or before PR for a fresh checkpoint.")
    return "\n".join(lines)
