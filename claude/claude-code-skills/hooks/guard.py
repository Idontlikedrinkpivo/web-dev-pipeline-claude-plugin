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
- Bash `sed -i` without a suffix argument (`sed -i ''` and `sed -i.bak` pass) — BSD sed on macOS takes the next
  argument as the backup suffix and corrupts files; Edit instead;
- Bash that writes a progress file (documentation/plans/…/progress*.md, test-run.md, security-audit.md) — the page
  is redrawn only after Edit/Write or by the progress scripts (pipeline → references/progress-files.md → How);
- Bash `git stash`, `git reset --hard`, `git clean`, `git checkout -- .` / `git restore .` in the main working tree
  — they wipe other agents' and the user's uncommitted work (run-hygiene → Executors in the shared tree);
- Edit / Write of a file outside the worktree the agent runs in — its edit lands in the main tree
  (executor-catalog → worker-prompt RULES).

Acts only in a project with documentation/.dev-pipeline.json. Never fails the tool call on its own error. Each
refusal is also logged outside the project (~/.claude/dev-pipeline-feedback/.guard/<project>.jsonl), and reflect
reports them (reflect/scripts/guard_report.py).
`decide()` is pure, so `claude/tools/guard_replay.py` can run it over past sessions.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RUNNER = re.compile(r"\b(?:npm (?:run )?(?:test|lint|typecheck)|npx (?:vitest|jest|tsc|eslint|playwright test)|"
                    r"pnpm (?:run )?(?:test|lint|typecheck)|yarn (?:test|lint|typecheck)|pytest|"
                    r"uv run (?:pytest|ruff|mypy)|ruff check|mypy|tsc|vitest|run_check\.py)\b")
COMMIT = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?commit\b")
CHAIN = re.compile(r"&&|\|\||;|\n")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2(?=\s|$|\))", re.S)
PROGRESS_FILE = re.compile(r"documentation/plans/[^/\s'\"]+/(?:progress[\w-]*\.md|test-run\.md|security-audit\.md)$")
PROGRESS_SCRIPTS = re.compile(r"progress_(?:set|e2e|mutation|link|page)\.py")
PY_WRITES = re.compile(r"write_text|\.write\(|open\([^)]*['\"][wa]\+?['\"]")
# a progress file named as a path of its own — a string literal that is the path and nothing else — not the name
# mentioned inside prose the script writes elsewhere (a journal naming progress-architecture.md was refused)
PY_PROGRESS_PATH = re.compile(r"""["']([^"'\s]*documentation/plans/[^/\s'"]+/(?:progress[\w-]*|test-run|security-audit)\.md)["']""")


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


MOVES_MAIN = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:fetch\s+\.\s+\S+:(?:refs/heads/)?(?:main|master)\b"
                        r"|update-ref\s+refs/heads/(?:main|master)\b|push\s+\S+\s+\S*:(?:refs/heads/)?(?:main|master)\b)")
MERGE = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?merge(?![\w-])(?!\s+--abort)")   # not merge-base
TO_MAIN = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:checkout|switch)\s+(?:-\S+\s+)*(?:main|master)\b")


