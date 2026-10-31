"""Keep `progress-mutation.md` current while a mutation run's parts work — from their logs, not by hand.

    python3 progress_mutation.py <progress-mutation.md> <parts.json> [--done]
    python3 progress_mutation.py <progress-mutation.md> <parts.json> --watch [seconds]   # until every part ends

parts.json is written by the session before the first part starts (work → references/health.md → Progress):

    {"budget": "8 потоков из 10 ядер",
     "parts": [
       {"name": "Доменные правила", "scope": "src/domain/booking.ts:40-72, …", "workers": "4 потока",
        "tool": "stryker", "log": "<abs path>/domain.log", "mutants": 412},
       {"name": "Защиты на базе · доля 1", "scope": "…", "workers": "1 поток · база app_test_mut_1",
        "tool": "stryker", "log": "<abs path>/guards-1.log"},
       {"name": "Извлечение текста", "skip": "отдельный процесс — Stryker его не запускает"}]}

`mutants` is the dry run's count, used until the log names its own. Each log is the part's output redirected to a
file: Stryker with the `progress-append-only` and `clear-text` reporters («Instrumented … with N mutant(s)»,
«… 120/266 tested (12 survived, 0 timed out)», the final «All files» row), mutmut 3 as it prints
(«52/250  🎉 40 🫥 2  ⏰ 0  🤔 0  🙁 10  🔇 0»). A part is done when Stryker's final table is in its log, when
mutmut has tested every mutant, or on --done.

It rewrites the file from its top down to the first `## ` heading — the bar, the count line, the parts table, the
state line — and keeps every section below it (the survivors, which the session keeps with Edit); a missing file is
created with an empty survivors section. Then it redraws the page beside the file: like progress_e2e.py, it is an
allowed writer of a progress file outside Edit/Write (pipeline → references/progress-files.md → How). It prints one
line per part whose status changed since the last call, then the summary line. A part that has passed ~5% timed-out
mutants is marked for a look: the machine was overloaded (work → references/health.md). Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
S_TOTAL = re.compile(r"with (\d+) mutants?\(?s?\)?")
S_PROGRESS = re.compile(r"(\d+)/(\d+) tested \((\d+) survived, (\d+) timed out\)")
M_PROGRESS = re.compile(r"(\d+)/(\d+)\s+🎉\s*(\d+)\s+🫥\s*(\d+)\s+⏰\s*(\d+)\s+🤔\s*(\d+)\s+🙁\s*(\d+)\s+🔇\s*(\d+)")
SURVIVORS = "## Выжившие и эквивалентные"


def num(n: int | None) -> str:
    return "—" if n is None else f"{n:,}".replace(",", " ")


def stryker(text: str) -> dict:
    out: dict = {}
    m = S_TOTAL.findall(text)
    if m:
        out["total"] = int(m[-1])
    p = S_PROGRESS.findall(text)
    if p:
        tested, total, survived, timeout = map(int, p[-1])
        out.update(tested=tested, total=total, survived=survived, timeout=timeout)
    header = None
    for line in text.splitlines():  # the clear-text table: columns found by name, the version's order may differ
        cells = [c.strip() for c in line.split("|")]
        if any("# killed" in c for c in cells):
            header = cells
        elif header and cells and cells[0] == "All files" and len(cells) == len(header):
            col = {h: c for h, c in zip(header, cells)}
            pick = lambda key: int(next((v for h, v in col.items() if key in h), "0") or 0)
            out.update(killed=pick("# killed"), timeout=pick("# timeout"), survived=pick("# survived"),
                       nocov=pick("# no cov"), errors=pick("# error"), done=True)
            out["tested"] = out["killed"] + out["timeout"] + out["survived"] + out["nocov"]
            out.setdefault("total", out["tested"])
    return out


def mutmut(text: str) -> dict:
    p = M_PROGRESS.findall(text)
    if not p:
        return {}
    tested, total, killed, nocov, timeout, suspicious, survived, skipped = map(int, p[-1])
    return {"tested": tested, "total": total, "killed": killed, "nocov": nocov, "timeout": timeout + suspicious,
            "survived": survived, "done": tested >= total > 0}


def read(part: dict, finished: bool) -> dict:
    if part.get("skip"):
        return {"status": f"⏭ пропущено: не измерено — {part['skip']}"}
    log = Path(part.get("log", ""))
    text = ANSI.sub("", log.read_text(encoding="utf-8", errors="replace")).replace("\r", "\n") if log.is_file() else ""
    r = (mutmut if part.get("tool") == "mutmut" else stryker)(text)
    r.setdefault("total", part.get("mutants"))
    if not text.strip():
        r["status"] = "⛔ остановлено: лога нет" if finished else "⏳ ждёт"
        return r
    if "tested" not in r:
        r["status"] = "⛔ остановлено: лог не распознан — заполнить по итогу инструмента" if finished else "🔄 в работе: подготовка"
        return r
    if "killed" not in r:  # Stryker's progress line has no killed count until the end
        r["killed"] = r["tested"] - r.get("survived", 0) - r.get("timeout", 0)
    share = r.get("timeout", 0) * 100 // r["tested"] if r["tested"] else 0
    complete = r.get("done") or (r.get("total") and r["tested"] >= r["total"])
    if finished and not complete and r.get("total"):
        r["status"] = f"⛔ остановлено: оборвалась на {num(r['tested'])} из {num(r['total'])}"
    elif complete or finished:
        r["status"] = f"🔍 разбор: таймауты {share}% — перегрузка?" if share > 5 else "✅ готово"
    else:
        r["status"] = f"🔄 в работе: таймауты {share}%" if share > 5 else "🔄 в работе"
    return r


def top(version: str, parts: list[dict], results: list[dict], budget: str, finished: bool) -> str:
    total = sum(r.get("total") or 0 for r in results)
    tested = sum(r.get("tested") or 0 for r in results)
    killed = sum(r.get("killed") or 0 for r in results)
    survived = sum(r.get("survived") or 0 for r in results)
    timeout = sum(r.get("timeout") or 0 for r in results)
    nocov = sum(r.get("nocov") or 0 for r in results)
    pct = tested * 100 // total if total else 0
    rows = [f"| {p['name']} | {p.get('scope', '—')} | {p.get('workers', '—')} | {r['status']} | "
            f"{num(r.get('total'))} | {num(r.get('tested'))} | {num(r.get('killed'))} | {num(r.get('survived'))} | "
            f"{num(r.get('timeout'))} | {num(r.get('nocov'))} |" for p, r in zip(parts, results)]
    running = [p["name"] for p, r in zip(parts, results) if r["status"].startswith("🔄")]
    state = "закончен" if finished or not any(r["status"].startswith(("🔄", "⏳")) for r in results) else (
        "идут: " + ", ".join(running) if running else "ждёт старта")
    return "\n".join([
        f"# Прогресс мутационной проверки — итерация {version}",
        "",
        "```text",
        "█" * pct + "░" * (100 - pct) + f" {pct}%",
        "```",
        "",
        f"Проверено: {tested} из {total} мутантов · убито {num(killed)} · выжило {num(survived)} · "
        f"таймаут {num(timeout)} · без покрытия {num(nocov)}",
        "",
        "| Часть | Что мутируется | Потоки | Статус | Мутантов | Проверено | Убито | Выжило | Таймаут | Без покрытия |",
        "|---|---|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"Состояние: {state} · бюджет: {budget or '—'} · обновлено {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ])


def watch(args: list[str]) -> None:
    """Rewrite the page every N seconds (default 120) until every part has ended, printing only the lines of parts
    whose status changed — one Monitor over this command follows the whole run, and it ends by itself."""
    import subprocess
    import time
    i = args.index("--watch")
    every = float(args[i + 1]) if i + 1 < len(args) and args[i + 1].replace(".", "", 1).isdigit() else 120.0
    base = [sys.executable, str(Path(__file__).resolve()), args[0], args[1]]
    while True:
        out = subprocess.run(base, capture_output=True, text=True).stdout
        for line in out.splitlines():
            if line.startswith("часть "):
                print(line, flush=True)
        if "все части закончены" in out:
            break
        time.sleep(every)
    final = subprocess.run(base + ["--done"], capture_output=True, text=True).stdout.strip().splitlines()
    print(final[-1] if final else "мутации: закончено", flush=True)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    if "--watch" in args:
        watch(args)
        return
    md, cfg = Path(args[0]), Path(args[1])
    finished = "--done" in args
    spec = json.loads(cfg.read_text(encoding="utf-8"))
    parts = spec["parts"]
    results = [read(p, finished) for p in parts]
    old = md.read_text(encoding="utf-8") if md.is_file() else ""
    was = {}
    for line in old.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 10:
            was[cells[0]] = cells[3]
    m = re.search(r"^## ", old, re.M)
    rest = old[m.start():] if m else (f"{SURVIVORS}\n\n| Мутант | Часть | Решение | Куда | Статус |\n"
                                      "|---|---|---|---|---|\n")
    version = md.resolve().parent.name
    md.write_text(top(version, parts, results, spec.get("budget", ""), finished) + "\n" + rest, encoding="utf-8")
    try:
        import progress_page
        progress_page.page(md)
    except Exception as e:  # the page is a view; the file is already right
        print(f"progress_mutation: page not rebuilt ({e})", file=sys.stderr)
    for p, r in zip(parts, results):
        if was.get(p["name"]) != r["status"]:
            print(f"часть «{p['name']}»: {r['status']}")
    total = sum(r.get("total") or 0 for r in results)
    tested = sum(r.get("tested") or 0 for r in results)
    left = [p["name"] for p, r in zip(parts, results) if r["status"].startswith(("🔄", "⏳"))]
    print(f"мутации: {tested} из {total} · " + ("все части закончены" if not left else f"осталось частей: {len(left)}"))


if __name__ == "__main__":
    main()
