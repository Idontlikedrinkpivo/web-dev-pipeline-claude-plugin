#!/usr/bin/env python3
"""What a project's pipeline runs cost, and who spent it — from Claude Code's own session logs, for `reflect`.

usage:
  measure.py <project-dir> [--since YYYY-MM-DD[THH:MM]] [--also <old-project-dir> ...]

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
from sessions import MAX_NAME, ours, sanitized, session_dirs  # noqa: E402  same discovery as `sessions.py list`

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
    w5 = max(write - w1h, 0)
    tin, read, out = (int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "output_tokens"))
    units = W_IN * tin + W_WRITE * w5 + W_WRITE_1H * w1h + W_READ * read + W_OUT * out
    ctx = tin + write + read
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


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    cwd = args[0]
    since = args[args.index("--since") + 1] if "--since" in args else None
    also = [args[i + 1] for i, a in enumerate(args) if a == "--also" and i + 1 < len(args)]
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
    print("\n#### На что посмотреть\n")
    print("\n".join(f"- {f}" for f in flags) if flags else "- ничего необычного по порогам скрипта")


if __name__ == "__main__":
    main()
