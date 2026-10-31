#!/usr/bin/env python3
"""Flag the UI-code anti-patterns of web-design-guidelines that a text search can find.

usage: python3 flag_antipatterns.py <file or folder> [...]
Exit 0 — nothing flagged; 1 — candidates printed in the skill's report format (grouped by file,
`file:line — UX-n — суть`). Standard library only.

Every line is a candidate, not a finding: the reviewer opens it and keeps it only when the rule
holds there (an `autoFocus` on the one main field of a desktop form is allowed). Patterns that need
judgement — a long list without virtualization, an icon button's name, a form field's label, a
gesture-only action — are not searched; they are read.
Folders are walked for .tsx .jsx .ts .js .vue .svelte .html .css .scss, skipping node_modules,
dist, build, .next, coverage, test and story files.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

EXT = {".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html", ".css", ".scss"}
SKIP_DIRS = {"node_modules", "dist", "build", ".next", "coverage", ".git", "playwright-report", "test-results"}
SKIP_FILE = re.compile(r"\.(test|spec|stories)\.\w+$")

# (rule, what to say, pattern); a pattern may span lines — the line of its start is reported.
PATTERNS = [
    ("UX-55", "масштабирование запрещено (user-scalable / maximum-scale)",
     re.compile(r"user-scalable\s*=\s*['\"]?(?:no|0)\b|maximum-scale\s*=\s*['\"]?1(?:\.0)?\b")),
    ("UX-19", "вставка заблокирована (onPaste + preventDefault)",
     re.compile(r"onPaste\s*=\s*\{[^}]{0,300}?preventDefault|['\"]paste['\"][^;]{0,300}?preventDefault", re.S)),
    ("UX-19", "type=\"number\" — нужен type=\"text\" с inputmode",
     re.compile(r"type\s*=\s*\{?\s*['\"]number['\"]")),
    ("UX-61", "transition: all — перечислить свойства",
     re.compile(r"transition\s*:\s*all\b|['\"`\s]transition-all\b|transition\s*:\s*['\"]all\b")),
    ("UX-63", "outline убран без замены через focus-visible",
     re.compile(r"^(?!.*focus-visible).*(?:\boutline-none\b|outline\s*:\s*(?:none|0)\b)", re.M)),
    ("UX-64", "<div>/<span> с onClick — нужен <button> или <a>",
     re.compile(r"<(?:div|span)\b[^>]*?\bonClick\s*=", re.S)),
    ("UX-64", "переход по onClick — нужна ссылка <a> / <Link>",
     re.compile(r"onClick\s*=\s*\{[^}]{0,200}?\b(?:navigate\(|router\.push\(|window\.location)", re.S)),
    ("UX-75", "<img> без width и height",
     re.compile(r"<img\b(?![^>]*\bwidth\b[^>]*\bheight\b)(?![^>]*\bheight\b[^>]*\bwidth\b)[^>]*>", re.S)),
    ("UX-75", "анимированный GIF — видео или статичное изображение",
     re.compile(r"['\"(][^'\"()\s]+\.gif\b", re.I)),
    ("UX-76", "autoFocus — только на десктопе и только на одном главном поле",
     re.compile(r"\bautoFocus\b|\sautofocus\b")),
    ("UX-77", "дата собрана вручную — Intl.DateTimeFormat",
     re.compile(r"getMonth\(\)\s*\+\s*1")),
]


def files(args: list[str]):
    for a in args:
        p = Path(a)
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if (f.suffix in EXT and f.is_file() and not SKIP_FILE.search(f.name)
                        and not SKIP_DIRS & set(f.relative_to(p).parts)):
                    yield f


def outline_replaced(text: str, at: int) -> bool:
    """In a CSS block, `outline: none` is fine when the selector is :focus-visible or the block draws
    another ring (box-shadow, border-color)."""
    start = text.rfind("{", 0, at)
    if start < 0 or text.rfind("}", 0, at) > start:
        return False
    selector = text[text.rfind("}", 0, start) + 1:start]
    block = text[start:text.find("}", at) if text.find("}", at) > 0 else len(text)]
    return "focus-visible" in selector or re.search(r"box-shadow|border-color|outline-offset", block) is not None


def scan(f: Path) -> list[tuple[int, str, str]]:
    text = f.read_text(errors="replace")
    css = f.suffix in {".css", ".scss"}
    hits = set()
    for rule, what, rx in PATTERNS:
        for m in rx.finditer(text):
            if css and rule == "UX-63" and outline_replaced(text, m.start()):
                continue
            hits.add((text.count("\n", 0, m.start()) + 1, rule, what))
    return sorted(hits)


def main():
    if len(sys.argv) < 2:
        print(__doc__.split("\n\n")[0])
        print("usage: python3 flag_antipatterns.py <file or folder> [...]")
        sys.exit(2)
    total = 0
    for f in files(sys.argv[1:]):
        hits = scan(f)
        if not hits:
            continue
        print(f"## {f}\n")
        for line, rule, what in hits:
            print(f"{f}:{line} — {rule} — {what}")
        print()
        total += len(hits)
    print(f"flag-antipatterns: кандидатов {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
