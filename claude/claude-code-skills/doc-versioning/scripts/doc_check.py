#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the form of the pipeline's contract documents — what code can decide, so a stage closes on facts.

    python3 doc_check.py [<project dir>] [--only <path> …] [--quiet]

Over the documents of the Registry (doc-versioning → Registry) that exist — SRS (srs.md + areas/), DB schema,
OpenAPI, the three architecture documents, the screen specs — and the open-questions files beside them:

  frontmatter   SRS: title, date, updated, version — and no sources / grilled / reviewed. Every other one: updated,
                version, `sources:` (plural; pins or `stated-directly`), never `source:`. DB schema: `migration:`.
  journal       «## Журнал изменений»: the five columns Версия · Дата · Изменение · Тип · Кого затрагивает, newest
                first, the first row's Версия = `version`, Тип one of ломает / добавляет / уточняет (— only on
                «первый выпуск»), no empty cell. OpenAPI: info.x-changelog's first version = info.version.
  pins          every `path@version` in sources: the path exists; the version is not ahead of the source's own and
                is one the source has had (a row of its journal).
  ids           an FR / NFR / BR / UC / A id (SRS) or an operationId (OpenAPI) that the main branch has and the
                working copy lost, with no «удалён: <id>» journal row — a renumber or a silent deletion.
  migrations    a migration file the main branch has, changed or deleted (they are append-only); the schema's
                `migration:` is not the newest file's number.
  openapi       an operationId used twice; a `$ref` to a file that does not exist or to a component no file
                defines; an operation without a 500 (or 5XX / default) response.
  questions     an open-questions.md without `# Открытые вопросы` or the «Вопрос | Класс» table, or with a Класс
                other than Блокирует старт / Можно решить при архитектуре / Отложено; an empty one.

Exit 0 — clean; 1 — a line per problem. Run at a stage's close before the stamp commit (pipeline → Commit each
document); push_branch.py and docs-consistency run it too. Standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline" / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "ui-test-cases" / "scripts"))
import where_am_i as w  # noqa: E402

