"""Keep the «e2e» section of a progress file current while a Playwright suite runs.

    python3 progress_e2e.py <playwright log> <progress file .md> --total <N> [--stand "<one line>"] [--done]

The log is the output of `npx playwright test --reporter=list` (or `list,json`) redirected to a file. Each finished
test is one line: a mark (✓ / ok passed, ✘ / x failed, - skipped, ± flaky), its number, `[project] › <file>:<line>:<col> ›
<title> (<duration>)`. A retried test counts once, by its last result. --total is the suite's size from
`npx playwright test --list` («Total: N tests in M files»). Run it every minute or two while the suite runs — a
loop or a watch — and once more with --done when it ends.

It rewrites only the «## e2e» section of the file (created when missing, at the end), then rebuilds the page beside
the file itself: this script is the one allowed writer of a progress file outside Edit/Write, because a run of
hundreds of tests cannot be followed one Edit at a time (work → references/progress-file.md → The e2e section).
Standard library only.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LINE = re.compile(
    r"^\s*(?P<mark>✓|✔|ok|✘|✗|x|-|±)\s+\d+\s+(?:\[(?P<project>[^\]]+)\]\s+›\s+)?"
    r"(?P<file>[^\s:›]+\.(?:spec|test)\.[cm]?[jt]sx?):(?P<pos>\d+:\d+)\s+›\s+(?P<title>.*?)"
    r"(?:\s+\((?P<dur>[\d.]+m?s|[\d.]+m)\))?\s*$"
)
STATE = {"✓": "pass", "✔": "pass", "ok": "pass", "✘": "fail", "✗": "fail", "x": "fail", "-": "skip", "±": "flaky"}


def parse(log: Path) -> dict[tuple[str, str, str, str], str]:
    """(project, file, position, title) -> its last state; a retry overwrites the earlier attempt."""
    results: dict[tuple[str, str, str, str], str] = {}
    for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = re.sub(r"\x1b\[[0-9;]*m", "", raw)  # colours, when the log came from a terminal
        m = LINE.match(line)
        if not m:
            continue
        title = re.sub(r"\s*\(retry #\d+\)\s*$", "", m["title"])
        results[(m["project"] or "", m["file"], m["pos"], title)] = STATE[m["mark"]]
    return results


def bar(done: int, total: int) -> str:
    pct = done * 100 // total if total else 0
    return "█" * pct + "░" * (100 - pct) + f" {pct}%"


def section(results: dict, total: int, stand: str, finished: bool) -> str:
    files: dict[str, dict[str, int]] = {}
    for (_, file, _, _), state in results.items():
        files.setdefault(file, {"pass": 0, "fail": 0, "skip": 0, "flaky": 0})[state] += 1
    passed = sum(s == "pass" for s in results.values()) + sum(s == "flaky" for s in results.values())
    failed = sum(s == "fail" for s in results.values())
    skipped = sum(s == "skip" for s in results.values())
    checked = len(results)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = []
    for file in sorted(files):
        c = files[file]
        status = "⛔ есть падения" if c["fail"] else "✅ прошёл" if not c["skip"] else "✅ прошёл, есть пропуски"
        rows.append(f"| `{file}` | {c['pass'] + c['flaky']} | {c['fail']} | {c['skip']} | {status} |")
    state = "закончен" if finished else "идёт"
    return "\n".join([
        "## e2e",
        "",
        "```text",
        bar(passed, total),
        "```",
        "",
        f"Проверено: {checked} из {total} · успешно {passed} · не прошли {failed} · пропущено {skipped}",
        "",
        "| Файл | Успешно | Не прошли | Пропущено | Статус |",
        "|---|---|---|---|---|",
        *rows,
        "",
        f"Стенд: {stand or '—'} · прогон {state} · обновлено {now}",
        "",
    ])


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2 or "--total" not in args:
        sys.exit(__doc__)
    log, md = Path(args[0]), Path(args[1])
    total = int(args[args.index("--total") + 1])
    stand = args[args.index("--stand") + 1] if "--stand" in args else ""
    if not md.is_file():
        sys.exit(f"progress_e2e: no progress file {md}")
    results = parse(log) if log.is_file() else {}
    text = md.read_text(encoding="utf-8")
    new = section(results, total, stand, "--done" in args)
    m = re.search(r"^## e2e\n.*?(?=^## |\Z)", text, re.M | re.S)
    text = text[: m.start()] + new + text[m.end():] if m else text.rstrip("\n") + "\n\n" + new
    md.write_text(text, encoding="utf-8")
    try:
        import progress_page
        progress_page.page(md)
    except Exception as e:  # the page is a view; the file is already right
        print(f"progress_e2e: page not rebuilt ({e})", file=sys.stderr)
    passed = sum(s in ("pass", "flaky") for s in results.values())
    print(f"e2e: {len(results)} из {total} · успешно {passed} · не прошли {sum(s == 'fail' for s in results.values())}")


if __name__ == "__main__":
    main()
