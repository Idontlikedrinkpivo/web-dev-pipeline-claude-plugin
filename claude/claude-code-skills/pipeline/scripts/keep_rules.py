#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The rules a stage must not lose after a compaction — the section of references/keep-after-compaction.md for the
stage skill the session ran last, printed by the session-start hook right after a compaction.

    python3 keep_rules.py <transcript .jsonl>

The skill is read from the transcript: the last stage skill invoked (`"skill": "dev-pipeline:<name>"`, Claude Code)
or loaded (`…/skills/<name>/SKILL.md` or its base directory, both builds), the last one that has a section.
None found — the «pipeline» section. Prints nothing when the file is missing. Never fails: the hook must not break
a session. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references" / "keep-after-compaction.md"
SKILL = re.compile(r'"skill"\s*:\s*"dev-pipeline:([a-z][\w-]*)"|\$dev-pipeline:([a-z][\w-]*)'
                   r'|Base directory for this skill: [^"\n]*?/([a-z][\w-]*)(?=[\\"\n])|/skills/([a-z][\w-]*)/SKILL\.md')


def sections(text: str) -> dict[str, str]:
    out, name, body = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^## ([\w-]+)\s*$", line)
        if m:
            if name:
                out[name] = "\n".join(body).strip()
            name, body = m.group(1), []
        elif name:
            body.append(line)
    if name:
        out[name] = "\n".join(body).strip()
    return out


def main() -> None:
    if len(sys.argv) < 2 or not REF.exists():
        return
    known = sections(REF.read_text(encoding="utf-8"))
    stage = "pipeline"
    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
        names = [next(g for g in m.groups() if g) for m in SKILL.finditer(text)]
        stage = next((n for n in reversed(names) if n in known), "pipeline")
    except OSError:
        pass
    if stage in known:
        print(f"dev-pipeline: not to lose in this stage ({stage}, pipeline → references/keep-after-compaction.md):")
        print(known[stage])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
