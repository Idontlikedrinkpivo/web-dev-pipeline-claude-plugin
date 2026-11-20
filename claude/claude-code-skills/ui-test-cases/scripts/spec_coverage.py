# -*- coding: utf-8 -*-
"""Which rows of the screen specs no test case names: hints for the review of the test-case set.

usage: python3 spec_coverage.py [--docs documentation]
Always exit 0 (2 — no test cases): it prints hints, not failures. A hint is a row worth a look — a reviewer
(`doc-review` on a `test-cases` document, the design lens) decides whether a case is missing or the set only names
the row in other words. A real gap becomes a finding, and the writer adds the case.

Reads every screen spec `ui/**/screen-specs/S-*.md` and every test-case set `ui/**/test-cases/` (README.md and the
section files), and per screen:
  - «Состояния экрана»: a row whose state no case's trace names («состояние «…»») and no row of the README's
    states → cases table (the cell, split at «;», a part starting with «·» continuing the previous one) names
    with a TC id. Rows «не бывает» and «Общие состояния» are skipped: the app-wide states have their own rows.
  - «Ошибки ответов»: a row with an `operationId` and a status that no case of that screen names together — the
    operation and the status in one stretch of a case («`cancelBooking` → mock 409»,
    «`completeDescription` 404, 409 …»), nor the README's «Без интерфейса» or gaps. Rows the general handler
    takes («общий обработчик»), rows «не бывает» and rows the spec calls a gap («Разрыв») are skipped.
A case belongs to every screen its text names (S-<n>). «Поля ввода» is not read: specs write it as a table or as
prose, and the reviewer reads it. Standard library only, like check_trace.py and check_coverage.py beside it.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CASE = re.compile(r"^## (TC-\d+)\b.*$", re.M)
SID = re.compile(r"\bS-\d+\b")
TCID = re.compile(r"\bTC-\d+")
TRACE_STATE = re.compile(r"состояни[ея]\s+«(.+?)»(?=\s*(?:[·;,(]|</sub>|$))", re.M)
OP_SPAN = re.compile(r"`([A-Za-z_]\w*)`([^·;`\n]{0,160})")
CODE = re.compile(r"(?<![\d:.])([1-5]\d\d)(?![\d:])")
SKIP_ERR = ("не бывает", "общий обработчик", "разрыв")


def norm(s: str) -> str:
    """A state's name without ids in brackets, quotes and backticks, lower case: «Empty (UC-3 Alt-1)» → «empty»."""
    s = re.sub(r"\([^)]*\)|\[[^\]]*\]", "", s).replace("`", "").replace("«", "").replace("»", "")
    return re.sub(r"\s+", " ", s).strip(" ·;,.").lower()


def section(text: str, head: str) -> str:
    m = re.search(rf"^## {head}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def rows(text: str):
    """Data rows of every table in a section: header rows (followed by `|---`) dropped."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("|") or re.match(r"\|\s*:?-{3}", line):
            continue
        if i + 1 < len(lines) and re.match(r"\|\s*:?-{3}", lines[i + 1]):
            continue
        yield [c.strip() for c in line.strip().strip("|").split("|")]


def collect(folders: list[Path]):
    """Per screen: the state names the set uses, the (operation, status) pairs its cases name, and the README text
    outside the cases (for «Без интерфейса» and the gaps)."""
    states: dict[str, set[str]] = {}
    pairs: dict[str, set[tuple[str, str]]] = {}
    readme = ""
    for d in folders:
        for f in sorted(d.glob("*.md")):
            text = f.read_text(errors="replace")
            if f.name == "README.md":
                readme += text
                for line in text.splitlines():
                    if not (line.startswith("|") and TCID.search(line)):
                        continue
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    sids = SID.findall(cells[0]) or ["*"]
                    for cell in cells[1:]:
                        head = ""
                        for part in cell.split(";"):
                            p = norm(part)
                            if not p:
                                continue
                            if part.strip().startswith("·") and head:
                                p = f"{head} · {p}"
                            else:
                                head = p.split(" · ")[0]
                            for s in sids:
                                states.setdefault(s, set()).add(p)
                continue
            heads = list(CASE.finditer(text))
            for i, h in enumerate(heads):
                body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
                sids = set(SID.findall(body)) or {"*"}
                names = {norm(m.group(1)) for m in TRACE_STATE.finditer(body)}
                found = {(m.group(1), c) for m in OP_SPAN.finditer(body) for c in CODE.findall(m.group(2))}
                for s in sids:
                    states.setdefault(s, set()).update(names)
                    pairs.setdefault(s, set()).update(found)
    return states, pairs, readme


def named(name: str, known: set[str]) -> bool:
    """The set names this state: the same name, or its last «·» part alone, or a longer name starting with it."""
    n = norm(name)
    last = n.split(" · ")[-1]
    return any(x == n or x == last or x.endswith(" · " + last) or (len(n) > 4 and x.startswith(n)) for x in known)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="documentation")
    docs = Path(ap.parse_args().docs).resolve()
    folders = sorted(p for p in docs.glob("ui/**/test-cases") if p.is_dir())
    if not folders:
        print("spec-coverage: тест-кейсов нет — сверять нечего")
        sys.exit(2)
    states, pairs, readme = collect(folders)
    st_total = st_hint = er_total = er_hint = 0
    for spec in sorted(docs.glob("ui/**/screen-specs/S-*.md")):
        text = spec.read_text(errors="replace")
        m = SID.match(spec.name)
        if not m:
            continue
        sid = m.group(0)
        known = states.get(sid, set()) | states.get("*", set())
        for c in rows(section(text, "Состояния экрана")):
            low = " ".join(c).lower()
            if not c[0] or "не бывает" in low or c[0].lower().startswith("общие состояния"):
                continue
            st_total += 1
            if not named(c[0], known):
                st_hint += 1
                print(f"⚠ {sid}: состояние «{c[0]}» — его не называет ни трассировка кейса, ни таблица состояний README")
        got = pairs.get(sid, set()) | pairs.get("*", set())
        for c in rows(section(text, "Ошибки ответов")):
            if len(c) < 3:
                continue
            ops = re.findall(r"`([A-Za-z_]\w*)`", c[0])
            codes = CODE.findall(c[1])
            if not ops or not codes or any(w in c[2].lower() for w in SKIP_ERR):
                continue
            er_total += 1
            if any((o, k) in got for o in ops for k in codes):
                continue
            if any(o in readme for o in ops) and any(re.search(rf"`{o}`[^|\n]*\b{k}\b", readme)
                                                     for o in ops for k in codes):
                continue
            er_hint += 1
            print(f"⚠ {sid}: ответ {', '.join(f'`{o}`' for o in ops)} → {', '.join(codes)} — ни один кейс экрана "
                  "не называет эту операцию с этим кодом")
    print(f"spec-coverage: состояний {st_total}, без явного кейса {st_hint}; исходов ответов {er_total}, "
          f"без явного кейса {er_hint} — подсказки для ревью, не ошибки")


if __name__ == "__main__":
    main()
