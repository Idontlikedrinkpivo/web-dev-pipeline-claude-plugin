#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The open questions of every document, grouped by the stage they are addressed to — so a stage sees the questions
another document's writer left for it, while each question stays in its own document's file.

    python3 open_questions.py <project dir> [--for <этап>] [--pending]

Reads every `documentation/**/open-questions.md` (not `_web-docs/`; `plans/<version>/` included): the
«| Вопрос | Класс |» table, the Класс column found by its header, and the business requirements' question blocks
(`<!-- ce-question: OQ-n; class: …; … -->` and the heading after it). The class is the addressee (doc-versioning →
Открытые вопросы): «Блокирует старт»; «Решить при: <этап>» — схема БД, API, архитектура, макеты, ТЗ на экраны,
тест-кейсы, план, разработка, релиз, эксплуатация; «Отложено»; «Решено: <где>» — kept for history, never printed.
The legacy «Можно решить при архитектуре» reads as «Решить при: архитектура».

  no flag     every open row grouped by addressee: the addressee on a line of its own, then `<file>\t<question>`
              lines; blocks first, then the stages in chain order, then «Отложено», then any other class.
  --for X     the rows for stage X: a group «Блокирует старт» first (they block every stage), then a group
              «Решить при: X»; the last line `вопросов для «X»: N` counts both groups.
  --pending   one line per addressee: `Решить при: архитектура — 3 (requirements/srs/open-questions.md, …)`.

<file> is relative to documentation/. No question files — nothing printed. A «Вопрос» table without a Класс column
is one line on stderr and is skipped (doc_check.py reports it as a problem). Exit 0 whatever is found — the caller
decides; 2 for a stage name outside the list. Importable: `collect(root)`, `pending(rows)`, `STAGE_NO` (where_am_i.py,
docs-consistency). Python 3.9+, standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

BLOCKS = "Блокирует старт"
LATER = "Отложено"
SOLVED = "Решено"
AT = "Решить при:"
LEGACY_ARCH = "Можно решить при архитектуре"
# addressee stage -> its number in the chain (pipeline → the stage table; where_am_i.py prints the same numbers)
STAGE_NO = {"схема БД": 3, "API": 4, "архитектура": 5, "макеты": 7, "ТЗ на экраны": 8, "тест-кейсы": 9,
            "план": 11, "разработка": 12, "релиз": 15, "эксплуатация": 16}
CE_QUESTION = re.compile(r"<!--\s*ce-question:\s*([^;>]+);\s*class:\s*([^;>]+?)\s*(?:;[^>]*)?-->\s*\n+\s*#+\s*(.+)")


class Row(NamedTuple):
    file: str        # relative to documentation/
    question: str
    addressee: str   # «Блокирует старт», a stage of STAGE_NO, «Отложено», or the raw class when it is none of them
    stage: int | None  # the addressee's chain number; 0 for «Блокирует старт»; None for «Отложено» and the rest


def stage_name(text: str) -> str | None:
    """A stage of STAGE_NO named in text, matched without case: «api» → «API»."""
    t = text.strip().rstrip(".").lower()
    return next((s for s in STAGE_NO if s.lower() == t), None)


def addressee(cls: str) -> tuple[str, int | None] | None:
    """The addressee of a Класс cell, or None for a settled row («Решено: …») and an empty cell."""
    c = cls.strip()
    if not c or c.startswith(SOLVED):
        return None
    if c.startswith(BLOCKS):
        return BLOCKS, 0
    if c.startswith(LEGACY_ARCH):
        return "архитектура", STAGE_NO["архитектура"]
    if c.startswith(AT):
        s = stage_name(c[len(AT):])
        return (s, STAGE_NO[s]) if s else (c, None)
    if c.startswith(LATER):
        return LATER, None
    return c, None


def cells(line: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def read_file(path: Path, rel: str, out: list) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for m in CE_QUESTION.finditer(text):   # the business requirements' blocks (brainstorm → business-audience.md)
        who = addressee(m.group(2))
        if who:
            out.append(Row(rel, f"{m.group(1).strip()}. {m.group(3).strip()}", *who))
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("|") or "Вопрос" not in cells(line):
            continue
        head = cells(line)
        if "Класс" not in head:
            print(f"open_questions: {rel}: в таблице вопросов нет столбца «Класс» — пропущена", file=sys.stderr)
            continue
        q, k = head.index("Вопрос"), head.index("Класс")
        for row in lines[i + 2:]:
            if not row.startswith("|"):
                break
            c = cells(row)
            who = addressee(c[k]) if len(c) > k else None
            if who and len(c) > q and c[q]:
                out.append(Row(rel, c[q], *who))


def collect(root: Path) -> list[Row]:
    """Every open row of the project's question files, in file order."""
    doc = root / "documentation"
    out: list[Row] = []
    if not doc.is_dir():
        return out
    for f in sorted(doc.rglob("open-questions.md")):
        if "_web-docs" in f.relative_to(doc).parts:
            continue
        read_file(f, f.relative_to(doc).as_posix(), out)
    return out


def label(name: str) -> str:
    return name if name in (BLOCKS, LATER) or name not in STAGE_NO else f"{AT} {name}"


def order(name: str, stage: int | None) -> tuple:
    return (0, stage) if stage is not None else ((1, 0) if name == LATER else (2, 0))


def grouped(rows: list[Row]) -> list[tuple[str, list[Row]]]:
    groups: dict = {}
    for r in rows:
        groups.setdefault(r.addressee, []).append(r)
    return sorted(groups.items(), key=lambda kv: order(kv[0], kv[1][0].stage))


def pending(rows: list[Row]) -> list[str]:
    """One line per addressee, blocks first: «Решить при: архитектура — 3 (a.md, b.md)»."""
    return [f"{label(name)} — {len(rs)} ({', '.join(dict.fromkeys(r.file for r in rs))})" for name, rs in grouped(rows)]


def main() -> None:
    args = sys.argv[1:]
    for_stage = None
    if "--for" in args:
        i = args.index("--for")
        given = " ".join(args[i + 1:i + 2])
        for_stage = stage_name(given)
        if not for_stage:
            print(f"open_questions: этап «{given}» не из списка: {', '.join(STAGE_NO)}", file=sys.stderr)
            sys.exit(2)
        del args[i:i + 2]
    root = Path(next((a for a in args if not a.startswith("--")), ".")).resolve()
    rows = collect(root)
    if "--pending" in args:
        for line in pending(rows):
            print(line)
        return
    if for_stage:
        mine = [r for r in rows if r.stage == 0] + [r for r in rows if r.addressee == for_stage]
        for name, rs in grouped(mine):
            print(label(name))
            for r in rs:
                print(f"{r.file}\t{r.question}")
        print(f"вопросов для «{for_stage}»: {len(mine)}")
        return
    for name, rs in grouped(rows):
        print(label(name))
        for r in rs:
            print(f"{r.file}\t{r.question}")


if __name__ == "__main__":
    main()
