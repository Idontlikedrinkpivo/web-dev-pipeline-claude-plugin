#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-pipeline: PreCompact — automatic compaction waits for a boundary between units in the session that runs `work`,
and every compaction in a pipeline project is told what its summary must keep.

Why: auto-compaction fires at any moment. In the ai-initiatives 2.3.0 run (2026-11-17/18) six of eight compactions of
the development session fell in the middle of a unit — an executor out, a review round open, fixes at the executor —
and the session only came through because it wrote every step into resume.md. A session cannot compact itself, a
parent's «/compact» arrives as plain text, and a parent's clear_session was refused by the auto-mode classifier, so
the plugin's own hand-over never worked there; the session stopped at «готово к /compact» and waited for the user.
Claude Code skips a proactive auto-compaction a PreCompact hook blocks and the conversation goes on uncompacted, so
holding it until the unit is committed puts the compaction where nothing is in flight.

How (trigger `auto` only — a `/compact` the user typed always runs):
- the session ran `work`: its transcript loaded the work skill;
- a unit is in flight: the newest `documentation/plans/<version>/progress.md` has a row whose status is none of
  «⏳ ждёт», «✅ готово», «⛔ остановлено», «⏭ пропущено» (so «🔄 в работе», «🔍 ревью»);
- there is room: the model's window is 1M (Fable, Opus 4.7+, Sonnet 5+, Haiku 5.5+, a `[1m]` id) and
  CLAUDE_CODE_DISABLE_1M_CONTEXT is not set, and the context is under the hold cap — `context_limit` of
  documentation/.dev-pipeline.json (300000 when absent) plus 150000. Past the cap the compaction goes through
  mid-unit and resume.md carries the step (work → run-hygiene.md → Context). On a 200K window nothing is held: a
  blocked compaction there would be the one that recovers from the context-limit error, and the request would fail.
All three → block, with the reason. Otherwise the hook prints what the summary must keep (its stdout becomes the
compaction's instructions). Each decision is one line in plans/<version>/.progress-compact.log (outside git).

    stdin: the PreCompact JSON (transcript_path, trigger, cwd)

Acts only in a pipeline project: documentation/.dev-pipeline.json or documentation/plans/. Never fails on its own
error: anything unexpected lets the compaction run.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HEADROOM = 150_000
DEFAULT_LIMIT = 300_000
WORK_SKILL = re.compile(r"Base directory for this skill: [^\n\"]*?/work(?:\\n|\n|\s|$)")
MODEL = re.compile(r"claude-(opus|sonnet|haiku)-(\d+)-(\d+)")
SETTLED = ("⏳", "✅", "⛔", "⏭")   # waiting, done, stopped, skipped — nothing out

KEEP = """This is a dev-pipeline project. Keep in the summary, each with its exact name:
- the stage this session runs, the version, and whether it reports to a parent session (its id);
- the item in hand and its step: the unit (U<n>), its executor and task id if one is out, the review round and its
  open findings, the commit hash if it is committed; the next item;
- every decision the chat settled that no document or commit holds yet, and every rule the user or the parent gave
  this session (no pauses, what needs the user's consent);
- the files that hold the state: documentation/plans/<version>/resume.md, the progress file, the run report.
After the compaction the state is read from those files and git, not from this summary."""


def project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def is_pipeline(project: str) -> bool:
    doc = Path(project, "documentation")
    return (doc / ".dev-pipeline.json").is_file() or (doc / "plans").is_dir()


def read_transcript(path: str) -> tuple[bool, int, str]:
    """(the session loaded the work skill, the last main-chain context size, the last model id)."""
    ran_work, tokens, model = False, 0, ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not ran_work and "Base directory for this skill" in line and WORK_SKILL.search(line):
                ran_work = True
            if '"assistant"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            msg = d.get("message") or {}
            u = msg.get("usage") or {}
            size = sum(int(u.get(k) or 0) for k in
                       ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            if size:
                tokens = size
            if str(msg.get("model") or "").startswith("claude"):   # not «<synthetic>», the app's own entries
                model = msg["model"]
    return ran_work, tokens, model


def one_million(model: str) -> bool:
    if os.environ.get("CLAUDE_CODE_DISABLE_1M_CONTEXT"):
        return False
    m = model.lower()
    if "fable" in m or "[1m]" in m:
        return True
    r = MODEL.search(m)
    if not r:
        return False
    family, major, minor = r.group(1), int(r.group(2)), int(r.group(3))
    return {"opus": (major, minor) >= (4, 7), "sonnet": major >= 5,
            "haiku": (major, minor) >= (5, 5)}[family]


def context_limit(project: str) -> int:
    try:
        v = json.loads(Path(project, "documentation", ".dev-pipeline.json").read_text(encoding="utf-8"))
        n = int(v.get("context_limit") or DEFAULT_LIMIT)
        return n if n > 0 else DEFAULT_LIMIT
    except Exception:
        return DEFAULT_LIMIT


def newest_progress(project: str) -> Path | None:
    files = [p for p in Path(project, "documentation", "plans").glob("*/progress.md") if p.is_file()]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def in_flight(progress: Path) -> list[str]:
    """Units whose status is neither waiting nor done, from every table with a «Статус» column."""
    out: list[str] = []
    col = -1
    for line in progress.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("|"):
            col = -1
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Статус" in cells:
            col = cells.index("Статус")
            continue
        if col < 0 or col >= len(cells) or set(cells[0]) <= set("-: "):
            continue
        status = cells[col]
        if status and not status.startswith(SETTLED):
            out.append(f"{cells[0]} {status}")
    return out


def log(progress: Path | None, text: str) -> None:
    if progress is None:
        return
    try:
        with open(progress.parent / ".progress-compact.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} {text}\n")
    except OSError:
        pass


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    project = project_dir(data)
    if not is_pipeline(project):
        return
    trigger = data.get("trigger") or ""
    progress = newest_progress(project)
    t = data.get("transcript_path")
    if trigger == "auto" and t and Path(t).is_file() and progress is not None:
        ran_work, tokens, model = read_transcript(t)
        if ran_work:
            units = in_flight(progress)
            cap = context_limit(project) + HEADROOM
            if units and one_million(model) and tokens < cap:
                reason = (f"dev-pipeline: compaction held until {', '.join(units)} is committed — work compacts "
                          f"between units (context {tokens // 1000}k, held up to {cap // 1000}k).")
                log(progress, f"held {tokens} {'; '.join(units)}")
                print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
                return
            log(progress, f"passed {tokens} {'; '.join(units) or 'between units'}"
                          f"{'' if one_million(model) else ' (window not 1M)'}")
    elif progress is not None:
        log(progress, f"{trigger or 'unknown'} compaction")
    print(KEEP)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
