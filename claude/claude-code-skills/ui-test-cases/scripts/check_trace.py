#!/usr/bin/env python3
"""Check the «Трассировка» line of every user test case against the documents it cites.

usage: python3 check_trace.py [--docs documentation] [--quiet]
Exit 0 — every trace resolves; 1 — broken references (printed one per line); 2 — no test cases found.
Standard library only, so it runs in the plugin, in a git pre-commit hook and in CI alike.

Checks, per case (`## TC-<n>.` … next case):
  - a «Трассировка:» line exists;
  - every `шаг N` is a row of the case's table;
  - every `эл. M` is an element number of a screen spec the case names (S-<n> in its «Экран» line);
  - every frame nodeId (`12:160`) appears in those screen specs or in the frames register;
  - every `operationId` written before `→` exists in the OpenAPI, and a status code after it is among
    that operation's responses.
Warnings (not failures): a step that selects or enters something with no `шаг N →` mapping.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

CASE = re.compile(r"^## (TC-\d+)\b.*$", re.M)
TRACE = re.compile(r"Трассировка:(.*?)(?:</sub>|$)", re.S)
STEP_MAP = re.compile(r"шаг\s+(\d+)\s*→([^;·]*)")
ELEM = re.compile(r"эл\.\s*(\d+)")
NODE = re.compile(r"(?<![\d.])(\d{1,6}:\d{1,7})(?![\d:])")
OP = re.compile(r"`([a-z][A-Za-z0-9]+)`\s*→\s*(?:mock\s+)?(\d{3})?")
SCREEN = re.compile(r"\((S-\d+)\)|\b(S-\d+)\b")
ROW = re.compile(r"^\|\s*(\d+)\s*\|", re.M)
ACTION = re.compile(r"^(Выбрать|Ввести|Нажать|Отметить|Указать|Заполнить)", re.I)


def load_specs(docs: Path) -> dict[str, tuple[str, set[str]]]:
    specs = {}
    for f in sorted(docs.glob("ui/**/screen-specs/S-*.md")):
        m = re.match(r"(S-\d+)", f.name)
        if m:
            text = f.read_text(errors="replace")
            specs[m.group(1)] = (text, set(ROW.findall(text)))
    return specs


def load_operations(docs: Path) -> dict[str, str]:
    ops = {}
    for f in docs.glob("api/**/*.y*ml"):
        text = f.read_text(errors="replace")
        for m in re.finditer(r"operationId:\s*['\"]?([A-Za-z0-9_]+)", text):
            ops.setdefault(m.group(1), "")
            ops[m.group(1)] += text
    return ops


def check(docs: Path):
    case_files = sorted(docs.glob("ui/**/test-cases/*.md"))
    case_files += sorted(docs.glob("ui/**/test-cases.md"))
    if not case_files:
        return None, [], []
    specs = load_specs(docs)
    register = "".join(f.read_text(errors="replace") for f in docs.glob("ui/**/frames-register.md"))
    ops = load_operations(docs)
    api_text = "".join(f.read_text(errors="replace") for f in docs.glob("api/**/*.y*ml"))
    errors, warnings = [], []
    for f in case_files:
        text = f.read_text(errors="replace")
        heads = list(CASE.finditer(text))
        for i, h in enumerate(heads):
            body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            line = text[: h.start()].count("\n") + 1
            where = f"{f.relative_to(docs.parent)}:{line} {h.group(1)}"
            t = TRACE.search(body)
            if not t:
                errors.append(f"{where}: нет строки «Трассировка»")
                continue
            trace = t.group(1)
            head = body[: t.start()]
            rows = [r for r in re.findall(r"^\|\s*(\d+)\s*\|(.*)$", head, re.M)]
            steps = {n for n, _ in rows}
            screens = {a or b for a, b in SCREEN.findall(head.split("|", 1)[0])}
            spec_text = "".join(specs[s][0] for s in screens if s in specs)
            elems = set().union(*(specs[s][1] for s in screens if s in specs)) if screens & specs.keys() else set()
            for s in sorted(screens - specs.keys()):
                errors.append(f"{where}: экран {s} — нет файла ТЗ screen-specs/{s}-*.md")
            mapped = set()
            for n, refs in STEP_MAP.findall(trace):
                mapped.add(n)
                if n not in steps:
                    errors.append(f"{where}: «шаг {n}» — в таблице кейса нет шага {n}")
            if elems:
                for e in sorted(set(ELEM.findall(trace)), key=int):
                    if e not in elems:
                        errors.append(f"{where}: «эл. {e}» — нет в ТЗ {', '.join(sorted(screens))}")
            frame_parts = re.findall(r"кадр\w*\s+([^·]*)", trace) + re.findall(r"\(([^)]*)\)", trace)
            for node in sorted({n for part in frame_parts for n in NODE.findall(part)}):
                if node not in spec_text and node not in register:
                    errors.append(f"{where}: кадр {node} — нет ни в ТЗ, ни в реестре кадров")
            if ops:
                for op, code in OP.findall(trace):
                    if op not in ops and re.search(rf"\b{op}\b", api_text):
                        continue  # a parameter or field name, not a call
                    if op not in ops:
                        errors.append(f"{where}: `{op}` — нет такой операции или поля в OpenAPI")
                    elif code and not re.search(rf"['\"]?{code}['\"]?\s*:", ops[op]):
                        errors.append(f"{where}: `{op}` → {code} — такого ответа у операции нет")
            for n, cell in rows:
                if n not in mapped and ACTION.match(cell.split("|")[0].strip()):
                    warnings.append(f"{where}: шаг {n} что-то выбирает или вводит, но в трассировке нет «шаг {n} →»")
    return len(case_files), errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="documentation")
    ap.add_argument("--quiet", action="store_true", help="errors only")
    a = ap.parse_args()
    n, errors, warnings = check(Path(a.docs).resolve())
    if n is None:
        print("check-trace: тест-кейсов нет — проверять нечего")
        sys.exit(0)
    for e in errors:
        print("✗", e)
    if not a.quiet:
        for w in warnings:
            print("⚠", w)
    print(f"check-trace: файлов {n}, ошибок {len(errors)}, предупреждений {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
