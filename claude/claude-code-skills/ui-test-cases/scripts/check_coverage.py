#!/usr/bin/env python3
"""Check that every acceptance criterion of the SRS has a test case or a «Без интерфейса» line.

usage: python3 check_coverage.py [--docs documentation]
Exit 0 — every AC is covered; 1 — gaps or broken references (printed one per line); 2 — no test cases found.
Standard library only, like check_trace.py beside it.

Reads the AC ids of every use case in requirements/srs/srs.md and its areas/*.md (`### UC-<n>` headings; AC rows of the
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
AC_ROW = re.compile(r"^\|\s*(AC(?:-(?:Alt|Exc)-\d+)?)\s*(?:\(([^)|]*)\))?\s*\|")
AC_BULLET = re.compile(r"\*\*(AC(?:-(?:Alt|Exc)-\d+)?)\s*(?:\(([^)*]*)\))?\*\*")
TOKEN = re.compile(r"(?<![\w-])(UC-\d+|AC-(?:Alt|Exc)-\d+|AC(?:\s*\([^)]*\))?)(?![\w-])")
MAIN_FLOW = ("основной поток", "main flow", "")


def ac_key(ac: str, label: str | None = None) -> str:
    """`AC (обновление)` → «AC(обновление)»; `AC (основной поток)` → «AC»; AC-Alt-n / AC-Exc-n keep no label."""
    m = re.fullmatch(r"(AC)\s*\(([^)]*)\)", ac.strip())
    if m:
        ac, label = m.group(1), m.group(2)
    if ac != "AC":
        return ac
    label = (label or "").strip().lower()
    return "AC" if label in MAIN_FLOW else f"AC({label})"
TC = re.compile(r"\bTC-\d+\b")
CASE = re.compile(r"^## (TC-\d+)\b", re.M)
CHECKS = re.compile(r"^\*\*Проверяет:\*\*(.*)$", re.M)
NO_UI = "без интерфейса"


def srs_all(srs: Path) -> tuple[list[str], set[str]]:
    """Every `UC-n AC-…` of the SRS — srs.md and, when the SRS is split, every areas/*.md beside it (srs.md is then
    only the table of contents): the criteria that need a case, and those withdrawn («[deprecated …]») — they still
    exist, so a reference to one is not an unknown id, but they need no case."""
    found, withdrawn, uc = [], set(), None
    files = [srs] + sorted((srs.parent / "areas").glob("*.md"))
    lines = [l for f in files for l in (f.read_text(errors="replace").splitlines() + ["# end"])]
    for line in lines:
        m = UC_HEAD.match(line)
        if m:
            uc = m.group(1)
            continue
        if SECTION.match(line):
            uc = None
            continue
        if uc:
            for ac, label in AC_ROW.findall(line) + AC_BULLET.findall(line):
                key = f"{uc} {ac_key(ac, label)}"
                if "[deprecated" in line.lower():
                    withdrawn.add(key)
                elif key not in found:
                    found.append(key)
    return found, withdrawn - set(found)


def srs_criteria(srs: Path) -> list[str]:
    """The criteria that need a case (srs_all without the withdrawn ones)."""
    return srs_all(srs)[0]


def resolve(key: str, known: set[str]) -> str:
    """«UC-5 AC(чужие брони)» is a labelled criterion only when the SRS has that label; otherwise the brackets are a
    comment and the criterion is the main flow's «UC-5 AC»."""
    if key in known or "(" not in key:
        return key
    plain = key.split("(", 1)[0]
    return plain if plain in known else key


def labels_hint(key: str, known: set[str]) -> str:
    """For «UC-12 AC» when the SRS names its main criteria by label: which labels there are."""
    if not key.endswith(" AC"):
        return ""
    same = sorted(k.split(" ", 1)[1] for k in known if k.startswith(key + "("))
    return f" (у {key[:-3]} основные критерии с подписями: {', '.join(same)} — назовите нужный)" if same else ""


def criteria_in(text: str) -> list[str]:
    """`UC-1 AC, AC-Exc-1 · UC-2 AC-Alt-1` -> each `UC-n AC-…` it names."""
    out, uc = [], None
    for tok in TOKEN.findall(text):
        if tok.startswith("UC-"):
            uc = tok
        elif uc:
            out.append(f"{uc} {ac_key(tok)}")
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
    criteria, withdrawn = srs_all(srs)
    known = set(criteria) | withdrawn
    cases = {tc for f in case_files for tc in CASE.findall(f.read_text(errors="replace"))}
    covered, errors = set(), []
    for f in [d / "README.md" for d in folders if (d / "README.md").exists()] + single:
        for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            k = 0   # the leading id cells: «UC-1 AC-Exc-1 | TC-20» has one, «UC-1 | AC-Exc-1 | TC-20» two
            while k < len(cells) - 1 and TOKEN.search(cells[k]) and not TC.search(cells[k]) \
                    and NO_UI not in cells[k].lower():
                k += 1
            named = [resolve(x, known) for x in criteria_in(" ".join(cells[:k]))]
            if not named or len(cells) <= k:
                continue
            rest = " ".join(cells[k:])
            where = f"{f.relative_to(docs.parent)}:{n}"
            for key in named:
                if key not in known:
                    errors.append(f"{where}: «{key}» — такого критерия в ТЗ нет{labels_hint(key, known)}")
            for tc in TC.findall(rest):
                if tc not in cases:
                    errors.append(f"{where}: {tc} — такого кейса нет ни в одном разделе")
            if len(named) == 1:
                parts = [rest]
            else:  # `UC-1 AC · AC-Exc-1` | `TC-5 · Без интерфейса` — matched part by part; one part covers them all
                parts = [p.strip() for p in rest.split("·")]
                if len(parts) == 1:
                    parts = parts * len(named)
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
            for key in (resolve(x, known) for x in criteria_in(m.group(1))):
                if key not in known:
                    line = text[: h.start()].count("\n") + 1
                    errors.append(f"{f.relative_to(docs.parent)}:{line} {h.group(1)}: «Проверяет» называет «{key}» — такого критерия в ТЗ нет{labels_hint(key, known)}")
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
