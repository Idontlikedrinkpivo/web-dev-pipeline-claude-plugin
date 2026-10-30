"""Find in an agent's details file what may need the orchestrator, when its short report says nothing about it.

    python3 report_alarm.py <details file> [--concerns "<the short report's CONCERNS and NEEDS lines>"]

Prints each line of the details file that carries an alarm word — something not done, skipped, worked around,
left for later, unverified — with its line number. With --concerns empty (or «нет» / «none»), any hit means the
orchestrator reads the details file before the commit (work → references/run-hygiene.md → What reaches the
orchestrator). Exit 1 when there are hits and no concerns, else 0. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALARM = re.compile(
    r"не удалось|не получилось|не проверен|не проверял|не запускал|пропущ|пропуст|временн|обход|костыл|заглушк|"
    r"отключ|потом|позже|не успел|не нашёл|не нашел|упал[аи]?\b|падает|"
    r"\bTODO\b|\bFIXME\b|\bXXX\b|\bskip(?:ped)?\b|\.only\b|--no-verify|eslint-disable|# ?noqa|type: ?ignore|"
    r"@ts-(?:ignore|expect-error)|\bworkaround\b|\bhack\b|not (?:verified|tested|run)|could not|couldn't|failed|"
    r"\bwarning\b|deprecated|flaky",
    re.I,
)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path = Path(args[0])
    concerns = args[args.index("--concerns") + 1] if "--concerns" in args and args.index("--concerns") + 1 < len(args) else ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        print(f"report_alarm: no details file {path} — the executor did not write it: return the report")
        sys.exit(1)
    hits = [(i, l.strip()) for i, l in enumerate(lines, 1) if ALARM.search(l)]
    quiet = not concerns.strip() or concerns.strip().lower() in ("нет", "none", "—", "-")
    if not hits:
        print("report_alarm: тревожных слов нет")
        return
    print(f"report_alarm: {len(hits)} строк с тревожными словами" + (" — CONCERNS пусты: прочитать файл до коммита"
                                                                   if quiet else ""))
    for i, l in hits[:25]:
        print(f"  {i}: {l[:200]}")
    sys.exit(1 if quiet else 0)


if __name__ == "__main__":
    main()
