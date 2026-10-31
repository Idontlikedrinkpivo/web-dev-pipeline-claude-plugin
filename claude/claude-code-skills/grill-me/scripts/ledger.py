#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The ledger of a grill, a document review or a brainstorm's input list: a file outside the repo that survives a
compaction or a cut-off session, so a decision already made is never asked again.

    python3 ledger.py open  --kind grill|review --doc <document path>   # create, or resume, the ledger of a document
    python3 ledger.py open  --kind grill --chat <topic-slug>            # a grill whose subject lives only in the chat
    python3 ledger.py open  --kind input                                # brainstorm: a list given as input
    python3 ledger.py add   <the same selector> "<line>" ["<line>" …]   # append one line per decision
    python3 ledger.py show  <the same selector>                         # print it
    python3 ledger.py close <the same selector>                         # delete it — once its content has landed

Run from the project's root. The file is `${TMPDIR:-/tmp}/<kind>-<repo>-<slug>.md` — `<repo>` the repo folder's
name, `<slug>` the document's path under `documentation/` without the extension, slashes as dashes
(`requirements-srs-srs`, `plans-1.1.0-plan`); `chat-<topic-slug>` for a chat subject; `input` for the brainstorm list
(`brainstorm-<repo>-input.md`). Its first line, written by `open`:
`# <Гриль | Ревью | Список на входе> <path> · итерация <version> · <git hash-object of the document, 7 chars>` —
the version of the open `documentation/plans/<version>/` (no `summary.md`), else of the `iteration/<version>` branch,
else `—`.

`open` prints `path: <file>` and `state:`
  new        — no ledger: round 1;
  resumed    — read the lines it prints before anything else and never ask a logged decision again;
  restarted  — the old ledger was of another iteration: a past grill or review, deleted; round 1;
  changed    — same iteration, but the document differs from the one round 1 saw (a decision changed elsewhere, or
               a review applied its fixes): keep the logged decisions and re-check what is left against the new text.
Exit 0; 2 — wrong arguments or `add` before `open`. Standard library only.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

TITLES = {"grill": "Гриль", "review": "Ревью", "input": "Список на входе"}
PREFIX = {"grill": "grill", "review": "review", "input": "brainstorm"}
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def repo_root() -> Path:
    top = git("rev-parse", "--show-toplevel")
    return Path(top) if top else Path.cwd()


def vkey(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def iteration(root: Path) -> str:
    plans = root / "documentation" / "plans"
    open_ = [p.name for p in plans.iterdir() if p.is_dir() and VERSION.match(p.name)
             and not (p / "summary.md").exists()] if plans.is_dir() else []
    if open_:
        return max(open_, key=vkey)
    branch = git("-C", str(root), "rev-parse", "--abbrev-ref", "HEAD")
    m = re.fullmatch(r"iteration/(\d+\.\d+\.\d+)", branch)
    return m.group(1) if m else "—"


def blob(path: Path) -> str:
    if not path.is_file():
        return "—"
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()[:7]


def usage(msg: str) -> None:
    print(msg, file=sys.stderr)
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    sys.exit(2)


def parse(argv: list) -> tuple:
    if not argv or argv[0] not in ("open", "add", "show", "close"):
        usage("the first argument is open, add, show or close")
    cmd, rest = argv[0], argv[1:]
    opts: dict = {}
    lines: list = []
    i = 0
    while i < len(rest):
        if rest[i] in ("--kind", "--doc", "--chat") and i + 1 < len(rest):
            opts[rest[i][2:]] = rest[i + 1]
            i += 2
        else:
            lines.append(rest[i])
            i += 1
    kind = opts.get("kind")
    if kind not in TITLES:
        usage("--kind is grill, review or input")
    if kind == "input" and (opts.get("doc") or opts.get("chat")):
        usage("--kind input takes no --doc or --chat")
    if kind != "input" and bool(opts.get("doc")) == bool(opts.get("chat")):
        usage("give --doc <document path> or --chat <topic-slug>, one of them")
    if opts.get("chat") and kind != "grill":
        usage("--chat is for a grill only")
    return cmd, kind, opts.get("doc"), opts.get("chat"), lines


def main() -> None:
    cmd, kind, doc, chat, lines = parse(sys.argv[1:])
    root = repo_root()
    doc_path = None
    if doc:
        doc_path = Path(doc) if Path(doc).is_absolute() else root / doc
        try:
            rel = doc_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            usage(f"{doc} is outside the project {root}")
        under = rel.split("documentation/", 1)[-1]
        slug = re.sub(r"\.[^./]+$", "", under).replace("/", "-")
        shown = rel
    elif chat:
        slug, shown = "chat-" + re.sub(r"[^\w.-]+", "-", chat).strip("-"), "чат: " + chat
    else:
        slug, shown = "input", "список на входе"
    folder = Path(os.environ.get("TMPDIR") or "/tmp")
    path = folder / f"{PREFIX[kind]}-{root.name}-{slug}.md"

    if cmd == "close":
        existed = path.exists()
        path.unlink(missing_ok=True)
        print(f"path: {path}\nstate: {'deleted' if existed else 'none'}")
        return
    if cmd == "show":
        print(path.read_text(encoding="utf-8") if path.exists() else f"path: {path}\nstate: none")
        return
    if cmd == "add":
        if not path.exists():
            usage(f"no ledger at {path}: run open first")
        if not lines:
            usage("add takes at least one line")
        with path.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(line.rstrip("\n") + "\n")
        entries = [l for l in path.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        print(f"path: {path}\nlines: {len(entries)}")
        return

    version = iteration(root)
    digest = blob(doc_path) if doc_path else "—"
    header = f"# {TITLES[kind]} {shown} · итерация {version} · {digest}\n"
    state = "new"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        m = re.search(r"· итерация (\S+) · (\S+)\s*$", first)
        if not m or m.group(1) != version:
            state = "restarted"
            was = m.group(1) if m else "?"
        elif doc_path and m.group(2) != digest:
            state = "changed"
        else:
            state = "resumed"
    if state in ("new", "restarted"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header, encoding="utf-8")
    print(f"path: {path}")
    print(f"state: {state}" + (f" (the old ledger was of iteration {was})" if state == "restarted" else ""))
    if state in ("resumed", "changed"):
        entries = [l for l in path.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        print(f"lines: {len(entries)}")
        for l in entries:
            print(l)


if __name__ == "__main__":
    main()