def merge_issue(bare: str, branch: str, open_iteration: str | None, tagged: bool) -> str | None:
    """main/master moved — a local merge or fast-forward, a push to it — or the iteration branch deleted while the
    open iteration has no tag: the close (audit, summary, tag) has not run (pipeline → End of the pipeline). A
    command that tags the iteration first passes."""
    if not open_iteration or tagged or re.search(rf"\bgit\s+tag\s+(?:-\S+\s+)*v{re.escape(open_iteration)}\b", bare):
        return None
    drop = re.search(rf"\bgit\s+(?:-C\s+\S+\s+)?branch\s+(?:-\S+\s+)*-[dD]\w*\s+(?:\S+\s+)*"
                     rf"iteration/{re.escape(open_iteration)}(?![\w.])", bare)   # this iteration's branch only
    if MOVES_MAIN.search(bare) or drop or (MERGE.search(bare) and (branch in ("main", "master") or TO_MAIN.search(bare))):
        return deny(f"iteration {open_iteration} is not closed (no tag v{open_iteration}): moving main/master or "
                    "deleting the iteration branch now skips its close — the audit, the summary, the tag. Run "
                    "close_iteration.py, tell the user the steps it marks ✗ and ask «Слить как есть или сначала "
                    "закрыть итерацию?» (pipeline → End of the pipeline); merging as it is stays the user's, on GitHub.")
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
    return any(PY_WRITES.search(b) and PY_PROGRESS_PATH.search(b) for b in bodies
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
    paths = []   # the files the edit writes: Claude Code's file_path, or the headers of Codex's apply_patch
    if tool == "apply_patch":
        patch = inp if isinstance(inp, str) else str(inp.get("command") or inp.get("input") or "")
        paths = re.findall(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+?)\s*$", patch, re.M)
    elif tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        paths = [str(inp.get("file_path") or inp.get("notebook_path") or "")]
    if worktree_root and main_root:
        for path in paths:
            if not path:
                continue
            path = os.path.join(cwd, path)   # a relative patch path is the worktree's; an absolute one stays
            real, wt, main = (os.path.realpath(p) for p in (path, worktree_root, main_root))
            inside = lambda root: real == root or real.startswith(root + os.sep)
            plans = os.path.join(main, "documentation", "plans")   # out of git: it lives only in the main tree
            if inside(main) and not inside(wt) and not inside(plans):
                return deny(f"you work in the worktree {worktree_root}, but this edit targets {path} in the main "
                            "tree. Use the same path inside the worktree (executor-catalog → "
                            "references/worker-prompt.md → RULES).")
    return None


RULES = [("commit-chained", "chained to a test"), ("commit-on-main", "would land on"), ("merge-before-close", "is not closed (no tag"),
         ("plan-unit-trailer", "Plan-Unit"), ("sed-i", "sed -i"), ("progress-from-shell", "progress file from the shell"),
         ("wipe-shared-tree", "git stash (of everything)"), ("edit-outside-worktree", "you work in the worktree")]


def host_home() -> Path:
    """The host's own folder: $CODEX_HOME, ~/.codex for the Codex build (its manifest is .codex-plugin), else
    ~/.claude."""
    if os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"])
    codex = (Path(__file__).resolve().parent.parent / ".codex-plugin").is_dir()
    return Path.home() / (".codex" if codex else ".claude")


def log_refusal(project: str, tool: str, inp: dict, why: str) -> None:
    """One line per refusal outside the project, for reflect's «Отказы хука» (reflect/scripts/guard_report.py): how
    often each rule fires in real work, and the commands to judge whether a refusal was wrong."""
    store = host_home() / "dev-pipeline-feedback" / ".guard"
    store.mkdir(parents=True, exist_ok=True)
    rule = next((code for code, mark in RULES if mark in why), "other")
    what = inp if isinstance(inp, str) else str(inp.get("command") or inp.get("file_path") or inp.get("notebook_path") or "")
    row = {"ts": datetime.now().isoformat(timespec="seconds"), "rule": rule, "tool": tool, "what": what[:240]}
    with (store / f"{Path(project).resolve().name}.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def commit_dir(cmd: str, cwd: str) -> str:
    """The folder whose repository the commit lands in: `git -C <dir> commit`, else the last `cd <dir>` before the
    commit, else the session's cwd — a live refusal came from reading the branch of the session's folder while the
    command had changed into the project («cd <project> && … git commit» on the iteration branch)."""
    bare = heredocs(cmd)[0]
    at = COMMIT.search(bare)
    if not at:
        return cwd
    m = re.search(r"\bgit\s+-C\s+(['\"]?)([^'\"\s]+)\1\s+commit\b", bare)
    if m:
        return os.path.join(cwd, os.path.expanduser(m.group(2)))
    cds = re.findall(r"(?:^|[;&|(]\s*)cd\s+(['\"]?)([^'\"\s;&|]+)\1", bare[: at.start()])
    return os.path.join(cwd, os.path.expanduser(cds[-1][1])) if cds else cwd


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
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    # Codex runs a command in its own workdir; Claude Code names the project in CLAUDE_PROJECT_DIR
    cwd = (inp.get("workdir") if isinstance(inp, dict) else None) or data.get("cwd") or os.getcwd()
    top = git(cwd, "rev-parse", "--show-toplevel")
    is_worktree = bool(top) and git(cwd, "rev-parse", "--absolute-git-dir") != os.path.realpath(
        git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir") or "-")
    main_root = os.path.dirname(git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")) if is_worktree else None
    project = os.environ.get("CLAUDE_PROJECT_DIR") or main_root or top or cwd   # the stamp lives in the main tree
    if not os.path.isfile(os.path.join(project, "documentation", ".dev-pipeline.json")):
        return
    branch = ""
    if tool == "Bash" and re.search(r"\b(?:merge|fetch|update-ref|push|branch)\b", str(inp.get("command", ""))):
        cmd = str(inp.get("command", ""))
        target = commit_dir(cmd, cwd)
        if os.path.realpath(git(target, "rev-parse", "--show-toplevel") or "-") == \
                os.path.realpath(git(project, "rev-parse", "--show-toplevel") or "+"):
            it = open_iteration(project)
            tagged = bool(it) and bool(git(project, "rev-parse", "-q", "--verify", f"refs/tags/v{it}"))
            why = merge_issue(heredocs(cmd)[0], git(target, "rev-parse", "--abbrev-ref", "HEAD"), it, tagged)
            if why:
                try:
                    log_refusal(project, tool, inp, why)
                except Exception:
                    pass
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                         "permissionDecisionReason": why}}, ensure_ascii=False))
                return
    if tool == "Bash" and "commit" in str(inp):
        target = commit_dir(str(inp.get("command", "")), cwd)
        # the iteration rule is about this project's repository only, not another one the command commits to
        if os.path.realpath(git(target, "rev-parse", "--show-toplevel") or "-") == \
                os.path.realpath(git(project, "rev-parse", "--show-toplevel") or "+"):
            branch = git(target, "rev-parse", "--abbrev-ref", "HEAD")
    why = decide(tool, inp, cwd, branch=branch, open_iteration=open_iteration(project) if branch else None,
                 worktree_root=top if is_worktree else None, main_root=main_root)
    if why:
        try:
            log_refusal(project, tool, inp, why)
        except Exception:
            pass
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": why}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a guard must never break the tool call it watches
