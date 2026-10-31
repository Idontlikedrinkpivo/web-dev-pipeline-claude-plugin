#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split a single-file OpenAPI contract into the layout of Step 8 and prove the split changed nothing.

    python3 split_spec.py [<project root>]

Over documentation/api/openapi.yaml:

  1. Already split (a `paths/` or `components/` folder beside it, or a `$ref` into one) — says so, exit 0.
  2. Bundles the file as it is (`npx --yes @redocly/cli bundle … -o old.json`).
  3. Splits it into a temporary folder (`npx --yes @redocly/cli split … --outDir …`) and bundles the new root.
  4. Compares the two bundles as parsed JSON. They differ — prints the first differing JSON pointers, touches
     nothing, exit 1. They match — moves the split files into documentation/api/ (the root replaces
     openapi.yaml), prints what it wrote, exit 0. It commits nothing: the session commits the move on its own.

Exit 3 — Node, npx or the network is missing, or redocly failed: nothing touched; split by hand (Step 2 of the
skill) and say in the close that the bundle comparison did not run. Standard library only.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REDOCLY = ["npx", "--yes", "@redocly/cli"]


def redocly(root: Path, *args: str) -> None:
    run = subprocess.run([*REDOCLY, *args], cwd=root, capture_output=True, text=True, timeout=600)
    if run.returncode != 0:
        tail = "\n".join((run.stderr or run.stdout).strip().splitlines()[-5:])
        print(f"redocly {args[0]} не прошёл (код {run.returncode}):\n{tail}")
        print("Ничего не тронуто. Разложите вручную по Step 8 и скажите в итоге, что сравнение бандлов не запускалось.")
        sys.exit(3)


def diff(a, b, path: str = "", out: list | None = None) -> list:
    out = [] if out is None else out
    if len(out) >= 10:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            p = f"{path}/{str(k).replace('~', '~0').replace('/', '~1')}"
            if k not in a:
                out.append(f"{p}: появилось после разбиения")
            elif k not in b:
                out.append(f"{p}: пропало после разбиения")
            else:
                diff(a[k], b[k], p, out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}/{i}", out)
    elif a != b:
        out.append(f"{path or '/'}: было {json.dumps(a, ensure_ascii=False)[:80]}, стало {json.dumps(b, ensure_ascii=False)[:80]}")
    return out


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    api = root / "documentation" / "api"
    spec = api / "openapi.yaml"
    if not spec.is_file():
        print(f"нет {spec.relative_to(root)} — разбивать нечего")
        sys.exit(2)
    text = spec.read_text(encoding="utf-8")
    if (api / "paths").is_dir() or (api / "components").is_dir() or re.search(
            r"\$ref:\s*['\"]?\.?/?(paths|components)/", text):
        print("documentation/api/openapi.yaml уже разложен по файлам — разбивать нечего")
        sys.exit(0)
    if not shutil.which("npx"):
        print("нет npx (Node) — ничего не тронуто. Разложите вручную по Step 8 и скажите в итоге, "
              "что сравнение бандлов не запускалось.")
        sys.exit(3)
    with tempfile.TemporaryDirectory(prefix="split-spec-") as tmp:
        t = Path(tmp)
        redocly(root, "bundle", str(spec), "-o", str(t / "old.json"))
        redocly(root, "split", str(spec), "--outDir", str(t / "split"))
        new_root = t / "split" / "openapi.yaml"
        if not new_root.is_file():
            print("redocly split не оставил openapi.yaml в корне — ничего не тронуто")
            sys.exit(3)
        redocly(root, "bundle", str(new_root), "-o", str(t / "new.json"))
        old = json.loads((t / "old.json").read_text(encoding="utf-8"))
        new = json.loads((t / "new.json").read_text(encoding="utf-8"))
        lines = diff(old, new)
        if lines:
            for line in lines:
                print("✗", line)
            print("Бандлы до и после разбиения расходятся — ничего не тронуто.")
            sys.exit(1)
        written = []
        for f in sorted(p for p in (t / "split").rglob("*") if p.is_file()):
            rel = f.relative_to(t / "split")
            dest = api / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)
            written.append(rel.as_posix())
    print(f"разложено: {len(written)} файлов в documentation/api/ — бандлы до и после совпали")
    for rel in written:
        print("  ", rel)


if __name__ == "__main__":
    main()
