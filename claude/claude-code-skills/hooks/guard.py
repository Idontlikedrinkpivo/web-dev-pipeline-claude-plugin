#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-pipeline: PreToolUse guard — refuse the few commands that broke real runs again and again although the rules
said not to (reflect's reports, the findings doc Т-19, Т-23, 2.1.x). Each refusal names the rule and what to do
instead; the model reads it and does the right thing. Only clear-cut cases are refused — everything else passes.

    stdin: the hook's JSON (tool_name, tool_input, cwd)   stdout: a deny decision, or nothing

Refused:
- Bash `git commit` chained in one command to a test, lint or typecheck run — the commit lands before anyone read
  the output (work → references/run-hygiene.md → Commits);
- Bash `git commit` on main / master while the project has an open iteration — every commit goes on
  `iteration/<version>` (pipeline → One branch per iteration);
- Bash `git commit` whose `Plan-Unit:` line is split from the next trailer by a blank line or another `-m` — git
  then drops it from the trailers and the unit reads as unmapped (run-hygiene → Commits);
- Bash `sed -i` — BSD sed on macOS takes the next argument as the backup suffix and corrupts files; Edit instead;
- Bash that writes a progress file (documentation/plans/…/progress*.md, test-run.md, security-audit.md) — the page
  is redrawn only after Edit/Write or by the progress scripts (pipeline → references/progress-files.md → How);
- Bash `git stash`, `git reset --hard`, `git clean`, `git checkout -- .` / `git restore .` in the main working tree
  — they wipe other agents' and the user's uncommitted work (run-hygiene → Executors in the shared tree);
- Edit / Write of a file outside the worktree the agent runs in — its edit lands in the main tree
  (executor-catalog → worker-prompt RULES).

Acts only in a project with documentation/.dev-pipeline.json. Never fails the tool call on its own error.
`decide()` is pure, so `claude/tools/guard_replay.py` can run it over past sessions.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

RUNNER = re.compile(r"\b(?:npm (?:run )?(?:test|lint|typecheck)|npx (?:vitest|jest|tsc|eslint|playwright test)|"
                    r"pnpm (?:run )?(?:test|lint|typecheck)|yarn (?:test|lint|typecheck)|pytest|"
                    r"uv run (?:pytest|ruff|mypy)|ruff check|mypy|tsc|vitest|run_check\.py)\b")
COMMIT = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?commit\b")
CHAIN = re.compile(r"&&|\|\||;|\n")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2(?=\s|$|\))", re.S)
PROGRESS_FILE = re.compile(r"documentation/plans/[^/\s'\"]+/(?:progress[\w-]*\.md|test-run\.md|security-audit\.md)$")
PROGRESS_SCRIPTS = re.compile(r"progress_(?:set|e2e|mutation|link|page)\.py")
PY_WRITES = re.compile(r"write_text|\.write\(|open\([^)]*['\"][wa]\+?['\"]")


def deny(why: str) -> str:
    return "dev-pipeline: " + why


def heredocs(cmd: str) -> tuple[str, list[str]]:
    """The command with its here-document bodies taken out, and the bodies."""
    bodies = [m.group(3) for m in HEREDOC.finditer(cmd)]
    return HEREDOC.sub("<<HEREDOC", cmd), bodies


def unquoted(cmd: str) -> str:
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", "Q", cmd)


def commit_message(cmd: str, bodies: list[str]) -> str | None:
    body = next((b for b in bodies if re.search(r"^Plan-Unit:", b, re.M)), None)
    if body is not None:
        return body
    seg = cmd[COMMIT.search(cmd).end():]
    try:
        words = shlex.split(seg, posix=True)
    except ValueError:
        return None
    msgs = []
    for i, w in enumerate(words):
        if w in ("-m", "--message") and i + 1 < len(words):
            msgs.append(words[i + 1])
        elif w.startswith("-m") and len(w) > 2:
            msgs.append(w[2:])
        elif w.startswith("--message="):
            msgs.append(w.split("=", 1)[1])
    return "\n\n".join(msgs) if msgs else None


def trailer_lost(message: str) -> bool:
    """True when the message has a `Plan-Unit:` line that git does not read as a trailer."""
    if not re.search(r"^Plan-Unit:", message, re.M):
        return False
    try:
        out = subprocess.run(["git", "interpret-trailers", "--parse"], input=message, capture_output=True,
                             text=True, timeout=5).stdout
    except Exception:
        return False
    return "Plan-Unit:" not in out


def commit_issue(cmd: str, bare: str, bodies: list[str], branch: str, open_iteration: str | None) -> str | None:
    if not COMMIT.search(bare):
        return None
    parts = [p for p in CHAIN.split(unquoted(bare)) if p.strip()]
    if len(parts) > 1 and any(RUNNER.search(p) for p in parts if not COMMIT.search(p)):
        return deny("git commit is chained to a test, lint or typecheck run in one command, so it lands before anyone "
                    "has read the output. Run the check first (run_check.py), read its summary, then commit in its own "
                    "call (work → references/run-hygiene.md → Commits).")
    if branch in ("main", "master") and open_iteration:
        return deny(f"this commit would land on {branch} while iteration {open_iteration} is open; every commit of "
                    f"the iteration goes on iteration/{open_iteration}. Switch with "
                    f"`python3 <pipeline>/scripts/open_iteration.py {open_iteration}` (it only switches) and commit "
                    "there (pipeline → One branch per iteration).")
    message = commit_message(cmd, bodies)
    if message and trailer_lost(message):
        return deny("git would not read this commit's `Plan-Unit:` line as a trailer (a blank line or another -m "
                    "splits it from the last paragraph), so the unit reads as unmapped. Put `Plan-Unit: "
                    "<version>/<id>` and `Co-Authored-By:` together in the message's last paragraph, no blank line "
                    "between them (work → references/run-hygiene.md → Commits).")
    return None


