#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What the plugin's command guard (hooks/guard.py) refused in a project, for reflect's «### Отказы хука».

    python3 guard_report.py <project dir> [--since YYYY-MM-DD]

Reads ~/.claude (or ~/.codex)/dev-pipeline-feedback/.guard/<project folder>.jsonl — one line per refusal, written by
the hook — and prints a block to paste unchanged: the count per rule and, for each rule, up to three distinct
commands it refused. Reflect reads those commands: a refusal of a command that was right is a finding on the hook
(its rule is too wide); a rule that fires again and again in one session is a finding on the skill that keeps
asking for that command. Standard library only.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

NAMES = {"commit-chained": "коммит склеен с проверкой", "commit-on-main": "коммит в main во время итерации",
         "plan-unit-trailer": "Plan-Unit, который git не прочитает", "sed-i": "sed -i по-GNU",
         "progress-from-shell": "файл прогресса из оболочки", "wipe-shared-tree": "stash / reset / clean в общей папке",
         "edit-outside-worktree": "правка основной папки из worktree", "other": "другое"}


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    project = Path(args[0]).resolve().name
    since = args[args.index("--since") + 1] if "--since" in args else ""
    rows = []
    for home in (".claude", ".codex"):
        f = Path.home() / home / "dev-pipeline-feedback" / ".guard" / f"{project}.jsonl"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("ts", "") >= since:
                    rows.append(r)
    print("### Отказы хука")
    print()
    if not rows:
        print(f"Отказов нет{' с ' + since if since else ''}.")
        return
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get("rule", "other")].append(r)
    print(f"Всего: {len(rows)} ({rows[0]['ts'][:10]} — {rows[-1]['ts'][:10]})")
    print()
    print("| Правило | Отказов | Примеры команд |")
    print("|---|---|---|")
    for rule, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        seen, examples = set(), []
        for r in rs:
            w = " ".join(r.get("what", "").split())[:110]
            if w and w not in seen:
                seen.add(w)
                examples.append(f"`{w.replace('|', '¦').replace('`', '')}`")
            if len(examples) == 3:
                break
        print(f"| {NAMES.get(rule, rule)} | {len(rs)} | {'<br>'.join(examples) or '—'} |")


if __name__ == "__main__":
    main()
