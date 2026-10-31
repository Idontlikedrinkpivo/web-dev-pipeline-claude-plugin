#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where an iteration's close stands, step by step, in the order pipeline → End of the pipeline sets — so no step is
skipped and none runs out of order (a tag before the last stamp, a risk recorded after the tag).

    python3 close_iteration.py [<project dir>] [--version <v>]

One line per step, ✅ done or ✗ what is missing, in order:
  1 stamp     no contract document changed on the iteration branch since its last stamp (where_am_i.unstamped)
  2 site      documentation/ (the site included) has nothing uncommitted
  3 summary   documentation/plans/<version>/summary.md exists
  4 tag       v<version> exists — and points at a commit that has steps 1–3 in it
  5 reflect   ~/.claude (or ~/.codex)/dev-pipeline-feedback/<project>.md mentions <version>
  6 servers   no progress or documentation-site server of this project still running

The first ✗ is the next thing to do; a later step that is ✅ while an earlier one is ✗ is reported as out of order.
Exit 0 — all six done; 2 — something left (the first ✗ says what). The version: --version, else the iteration branch.
Standard library only.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import where_am_i as w  # noqa: E402


def git(root: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def alive(marker: Path) -> bool:
    try:
        pid = int(marker.read_text().split()[0])
        os.kill(pid, 0)
        return True
    except (OSError, ValueError, IndexError):
        return False


def main() -> None:
    args = sys.argv[1:]
    root = Path(next((a for a in args if not a.startswith("--") and Path(a).is_dir()), ".")).resolve()
    version = args[args.index("--version") + 1] if "--version" in args else None
    if not version:
        _, branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
        m = re.fullmatch(r"iteration/(\d+(?:\.\d+)*)", branch)
        version = m.group(1) if m else None
    if not version:
        print("close: версия не найдена — запустите на ветке iteration/<версия> или с --version")
        sys.exit(1)
    folder = root / "documentation" / "plans" / version
    steps: list[tuple[str, bool, str]] = []

    open_docs = [d.label for d in w.registry(root)   # business requirements carry no version: never stamped
                 if d.path.is_file() and "business-requirements" not in d.rel and w.unstamped(root, d, version)]
    steps.append(("1 штамп", not open_docs, "без штампа: " + ", ".join(open_docs) if open_docs else ""))
    _, dirty = git(root, "status", "--porcelain", "--", "documentation", ":!documentation/plans")
    steps.append(("2 сайт", not dirty, f"не закоммичено в documentation/: {len(dirty.splitlines())} файл(ов) — "
                  "пересоберите сайт и закоммитьте" if dirty else ""))
    summary = folder / "summary.md"
    steps.append(("3 итог", summary.exists(), f"нет {summary.relative_to(root)} (pipeline → references/summary.md)"
                  if not summary.exists() else ""))
    code, tag_sha = git(root, "rev-list", "-n", "1", f"v{version}")
    tagged = code == 0 and bool(tag_sha)
    late = ""
    if tagged:
        _, after = git(root, "log", "--format=%s", f"v{version}..HEAD", "--", "documentation", ":!documentation/plans")
        if after:
            late = f"после метки ещё коммиты в документах ({len(after.splitlines())}) — метка не несёт их"
    steps.append(("4 метка", tagged and not late, late or (f"нет метки v{version}" if not tagged else "")))
    feedback = [Path.home() / d / "dev-pipeline-feedback" / f"{root.name}.md" for d in (".claude", ".codex")]
    head = re.compile(rf"^#+ .*(?<![\d.]){re.escape(version)}(?![\d.])", re.M)   # a section of this version
    reflected = any(f.exists() and head.search(f.read_text(encoding="utf-8", errors="replace")) for f in feedback)
    steps.append(("5 reflect", reflected, "в разборе сессий нет раздела этой версии — запустите reflect"
                  if not reflected else ""))
    running = [m for m in (folder / ".progress-server", root / "documentation" / "_web-docs" / ".site-server")
               if m.exists() and alive(m)]
    steps.append(("6 серверы", not running, "работают: " + ", ".join(str(m.parent.relative_to(root)) for m in running)
                  if running else ""))

    first = next((i for i, (_, ok, _) in enumerate(steps) if not ok), None)
    for i, (name, ok, why) in enumerate(steps):
        mark = "✅" if ok else "✗"
        note = f" — {why}" if why else ""
        if ok and first is not None and i > first and name.startswith("4"):   # a reflect part may come early
            note = " — сделано раньше шага, который ещё не закрыт (порядок нарушен)"
        print(f"{mark} {name}{note}")
    if first is None:
        print(f"close: итерация {version} закрыта")
        sys.exit(0)
    print(f"close: дальше — шаг «{steps[first][0]}»" + (" — метку ставить только после шагов 1–3" if first < 3 else ""))
    sys.exit(2)


if __name__ == "__main__":
    main()