def bad_sed(cmd: str) -> bool:
    """`sed -i` written the GNU way: on macOS the next word becomes the backup suffix. `sed -i ''`, `sed -i.bak` pass."""
    for m in re.finditer(r"(?:^|[\s;&|(])sed\s+((?:-[A-Za-z]+\s+)*)-i(\S*)(?:\s+(\S+))?", cmd):
        if m.group(2):          # -i.bak, -i'' — a suffix attached
            continue
        if m.group(3) in ("''", '""'):
            continue
        return True
    return False


def writes_progress(bare: str, bodies: list[str]) -> bool:
    if PROGRESS_SCRIPTS.search(bare):
        return False
    targets = re.findall(r"(?:(?<![<>&\d])>{1,2}|\btee\s+(?:-a\s+)?)\s*['\"]?([^\s'\";|&)]+)", bare)
    if any(PROGRESS_FILE.search(t) for t in targets):
        return True
    return any(PY_WRITES.search(b) and re.search(PROGRESS_FILE.pattern.rstrip("$"), b) for b in bodies
               if re.search(r"\bpython3?\b", bare))


def destructive(bare: str) -> bool:
    b = unquoted(bare)
    for m in re.finditer(r"\bgit\s+(?:-C\s+\S+\s+)?stash\b([^;&|\n]*)", b):
        rest = m.group(1).split()
        sub = rest[0] if rest and not rest[0].startswith("-") else "push"
        if sub in ("push", "save") and "--" not in rest:
            return True
    return bool(re.search(r"\bgit\s+(?:-C\s+\S+\s+)?(?:reset\s+(?:\S+\s+)*--hard\b|clean\s+(?:\S+\s+)*-\w*f"
                          r"|checkout\s+(?:--\s+)?\.(?:\s|$)|restore\s+(?!.*--staged)(?:--\S+\s+)*\.(?:\s|$))", b))


def decide(tool: str, inp: dict, cwd: str, *, branch: str = "", open_iteration: str | None = None,
           worktree_root: str | None = None, main_root: str | None = None) -> str | None:
    """A refusal text, or None to let the call through."""
    if tool == "Bash":
        cmd = str(inp.get("command", ""))
        bare, bodies = heredocs(cmd)
        why = commit_issue(cmd, bare, bodies, branch, open_iteration)
        if why:
            return why
        if bad_sed(bare):
            return deny("`sed -i` without a suffix argument: BSD sed on macOS takes the next word as the backup "
                        "suffix and corrupts the file. Change files with the Edit tool (or `sed -i ''` if a shell "
                        "edit is unavoidable).")
        if writes_progress(bare, bodies):
            return deny("this command writes a progress file from the shell; the page the user watches is redrawn "
                        "only after Edit/Write or by the progress scripts. Change rows with Edit, the bar and count "
                        "with progress_set.py (pipeline → references/progress-files.md → How).")
        if not worktree_root and destructive(bare) and "/.claude/worktrees/" not in bare:
            return deny("git stash (of everything) / reset --hard / clean -f / checkout -- . in the main working "
                        "tree wipe uncommitted work of other agents and of the user. Restore only the files you "
                        "changed, by name (`git checkout -- <file>`, `git stash push -- <paths>`), or ask the user "
                        "(work → references/run-hygiene.md → Executors in the shared tree).")
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit") and worktree_root and main_root:
        path = str(inp.get("file_path") or inp.get("notebook_path") or "")
        if path and os.path.isabs(path):
            real, wt, main = (os.path.realpath(p) for p in (path, worktree_root, main_root))
            inside = lambda root: real == root or real.startswith(root + os.sep)
            plans = os.path.join(main, "documentation", "plans")   # out of git: it lives only in the main tree
            if inside(main) and not inside(wt) and not inside(plans):
                return deny(f"you work in the worktree {worktree_root}, but this edit targets {path} in the main "
                            "tree. Use the same path inside the worktree (executor-catalog → "
                            "references/worker-prompt.md → RULES).")
    return None


def git(cwd: str, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def open_iteration(project: str) -> str | None:
    plans = os.path.join(project, "documentation", "plans")
    try:
        vs = [v for v in os.listdir(plans) if re.fullmatch(r"\d+(\.\d+)*", v)
              and not os.path.exists(os.path.join(plans, v, "summary.md"))]
    except OSError:
        return None
    return max(vs, key=lambda v: [int(x) for x in v.split(".")]) if vs else None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if not os.path.isfile(os.path.join(project, "documentation", ".dev-pipeline.json")):
        return
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    cwd = data.get("cwd") or project
    top = git(cwd, "rev-parse", "--show-toplevel")
    is_worktree = bool(top) and git(cwd, "rev-parse", "--absolute-git-dir") != os.path.realpath(
        git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir") or "-")
    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD") if tool == "Bash" and "commit" in str(inp) else ""
    main_root = os.path.dirname(git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")) if is_worktree else None
    why = decide(tool, inp, cwd, branch=branch, open_iteration=open_iteration(project) if branch else None,
                 worktree_root=top if is_worktree else None, main_root=main_root)
    if why:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": why}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a guard must never break the tool call it watches
