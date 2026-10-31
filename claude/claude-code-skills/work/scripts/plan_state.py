"""Where a plan's execution stands, from git — what `work` reads before its first dispatch and after a compaction.

    python3 plan_state.py <documentation/plans/<version>/plan.md> [--base <branch>] [--range <BASE>]

Prints one line per fact:

    plan      the plan, its version, how many units it has
    where     the branch the done units are read from; a wrong branch or a linked worktree is named
    lint      plan/scripts/plan_lint.py over the plan: its mechanical errors stop the run like a failed gate
    review    the plan-review gate: plan-review.md says «Verdict: PASS» and its «checked:» line is the sha256 of
              plan.md as it is now — or why the gate does not pass (no review, another verdict, the plan changed)
    done      units with a «Plan-Unit: <version>/U<n>» trailer on the iteration branch (git log <base>..<branch>)
    todo      units without one, in plan order — the default scope of a run
    ready     todo units whose «Зависит от» are all done — what may be dispatched now
    waiting   todo units still waiting, with what they wait for
    other     the iteration's other trailers (review-fix-<n>, health-<n>, decision-<n>, verify-skill, stand,
              chat-<n>), so a run numbers its next one from here
    count     «<done> из <total>» — the numbers of the progress file's count line

With --range <BASE> (code-review-full, Step 1: BASE is the HEAD the last whole review covered), three more lines map
every commit of BASE..HEAD to its «Plan-Unit: <version>/<kind>» trailer, read from the message body:

    range     BASE..HEAD and how many commits it holds
    mapped    each kind found in the range (U<n>, review-fix-<n>, health-<n>, decision-<n>, verify-skill, stand,
              chat-<n>) with its commit count — the run report must list each
    units     the plan's units with a U<n> trailer in the range — compare with the units the run report marks
              committed: one missing here, or one here the report lacks, means the report is stale
    unmapped  one line per commit with no trailer of this version, or with a kind outside that list or a U<n> the
              plan lacks: short sha, subject, files touched — read its diff with the rest

Done is read from the whole iteration branch, not from the run's start: a second run in the same iteration (units
appended to the plan after the first run, a fix plan) sees the first run's units as done and dispatches only the
new ones. A unit with a trailer is never dispatched again.

Exit 0: the gate passes and the branch is the iteration's. Exit 2: something to do first (the lines say what).
Exit 1: the plan cannot be read. Standard library only.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

UNIT = re.compile(r"^###\s+U(\d+)\.", re.M)
KINDS = re.compile(r"U\d+|review-fix-\d+|health-\d+|decision-\d+|verify-skill|stand|chat-\d+")
DEPS = re.compile(r"^\|\s*\*\*(?:Зависит от|Depends on)\*\*\s*\|(.*)\|\s*$", re.M)
SHA = re.compile(r"\b[0-9a-f]{64}\b")


def git(cwd: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def has_ref(cwd: Path, ref: str) -> bool:
    return bool(git(cwd, "rev-parse", "--verify", "--quiet", ref + "^{commit}"))


def units_of(text: str) -> list:
    """[(n, [deps])] in plan order; a block runs from its «### U<n>.» heading to the next heading of level ≤ 3."""
    out = []
    marks = list(UNIT.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        nxt = re.search(r"^#{1,3}\s", text[m.end():end], re.M)
        block = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():end]
        d = DEPS.search(block)
        deps = sorted({int(x) for x in re.findall(r"\bU(\d+)\b", d.group(1))}) if d else []
        out.append((int(m.group(1)), deps))
    return out


def review_gate(plan: Path) -> tuple:
    """(ok, line) for plan-review.md beside the plan."""
    rv = plan.parent / "plan-review.md"
    if not rv.exists():
        return False, "review    none — plan-review.md is missing: run plan-review before the first dispatch"
    head = rv.read_text(encoding="utf-8", errors="replace").splitlines()[:6]
    verdict = ""
    if head and head[0].strip().lower().startswith("verdict:"):
        verdict = head[0].split(":", 1)[1].strip().split()[0].strip("`*·") if head[0].split(":", 1)[1].strip() else ""
    if verdict.upper() != "PASS":
        return False, f"review    {verdict or 'no verdict line'} — plan-review did not pass: run its rounds first"
    checked = next((SHA.search(l).group(0) for l in head if l.strip().lower().startswith("checked:") and SHA.search(l)), "")
    now = hashlib.sha256(plan.read_bytes()).hexdigest()
    if not checked:
        return False, ("review    PASS without a «checked:» line — the review predates the plan's hash: "
                       "run plan-review again over plan.md as it is now")
    if checked != now:
        return False, (f"review    STALE — plan.md changed after plan-review (checked {checked[:12]}, now {now[:12]}): "
                       "run plan-review again before any dispatch")
    return True, f"review    PASS · checked {now[:12]} = plan.md"


