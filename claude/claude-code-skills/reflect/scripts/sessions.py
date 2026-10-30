#!/usr/bin/env python3
"""Find this project's Claude Code sessions and boil each down to a readable digest for `reflect`.

usage:
  sessions.py list   <project-dir> [--since YYYY-MM-DD[THH:MM]] [--also <old-project-dir> ...]
                     one line per main session: path, start, end, size; a session copied
                     under several project folders is listed once, and a session whose typed
                     messages all reappear, in order, at the start of a longer one (it was
                     resumed into a new file) is marked «# повтор <id>» and skipped
  sessions.py digest <session.jsonl> <out.md>             the session as a short chronological digest
  sessions.py errors <project-dir> <out.md> [--since YYYY-MM-DD[THH:MM]] [--also <old-project-dir> ...]
                     the failed tool calls of the main sessions AND of every agent they ran
                     (<session>/subagents/), grouped by kind and shape, most repeated first

The transcripts live in ~/.claude/projects/<project dir with every non-alphanumeric character as '-'>/. A path
whose name runs past 200 characters is cut there and gets a short hash (-Users-…-run-1--4izqz2), and a session
started in a worktree of the repository (the desktop app's, `git worktree add`, a folder nested in the project)
sits under the worktree's own path. So the folders read are: the project's own name, its shortened-and-hashed
form, the names of the repository's worktrees (`git worktree list`) and of folders nested in the project — each
session of a candidate kept only when the `cwd` it recorded is the project, one of those worktrees, or a folder
inside them. Only this project's sessions are read — never another project's. `digest` skips subagent transcripts
(in <session>/subagents/): the main session already shows what each dispatch returned. `errors` reads them: an agent
that fixed its own failed command says nothing about it to the session, and a wrong flag or path a skill gave shows
up only there. It reads no model; its digest goes to one session-reviewer.
"""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path

HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
MAX_NAME = 200  # a longer folder name is cut here and gets "-<hash>"


