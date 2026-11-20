# -*- coding: utf-8 -*-
"""Which screens a code change reaches: the import graph of the frontend, from a changed file up to the pages.

usage: python3 code_reach.py <project dir> <changed file> [<changed file> …]
Used by affected_cases.py (the scope of a run); run alone, it prints the same answer for the files named.

A shared file (a button, a form field, the API wrapper, a hook) names no screen and no operation, so the trace of a
case cannot tie it to the change. The graph can: every tracked source file of the frontend is parsed for its imports
(`import … from`, `export … from`, `import("…")`, `require("…")`, side-effect `import "…"`), resolved relative to the
file or through the `paths` of the nearest tsconfig.json / jsconfig.json (`@/` → `src/` when none is set), with the
`.js` → `.ts` swap of ESM TypeScript. A type-only import (`import type …`) is no edge, and a `.d.ts` file is no
change: nothing of a type runs on the screen, and the typecheck owns it. From a changed file the walk goes up through its importers:
  - it stops at a page — a file in a `pages/` folder, a Next.js `page.*`, or a `*Page.*` file — naming `S-<n>` — the first id
    (or run of ids, «S-3, S-4») on its first line of 40 that names one, its first comment by `frontend`'s rule;
    an id later on that line («shared with S-8») is a note, not the page's screen: that screen is reached;
  - it reaches the app shell when it gets to a file nothing imports that is not a page — main.tsx, the router, the root
    layout: everything under it, every screen, can break. The run takes the cross-cutting cases for that.
Test files (`*.test.*`, `*.spec.*`, `*.stories.*`, `*TestKit.*`, `test/`, `tests/`, `__tests__/`, `__mocks__/`, `e2e/`) are
left out of the graph: they import
everything and run nothing for the user. The server is not walked: its layers meet in one wiring file that imports
them all, so every change would reach every operation; a server change is tied to an operation only where its lines
name the operationId (affected_cases.py), and the rest is reported as shared server code.
Standard library only, Python 3.9+.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SRC = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte")
CODE = SRC + (".py", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs")
IMPORT = re.compile(
    r"""(?:^|[;\s])(?:import|export)\s[^'";]*?\bfrom\s*['"]([^'"\n]+)['"]"""
    r"""|\bimport\s*\(\s*['"]([^'"\n]+)['"]\s*\)"""
    r"""|(?:^|[;\s])import\s*['"]([^'"\n]+)['"]"""
    r"""|\brequire\s*\(\s*['"]([^'"\n]+)['"]\s*\)""", re.M)
SID = re.compile(r"\bS-\d+\b")
LEAD = re.compile(r"\bS-\d+(?:\s*(?:,|/|\bи\b)\s*S-\d+)*")
TEST = re.compile(r"(?:^|/)(?:e2e|tests?|__tests__|__mocks__)/|\.(?:test|spec|stories)\.[^/]+$|TestKit\.[^/]+$"
                  r"|(?:^|/)test_[^/]*\.py$|(?:^|/)conftest\.py$")
ENTRY = re.compile(r"(?:^|/)(?:main|index|_app|_document|layout|App|app|router|routes)\.[^/]+$")
PAGE = re.compile(r"(?:^|/)pages/|(?:^|/)page\.[jt]sx?$|Page\.(?:[jt]sx?|vue|svelte)$")


def tracked(root: Path) -> list[str]:
    r = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=false", "ls-files"], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else []


def is_test(f: str) -> bool:
    return bool(TEST.search(f))