def range_lines(cwd: Path, version: str, base: str, plan_ids: list) -> list:
    """The --range lines: every commit of base..HEAD mapped to its trailer kind, or named as unmapped."""
    if not has_ref(cwd, base):
        return [f"range     {base} is not a commit here — pass the BASE the run report records"]
    log = git(cwd, "log", f"{base}..HEAD", "--format=%h%x1f%s%x1f%B%x1e")
    commits = [c.strip("\n").split("\x1f", 2) for c in log.split("\x1e") if c.strip()]
    kinds: dict = {}
    units = set()
    unmapped = []
    for sha, subject, body in commits:
        found = re.findall(rf"^Plan-Unit:\s*{re.escape(version)}/(\S+)\s*$", body, re.M)
        good = [k for k in found if KINDS.fullmatch(k) and not (k[0] == "U" and int(k[1:]) not in plan_ids)]
        for k in good:
            kind = "U<n>" if k.startswith("U") else re.sub(r"-\d+$", "-<n>", k)
            kinds[kind] = kinds.get(kind, 0) + 1
            if k.startswith("U"):
                units.add(int(k[1:]))
        if not good:
            files = git(cwd, "show", "--name-only", "--format=", sha).splitlines()
            why = f" · trailer {', '.join(found)} is not a kind of this run" if found else ""
            unmapped.append(f"unmapped  {sha} {subject} — {len(files)} files{why}")
    out = [f"range     {base}..HEAD · {len(commits)} commits",
           "mapped    " + (" · ".join(f"{k} ×{n}" for k, n in sorted(kinds.items())) or "—"),
           "units     " + (" ".join(f"U{n}" for n in plan_ids if n in units) or "—")]
    return out + (unmapped or ["unmapped  —"])


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 1
    plan = Path(os.path.abspath(args[0]))  # not resolved: a plans folder linked into a worktree stays the worktree's
    base = args[args.index("--base") + 1] if "--base" in args and args.index("--base") + 1 < len(args) else ""
    rbase = args[args.index("--range") + 1] if "--range" in args and args.index("--range") + 1 < len(args) else ""
    version = plan.parent.name
    cwd = plan.parent
    while cwd.is_symlink():  # git runs in the tree that holds the link, not in the tree it points to
        cwd = cwd.parent
    if not cwd.exists():
        cwd = Path.cwd()

    gitdir = git(cwd, "rev-parse", "--absolute-git-dir")
    common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")  # git ≥ 2.31
    if not common and gitdir:
        rel = git(cwd, "rev-parse", "--git-common-dir")
        common = str((cwd / rel).resolve()) if rel else gitdir
    linked = bool(gitdir and common and Path(gitdir).resolve() != Path(common).resolve())
    main_tree = ""
    if linked:
        wl = git(cwd, "worktree", "list", "--porcelain").splitlines()
        main_tree = wl[0][len("worktree "):] if wl and wl[0].startswith("worktree ") else str(Path(common).parent)

    if not plan.exists():
        print(f"plan      not found: {plan}")
        if linked:
            print(f"where     this session runs in a linked worktree ({Path.cwd()}); documentation/plans/ is out of "
                  f"git, so the plan lives only in the main working tree {main_tree} — open the session there")
        return 1

    text = plan.read_text(encoding="utf-8", errors="replace")
    units = units_of(text)
    if not units:
        print(f"plan      {plan} · version {version} · no «### U<n>.» unit found")
        return 1
    print(f"plan      {plan} · version {version} · units {len(units)}")

    problems = 0
    lint = Path(__file__).resolve().parents[2] / "plan" / "scripts" / "plan_lint.py"
    if lint.exists():
        r = subprocess.run([sys.executable, str(lint), str(plan)], capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        if r.returncode:
            problems += 1
            print(f"lint      {last} — fix the plan (plan_lint.py prints each line), then plan-review again")
        else:
            print(f"lint      {last}")
    branch = f"iteration/{version}"
    head = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    ref = branch if has_ref(cwd, branch) else "HEAD"
    if not base:
        base = next((b for b in ("main", "master", "origin/main", "origin/master") if has_ref(cwd, b)), "")
    rng = f"{base}..{ref}" if base and git(cwd, "rev-parse", base) != git(cwd, "rev-parse", ref) else ref
    where = f"where     done read from {rng}"
    if linked and head == branch:
        where += (" · a linked worktree with the plans folder linked in — finishing an older iteration "
                  "(work → references/run-hygiene.md); one stand per machine")
    elif linked:
        where += (f" · this session runs in a linked worktree on {head or '?'}, not {branch}; the iteration's files "
                  f"live in {main_tree} — stop and open the session there")
        problems += 1
    elif head != branch:
        where += f" · HEAD is on {head or '?'}, not {branch} — switch to it before the first dispatch"
        problems += 1
    print(where)

    ok, line = review_gate(plan)
    print(line)
    problems += 0 if ok else 1

    log = git(cwd, "log", rng, "--format=%B")
    trailers = re.findall(rf"^Plan-Unit:\s*{re.escape(version)}/(\S+)\s*$", log, re.M)
    done_ids = {int(t[1:]) for t in trailers if re.fullmatch(r"U\d+", t)}
    other = sorted({t for t in trailers if not re.fullmatch(r"U\d+", t)})
    plan_ids = [n for n, _ in units]
    done = [n for n in plan_ids if n in done_ids]
    todo = [n for n in plan_ids if n not in done_ids]
    deps = dict(units)
    ready = [n for n in todo if all(d in done_ids for d in deps[n])]
    waiting = [n for n in todo if n not in ready]
    unknown = sorted(done_ids - set(plan_ids))

    def ids(xs: list) -> str:
        return " ".join(f"U{n}" for n in xs) or "—"

    print(f"done      {len(done)} — {ids(done)}" + (f" · trailers of units not in the plan: {ids(unknown)}" if unknown else ""))
    print(f"todo      {len(todo)} — {ids(todo)}")
    print(f"ready     {ids(ready)}")
    print("waiting   " + ("; ".join(f"U{n} ← {ids([d for d in deps[n] if d not in done_ids])}" for n in waiting) or "—"))
    print(f"other     {' '.join(other) or '—'}")
    print(f"count     {len(done)} из {len(units)}")
    if rbase:
        print("\n".join(range_lines(cwd, version, rbase, plan_ids)))
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
