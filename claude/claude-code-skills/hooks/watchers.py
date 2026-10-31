#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-pipeline: SubagentStop — an agent may not end while a background task it started is still running.

Why: finished executors left their watchers running for hours — nine Monitor loops in one run (reflect, 2.1.1 and
2.1.4) — holding the panel and waking the session for nothing. The rule was in every packet (executor-catalog →
worker-prompt RULES: stop every background task before the report) and was broken, so it is held here.

How: the agent's own transcript says what it started — «Command running in background with ID: <id>» (Bash with
run_in_background) and «Monitor started (task <id>» — and what ended it: a TaskStop of that id, «Successfully stopped
task: <id>», or a <task-notification> for that id. Started and not ended → the stop is blocked once, with the ids and
their commands; the agent stops them (TaskStop) and ends. A second stop in a row (stop_hook_active) always passes,
so the hook can never trap an agent.

    stdin: the SubagentStop JSON (transcript_path, agent_id or agent_transcript_path, stop_hook_active)

Acts only in a project with documentation/.dev-pipeline.json. Never fails on its own error.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

STARTED = re.compile(r"(?:running in background with ID:\s*|Monitor started \(task\s+)([A-Za-z0-9_-]{5,})")
STOPPED = re.compile(r"Successfully stopped task:\s*([A-Za-z0-9_-]{5,})")
NOTIFIED = re.compile(r"<task-id>([A-Za-z0-9_-]{5,})</task-id>")


def agent_transcript(data: dict) -> Path | None:
    p = data.get("agent_transcript_path")
    if p and Path(p).is_file():
        return Path(p)
    main, agent = data.get("transcript_path"), data.get("agent_id")
    if main and agent:
        cand = Path(main).with_suffix("") / "subagents" / f"agent-{agent}.jsonl"
        if cand.is_file():
            return cand
    return None


def running(transcript: Path) -> dict[str, str]:
    """id -> the command or description that started it, for tasks started and not ended."""
    uses: dict[str, str] = {}
    started: dict[str, str] = {}
    ended: set[str] = set()
    polled: dict[str, str] = {}
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        content = (d.get("message") or {}).get("content")
        if isinstance(content, str):
            ended.update(NOTIFIED.findall(content))
            continue
        for c in content if isinstance(content, list) else []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                inp = c.get("input") or {}
                uses[c.get("id", "")] = str(inp.get("description") or inp.get("command") or "")[:90]
                if c.get("name") in ("TaskStop", "KillShell"):
                    ended.add(str(inp.get("task_id") or inp.get("shell_id") or ""))
                if c.get("name") in ("BashOutput", "TaskOutput"):   # polled: ended if the answer says so
                    polled[c.get("id", "")] = str(inp.get("bash_id") or inp.get("task_id") or "")
            elif c.get("type") == "tool_result":
                t = c.get("content")
                t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
                for tid in STARTED.findall(t[:600]):
                    started[tid] = uses.get(c.get("tool_use_id", ""), "")
                ended.update(STOPPED.findall(t[:600]))
                tid = polled.get(c.get("tool_use_id", ""))
                if tid and re.search(r"status[\"']?\s*[:>=]\s*[\"']?(?:completed|failed|killed|exited)", t[:800]):
                    ended.add(tid)
            elif c.get("type") == "text":
                ended.update(NOTIFIED.findall(c.get("text", "")))
    return {k: v for k, v in started.items() if k not in ended}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if data.get("stop_hook_active") or not os.path.isfile(os.path.join(project, "documentation", ".dev-pipeline.json")):
        return
    t = agent_transcript(data)
    if not t:
        return
    left = running(t)
    if left:
        listed = "; ".join(f"{tid} ({what})" if what else tid for tid, what in left.items())
        print(json.dumps({"decision": "block", "reason":
            f"dev-pipeline: background tasks you started are still running: {listed}. Stop each with TaskStop "
            "(load its schema with ToolSearch select:TaskStop if needed), then end with your report as it was — "
            "a finished agent's watchers keep running for hours (executor-catalog → worker-prompt RULES)."},
            ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