def sanitized(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def project_dir(cwd: str) -> Path:
    return HOME / "projects" / sanitized(cwd)


def worktrees(cwd: str) -> list:
    """The repository's working trees (the main one and every linked one), absolute paths."""
    try:
        out = subprocess.run(["git", "-C", cwd, "worktree", "list", "--porcelain"], capture_output=True, text=True,
                             timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [l[len("worktree "):] for l in out.splitlines() if l.startswith("worktree ")]


def recorded_cwd(path: Path) -> str:
    """The working folder the session recorded (its first «cwd» field), or ""."""
    try:
        with open(path, errors="ignore") as fh:
            for i, line in enumerate(fh):
                m = re.search(r'"cwd":"((?:[^"\\]|\\.)*)"', line)
                if m:
                    return json.loads('"' + m.group(1) + '"')
                if i > 200:
                    break
    except OSError:
        pass
    return ""


def session_dirs(cwd: str, also: list) -> tuple:
    """(folders to read, the roots a session's recorded cwd must sit in)."""
    roots = [os.path.abspath(p) for p in [cwd] + also]
    trees = worktrees(cwd)
    if trees:  # the project may be a folder inside the repository: the same folder inside each worktree
        rel = os.path.relpath(os.path.realpath(cwd), os.path.realpath(trees[0]))
        if not rel.startswith(".."):
            for w in trees:
                r = os.path.abspath(os.path.join(w, rel))
                if r not in roots:
                    roots.append(r)
    names = {sanitized(r) for r in roots}
    base = HOME / "projects"
    found = []
    for d in sorted(base.iterdir()) if base.is_dir() else []:
        if not d.is_dir():
            continue
        n = d.name
        for s in names:
            if (n == s or n.startswith(s + "-")  # the folder itself, or one nested in it (s + "-" + rest)
                    or (len(s) > MAX_NAME and n[:MAX_NAME] == s[:MAX_NAME])):  # shortened with a hash
                found.append(d)
                break
    return found, roots


def ours(path: Path, roots: list) -> bool:
    c = recorded_cwd(path)
    if not c:
        return False
    c = os.path.abspath(c)
    return any(c == r or c.startswith(r.rstrip(os.sep) + os.sep) for r in roots)


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def span(path: Path) -> tuple[str, str]:
    first = last = ""
    with open(path, errors="ignore") as fh:
        for line in fh:
            m = re.search(r'"timestamp":"([0-9T:.\-]+)Z?"', line)
            if m:
                first = first or m.group(1)
                last = m.group(1)
    return first[:16], last[:16]


def typed(path: Path) -> list[str]:
    out = []
    for line in open(path, errors="ignore"):
        if '"kind":"human"' not in line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        txt = text_of(d.get("message", {}).get("content")).strip()
        if txt:
            out.append(txt[:200])
    return out


def cmd_list(cwd: str, since: str | None, also: list[str]) -> None:
    dirs, roots = session_dirs(cwd, also)
    if not dirs:
        print(f"no sessions: {project_dir(cwd)}", file=sys.stderr)
        sys.exit(1)
    exact = {sanitized(r) for r in roots if len(sanitized(r)) <= MAX_NAME}
    seen: dict[str, Path] = {}
    for d in dirs:
        for p in d.glob("*.jsonl"):
            if d.name not in exact and not ours(p, roots):  # a prefix match is confirmed by the recorded cwd
                continue
            if p.stem not in seen or p.stat().st_size > seen[p.stem].stat().st_size:
                seen[p.stem] = p
    rows = []
    for p in sorted(seen.values(), key=lambda p: p.stat().st_mtime):
        a, b = span(p)
        if since and b and b[:len(since)] < since:  # a date, or a date and time (2026-10-09T12:10)
            continue
        rows.append((p, a, b, typed(p)))
    for p, a, b, msgs in rows:
        dup = next((q for q, _, _, m in rows if q != p and msgs and len(m) > len(msgs) and m[:len(msgs)] == msgs), None)
        if dup:
            print(f"# повтор {dup.stem[:8]}: {p}")
            continue
        print(f"{p}\t{a}\t{b}\t{p.stat().st_size // 1024} KB")


def cmd_digest(src: str, out: str) -> None:
    rows: list[str] = []
    for line in open(src, errors="ignore"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = (d.get("timestamp") or "")[:16].replace("T", " ")
        t = d.get("type")
        if t == "user":
            origin = d.get("origin") if isinstance(d.get("origin"), dict) else {}
            if origin.get("kind") != "human":
                continue
            txt = text_of(d.get("message", {}).get("content")).strip()
            if txt:
                rows.append(f"[{ts}] USER: {txt[:2000]}")
        elif t == "assistant":
            for b in d.get("message", {}).get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    rows.append(f"[{ts}] CLAUDE: {b['text'].strip()[:700]}")
                elif b.get("type") == "tool_use":
                    name, inp = b.get("name"), b.get("input") or {}
                    if name == "Skill":
                        rows.append(f"[{ts}] SKILL: {inp.get('skill')} {str(inp.get('args', ''))[:120]}")
                    elif name == "Agent":
                        rows.append(f"[{ts}] AGENT: {inp.get('subagent_type', 'general')} — {str(inp.get('description', ''))[:120]}")
        elif t == "system" and d.get("subtype") == "compact_boundary":
            rows.append(f"[{ts}] === CONTEXT COMPACTED ===")
    Path(out).write_text("\n".join(rows) + "\n")
    print(f"{out}: {len(rows)} entries")


KIND_RX = [  # (kind, pattern over the error text) — first match wins
    ("отказ в правах", r"permission|denied|not allowed|doesn't want to proceed|was rejected|requires approval"),
    ("правка не нашла текст", r"string to replace not found|found \d+ matches|has not been read|modified since"),
    ("нет файла или папки", r"no such file|not found|does not exist|cannot find|ENOENT|ModuleNotFoundError"),
    ("неверный флаг или аргумент", r"unknown (option|flag|argument)|unrecognized|invalid (option|argument)|usage:"),
    ("сеть или таймаут", r"timed? ?out|ETIMEDOUT|ECONNREFUSED|could not resolve|network|503|502"),
]
PROJECT_CHECK = re.compile(r"\b(test|vitest|jest|pytest|playwright|tsc|typecheck|lint|eslint|ruff|mypy|knip|"
                           r"stryker|mutmut|jscpd|depcruise|dependency-cruiser)\b")


def shape(s: str) -> str:
    """The same failure with other numbers, paths and ids is one shape."""
    s = re.sub(r"/[^\s'\"`]+", "<путь>", s)
    s = re.sub(r"\b[0-9a-f]{7,40}\b", "<id>", s)
    s = re.sub(r"\d+", "N", s)
    return re.sub(r"\s+", " ", s).strip()[:140]


def failures(path: Path, who: str, since: str | None) -> list:
    """(who, skill in use, tool, command or target, error text, timestamp) for each failed tool call of one log."""
    calls, out, skill = {}, [], ""
    for line in open(path, errors="ignore"):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = (o.get("timestamp") or "")[:16]
        if since and ts and ts < since:
            continue
        content = (o.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                inp = b.get("input") or {}
                name = b.get("name", "")
                if name == "Skill":
                    skill = str(inp.get("skill", "")).replace("dev-pipeline:", "")
                target = str(inp.get("command") or inp.get("file_path") or inp.get("skill") or inp.get("url")
                             or inp.get("pattern") or json.dumps(inp, ensure_ascii=False))[:300]
                m = re.search(r"(?:skills|claude-code-skills|dev-pipeline/[\d.]+)/([a-z0-9-]+)/(?:SKILL\.md|references/|scripts/)",
                              target)
                if m and name in ("Read", "Bash"):
                    skill = m.group(1)
                calls[b.get("id")] = (name, target, skill)
            elif b.get("type") == "tool_result" and b.get("is_error"):
                name, target, sk = calls.get(b.get("tool_use_id"), ("?", "", skill))
                err = b.get("content")
                if isinstance(err, list):
                    err = " ".join(x.get("text", "") for x in err if isinstance(x, dict))
                err = re.sub(r"</?tool_use_error>", "", str(err or "")).strip()
                out.append((who, sk, name, target, err, ts))
    return out


def cmd_errors(cwd: str, out: str, since: str | None, also: list) -> None:
    dirs, roots = session_dirs(cwd, also)
    exact = {sanitized(r) for r in roots if len(sanitized(r)) <= MAX_NAME}
    mains = [p for d in dirs for p in d.glob("*.jsonl") if d.name in exact or ours(p, roots)]
    rows = []
    for p in mains:
        rows += failures(p, "сессия", since)
        for log in sorted((p.parent / p.stem / "subagents").glob("agent-*.jsonl")):
            try:
                kind = json.loads(log.with_suffix(".meta.json").read_text()).get("agentType") or "агент"
            except (OSError, ValueError):
                kind = "агент"
            rows += failures(log, kind, since)
    groups: dict = {}
    for who, sk, tool, target, err, ts in rows:
        first = next((l for l in err.splitlines() if l.strip() and not l.startswith("Exit code")), err[:100])
        kind = next((k for k, rx in KIND_RX if re.search(rx, err, re.I)), "ошибка команды")
        if tool == "Bash" and kind == "ошибка команды" and PROJECT_CHECK.search(target):
            kind = "проверка проекта (скорее код, чем плагин)"
        head = " ".join(target.split()[:2]) if tool == "Bash" else tool
        key = (kind, tool, shape(head), shape(first))
        g = groups.setdefault(key, {"n": 0, "who": set(), "skills": set(), "ex": (target, err, ts), "ts": ts})
        g["n"] += 1
        g["who"].add(who)
        if sk:
            g["skills"].add(sk)
    order = sorted(groups.items(), key=lambda kv: (kv[0][0].startswith("проверка проекта"), -kv[1]["n"]))
    lines = [f"# Ошибки вызовов · {Path(cwd).name}" + (f" · с {since}" if since else ""), "",
             f"Вызовов с ошибкой: {len(rows)} · групп: {len(groups)} · журналов: сессии {len(mains)} и их агенты. "
             "Группа — одна и та же ошибка с другими числами и путями; «проверка проекта» — упавшие тесты и "
             "линтеры, обычно дело кода, а не плагина.", ""]
    for (kind, tool, head, first), g in order[:80]:
        target, err, ts = g["ex"]
        lines += [f"## ×{g['n']} · {kind} · {tool}",
                  f"- кто: {', '.join(sorted(g['who']))}" + (f" · скилл: {', '.join(sorted(g['skills']))}" if g["skills"] else ""),
                  f"- пример ({ts.replace('T', ' ')}): `{target[:240]}`",
                  "- ошибка: " + re.sub(r"\s+", " ", err)[:400], ""]
    if len(order) > 80:
        lines.append(f"… и ещё {len(order) - 80} групп по одному-двум случаям.")
    Path(out).write_text("\n".join(lines) + "\n")
    print(f"{out}: {len(rows)} failed calls in {len(groups)} groups")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "list":
        since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
        also = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--also"]
        cmd_list(sys.argv[2], since, also)
    elif len(sys.argv) == 4 and sys.argv[1] == "digest":
        cmd_digest(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == "errors":
        since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
        also = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--also"]
        cmd_errors(sys.argv[2], sys.argv[3], since, also)
    else:
        print(__doc__)
        sys.exit(2)
