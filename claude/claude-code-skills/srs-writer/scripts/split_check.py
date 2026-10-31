#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that a single-file SRS was split into srs.md + areas/ as a move: every id, row and use case the same.

    python3 split_check.py [<project dir>] [--before <git ref | file>]

Before: the single `documentation/requirements/srs/srs.md` at `--before` (a git ref, `HEAD` by default — the split
is checked before its commit; or a saved copy of the old file). After: `srs.md` and every `areas/*.md` in the working
tree (srs-writer/references/srs-template.md → Artifact Root and Resume, step 1; Document Structure → Layout).

It reports, one line each:
  lost       an id (A-, FR-, NFR-, BR-, UC-) the old file had that no new file mentions;
  changed    a table row whose first cell is an id, or a `### UC-n.` subsection, whose text differs (spaces aside);
  missing    such a row or use case that is in no new file;
  twice      a row or use case that now sits in two places;
  added      a row or use case the old file did not have;
  misplaced  an FR row or a use case left in srs.md (they belong to an area file), or an NFR / BR / A row moved into
             an area file (they stay in srs.md).
The map tables srs.md gains (`№ | Группа | Файл | FR`, `UC | Название | Файл`) are not rows of the old file and are
skipped. Exit 0 — the split is a pure move; 1 — a line per problem; 2 — no old file to compare with.
Standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SRS = "documentation/requirements/srs"
ID = r"(?:FR|NFR|BR|UC|A)-\d+(?:\.\d+)*"
ANY_ID = re.compile(rf"(?<![\w-])({ID})(?![\w.]*\d)")
ROW = re.compile(rf"^\|\s*({ID})\s*\|")
UC_HEAD = re.compile(r"^###\s+(UC-\d+(?:\.\d+)*)\b")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse(text: str) -> tuple[dict, dict]:
    """{id: [row text]} for table rows led by an id, outside the map tables; {UC id: [subsection text]}."""
    rows: dict = {}
    ucs: dict = {}
    header = ""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-", lines[i + 1]):
            header = line          # a table starts: remember its header
        m = ROW.match(line)
        if m and "Файл" not in header:
            rows.setdefault(m.group(1), []).append(norm(line))
        h = UC_HEAD.match(line)
        if h:
            j = i + 1
            while j < len(lines) and not re.match(r"^#{1,3}\s", lines[j]):
                j += 1
            ucs.setdefault(h.group(1), []).append(norm("\n".join(lines[i:j])))
            i = j
            continue
        i += 1
    return rows, ucs


def old_text(root: Path, before: str) -> str:
    f = Path(before)
    if f.is_file():
        return f.read_text(encoding="utf-8")
    r = subprocess.run(["git", "-C", str(root), "show", f"{before}:{SRS}/srs.md"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"split_check: no {SRS}/srs.md at {before} — give --before <ref or file>", file=sys.stderr)
        sys.exit(2)
    return r.stdout


def main() -> None:
    args = sys.argv[1:]
    before = "HEAD"
    if "--before" in args:
        k = args.index("--before")
        before = args[k + 1] if k + 1 < len(args) else ""
        del args[k:k + 2]
    root = Path(args[0] if args else ".").resolve()
    folder = root / SRS
    index = folder / "srs.md"
    areas = sorted((folder / "areas").glob("*.md"))
    if not index.is_file() or not areas:
        print(f"split_check: {SRS}/srs.md and areas/*.md are not both there — nothing split yet", file=sys.stderr)
        sys.exit(2)

    old = old_text(root, before)
    o_rows, o_ucs = parse(old)
    new: list = []                      # (file name, rows, ucs, text)
    for f in [index] + areas:
        t = f.read_text(encoding="utf-8")
        r, u = parse(t)
        new.append((f.relative_to(folder).as_posix(), r, u, t))

    out: list = []
    now_ids = set().union(*(set(ANY_ID.findall(t)) for *_, t in new))
    for i in sorted(set(ANY_ID.findall(old)) - now_ids):
        out.append(f"lost: {i} — был в старом файле, в новых его нет нигде")

    def compare(kind: str, old_map: dict, pick) -> None:
        for key, texts in old_map.items():
            places = [(name, x) for name, *maps, _ in new for x in pick(maps).get(key, [])]
            if not places:
                out.append(f"missing: {kind} {key} — нет ни в srs.md, ни в areas/")
                continue
            if len(places) > len(texts):
                out.append(f"twice: {kind} {key} — в {', '.join(n for n, _ in places)}")
            for t in texts:
                if t not in [x for _, x in places]:
                    out.append(f"changed: {kind} {key} ({places[0][0]})\n    было:  {t[:300]}\n    стало: {places[0][1][:300]}")
            for name, _ in places:
                in_index = name == "srs.md"
                belongs_to_area = kind == "сценарий" or key.startswith("FR-")
                if in_index and belongs_to_area:
                    out.append(f"misplaced: {kind} {key} остался в srs.md — его место в файле группы areas/")
                elif not in_index and not belongs_to_area:
                    out.append(f"misplaced: {kind} {key} в {name} — строки NFR, BR и акторов остаются в srs.md")

    compare("строка", o_rows, lambda maps: maps[0])
    compare("сценарий", o_ucs, lambda maps: maps[1])
    for name, rows, ucs, _ in new:
        for key in sorted(set(rows) - set(o_rows)):
            out.append(f"added: строка {key} в {name} — в старом файле её не было; разбиение только переносит")
        for key in sorted(set(ucs) - set(o_ucs)):
            out.append(f"added: сценарий {key} в {name} — в старом файле его не было; разбиение только переносит")

    for line in out:
        print("✗", line)
    print(f"split_check: строк {sum(len(v) for v in o_rows.values())}, сценариев {len(o_ucs)}, "
          f"файлов {len(new)}, проблем {len(out)}")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
