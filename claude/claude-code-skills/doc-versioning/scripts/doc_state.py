#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What a stamp has to type, and which pins lag their sources — the git and pin reading the stamp and the stale
sweep would otherwise do by hand.

    python3 doc_state.py [<project dir>] dirty [--only <path> …] [--diff]
    python3 doc_state.py [<project dir>] stale

dirty   For each contract document (SRS with areas/, DB schema, OpenAPI with paths/ and components/, the three
        architecture documents, the screen specs): its last stamped state — the commit that last moved its
        `version` line (`info.version` for OpenAPI; the index file's for a split set) — and whether the document
        differs from it, uncommitted edits and new files included. A document that differs gets its files and
        the commits since that stamp, the decision-change and upgrade-docs ones marked (an upgrade-docs commit's
        hunks get no journal row; `git log <stamp>..HEAD -- <files>` lists the rest). A document whose version line was only ever written by its writer's commit
        («… написан, этап не закрыт») has never been stamped: it is its first release. --diff prints each
        differing document's diff against its last stamp — what the stamp types. Exit 0 — nothing differs
        (version-birth step 2: stop, commit nothing); 2 — something differs.
stale   Every `path@<version>` pin under documentation/ (OpenAPI's info.x-sources, the frames register's and the
        test cases' README pins included) that is behind its source, as
        «document → source@<pin> (сейчас <version>): stale | behind | refresh» with the source's journal rows
        that decided it (doc-versioning → Staleness and cascade). Read-only; exit 0.

Standard library only; reuses pipeline/scripts/where_am_i.py for the registry, the frontmatter and the journals.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline" / "scripts"))
import where_am_i as w  # noqa: E402

DOCS = "documentation/"
SKIP_DIRS = ("documentation/plans/", "documentation/_web-docs/")
DECISION = re.compile(r"^docs: решение изменено")
UPGRADE = re.compile(r"\(плагин \d")
WRITTEN = re.compile(r"написан, этап не закрыт")


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def doc_files(root: Path, doc: "w.Doc") -> list[str]:
    """The files that make one document: an index and its split parts — never open-questions or wishes."""
    rel = doc.rel
    if rel.endswith("requirements/srs/srs.md"):
        return [rel, DOCS + "requirements/srs/areas"]
    if rel.endswith("api/openapi.yaml"):
        return [rel, DOCS + "api/paths", DOCS + "api/components"]
    return [rel]


def last_stamp(root: Path, doc: "w.Doc") -> tuple[str, str]:
    pattern = r"^  version:" if doc.rel.endswith("openapi.yaml") else r"^version:"
    line = git(root, "log", "-1", "--format=%H\t%s", "-G", pattern, "--", doc.rel)
    sha, _, subject = line.partition("\t")
    return sha, subject


def dirty(root: Path, only: list[str], show_diff: bool) -> int:
    docs = [d for d in w.registry(root) if d.path.is_file() and "business-requirements" not in d.rel]
    if only:
        docs = [d for d in docs if any(d.rel.startswith(o.rstrip("/")) or o.startswith(d.rel) for o in only)]
    differ, clean = [], []
    for d in docs:
        files = [f for f in doc_files(root, d) if (root / f).exists()]
        sha, subject = last_stamp(root, d)
        new = git(root, "ls-files", "--others", "--exclude-standard", "--", *files).splitlines()
        if not sha:
            differ.append((d, "", "в git его нет или строки версии не было — первый выпуск", files, new, []))
            continue
        changed = git(root, "diff", "--name-only", sha, "--", *files).splitlines()
        if not changed and not new:
            clean.append(d.label)
            continue
        log = git(root, "log", "--format=%h\t%s", f"{sha}..HEAD", "--", *files).splitlines()
        if (log and not new and all(UPGRADE.search(l.partition("\t")[2]) for l in log)
                and not git(root, "status", "--porcelain", "--", *files)):
            clean.append(f"{d.label} (только upgrade-docs — строк нет)")
            continue
        note = (f"штампа ещё не было — версию записал автор ({sha[:8]} «{subject}»): первый выпуск"
                if WRITTEN.search(subject) else f"последний штамп {sha[:8]} «{subject}»")
        differ.append((d, sha, note, changed, new, log))
    for d, sha, note, changed, new, log in differ:
        print(f"✗ {d.label} ({d.rel}) — {note}")
        names = [Path(f).name for f in changed] + [f"{Path(f).name} (новый, не в git)" for f in new]
        if names:
            print(f"    файлы: {', '.join(names)}")
        uncommitted = git(root, "status", "--porcelain", "--", *doc_files(root, d))
        if uncommitted:
            print("    есть незакоммиченные правки — они тоже в разнице")
        if log:
            dec = sum(1 for l in log if DECISION.search(l.partition("\t")[2]))
            upg = [l.partition("\t")[0] for l in log if UPGRADE.search(l.partition("\t")[2])]
            print(f"    коммитов после штампа: {len(log)}" + (f" · решение изменено: {dec}" if dec else "")
                  + (f" · upgrade-docs: {', '.join(upg)} — их правки без строк журнала (git show <sha>)" if upg else ""))
        if show_diff and sha:
            print(git(root, "diff", sha, "--", *doc_files(root, d)))
    if clean:
        print(f"✓ не отличаются от последнего штампа: {', '.join(clean)}")
    if not differ:
        print("doc_state: ни один документ не отличается от своего штампа — штамповать нечего, коммита нет")
        return 0
    print(f"doc_state: отличаются {len(differ)} — их и штампует version-birth, шаг 4"
          + ("" if show_diff else "; разница: --diff или git diff <штамп> -- <файлы>"))
    return 2


def pinned_files(root: Path) -> list[Path]:
    base = root / "documentation"
    out = [p for p in sorted(base.rglob("*.md")) if not any(p.relative_to(root).as_posix().startswith(s)
                                                            for s in SKIP_DIRS)]
    api = base / "api" / "openapi.yaml"
    return out + ([api] if api.is_file() else [])


def stale(root: Path) -> int:
    sources: dict = {}
    found = 0
    for p in pinned_files(root):
        rel = p.relative_to(root).as_posix()
        text = w.read(p)
        meta = w.openapi_info(text) if rel.endswith("openapi.yaml") else w.front(text)
        for src in meta.get("sources", []):
            if "@" not in src:
                continue
            path, pin = src.rsplit("@", 1)
            if path not in sources:
                sources[path] = w.Doc(root, path, path, 0)
            s = sources[path]
            cur = s.meta.get("version")
            if not s.path.is_file() or not cur:
                print(f"? {rel} → {src}: источника нет или у него нет версии")
                found += 1
                continue
            if w.vkey(pin) >= w.vkey(cur):
                continue
            after = [r for r in s.rows if w.vkey(r[0]) > w.vkey(pin)]
            types = {r[1] for r in after}
            state, why = (("stale", "ломает") if "ломает" in types else ("behind", "добавляет")
                          if "добавляет" in types else ("refresh", "уточняет"))
            print(f"{rel} → {Path(path).name}@{pin} (сейчас {cur}): {state}")
            for r in after:
                if r[1] == why:
                    print(f"    {r[0]} {r[1]}: {r[2][:120]}")
            found += 1
    print(f"doc_state: пинов позади источника — {found}" if found else "doc_state: все пины равны версиям источников")
    return 0


def main() -> None:
    args = sys.argv[1:]
    mode = next((a for a in args if a in ("dirty", "stale")), None)
    if not mode:
        print(__doc__)
        sys.exit(1)
    root = Path(next((a for a in args if not a.startswith("--") and a not in ("dirty", "stale")
                      and (Path(a) / "documentation").is_dir()), ".")).resolve()
    if not (root / "documentation").is_dir():
        print(f"doc_state: в {root} нет documentation/")
        sys.exit(1)
    only = [a for i, a in enumerate(args) if i and args[i - 1] == "--only"]
    sys.exit(dirty(root, only, "--diff" in args) if mode == "dirty" else stale(root))


if __name__ == "__main__":
    main()
