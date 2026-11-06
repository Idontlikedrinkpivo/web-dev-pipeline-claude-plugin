#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-pipeline: Stop — a turn that changed a progress file ends with the progress line, and the line's link is the
page, never the Markdown.

Why: the rule («After each item … run the script and paste its line»; «the link the user gets is always the page»)
was in the stage skills, in the packet of the nested session and in pipeline → references/progress-keeping.md, and a
live run (Дашборд руководителя 1.2.0, 2026-11-06) still went a whole hand-over without one line: the session edited
progress.md, dispatched, reviewed, and the user had to ask «где файл прогресса?» — and got a link to the .md.

How: the session's own transcript says what this turn did. Since the last message that started the turn (the user's,
a task notification, another session's message), was a progress file written — an Edit/Write/MultiEdit of
documentation/plans/<version>/progress*.md, test-run.md or security-audit.md, or a progress_set.py / progress_e2e.py
call? Then the turn's assistant text must carry a link to the page (`[progress….html](…)`). And whatever the turn did,
its text may not link the .md itself. Either miss blocks the stop once, with what to do; a second stop in a row
(stop_hook_active) always passes, so the hook can never trap the session.

    stdin: the Stop JSON (transcript_path, stop_hook_active, cwd)

Acts only in a project with documentation/.dev-pipeline.json. Never fails on its own error.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

FILE = r"(?:progress[\w-]*|test-run|security-audit)\.md"
PROGRESS_PATH = re.compile(r"documentation/plans/[^/\s'\"]+/" + FILE + r"$")
PAGE_LINK = re.compile(r"\[(?:progress[\w-]*|test-run|security-audit)\.html\]\(")
MD_LINK = re.compile(r"\[" + FILE + r"\]\(")
SCRIPTS = re.compile(r"progress_(?:set|e2e)\.py")


def turn(transcript: Path) -> list[dict]:
    """The entries after the last message that started a turn: a user entry whose content is text, not tool
    results."""
    entries = []
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        content = (d.get("message") or {}).get("content")
        if d.get("type") == "user":
            is_result = isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "tool_result" for c in content)
            if not is_result:
                entries = []
                continue
        entries.append(d)
    return entries


def judge(entries: list[dict]) -> tuple[set[str], bool, set[str]]:
    """(progress files this turn wrote, whether its text links a page, the .md files its text links)."""
    wrote: set[str] = set()
    page = False
    md_links: set[str] = set()
    for d in entries:
        if d.get("type") != "assistant":
            continue
        for c in ((d.get("message") or {}).get("content") or []):
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                inp = c.get("input") or {}
                if c.get("name") in ("Edit", "Write", "MultiEdit"):
                    path = str(inp.get("file_path") or "").replace(os.sep, "/")
                    if PROGRESS_PATH.search(path):
                        wrote.add(os.path.basename(path))
                elif c.get("name") == "Bash" and SCRIPTS.search(str(inp.get("command") or "")):
                    for m in re.finditer(FILE, str(inp.get("command") or "")):
                        wrote.add(m.group(0))
            elif c.get("type") == "text":
                text = c.get("text") or ""
                if PAGE_LINK.search(text):
                    page = True
                md_links.update(m.group(0)[1:-2] for m in MD_LINK.finditer(text))
    return wrote, page, md_links


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if data.get("stop_hook_active") or not os.path.isfile(os.path.join(project, "documentation", ".dev-pipeline.json")):
        return
    t = data.get("transcript_path")
    if not t or not Path(t).is_file():
        return
    wrote, page, md_links = judge(turn(Path(t)))
    reasons = []
    if wrote and not page:
        names = ", ".join(sorted(wrote))
        reasons.append(f"this turn changed {names} but did not paste the progress line. Run "
                       f"python3 \"<pipeline skill folder>/scripts/progress_link.py\" documentation/plans/<version>/"
                       f"{sorted(wrote)[0]} (add --desktop when the session has the built-in browser) and paste the "
                       "line it prints as the last line of your message — the count and the link to the page")
    if md_links:
        names = ", ".join(sorted(md_links))
        reasons.append(f"your message links {names} itself; the user gets the page, never the Markdown — replace it "
                       "with the line progress_link.py prints")
    if reasons:
        print(json.dumps({"decision": "block", "reason": "dev-pipeline: " + "; ".join(reasons) +
                          " (pipeline → references/progress-keeping.md → After each item)."}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
