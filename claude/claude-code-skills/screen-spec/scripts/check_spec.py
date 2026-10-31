#!/usr/bin/env python3
"""Mechanical checks of the screen specs (ТЗ на экран) against the OpenAPI contract and each other.

usage: python3 check_spec.py [--docs documentation] [S-1 S-3 ...]
Exit 0 — nothing found; 1 — misses (printed one per line, grouped by file); 2 — no screen specs found.
Standard library only; the OpenAPI parser is the one of ui-test-cases/scripts/check_trace.py.

Per file (documentation/ui/**/screen-specs/S-*.md, or only the S-ids named):
  - frontmatter has version, updated, sources and figma;
  - the template's sections are present and in order (Поля ввода may be absent);
  - every operation the file calls — «Загрузка и вызовы» after `→`, «Ошибки ответов» first column, a
    «Метод и поля» or «Поля ввода» cell that starts with an operation — exists in the
    contract with the same spelling;
  - every non-success status those operations declare has a row in «Ошибки ответов»: a row of that
    operation, or a «любая» row naming the code or its range (`5xx`); «иной код» rows cover nothing;
  - no look words (colour, borders, px, cursor, hover) outside code spans, with the section they sit in.
Across the files of one screen-specs folder: the «любая» rows of «Ошибки ответов» (the общий обработчик)
read the same in every file; a file that differs from the most common set is named with the rows.
The frame nodeIds are not checked here: they need Figma.
"""
from __future__ import annotations
import argparse, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ui-test-cases" / "scripts"))
from check_trace import load_operations  # noqa: E402  (operationId -> declared status keys)

SECTIONS = ["Журнал изменений", "Экран", "Загрузка и вызовы", "Элементы", "Поля ввода",
            "Состояния экрана", "Ошибки ответов", "Производные значения", "Разрывы"]
OPTIONAL = {"Поля ввода"}
FRONT_KEYS = ("version", "updated", "sources", "figma")
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
CALL = re.compile(rf"→\s*(?:операция\s+)?`({IDENT})`")
CELL_START = re.compile(rf"^`({IDENT})`\s*(?::|←|→)")
OUTCOME_CALL = re.compile(rf"→\s*операци[яю]\s+`({IDENT})`")
CODE = re.compile(r"(?<!\d)([1-5]\d\d|[1-5]xx)(?!\d)", re.I)
LOOK = re.compile(r"цвет|зелён|зелен|красн|серым|обводк|шрифт|жирн|ховер|hover|"
                  r"курсор\w*\s+(?:мыши|руки|меняется|в виде)|cursor:\s*pointer|(?<![\w-])\d*\s?px\b", re.I)
SPAN = re.compile(r"`[^`]*`")


def sections(text: str) -> dict[str, tuple[int, list[str]]]:
    """«## name» -> (line number, its lines up to the next «## »); «### M<n>» stays inside its section."""
    out, name, start, buf = {}, None, 0, []
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            if name:
                out[name] = (start, buf)
            name, start, buf = line[3:].strip(), i, []
        elif name:
            buf.append(line)
    if name:
        out[name] = (start, buf)
    return out


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_rows(lines: list[str]) -> list[list[str]]:
    rows = [cells(l) for l in lines if l.lstrip().startswith("|")]
    return [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]  # header and rule dropped


def frontmatter(text: str) -> str:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def called_operations(secs: dict) -> set[str]:
    ops: set[str] = set()
    for name, (_, lines) in secs.items():
        body = "\n".join(lines)
        if name == "Загрузка и вызовы":
            ops.update(CALL.findall(body))
        if name == "Элементы":
            ops.update(OUTCOME_CALL.findall(body))
        if name in ("Элементы", "Поля ввода"):
            for row in table_rows(lines):
                for c in row:
                    for part in re.split(r"<br>", c):
                        m = CELL_START.match(part.strip())
                        if m:
                            ops.add(m.group(1))
        if name == "Ошибки ответов":
            for row in table_rows(lines):
                if row and not row[0].startswith("любая"):
                    ops.update(row_operations(row[0]))
    return ops


def row_operations(cell: str) -> list[str]:
    """The operations a «Ошибки ответов» first cell names; a note in brackets (`dry_run` = `true`) is not one."""
    return re.findall(rf"`({IDENT})`", re.sub(r"\([^)]*\)", "", cell))


def error_rows(secs: dict) -> list[list[str]]:
    return table_rows(secs.get("Ошибки ответов", (0, []))[1])


