#!/usr/bin/env python3
"""Check that every acceptance criterion of the SRS has a test case or a «Без интерфейса» line.

usage: python3 check_coverage.py [--docs documentation]
Exit 0 — every AC is covered; 1 — gaps or broken references (printed one per line); 2 — no test cases found.
Standard library only, like check_trace.py beside it.

Reads the AC ids of every use case in requirements/srs/srs.md (`### UC-<n>` headings; AC rows of the
«Критерии приёмки» table or `**AC-…**` bullets) and the coverage table at the end of the set's README.md
(«Критерий | Кейсы»: `UC-1 AC-Exc-1` → `TC-20` or «Без интерфейса»). Fails on:
  - an AC with no row in the coverage table that names a TC or «Без интерфейса»;
  - a coverage row or a case's «Проверяет» line naming an AC the SRS does not have;
  - a coverage row naming a TC that no section holds.
A frontend repository without the SRS (its coverage table lists UC and state rows) is not checked: exit 0.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

UC_HEAD = re.compile(r"^#{2,4}\s*(UC-\d+)\b")
SECTION = re.compile(r"^#{1,2}\s")
AC_ROW = re.compile(r"^\|\s*(AC(?:-(?:Alt|Exc)-\d+)?)\s*\|")
AC_BULLET = re.compile(r"\*\*(AC(?:-(?:Alt|Exc)-\d+)?)\*\*")
TOKEN = re.compile(r"(?<![\w-])(UC-\d+|AC(?:-(?:Alt|Exc)-\d+)?)(?![\w-])")
TC = re.compile(r"\bTC-\d+\b")
CASE = re.compile(r"^## (TC-\d+)\b", re.M)
CHECKS = re.compile(r"^\*\*Проверяет:\*\*(.*)$", re.M)
NO_UI = "без интерфейса"


def srs_criteria(srs: Path) -> list[str]:
    found, uc = [], None
    for line in srs.read_text(errors="replace").splitlines():
        m = UC_HEAD.match(line)
        if m:
            uc = m.group(1)
            continue
        if SECTION.match(line):
            uc = None
            continue
        if uc:
            for ac in AC_ROW.findall(line) + AC_BULLET.findall(line):
                key = f"{uc} {ac}"
                if key not in found:
                    found.append(key)
    return found


def criteria_in(text: str) -> list[str]:
    """`UC-1 AC, AC-Exc-1 · UC-2 AC-Alt-1` -> each `UC-n AC-…` it names."""
    out, uc = [], None
    for tok in TOKEN.findall(text):
        if tok.startswith("UC-"):
            uc = tok
        elif uc:
            out.append(f"{uc} {tok}")
    return out


def check(docs: Path):
    folders = sorted(p for p in docs.glob("ui/**/test-cases") if p.is_dir())
    single = sorted(docs.glob("ui/**/test-cases.md"))
    case_files = [f for d in folders for f in sorted(d.glob("*.md"))] + single
    if not case_files:
        return None
    srs = docs / "requirements" / "srs" / "srs.md"
    if not srs.exists():
        return "no-srs"
    criteria = srs_criteria(srs)
    known = set(criteria)
    cases = {tc for f in case_files for tc in CASE.findall(f.read_text(errors="replace"))}
    covered, errors = set(), []
    for f in [d / "README.md" for d in folders if (d / "README.md").exists()] + single:
        for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            named = criteria_in(cells[0])
            if not named or len(cells) < 2:
                continue
            rest = " ".join(cells[1:])
            where = f"{f.relative_to(docs.parent)}:{n}"
            for key in named:
                if key not in known:
                    errors.append(f"{where}: «{key}» — такого критерия в ТЗ нет")
            for tc in TC.findall(rest):
                if tc not in cases:
                    errors.append(f"{where}: {tc} — такого кейса нет ни в одном разделе")
            if len(named) == 1:
                parts = [rest]
            else:  # `UC-1 AC · AC-Exc-1` | `TC-5 · Без интерфейса` — matched part by part
                parts = [p.strip() for p in rest.split("·")]
                if len(parts) != len(named):
                    errors.append(f"{where}: строка называет критериев {len(named)}, а частей в «Кейсы» {len(parts)} — "
                                  "одна строка на критерий")
                    continue
            for key, part in zip(named, parts):
                if set(TC.findall(part)) & cases or NO_UI in part.lower():
                    covered.add(key)
    proving: dict[str, list[str]] = {}
    for f in case_files:
        text = f.read_text(errors="replace")
        heads = list(CASE.finditer(text))
        for i, h in enumerate(heads):
            body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            m = CHECKS.search(body)
            if not m:
                continue
            for key in criteria_in(m.group(1)):
                if key not in known:
                    line = text[: h.start()].count("\n") + 1
                    errors.append(f"{f.relative_to(docs.parent)}:{line} {h.group(1)}: «Проверяет» называет «{key}» — такого критерия в ТЗ нет")
                else:
                    proving.setdefault(key, []).append(h.group(1))
    missing = [k for k in criteria if k not in covered]
    for key in missing:
        hint = f" (его проверяют {', '.join(proving[key])} — допишите строку в таблицу покрытия)" if key in proving else ""
        errors.append(f"{key}: нет ни кейса, ни строки «Без интерфейса» в таблице покрытия{hint}")
    return len(criteria), len(criteria) - len(missing), errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="documentation")
    a = ap.parse_args()
    result = check(Path(a.docs).resolve())
    if result is None:
        print("check-coverage: тест-кейсов нет — проверять нечего")
        sys.exit(2)
    if result == "no-srs":
        print("check-coverage: ТЗ (requirements/srs/srs.md) в этом репозитории нет — покрытие не сверяется")
        sys.exit(0)
    total, done, errors = result
    for e in errors:
        print("✗", e)
    print(f"check-coverage: критериев в ТЗ {total}, покрыто {done}, ошибок {len(errors)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
