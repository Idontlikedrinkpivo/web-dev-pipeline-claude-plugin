"""How big this session's context is now — the last model call of the newest session of the project.

    python3 context_size.py <project-dir> [--limit <tokens>] [--next high|mid|low|<tokens>] [--session <id>]

Prints one line: the context of the newest main session's last call, in tokens, and whether it is over the
limit («передать»). `work` runs it after each commit (work → references/run-hygiene.md → Context): over the limit,
the run hands over to a fresh session at that boundary. The newest session is the one written last; with two
sessions working in the same project at once it may be the other one — the line names the session it read.
--session <id> (Claude Code only) reads the transcript whose file name is that session id instead of the newest: a
nested session passes its own id (it has it from `mcp__ccd_session_mgmt__get_session` with `self`), so two sessions
working in one project do not measure each other; an id with no transcript falls back to the newest, and the line says so.
Limit: --limit, else the integer `context_limit` in <project-dir>/documentation/.dev-pipeline.json, else 300000. The
default suits a 1,000,000-token window; a 200,000 window needs a lower value, because the host compacts earlier.
Claude Code: input + cache read + cache write of the last assistant message; the Codex build (codex_logs.py
beside this file): `last_token_usage.input_tokens` of the last token_count event. Exit 2 over the limit.
--next adds what the next item usually takes (a High unit 120 thousand, a Mid 70, a Low 35, or a number): when the
context and it pass the limit, exit 2 now — hand over at this boundary rather than cross the limit inside the item.
Either way the run goes on without the user: exit 2 is a hand-over, exit 0 the next item, never a pause.
In Claude Desktop the stage measures its context with the app's own tool (`mcp__ccd_session_mgmt__get_usage`, session
"self": tokens used, the window and where auto-compact starts). This script is the measure only where that tool does not
exist (a terminal) and in the Codex build; it cannot see the window, so it hands over at `context_limit` alone.
Standard library only.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def claude_newest(cwd: str, want: str = "") -> tuple[str, int, str, bool]:
    from sessions import MAX_NAME, ours, sanitized, session_dirs
    dirs, roots = session_dirs(cwd, [])
    exact = {sanitized(r) for r in roots if len(sanitized(r)) <= MAX_NAME}
    mains = [p for d in dirs for p in d.glob("*.jsonl") if d.name in exact or ours(p, roots)]
    if not mains:
        return "", 0, "", True
    named = [p for p in mains if want and p.stem == want]
    p = named[0] if named else max(mains, key=lambda x: x.stat().st_mtime)
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
    return p.stem, ctx, ts, bool(named) or not want


def codex_newest(cwd: str, want: str = "") -> tuple[str, int, str, bool]:
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
        return "", 0, "", True
    ctx, ts = 0, ""
    for d in sessions.records(best):
        pl = d.get("payload") or {}
        if d.get("type") == "event_msg" and pl.get("type") == "token_count" and pl.get("info"):
            ctx = int(((pl["info"].get("last_token_usage") or {}).get("input_tokens")) or 0)
            ts = (d.get("timestamp") or "")[:16]
    return best.name, ctx, ts, True


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    limit, from_project = 300_000, False
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    else:  # the project's own threshold: it depends on the model's window, which only the project knows
        try:
            v = json.loads((Path(args[0]) / "documentation" / ".dev-pipeline.json").read_text(encoding="utf-8")).get("context_limit")
            if isinstance(v, int) and not isinstance(v, bool) and v > 0:
                limit, from_project = v, True
        except (OSError, ValueError, AttributeError):
            pass
    want = args[args.index("--session") + 1] if "--session" in args and args.index("--session") + 1 < len(args) else ""
    codex = (Path(__file__).resolve().parent / "codex_logs.py").exists()
    sid, ctx, ts, found = (codex_newest if codex else claude_newest)(args[0], want)
    if not sid:
        print("контекст: сессия не найдена — порог считается не перейдённым; скажите это одной строкой и продолжайте")
        return
    nxt = args[args.index("--next") + 1].lower() if "--next" in args and args.index("--next") + 1 < len(args) else ""
    ahead = {"high": 120_000, "mid": 70_000, "low": 35_000}.get(nxt) or (int(nxt) if nxt.isdigit() else 0)
    over = ctx > limit
    early = not over and ahead and ctx + ahead > limit
    print(f"контекст: {ctx // 1000} тыс. токенов (сессия {sid[:8]}, {ts.replace('T', ' ')}) · порог {limit // 1000} тыс."
          + (" (context_limit проекта)" if from_project else "")
          + (f" · сессия {want} не найдена, прочитана самая свежая" if not found else "")
          + (" · передать сейчас" if over else "")
          + (f" · передать сейчас: следующий пункт (~{ahead // 1000} тыс.) перейдёт порог" if early else "")
          + (" — без паузы и без вопроса пользователю" if over or early else ""))
    over = over or bool(early)
    sys.exit(2 if over else 0)


if __name__ == "__main__":
    main()