def covered(op: str, code: str, rows: list[list[str]]) -> bool:
    for row in rows:
        if len(row) < 2 or "иной код" in row[1]:
            continue
        names = row_operations(row[0])
        if row[0].startswith("любая"):
            if "кроме" in row[0] and op in names:
                continue
        elif op not in names:
            continue
        for c in CODE.findall(row[1]):
            c = c.upper()
            if c == code or (c.endswith("XX") and c[0] == code[0]) or (code.endswith("XX") and c[0] == code[0]):
                return True
    return False


def check_file(f: Path, ops: dict[str, set[str]], api_text: str) -> list[str]:
    text = f.read_text(errors="replace")
    out: list[str] = []
    front = frontmatter(text)
    missing = [k for k in FRONT_KEYS if not re.search(rf"^{k}\s*:", front, re.M)]
    if missing:
        out.append(f"frontmatter: нет {', '.join(missing)}")
    secs = sections(text)
    present = [s for s in SECTIONS if s in secs]
    for s in SECTIONS:
        if s not in secs and s not in OPTIONAL:
            out.append(f"нет раздела «{s}»")
    order = [s for s in secs if s in SECTIONS]
    if order != present:
        out.append(f"разделы не по порядку шаблона: {' → '.join(order)}")
    if ops:
        by_lower = {name.lower(): name for name in ops}
        used = called_operations(secs)
        rows = error_rows(secs)
        for op in sorted(used):
            if op not in ops and op.lower() not in by_lower and re.search(rf"\b{re.escape(op)}\b", api_text):
                continue  # a parameter or field of the contract, not a call
            if op not in ops:
                hint = f" (в контракте `{by_lower[op.lower()]}`)" if op.lower() in by_lower else ""
                out.append(f"`{op}` — нет такой операции в контракте{hint}")
                continue
            for code in sorted(ops[op]):
                if code == "DEFAULT" or code[0] in "123":
                    continue
                if not covered(op, code, rows):
                    out.append(f"«Ошибки ответов»: `{op}` объявляет {code} — строки нет")
    for name, (start, lines) in secs.items():
        for i, line in enumerate(lines, start + 1):
            m = LOOK.search(SPAN.sub("", line))
            if m:
                out.append(f"строка {i} («{name}»): слово о внешнем виде «{m.group(0).strip()}»")
    return out


def general_handler(f: Path) -> tuple[str, ...]:
    rows = error_rows(sections(f.read_text(errors="replace")))
    return tuple(" | ".join(r) for r in rows if r and r[0].startswith("любая"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="documentation")
    ap.add_argument("screens", nargs="*", help="S-ids to check (default: all)")
    a = ap.parse_args()
    docs = Path(a.docs).resolve()
    files = sorted(docs.glob("ui/**/screen-specs/S-*.md"))
    if not files:
        print("check-spec: файлов ТЗ на экран нет — проверять нечего")
        sys.exit(2)
    wanted = set(a.screens)
    ops = load_operations(docs)
    api_text = "".join(p.read_text(errors="replace") for p in docs.glob("api/**/*.y*ml"))
    if not ops:
        print("check-spec: в documentation/api/ нет операций — сверка с контрактом пропущена")
    total = 0
    for f in files:
        sid = re.match(r"(S-\d+)", f.name).group(1)
        if wanted and sid not in wanted:
            continue
        misses = check_file(f, ops, api_text)
        total += len(misses)
        for m in misses:
            print(f"✗ {f.relative_to(docs.parent)}: {m}")
    for folder in sorted({f.parent for f in files}):
        group = [f for f in files if f.parent == folder]
        sets = {f: general_handler(f) for f in group}
        common, _ = Counter(sets.values()).most_common(1)[0]
        for f, rows in sets.items():
            if rows != common and (not wanted or re.match(r"(S-\d+)", f.name).group(1) in wanted):
                total += 1
                extra = [r for r in rows if r not in common]
                lost = [r for r in common if r not in rows]
                print(f"✗ {f.relative_to(docs.parent)}: общий обработчик не совпадает с остальными ТЗ "
                      f"(лишние или изменённые строки: {len(extra)}, недостающие: {len(lost)})")
                for r in extra[:3]:
                    print(f"    + {r[:160]}")
                for r in lost[:3]:
                    print(f"    − {r[:160]}")
    print(f"check-spec: файлов {len(files) if not wanted else len(wanted)}, замечаний {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
