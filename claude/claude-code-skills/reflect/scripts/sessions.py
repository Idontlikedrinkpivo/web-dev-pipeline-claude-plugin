#!/usr/bin/env python3
"""Find this project's Claude Code sessions and boil each down to a readable digest for `reflect`.

usage:
  sessions.py list   <project-dir> [--since YYYY-MM-DD]   one line per main session: path, start, end, size
  sessions.py digest <session.jsonl> <out.md>             the session as a short chronological digest

The transcripts live in ~/.claude/projects/<project dir with every non-alphanumeric character as '-'>/.
Only this project's folder is read — never another project's sessions. Subagent transcripts (in
<session>/subagents/) are skipped: the main session already shows what each dispatch returned.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))


def project_dir(cwd: str) -> Path:
    return HOME / "projects" / re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))


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


def cmd_list(cwd: str, since: str | None) -> None:
    d = project_dir(cwd)
    if not d.is_dir():
        print(f"no sessions: {d}", file=sys.stderr)
        sys.exit(1)
    for p in sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        a, b = span(p)
        if since and b and b[:10] < since:
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


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "list":
        since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
        cmd_list(sys.argv[2], since)
    elif len(sys.argv) == 4 and sys.argv[1] == "digest":
        cmd_digest(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
