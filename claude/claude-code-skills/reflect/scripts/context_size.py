"""How big this session's context is now — the last model call of the newest session of the project.

    python3 context_size.py <project-dir> [--limit <tokens, default 300000>]

Prints one line: the context of the newest main session's last call, in tokens, and whether it is over the
limit («передать»). `work` runs it after each commit (work → references/run-hygiene.md → Context): over the limit,
the run hands over to a fresh session at that boundary. The newest session is the one written last; with two
sessions working in the same project at once it may be the other one — the line names the session it read.
Claude Code: input + cache read + cache write of the last assistant message; the Codex build (codex_logs.py
beside this file): `last_token_usage.input_tokens` of the last token_count event. Exit 2 over the limit.
Standard library only.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def claude_newest(cwd: str) -> tuple[str, int, str]:
    from sessions import MAX_NAME, ours, sanitized, session_dirs
    dirs, roots = session_dirs(cwd, [])
    exact = {sanitized(r) for r in roots if len(sanitized(r)) <= MAX_NAME}
    mains = [p for d in dirs for p in d.glob("*.jsonl") if d.name in exact or ours(p, roots)]
    if not mains:
        return "", 0, ""
    p = max(mains, key=lambda x: x.stat().st_mtime)
    ctx, ts = 0, ""
    with open(p, errors="ignore") as fh:
        for line in fh:
            if '"usage"' not in line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            u = (e.get("message") or {}).get("usage") or {}
            if e.get("type") == "assistant" and u:
                ctx = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens",
                                                         "cache_creation_input_tokens"))
                ts = (e.get("timestamp") or "")[:16]
    return p.stem, ctx, ts


def codex_newest(cwd: str) -> tuple[str, int, str]:
    import sessions  # the Codex build's sessions.py
    root = os.path.realpath(cwd)
    best = None
    for p in sessions.rollouts():
        m = sessions.meta(p)
        if not m or m.get("parent_thread_id") or os.path.realpath(str(m.get("cwd", ""))) != root:
            continue
        if best is None or p.stat().st_mtime > best.stat().st_mtime:
            best = p
    if best is None:
        return "", 0, ""
    ctx, ts = 0, ""
    for d in sessions.records(best):
        pl = d.get("payload") or {}
        if d.get("type") == "event_msg" and pl.get("type") == "token_count" and pl.get("info"):
            ctx = int(((pl["info"].get("last_token_usage") or {}).get("input_tokens")) or 0)
            ts = (d.get("timestamp") or "")[:16]
    return best.name, ctx, ts


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 300_000
    codex = (Path(__file__).resolve().parent / "codex_logs.py").exists()
    sid, ctx, ts = (codex_newest if codex else claude_newest)(args[0])
    if not sid:
        print("контекст: сессия не найдена — считать по числу задач (work → references/run-hygiene.md → Context)")
        return
    over = ctx > limit
    print(f"контекст: {ctx // 1000} тыс. токенов (сессия {sid[:8]}, {ts.replace('T', ' ')}) · порог {limit // 1000} тыс."
          + (" · передать новой сессии" if over else ""))
    sys.exit(2 if over else 0)


if __name__ == "__main__":
    main()
