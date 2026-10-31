#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a plan's mechanics before plan-review reads it — what code can decide, so no reviewer round is spent on it.

    python3 plan_lint.py documentation/plans/<version>/plan.md [--repo <dir>]

Errors (exit 1), one line each with the unit and what to fix:
  - a U-id used twice; a unit without one of the fields Документы, Файлы, Зависит от, Параллельно, Сложность,
    Почему, Исполнитель, Вложенный;
  - Сложность other than 0 / Low / Mid / High; Исполнитель not in executor-catalog → assignable-implementers.md
    (impl-critical is never written); Вложенный other than `—` or mechanical-worker; impl-ui with a Вложенный;
  - Зависит от naming a unit the plan does not have, or a cycle;
  - two units with Параллельно yes, neither depending on the other, that list the same file;
  - Образец naming a path that is neither in the repository nor in any unit's Файлы;
  - a model name (opus, sonnet, haiku, gpt-…) anywhere in a unit;
  - Документы citing an FR / BR / NFR / UC id the requirements do not have, or an operationId the API lacks.
Warnings (exit 0 when only these):
  - an acceptance criterion of a use case the plan cites that no unit names in Документы or Тестовые сценарии.

The repository is read at its current state (--repo, default the plan's repository): run it before work starts.
Standard library only; the plan format is plan → references/plan-template.md.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

UNIT = re.compile(r"^###\s+U(\d+)\.\s*(.*)$", re.M)
ROW = re.compile(r"^\|\s*\*\*([^*|]+)\*\*\s*\|(.*)\|\s*$", re.M)
REQUIRED = ["Документы", "Файлы", "Зависит от", "Параллельно", "Сложность", "Почему", "Исполнитель", "Вложенный"]
GRADES = {"0", "Low", "Mid", "High"}
PATH = re.compile(r"`([\w./@+-]+/[\w./@*+-]+|[\w-]+\.[\w.]+)`")
MODEL = re.compile(r"\b(?:opus|sonnet|haiku|fable|gpt-\d[\w.-]*)\b", re.I)
REQ_ID = re.compile(r"\b(FR|BR|NFR|UC)-(\d+)(?:\.\d+)?\b")
OPID = re.compile(r"\bapi\s+`([A-Za-z_]\w*)`")


def units(text: str) -> list[dict]:
    out = []
    marks = list(UNIT.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        nxt = re.search(r"^#{1,3}\s", text[m.end():end], re.M)
        block = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():end]
        fields = {k.strip(): v.strip() for k, v in ROW.findall(block)}
        out.append({"id": int(m.group(1)), "title": m.group(2), "block": block, "f": fields,
                    "line": text[: m.start()].count("\n") + 1})
    return out


def deps_of(u: dict) -> set[int]:
    return {int(x) for x in re.findall(r"\bU(\d+)\b", u["f"].get("Зависит от", ""))}


def closure(by_id: dict, n: int) -> set[int]:
    """Every unit n depends on, directly or through others."""
    seen, stack = set(), list(deps_of(by_id[n])) if n in by_id else []
    while stack:
        d = stack.pop()
        if d in seen or d not in by_id:
            continue
        seen.add(d)
        stack.extend(deps_of(by_id[d]))
    return seen


def files_of(u: dict) -> set[str]:
    return {p.rstrip("/") for p in PATH.findall(u["f"].get("Файлы", ""))}


def covers(listed: set[str], path: str) -> bool:
    return any(path == p or path.startswith(p + "/") or (("*" in p) and Path(path).match(p)) for p in listed)


def known_path(repo: Path, p: str, planned: set[str]) -> bool:
    """A path in the repository, a file some unit of the plan lists (it will exist), or — written as a bare file
    name — any tracked or planned file of that name."""
    if (repo / p).exists() or covers(planned, p.rstrip("/")) or any(q.startswith(p.rstrip("/") + "/") for q in planned):
        return True
    if Path(p).name in planned:  # «`dir/a.ts`, `b.ts`» — a sibling written by its name alone
        return True
    if "/" not in p:
        if any(Path(q).name == p for q in planned):
            return True
        r = subprocess.run(["git", "-C", str(repo), "ls-files", f"*/{p}", p], capture_output=True, text=True)
        return bool(r.stdout.strip())
    return False


def assignable(skills: Path) -> set[str]:
    f = skills / "executor-catalog" / "references" / "assignable-implementers.md"
    text = f.read_text(encoding="utf-8") if f.exists() else ""
    part = text.split("## Implementer", 1)[-1].split("## Nested", 1)[0]
    return set(re.findall(r"^\|\s*`([\w-]+)`", part, re.M)) or {"mechanical-worker", "impl-lite", "impl-medium",
                                                                 "impl-hard", "impl-ui"}


def requirement_ids(docs: Path) -> set[str]:
    ids: set[str] = set()
    for f in (docs / "requirements").rglob("*.md") if (docs / "requirements").is_dir() else []:
        ids.update(f"{a}-{b}" for a, b in REQ_ID.findall(f.read_text(encoding="utf-8", errors="replace")))
    return ids


def operation_ids(docs: Path) -> set[str]:
    out: set[str] = set()
    for f in (docs / "api").rglob("*.y*ml") if (docs / "api").is_dir() else []:
        out.update(re.findall(r"operationId:\s*['\"]?(\w+)", f.read_text(encoding="utf-8", errors="replace")))
    return out


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    plan = Path(args[0]).resolve()
    text = plan.read_text(encoding="utf-8")
    repo = Path(args[args.index("--repo") + 1]).resolve() if "--repo" in args else Path(
        subprocess.run(["git", "-C", str(plan.parent), "rev-parse", "--show-toplevel"], capture_output=True,
                       text=True).stdout.strip() or plan.parents[3])
    docs = repo / "documentation" if (repo / "documentation").is_dir() else plan.parents[2]
    skills = Path(__file__).resolve().parents[2]
    us = units(text)
    by_id = {u["id"]: u for u in us}
    errors: list[str] = []
    warnings: list[str] = []
    err = lambda u, msg: errors.append(f"U{u['id']} (строка {u['line']}): {msg}")

    seen: set[int] = set()
    for u in us:
        if u["id"] in seen:
            err(u, "этот номер уже есть у другой задачи")
        seen.add(u["id"])
    names = assignable(skills)
    planned = set().union(*(files_of(u) for u in us)) if us else set()
    for u in us:
        f = u["f"]
        missing = [k for k in REQUIRED if k not in f]
        if missing:
            err(u, "нет полей: " + ", ".join(missing))
        g = f.get("Сложность", "").split()[0] if f.get("Сложность") else ""
        if "Сложность" in f and g not in GRADES:
            err(u, f"Сложность «{f['Сложность']}» — допустимо 0, Low, Mid, High")
        ex = f.get("Исполнитель", "").strip("` ")
        if "Исполнитель" in f and ex not in names:
            err(u, f"Исполнитель «{ex}» не из executor-catalog → assignable-implementers.md ({', '.join(sorted(names))})")
        nested = f.get("Вложенный", "").strip("` ")
        if "Вложенный" in f and nested not in ("—", "-", "", "mechanical-worker"):
            err(u, f"Вложенный «{nested}» — допустимо «—» или mechanical-worker")
        if ex == "impl-ui" and nested == "mechanical-worker":
            err(u, "у impl-ui Вложенный — «—»")
        for d in sorted(deps_of(u)):
            if d not in by_id:
                err(u, f"Зависит от U{d}, а такой задачи в плане нет")
        if u["id"] in closure(by_id, u["id"]):
            err(u, "зависимости замкнуты в цикл")
        m = MODEL.search(u["block"])
        if m:
            err(u, f"в задаче названа модель «{m.group(0)}» — план называет исполнителей, не модели")
        for p in PATH.findall(f.get("Образец", "")):
            if not known_path(repo, p, planned):
                err(u, f"Образец `{p}` — такого файла нет ни в репозитории, ни в «Файлах» какой-либо задачи плана")

    for i, a in enumerate(us):
        for b in us[i + 1:]:
            if not (a["f"].get("Параллельно", "").lower().startswith("yes")
                    and b["f"].get("Параллельно", "").lower().startswith("yes")):
                continue
            if a["id"] in closure(by_id, b["id"]) or b["id"] in closure(by_id, a["id"]):
                continue
            common = files_of(a) & files_of(b)
            if common:
                errors.append(f"U{a['id']} и U{b['id']}: обе «Параллельно: yes», не зависят друг от друга и правят "
                              f"один файл — {', '.join(sorted(common))}")

    req, ops = requirement_ids(docs), operation_ids(docs)
    for u in us:
        cited = u["f"].get("Документы", "")
        if req:
            for a, b in REQ_ID.findall(cited):
                if f"{a}-{b}" not in req:
                    err(u, f"Документы: {a}-{b} — такого номера в требованиях нет")
        if ops:
            for op in OPID.findall(cited):
                if op not in ops:
                    err(u, f"Документы: операции `{op}` в API нет")

    srs = docs / "requirements" / "srs" / "srs.md"
    if srs.exists():
        sys.path.insert(0, str(skills / "ui-test-cases" / "scripts"))
        try:
            from check_coverage import srs_criteria
            named = "\n".join(u["f"].get("Документы", "") + "\n" + u["block"].split("**Тестовые сценарии**")[-1]
                              for u in us)
            cited_ucs = {f"UC-{n}" for n in re.findall(r"\bUC-(\d+)\b", text)}
            for key in srs_criteria(srs):
                uc, ac = key.split(" ", 1)
                if uc in cited_ucs and not re.search(rf"{uc}\b[^\n]*{re.escape(ac)}(?![\w-])|(?<![\w-]){re.escape(ac)}(?![\w-])[^\n]*{uc}\b", named):
                    warnings.append(f"{key}: сценарий есть в плане, а этот критерий не назван ни одной задачей")
        except Exception as e:  # coverage is a hint; never let it hide the errors above
            warnings.append(f"покрытие критериев не проверено: {e}")

    for e in errors:
        print("✗", e)
    for w in warnings:
        print("⚠", w)
    print(f"plan_lint: задач {len(us)}, ошибок {len(errors)}, предупреждений {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