def jsonc(text: str) -> dict:
    """tsconfig.json allows comments and trailing commas; strings are kept (a path holds `/*`)."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            i = text.find("\n", i) if text.find("\n", i) != -1 else n
        elif text.startswith("/*", i):
            i = text.find("*/", i) + 2 if text.find("*/", i) != -1 else n
        else:
            out.append(c); i += 1
    try:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))
    except ValueError:
        return {}


class Graph:
    def __init__(self, root: Path):
        self.root = root
        self.files = set(tracked(root))
        self.src = sorted(f for f in self.files if f.endswith(SRC) and not is_test(f))
        self.aliases: dict[str, list[tuple[str, str]]] = {}   # config dir -> [(prefix, target dir)]
        self.importers: dict[str, set[str]] = {}
        self.pages: dict[str, list[str]] = {}
        for f in self.src:
            text = (root / f).read_text(errors="replace")
            if PAGE.search(f):
                first = next((ln for ln in text.splitlines()[:40] if SID.search(ln)), "")
                if first:   # the screen the page opens with, not the ones its note mentions («shared with S-8»)
                    self.pages[f] = SID.findall(LEAD.search(first).group(0))
            for m in IMPORT.finditer(text):
                if re.match(r"[;\s]*(?:import|export)\s+type\s", m.group(0)):
                    continue   # types only: nothing of it runs on the screen, the typecheck owns it
                spec = next(g for g in m.groups() if g)
                target = self.resolve(f, spec)
                if target and target != f:
                    self.importers.setdefault(target, set()).add(f)

    def alias(self, f: str) -> list[tuple[str, str]]:
        d = Path(f).parent
        while True:
            key = str(d)
            if key in self.aliases:
                return self.aliases[key]
            cfg = next((d / n for n in ("tsconfig.json", "jsconfig.json") if str(d / n) in self.files), None)
            if cfg is not None or key == ".":
                home = Path(cfg).parent if cfg is not None else d
                pairs: list[tuple[str, str]] = []
                if cfg is not None:
                    opts = jsonc((self.root / cfg).read_text(errors="replace")).get("compilerOptions", {})
                    base = home / opts.get("baseUrl", ".")
                    for k, v in (opts.get("paths") or {}).items():
                        if v:
                            pairs.append((k.rstrip("*"), str(base / v[0].rstrip("*")).rstrip("/") + "/"))
                if not pairs:
                    pairs = [("@/", f"{home}/src/"), ("~/", f"{home}/src/")]
                self.aliases[key] = pairs
                return pairs
            d = d.parent

    def resolve(self, f: str, spec: str) -> str | None:
        if spec.startswith("."):
            base = str((Path(f).parent / spec))
        else:
            hit = next(((p, t) for p, t in self.alias(f) if spec.startswith(p)), None)
            if not hit:
                return None   # a package from node_modules
            base = hit[1] + spec[len(hit[0]):]
        parts: list[str] = []   # «a/./b», «a/../b» → normal form, relative to the repo root
        for p in base.split("/"):
            if p == ".." and parts:
                parts.pop()
            elif p not in (".", ""):
                parts.append(p)
        base = "/".join(parts)
        stem = re.sub(r"\.(?:m?js|jsx)$", "", base)
        for c in [base] + [stem + e for e in SRC + (".d.ts",)] + [f"{base}/index{e}" for e in SRC + (".d.ts",)]:
            if c in self.files:
                return c
        return None

    def reach(self, changed: str) -> tuple[list[str], bool]:
        """The screens a change of this file reaches, and whether it reaches the app shell."""
        screens, shell, seen, todo = [], False, {changed}, [changed]
        while todo:
            f = todo.pop()
            if f in self.pages:
                screens += self.pages[f]
                continue
            up = self.importers.get(f, set()) - seen
            if not self.importers.get(f) and (f != changed or ENTRY.search(f)):
                shell = True   # a file nothing imports above the pages: the entry, the router, the root layout
            seen |= up
            todo += sorted(up)
        return sorted(set(screens), key=lambda s: int(s[2:])), shell

    def in_front(self, f: str) -> bool:
        """A file of the frontend: under the folder of a config that also holds the pages."""
        return any(f.startswith(cfg) for cfg in self.front_roots())

    def front_roots(self) -> list[str]:
        roots = set()
        for p in self.pages:
            d = Path(p).parent
            while str(d) not in (".", ""):
                if any(str(d / n) in self.files for n in ("package.json", "tsconfig.json", "jsconfig.json")):
                    break
                d = d.parent
            roots.add("" if str(d) in (".", "") else str(d) + "/")
        return sorted(roots)


def split(root: Path, changed: list[str]) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """{screen: [files]} reached, the files that reach the app shell, and the other code files: the server, scripts,
    a frontend file no screen and no entry imports."""
    g = Graph(root)
    screens: dict[str, list[str]] = {}
    shell, other = [], []
    for f in changed:
        if is_test(f) or f.endswith(".d.ts") or not f.endswith(CODE + (".css", ".scss", ".sass", ".less")) \
                or f not in g.files:
            continue
        if g.pages and g.in_front(f):
            ids, top = g.reach(f)
            for s in ids:
                screens.setdefault(s, []).append(f)
            if top:
                shell.append(f)
            elif not ids:
                other.append(f)   # imported by no screen and by no entry: generated types, a file not wired yet
        elif f.endswith(CODE):
            other.append(f)
    return screens, shell, other


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__.split("\n\n")[0]); sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    screens, shell, other = split(root, sys.argv[2:])
    for s, fs in sorted(screens.items(), key=lambda x: int(x[0][2:])):
        print(f"{s}\t{', '.join(fs)}")
    for f in shell:
        print(f"каркас\t{f}")
    for f in other:
        print(f"другой код\t{f}")


if __name__ == "__main__":
    main()
