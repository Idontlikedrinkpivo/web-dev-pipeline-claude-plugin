"""Set a progress file's bar and count line from two numbers, so nobody copies a hundred-cell bar by hand.

    python3 progress_set.py <progress file .md> <done> <total> [--section "<heading>"]

Rewrites the first bar (`█…░… N%`) of the file — or of the section that starts at the heading given, e.g.
"## Исправления по финальному ревью" — and the «N из M» of the count line right under that bar, then redraws the
page beside the file. The rows themselves still change with Edit, one row per call. An Edit of the bar fails
whenever the copy in the old string is off by one cell; this script is the second allowed writer of a progress
file outside Edit/Write (pipeline → references/progress-files.md → How). Percent = ⌊done × 100 / total⌋, the
filled cells equal the percent. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 3:
        sys.exit(__doc__)
    md, done, total = Path(args[0]), int(args[1]), int(args[2])
    heading = args[args.index("--section") + 1] if "--section" in args else ""
    if not md.is_file() or total <= 0 or not 0 <= done <= total:
        sys.exit(f"progress_set: need an existing file and 0 <= done <= total > 0 ({md}, {done}, {total})")
    text = md.read_text(encoding="utf-8")
    start = 0
    if heading:
        m = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
        if not m:
            sys.exit(f"progress_set: no heading {heading!r} in {md}")
        start = m.end()
    bar = re.compile(r"^[█░]{20,}\s*\d+\s*%[^\n]*$", re.M)
    b = bar.search(text, start)
    if not b:
        sys.exit(f"progress_set: no bar after {heading or 'the top'} in {md}")
    pct = done * 100 // total
    text = text[: b.start()] + "█" * pct + "░" * (100 - pct) + f" {pct}%" + text[b.end():]
    after = text.index("\n", b.start()) + 1
    c = re.compile(r"\d+\s*из\s*\d+").search(text, after)
    nxt = re.compile(r"^#{1,3} ", re.M).search(text, after)
    if c and (not nxt or c.start() < nxt.start()):
        text = text[: c.start()] + f"{done} из {total}" + text[c.end():]
    md.write_text(text, encoding="utf-8")
    try:
        import progress_page
        progress_page.page(md)
    except Exception as e:  # the page is a view; the file is already right
        print(f"progress_set: page not rebuilt ({e})", file=sys.stderr)
    print(f"{md.name}: {done} из {total} · {pct}%")


if __name__ == "__main__":
    main()
