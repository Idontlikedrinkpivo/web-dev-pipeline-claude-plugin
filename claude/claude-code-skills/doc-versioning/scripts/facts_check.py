"""Prove that a readability rewrite of a Markdown document kept its facts.

    python3 facts_check.py snapshot <file.md> <out.json>   # before the rewrite
    python3 facts_check.py verify   <file.md> <snap.json>  # after it; exit 1 and a list when anything differs

The facts of the body — the `## Журнал изменений` section and the frontmatter left out — are compared as
multisets: requirement and rule ids (FR, NFR, BR, UC, AC, TC, A, S and dotted forms), `backticked` names and
values, and numbers outside both. Line breaks, list markers and table pipes do not count; what moved between
sections is the same fact. A fact that appears fewer times after the rewrite is listed as lost — fine when rule 4
of references/readable.md removed a duplicate, a defect otherwise. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

ID = re.compile(r"(?<![\w-])((?:FR|NFR|BR|UC|AC|TC|A|S)-\d+(?:\.\d+)*(?:\s+(?:Exc|Alt)-\d+)?)(?![\w-])")


def body(text: str) -> str:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    return re.sub(r"(?ms)^## Журнал изменений\s*\n.*?(?=^## |\Z)", "", text)


def facts(text: str) -> dict:
    t = body(text)
    ws = lambda s: re.sub(r"\s+", " ", s).strip()
    ticks = [ws(x) for x in re.findall(r"`([^`\n]+)`", t)]
    rest = re.sub(r"`[^`\n]+`", " ", t)
    ids = [ws(m.group(1)) for m in ID.finditer(rest)]
    rest = ID.sub(" ", rest)
    rest = re.sub(r"(?m)^\s*\d+\.\s", " ", rest)  # list markers
    nums = re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])", rest)
    return {"ids": Counter(ids), "names": Counter(ticks), "numbers": Counter(nums)}


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in ("snapshot", "verify"):
        sys.exit(__doc__)
    mode, path, snap = sys.argv[1:]
    now = facts(open(path, encoding="utf-8").read())
    if mode == "snapshot":
        json.dump({k: dict(v) for k, v in now.items()}, open(snap, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"snapshot: {sum(sum(v.values()) for v in now.values())} facts")
        return
    before = {k: Counter(v) for k, v in json.load(open(snap, encoding="utf-8")).items()}
    bad = 0
    for kind in ("ids", "names", "numbers"):
        lost, added = before[kind] - now[kind], now[kind] - before[kind]
        if lost:
            bad += 1
            print(f"{kind} lost: " + ", ".join(f"{k}×{v}" for k, v in sorted(lost.items())))
        if added:
            print(f"{kind} added: " + ", ".join(f"{k}×{v}" for k, v in sorted(added.items())))
    print("OK — every fact kept" if not bad else "facts lost — check each above")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