COLUMNS = ["Версия", "Дата", "Изменение", "Тип", "Кого затрагивает"]
TYPES = {"ломает", "добавляет", "уточняет"}
CLASSES = {"Блокирует старт", "Можно решить при архитектуре", "Отложено"}
SRS_ID = re.compile(r"(?<![\w-])((?:FR|NFR|BR|UC|A)-\d+(?:\.\d+)?)(?![\w.-]*\d)")


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def journal_table(text: str) -> tuple[list[str], list[list[str]]] | None:
    m = re.search(r"^## Журнал изменений\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    lines = []
    for l in m.group(1).splitlines():   # the first table only: older documents keep a second one below it
        if l.strip().startswith("|"):
            lines.append(l)
        elif lines:
            break
    if len(lines) < 2:
        return [], []
    cells = lambda l: [c.strip() for c in re.split(r"(?<!\\)\|", l.strip().strip("|"))]
    return cells(lines[0]), [cells(l) for l in lines[2:]]


def check_doc(root: Path, doc: "w.Doc", by_path: dict, out: list) -> None:
    rel, text = doc.rel, w.read(doc.path)
    say = lambda msg: out.append(f"{rel}: {msg}")
    is_srs, is_api = rel.endswith("srs/srs.md"), rel.endswith("openapi.yaml")
    unversioned = "business-requirements" in rel   # doc-versioning → Registry: no version, no journal
    meta = doc.meta
    if isinstance(meta.get("sources"), str):      # `sources: [a, b]` written inline
        meta["sources"] = [x.strip().strip("'\"") for x in meta["sources"].strip("[]").split(",") if x.strip()]
    if not is_api:
        head = re.match(r"---\n(.*?)\n---", text, re.S)
        keys = set(re.findall(r"^([A-Za-z_][\w-]*):", head.group(1), re.M)) if head else set()
        if not head:
            say("нет шапки (frontmatter)")
        elif is_srs:
            for k in ("title", "date", "updated", "version"):
                if k not in keys:
                    say(f"в шапке ТЗ нет `{k}`")
            for k in ("sources", "grilled", "reviewed"):
                if k in keys:
                    say(f"в шапке ТЗ лишнее поле `{k}` — у ТЗ только title, date, updated, version")
        elif unversioned:
            if "source" in keys:
                say("поле `source:` — правильно `sources:` (во множественном числе)")
        else:
            for k in ("updated", "version"):
                if k not in keys:
                    say(f"в шапке нет `{k}`")
            if "source" in keys:
                say("поле `source:` — правильно `sources:` (во множественном числе)")
            if "sources" not in keys:
                say("нет `sources:` — ссылки на источники с версиями или `stated-directly`")
            if rel.endswith("db/schema.md") and "migration" not in keys:
                say("в шапке схемы нет `migration:` — номер последнего файла миграции")
    version = meta.get("version", "")
    if unversioned:
        pass
    elif is_api:
        rows = meta.get("rows", [])
        if rows and version and rows[0][0] != version:
            say(f"info.x-changelog: первая запись {rows[0][0]}, а info.version {version}")
    else:
        jt = journal_table(text)
        if jt is None:
            say("нет раздела «## Журнал изменений»")
        else:
            header, rows = jt
            if header and header[:5] != COLUMNS:
                say(f"журнал: столбцы «{' | '.join(header)}» — нужны «{' | '.join(COLUMNS)}»")
            prev = None
            for i, r in enumerate(rows):
                if len(r) < 5:
                    say(f"журнал, строка {i + 1}: ячеек {len(r)} вместо пяти")
                    continue
                if any(not c for c in r[:5]):
                    say(f"журнал, строка {i + 1} ({r[0]}): пустая ячейка — пишется «—»")
                if r[3] not in TYPES and r[3] not in ("—", "-"):
                    say(f"журнал, строка {i + 1} ({r[0]}): Тип «{r[3]}» — ломает, добавляет или уточняет")
                if prev and w.VERSION_RX.search(r[0]) and w.VERSION_RX.search(prev) and w.vkey(r[0]) > w.vkey(prev):
                    say(f"журнал, строка {i + 1}: {r[0]} ниже {prev} — новые строки идут сверху")
                prev = r[0]
            if rows and version and rows[0][0] != version:
                say(f"журнал: первая строка {rows[0][0]}, а в шапке version {version}")
    for src in [] if unversioned else meta.get("sources", []):   # a BRD cites the user's own materials
        if src == "stated-directly":
            continue
        path, _, pin = src.partition("@")
        if not (root / path).exists() and not (doc.path.parent / path).exists():
            say(f"источник `{path}` не найден")
            continue
        source = by_path.get(path)
        if pin and source and source.meta.get("version"):
            cur = source.meta["version"]
            if w.vkey(pin) > w.vkey(cur):
                say(f"источник {Path(path).name}@{pin} — впереди самого источника ({cur})")
            elif pin != cur and pin not in {r[0] for r in source.rows}:
                say(f"источник {Path(path).name}@{pin} — у источника такой версии не было (журнал: "
                    f"{', '.join(sorted({r[0] for r in source.rows}, key=w.vkey, reverse=True)[:4]) or 'пуст'})")


def srs_text(root: Path, ref: str | None) -> str:
    rel = "documentation/requirements/srs"
    if ref is None:
        files = [root / rel / "srs.md"] + sorted((root / rel / "areas").glob("*.md"))
        return "\n".join(w.read(f) for f in files)
    names = [n for n in git(root, "ls-tree", "-r", "--name-only", ref, "--", rel).splitlines()
             if n.endswith(".md") and (n.endswith("/srs.md") or "/areas/" in n)]
    return "\n".join(git(root, "show", f"{ref}:{n}") for n in names)


def check_ids(root: Path, ref: str | None, out: list) -> None:
    if not ref:
        return
    before, now = srs_text(root, ref), srs_text(root, None)
    if before and now:
        removed_rows = " ".join(re.findall(r"(?i)удал[её]н[^|]*", now))
        lost = sorted(set(SRS_ID.findall(before)) - set(SRS_ID.findall(now)) - set(SRS_ID.findall(removed_rows)),
                      key=lambda x: (x.split("-")[0], [int(n) for n in re.findall(r"\d+", x)]))
        for i in lost:
            out.append(f"documentation/requirements/srs: {i} был в {ref}, а теперь его нет нигде и нет строки "
                       f"«удалён: {i}» — номера не меняют и не удаляют молча (doc-versioning → ID stability)")
    api_before = "\n".join(git(root, "show", f"{ref}:{n}") for n in git(
        root, "ls-tree", "-r", "--name-only", ref, "--", "documentation/api").splitlines() if n.endswith((".yaml", ".yml")))
    api_now = "\n".join(w.read(f) for f in (root / "documentation/api").rglob("*.y*ml"))
    if api_before and api_now:
        ops = lambda t: set(re.findall(r"operationId:\s*['\"]?(\w+)", t))
        removed = " ".join(re.findall(r"(?i)удал[её]н[^\n]*", api_now))
        for op in sorted(ops(api_before) - ops(api_now)):
            if op not in removed:
                out.append(f"documentation/api: операция `{op}` была в {ref}, а теперь её нет и нет записи "
                           f"«удалён: {op}» в info.x-changelog")


def check_migrations(root: Path, ref: str | None, schema: "w.Doc | None", out: list) -> None:
    folder = root / "documentation/db/migrations"
    if not folder.is_dir():
        return
    if ref:
        for line in git(root, "diff", "--name-status", ref, "--", "documentation/db/migrations").splitlines():
            st, _, name = line.partition("\t")
            if st[:1] in ("M", "D", "R"):
                out.append(f"{name}: миграция из {ref} {'изменена' if st[0] == 'M' else 'удалена или переименована'} "
                           "— файлы миграций только добавляются (doc-versioning → Registry)")
    nums = sorted(int(m.group(1)) for f in folder.glob("*.sql") for m in [re.match(r"(\d+)_", f.name)] if m)
    mig = schema.meta.get("migration") if schema else None
    if nums and mig and mig.isdigit() and int(mig) != nums[-1]:
        out.append(f"documentation/db/schema.md: migration: {mig}, а последний файл — {nums[-1]:04d}")


def check_openapi(root: Path, out: list) -> None:
    api = root / "documentation/api"
    files = sorted(api.rglob("*.y*ml")) if api.is_dir() else []
    if not files:
        return
    import check_trace
    seen: dict[str, str] = {}
    defined: set[str] = set()
    for f in files:
        t = w.read(f)
        for op in re.findall(r"operationId:\s*['\"]?(\w+)", t):
            if op in seen and seen[op] != f.name:
                out.append(f"documentation/api: operationId `{op}` дважды — {seen[op]} и {f.name}")
            seen.setdefault(op, f.name)
        defined.update(re.findall(r"^\s{2,6}([A-Za-z_][\w.-]*):\s*$", t, re.M))
    for f in files:
        for ref in re.findall(r"\$ref:\s*['\"]?([^'\"\s]+)", w.read(f)):
            target, _, frag = ref.partition("#")
            if target and not (f.parent / target).resolve().exists():
                out.append(f"{f.relative_to(root)}: $ref `{ref}` — файла {target} нет")
            elif frag and not target and frag.split("/")[-1] not in defined:
                out.append(f"{f.relative_to(root)}: $ref `{ref}` — компонент {frag.split('/')[-1]} нигде не описан")
    for op, codes in check_trace.load_operations(root / "documentation").items():
        if codes and not ({"500", "5XX", "DEFAULT"} & {c.upper() for c in codes}):
            out.append(f"documentation/api: у операции `{op}` нет ответа 500 (есть: {', '.join(sorted(codes))})")


def check_questions(root: Path, out: list) -> None:
    for f in sorted((root / "documentation").rglob("open-questions.md")):
        if "plans" in f.parts or "_web-docs" in f.parts:
            continue
        t = w.read(f)
        rel = f.relative_to(root)
        if not t.strip():
            out.append(f"{rel}: пустой — файл создаётся с первым вопросом")
            continue
        if not re.search(r"^# Открытые вопросы(?:\s+—.*)?\s*$", t, re.M):
            out.append(f"{rel}: заголовок не «# Открытые вопросы»")
        lines = t.splitlines()
        at = next((i for i, l in enumerate(lines) if l.startswith("|") and "Вопрос" in l), None)
        if at is None:
            if not any(l.startswith("|") for l in lines):
                out.append(f"{rel}: нет таблицы «| Вопрос | Класс |»")
            continue                  # only other tables (the architecture's assumptions ДП-n) — allowed
        cols = [c.strip() for c in lines[at].strip().strip("|").split("|")]
        if "Класс" not in cols:
            out.append(f"{rel}: в таблице вопросов нет столбца «Класс»")
            continue
        k = cols.index("Класс")
        for line in lines[at + 2:]:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) > k:
                if cells[k] and cells[k] not in CLASSES and not any(cells[k].startswith(c) for c in CLASSES):
                    out.append(f"{rel}: Класс «{cells[k][:40]}» — Блокирует старт, Можно решить при архитектуре "
                               "или Отложено")


def main() -> None:
    args = sys.argv[1:]
    root = Path(next((a for a in args if not a.startswith("--") and (Path(a) / "documentation").is_dir()), ".")).resolve()
    only = [a for i, a in enumerate(args) if i and args[i - 1] == "--only"]
    docs = [d for d in w.registry(root) if d.path.is_file()]
    by_path = {d.rel: d for d in docs}
    out: list[str] = []
    for d in docs:
        if not only or any(d.rel.startswith(o.rstrip("/")) or o.startswith(d.rel) for o in only):
            check_doc(root, d, by_path, out)
    ref = w.main_ref(root)
    if git(root, "rev-parse", "--abbrev-ref", "HEAD").strip() in (ref or "", (ref or "").split("/")[-1]):
        ref = None  # on main itself there is nothing to compare with
    check_ids(root, ref, out)
    check_migrations(root, ref, by_path.get("documentation/db/schema.md"), out)
    check_openapi(root, out)
    check_questions(root, out)
    for line in out:
        print("✗", line)
    print(f"doc_check: документов {len(docs)}, проблем {len(out)}")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
