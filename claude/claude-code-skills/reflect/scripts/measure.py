#!/usr/bin/env python3
"""What a project's pipeline runs cost, and who spent it — from Claude Code's own session logs, for `reflect`.

usage:
  measure.py <project-dir> [--since YYYY-MM-DD[THH:MM]] [--also <old-project-dir> ...]
             [--progress <plans/<version>/progress.md> ...] [--units <git range>] [--json <out.json>]

--json also writes the run's figures (total, by group, the session's spend and peak, executors over 250k, unit
acceptance) for compare.py, which compares several runs of two variants (reflect/references/comparing.md).

--progress (one per iteration whose progress file is still there) and --units (the iterations' git range, e.g.
v2.1.2..HEAD) add «Принятие задач»: how many plan units passed their review the first time, how many went back,
and what one accepted unit cost — executors and code review together, divided by the units accepted. From the
progress file's Ревью column (`COMMIT` alone is the first time; `RETURN_…`, `FIX_THEN_COMMIT`, `×2`, `→` mean
rounds). Each progress file read is also saved outside the project — ~/.claude/dev-pipeline-feedback/.acceptance/
<project>/<version>.txt — because reflect runs at the iteration's close before the cleanup removes the file; a
later run reads the saved numbers for a version whose file is gone. Without either, from git — a unit with more
than one commit carrying its Plan-Unit line was fixed after its commit.

Reads the project's main sessions (found as `sessions.py list` finds them) and every subagent transcript beside
them (<session>/subagents/agent-*.jsonl with its .meta.json, which names the agent: `dev-pipeline:impl-medium`).
Prints, in Russian Markdown: the total; the spend by group (the session itself, executors, code review, document
writers, document and plan review, Figma, UI runs, audit, other) and by agent; the models; the context the agents
reached; the flags worth a look. Read-only.

A call is one model request — a unique message id, counted once even when a resumed session repeats it or the log
writes it as several lines. Spend is in normalized units, relative to one input token, so runs and roles compare:
output ×5, cache write ×1.25 (×2 for the one-hour cache), cache read ×0.1. These are ratios, not money: a model's
own price is not applied — the models table says which model spent what. Python 3.9+, standard library only.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

W_IN, W_WRITE, W_WRITE_1H, W_READ, W_OUT = 1.0, 1.25, 2.0, 0.1, 5.0
IDLE = 300            # a gap longer than this between two calls of the session is a pause, not work
SMALL, BIG = 100_000, 250_000   # an executor that peaked below SMALL paid its cold start for little work; above BIG,
#                                 every call re-reads a context that big (cache reads grow with the square of the work)

GROUPS = [  # (group, agent names without the plugin prefix)
    ("Исполнители", {"impl-lite", "impl-medium", "impl-hard", "impl-critical", "impl-ui", "mechanical-worker"}),
    ("Ревью кода", {"review-medium", "review-hard", "review-full-plan"}),
    ("Писатели документов", {"srs-author", "design-lite", "design-medium", "design-hard", "plan-lite",
                             "plan-medium", "plan-hard", "doc-typist", "screen-writer", "ui-test-writer"}),
    ("Ревью документов и плана", {"doc-review-low", "doc-review-medium", "doc-review-hard", "plan-review-medium",
                                  "plan-review-hard", "docs-consistency-checker"}),
    ("Макеты в Figma", {"figma-opus", "figma-sonnet"}),
    ("Прогон UI-тестов", {"ui-test-runner"}),
    ("Аудит безопасности", {"security-auditor"}),
    ("Аудит кода", {"code-auditor"}),
    ("Поиск по коду и разбор сессий", {"code-explorer", "session-reviewer"}),
]
SESSION = "Сессия (оркестратор)"


def group_of(agent: str) -> str:
    if agent == SESSION:
        return SESSION
    name = agent.split(":", 1)[-1]
    return next((g for g, names in GROUPS if name in names), "Прочие агенты")


class Agent:
    def __init__(self, kind: str, label: str):
        self.kind, self.label = kind, label
        self.calls = 0
        self.tokens = defaultdict(int)          # in, write, write1h, read, out
        self.units = 0.0
        self.peak = 0
        self.first_ctx = 0
        self.t0 = self.t1 = ""
        self.models: dict = defaultdict(float)


def add_call(a: Agent, usage: dict, model: str, ts: str) -> float:
    cc = usage.get("cache_creation") or {}
    w1h = int(cc.get("ephemeral_1h_input_tokens") or 0)
    write = int(usage.get("cache_creation_input_tokens") or 0)
    tin, read, out = (int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "output_tokens"))
    return add_counts(a, tin, max(write - w1h, 0), w1h, read, out, model, ts)


def add_counts(a: Agent, tin: int, w5: int, w1h: int, read: int, out: int, model: str, ts: str) -> float:
    """One model call: uncached input, cache writes (5-minute, one-hour), cache reads, output."""
    units = W_IN * tin + W_WRITE * w5 + W_WRITE_1H * w1h + W_READ * read + W_OUT * out
    ctx = tin + w5 + w1h + read
    a.calls += 1
    for k, v in (("in", tin), ("write", w5), ("write1h", w1h), ("read", read), ("out", out)):
        a.tokens[k] += v
    a.units += units
    a.peak = max(a.peak, ctx)
    a.first_ctx = a.first_ctx or ctx
    a.models[model or "?"] += units
    if ts:
        a.t0 = min(a.t0, ts) if a.t0 else ts
        a.t1 = max(a.t1, ts)
    return units


def read_log(path: Path, a: Agent, seen: set, since: str | None, beats: list | None = None) -> None:
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return
    with fh:
        for line in fh:
            if '"usage"' not in line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = e.get("message") or {}
            usage, mid = m.get("usage"), m.get("id")
            if e.get("type") != "assistant" or not usage or not mid or mid in seen:
                continue
            ts = (e.get("timestamp") or "")[:19]
            if since and ts and ts[:len(since)] < since:
                continue
            seen.add(mid)
            add_call(a, usage, m.get("model", ""), ts)
            if beats is not None and ts:
                beats.append(ts)


def active_minutes(beats: list) -> int:
    from datetime import datetime
    ts = sorted(datetime.fromisoformat(b) for b in beats)
    return int(sum(min((b - a).total_seconds(), IDLE) for a, b in zip(ts, ts[1:])) // 60)


def fmt(n: float) -> str:
    return f"{n / 1e6:.1f} млн" if n >= 1e6 else f"{n / 1e3:.0f} тыс."


STORE = (Path.home() / (".codex" if (Path(__file__).resolve().parent / "codex_logs.py").exists() else ".claude")
         / "dev-pipeline-feedback" / ".acceptance")  # outside every project; the Codex build keeps its own


def acceptance(progress: list, rng: str, cwd: str) -> tuple[int, int, int, str]:
    """(accepted, first time, sent back, source) over the plan units of the progress files, else of git."""
    import re
    import subprocess
    accepted = first = back = 0
    for path in progress:
        saved = STORE / Path(cwd).resolve().name / f"{Path(path).parent.name}.txt"
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError:
            try:  # removed by the close's cleanup: the numbers this script saved while the file was there
                a, f, b = (int(x) for x in saved.read_text().split()[:3])
            except (OSError, ValueError):
                continue
            accepted, first, back = accepted + a, first + f, back + b
            continue
        a0, f0, b0 = accepted, first, back
        for line in text.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5 or not re.fullmatch(r"U\d+", cells[0]) or "✅" not in line:
                continue
            accepted += 1
            review = cells[-1]
            if re.search(r"RETURN|FIX_THEN|→|×\s*[2-9]|возвращ|эскалац", review + " " + line, re.I):
                back += 1
            else:
                first += 1
        try:
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_text(f"{accepted - a0} {first - f0} {back - b0}\n")
        except OSError:
            pass
    if accepted:
        return accepted, first, back, "файлы прогресса"
    if not rng:
        return 0, 0, 0, ""
    log = subprocess.run(["git", "-C", cwd, "log", rng, "--format=%B"], capture_output=True, text=True).stdout
    ids = re.findall(r"^Plan-Unit:\s*(\S+/U\d+)\s*$", log, re.M)
    count: dict = defaultdict(int)
    for u in ids:
        count[u] += 1
    accepted = len(count)
    back = sum(1 for n in count.values() if n > 1)
    return accepted, accepted - back, back, f"git {rng} (возвраты до коммита не видны)"


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    cwd = args[0]
    since = args[args.index("--since") + 1] if "--since" in args else None
    also = [args[i + 1] for i, a in enumerate(args) if a == "--also" and i + 1 < len(args)]
    try:  # the Codex build ships codex_logs.py beside this file: Codex rollouts instead of Claude Code's logs
        import codex_logs
        session, agents, active, beats = codex_logs.collect(cwd, since, also, Agent, add_counts, SESSION)
    except ImportError:
        session, agents, active, beats = collect_claude(cwd, since, also)
    report(args, cwd, since, session, agents, active, beats)


def collect_claude(cwd: str, since: str | None, also: list) -> tuple:
    """(the session, its agents, how many sessions were active, the session's call times) from Claude Code's logs."""
    from sessions import MAX_NAME, ours, sanitized, session_dirs  # same discovery as `sessions.py list`
    dirs, roots = session_dirs(cwd, also)
    exact = {sanitized(r) for r in roots if len(sanitized(r)) <= MAX_NAME}
    mains = [p for d in dirs for p in d.glob("*.jsonl") if d.name in exact or ours(p, roots)]
    if not mains:
        sys.exit(f"no sessions for {cwd}")

    seen: set = set()
    session = Agent(SESSION, SESSION)
    beats: list = []
    agents: list = []
    active = 0
    for p in sorted(mains, key=lambda p: p.stat().st_mtime):
        before = session.calls
        read_log(p, session, seen, since, beats)
        for log in sorted((p.parent / p.stem / "subagents").glob("agent-*.jsonl")):
            try:
                meta = json.loads(log.with_suffix(".meta.json").read_text())
            except (OSError, ValueError):
                meta = {}
            a = Agent(meta.get("agentType") or "?", (meta.get("description") or "")[:60])
            read_log(log, a, seen, since)
            if a.calls:
                agents.append(a)
        active += session.calls > before
    return session, agents, active, beats


def report(args: list, cwd: str, since: str | None, session, agents: list, active: int, beats: list) -> None:
    every = [session] + agents
    total = sum(a.units for a in every)
    if not total:
        sys.exit("no model calls in that window")
    stamps = [t for a in every for t in (a.t0, a.t1) if t]
    print(f"## Расход · {Path(cwd).name}" + (f" · с {since}" if since else ""))
    print()
    print(f"Окно: {min(stamps)[:16].replace('T', ' ')} — {max(stamps)[:16].replace('T', ' ')} · "
          f"сессий: {active} · агентов запущено: {len(agents)} · вызовов модели: {sum(a.calls for a in every)} · "
          f"всего: **{fmt(total)}** единиц · работа сессии: ~{active_minutes(beats) // 60} ч {active_minutes(beats) % 60} мин")
    print()
    print("Единицы — токены, приведённые к цене входного токена: вывод ×5, запись в кэш ×1,25 (часовой ×2), чтение "
          "кэша ×0,1. Это пропорции для сравнения ролей и прогонов, а не деньги: цена модели не учтена.")

    by_group: dict = defaultdict(lambda: [0.0, 0, 0])
    for a in every:
        g = by_group[group_of(a.kind)]
        g[0] += a.units
        g[1] += 1 if a is not session else 0
        g[2] += a.calls
    print("\n#### По группам\n")
    print("| Группа | Доля | Единиц | Агентов | Вызовов |")
    print("|---|---|---|---|---|")
    for name, (u, n, c) in sorted(by_group.items(), key=lambda kv: -kv[1][0]):
        print(f"| {name} | {u / total:.0%} | {fmt(u)} | {n or '—'} | {c} |")

    by_kind: dict = defaultdict(list)
    for a in agents:
        by_kind[a.kind].append(a)
    print("\n#### По агентам\n")
    print("| Агент | Запусков | Единиц | На запуск | Пик контекста, средний · max | Старт, средний |")
    print("|---|---|---|---|---|---|")
    for kind, xs in sorted(by_kind.items(), key=lambda kv: -sum(a.units for a in kv[1])):
        u = sum(a.units for a in xs)
        print(f"| {kind} | {len(xs)} | {fmt(u)} | {fmt(u / len(xs))} | {fmt(sum(a.peak for a in xs) / len(xs))} · "
              f"{fmt(max(a.peak for a in xs))} | {fmt(sum(a.first_ctx for a in xs) / len(xs))} |")
    print(f"| {SESSION} | — | {fmt(session.units)} | — | max {fmt(session.peak)} | — |")

    models: dict = defaultdict(float)
    for a in every:
        for m, u in a.models.items():
            models[m] += u
    print("\n#### По моделям\n")
    print("| Модель | Доля | Единиц |")
    print("|---|---|---|")
    for m, u in sorted(models.items(), key=lambda kv: -kv[1]):
        if u >= 0.5 and not m.startswith("<"):  # «<synthetic>» is Claude Code's own placeholder, not a model
            print(f"| {m} | {u / total:.0%} | {fmt(u)} |")

    toks = defaultdict(int)
    for a in every:
        for k, v in a.tokens.items():
            toks[k] += v
    parts = {"чтение кэша": W_READ * toks["read"], "запись в кэш": W_WRITE * toks["write"] + W_WRITE_1H * toks["write1h"],
             "вывод": W_OUT * toks["out"], "вход без кэша": W_IN * toks["in"]}
    print("\n#### Из чего сложились единицы\n")
    print(" · ".join(f"{k}: {v / total:.0%}" for k, v in sorted(parts.items(), key=lambda kv: -kv[1])))

    execs = [a for a in agents if group_of(a.kind) == "Исполнители"]
    flags = []
    if execs:
        small = [a for a in execs if a.peak < SMALL]
        big = [a for a in execs if a.peak > BIG]
        if small:
            flags.append(f"исполнителей с пиком контекста меньше {SMALL // 1000} тыс.: {len(small)} из {len(execs)} — "
                         f"их старт (в среднем {fmt(sum(a.first_ctx for a in small) / len(small))}) почти весь их "
                         "расход; задачи такого размера дешевле объединять")
        if big:
            flags.append(f"исполнителей с пиком больше {BIG // 1000} тыс.: {len(big)} из {len(execs)} — каждый их вызов "
                         "перечитывает большой контекст; такие задачи дешевле делить")
    review = by_group.get("Ревью кода", [0.0])[0]
    built = by_group.get("Исполнители", [0.0])[0]
    if built and review > built * 0.6:
        flags.append(f"ревью кода стоит {review / built:.0%} от работы исполнителей")
    if session.units / total > 0.4:
        flags.append(f"сама сессия — {session.units / total:.0%} расхода: оркестратор держит большой контекст "
                     f"(пик {fmt(session.peak)})")
    accepted = first = back = 0
    progress = [args[i + 1] for i, a in enumerate(args) if a == "--progress" and i + 1 < len(args)]
    rng = args[args.index("--units") + 1] if "--units" in args and args.index("--units") + 1 < len(args) else ""
    if progress or rng:
        accepted, first, back, source = acceptance(progress, rng, cwd)
        print("\n#### Принятие задач\n")
        if accepted:
            cost = (by_group.get("Исполнители", [0.0])[0] + by_group.get("Ревью кода", [0.0])[0]) / accepted
            label = "с первого ревью" if source.startswith("файлы прогресса") else "без исправлений после коммита"
            print(f"Задач принято: {accepted} · {label}: {first} ({first / accepted:.0%}) · возвращались: "
                  f"{back} · одна принятая задача (исполнители и ревью кода): **{fmt(cost)}** единиц · источник: {source}")
            print("Стоимость одной задачи считается по всему окну: работа других итераций в том же окне её завышает.")
            if first / accepted < 0.5:
                flags.append(f"с первого ревью прошло меньше половины задач ({first / accepted:.0%}) — переделки "
                             "стоят больше, чем экономят проверки; смотреть пакеты и границы задач")
        else:
            print("нет данных: файлов прогресса нет, коммитов с Plan-Unit в диапазоне нет")
    print("\n#### На что посмотреть\n")
    print("\n".join(f"- {f}" for f in flags) if flags else "- ничего необычного по порогам скрипта")
    if "--json" in args and args.index("--json") + 1 < len(args):
        built = by_group.get("Исполнители", [0.0])[0] + by_group.get("Ревью кода", [0.0])[0]
        Path(args[args.index("--json") + 1]).write_text(json.dumps({
            "total": total, "groups": {k: v[0] for k, v in by_group.items()},
            "session": session.units, "session_peak": session.peak, "calls": sum(a.calls for a in every),
            "executors": len(execs), "executors_over_250k": sum(1 for a in execs if a.peak > BIG),
            "accepted": accepted, "first_review": first, "sent_back": back,
            "first_review_share": first / accepted if accepted else None,
            "per_accepted_unit": built / accepted if accepted else None,
        }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
