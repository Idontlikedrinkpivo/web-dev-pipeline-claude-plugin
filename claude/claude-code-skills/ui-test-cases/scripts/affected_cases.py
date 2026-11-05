#!/usr/bin/env python3
"""Which user test cases an acceptance run takes in pass 1: the cases the iteration touched, from git and the files.

usage: python3 affected_cases.py <project dir> [--since <tag or ref>] [--plan <plan.md>] [--failed <test-run.md>]
                                 [--touch S-1,cancelBooking] [--rest <test-run.md>]

Prints one line per case in scope, `TC-<n><TAB><reason>[; <reason>…]`, then `затронуто: …` (the touched surface,
for the chat line) and last `всего: N из M`. A case is in scope when its «Экран» line or «Трассировка» names a
screen `S-n` (directly, by a frame nodeId of that screen, or by a modal `M-n` of it) or an operationId touched since
`--since`, when the case itself is new or changed since then, or when it failed (❌, ⛔) in the last run of `--failed`.
Touched: screen specs and frames-register rows changed in `git diff <since>..HEAD -- documentation`; operations whose
block or `operationId:` line the diff of `documentation/api` changes; SRS headings and lines naming UC-/BR-/FR- ids
(matched to the cases' «Проверяет» line); `--plan`: S-ids, screen-spec paths and operationIds in each unit's
«Документы», «Файлы» and «Цель»; `--touch`: screens and operations named by hand (a small iteration's unit).
`--rest <test-run.md>`: instead, the cases outside that report's last run — the close's full set.
`--since` defaults to the newest `v*` tag reachable from HEAD that is not the current version (the branch
`iteration/<v>`); none → every case, reason «первая итерация». Exit 0 always; 1 — no test-cases folder.
Standard library only, Python 3.9+.
"""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_trace import CASE, TRACE, NODE, OP  # noqa: E402  the same parsing as the trace check

SID = re.compile(r"\bS-\d+\b")
MID = re.compile(r"\bM\d+\b")
REQ = re.compile(r"\b(?:UC|BR|FR|NFR)-\d+\b")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
METHOD = re.compile(r"^(\s*)(get|post|put|patch|delete|head|options):\s*$")
OPID = re.compile(r"""^\s*operationId:\s*['"]?([^'"\s#]+)""")
STATUS_COL = re.compile(r"\|\s*Статус\s*\|")


def git(root: Path, *args: str) -> str | None:
    r = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=false", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def cases_of(texts: dict[str, str]) -> dict[str, tuple[str, str]]:
    """TC id -> (the case's whole text, its head above the trace)."""
    out = {}
    for text in texts.values():
        heads = list(CASE.finditer(text))
        for i, h in enumerate(heads):
            body = text[h.start(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            t = TRACE.search(body)
            out[h.group(1)] = (body.strip(), body[: t.start()] if t else body)
    return out


def case_files(root: Path, ref: str | None) -> dict[str, str]:
    pat = re.compile(r"^documentation/ui/(?:.+/)?test-cases(?:/[^/]+)?\.md$")
    if ref is None:
        files = [p for p in root.glob("documentation/ui/**/test-cases/*.md")] + list(root.glob("documentation/ui/**/test-cases.md"))
        return {str(p.relative_to(root)): p.read_text(errors="replace") for p in files}
    names = (git(root, "ls-tree", "-r", "--name-only", ref, "--", "documentation/ui") or "").splitlines()
    return {n: git(root, "show", f"{ref}:{n}") or "" for n in names if pat.search(n)}


def changed(root: Path, since: str, path: str) -> list[tuple[int, str]]:
    """(new-side line number, text) of every added or removed line of the diff since `since`."""
    out, line = [], 0
    for d in (git(root, "diff", "-U0", f"{since}..HEAD", "--", path) or "").splitlines():
        m = HUNK.match(d)
        if m:
            line = int(m.group(1))
        elif d[:1] in "+-" and not d.startswith(("+++", "---")):
            out.append((line, d[1:]))
            line += d[0] == "+"
    return out


def touched_ops(root: Path, since: str) -> set[str]:
    ops = set()
    for f in (git(root, "diff", "--name-only", f"{since}..HEAD", "--", "documentation/api") or "").splitlines():
        lines = (root / f).read_text(errors="replace").splitlines() if (root / f).exists() else []
        blocks, cur = [], None  # (start, end, operationId) per method block
        for i, ln in enumerate(lines, 1):
            m = METHOD.match(ln)
            if m or (cur and ln.strip() and len(ln) - len(ln.lstrip()) <= cur[0]):
                cur = (len(m.group(1)), i, []) if m else None
                if cur:
                    blocks.append(cur)
            if cur and OPID.match(ln):
                cur[2].append(OPID.match(ln).group(1))
        for n, text in changed(root, since, f):
            if OPID.match(text):
                ops.add(OPID.match(text).group(1))
            for j, b in enumerate(blocks):
                end = blocks[j + 1][1] if j + 1 < len(blocks) else len(lines) + 1
                if b[1] <= n < end:
                    ops.update(b[2])
    return ops


def last_run(report: Path) -> dict[str, str]:
    """TC -> its latest status from the report's last «## Прогон <n>» heading to the end."""
    text = report.read_text(errors="replace") if report.exists() else ""
    starts = [m.start() for m in re.finditer(r"^## Прогон \d+ —", text, re.M)]
    status, col = {}, None
    for ln in text[starts[-1]:].splitlines() if starts else []:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if STATUS_COL.search(ln):
            col = cells.index("Статус")
        elif col is not None and cells and re.fullmatch(r"TC-\d+", cells[0]) and len(cells) > col:
            status[cells[0]] = cells[col]
    return status


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    for o in ("--since", "--plan", "--failed", "--touch", "--rest"):
        ap.add_argument(o)
    a = ap.parse_args()
    root = Path(a.project).resolve()
    now = case_files(root, None)
    if not now:
        print("affected-cases: нет папки documentation/ui/test-cases/ — прогонять нечего"); sys.exit(1)
    cases = cases_of(now)
    order = sorted(cases, key=lambda c: int(c[3:]))
    reasons: dict[str, list[str]] = {c: [] for c in order}
    surface: list[str] = []

    def out() -> None:
        hit = [c for c in order if reasons[c]]
        for c in hit:
            print(f"{c}\t{'; '.join(dict.fromkeys(reasons[c]))}")
        if surface:
            print("затронуто: " + " · ".join(dict.fromkeys(surface)))
        print(f"всего: {len(hit)} из {len(order)}")
        sys.exit(0)

    if a.rest:
        ran = last_run(Path(a.rest))
        for c in order:
            if c not in ran:
                reasons[c].append("не входил в последний прогон")
        out()
    since = a.since
    if since is None:
        branch = (git(root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
        current = "v" + branch.split("/", 1)[1] if branch.startswith("iteration/") else None
        tags = (git(root, "tag", "--merged", "HEAD", "--list", "v*", "--sort=-v:refname") or "").split()
        since = next((t for t in tags if t != current), None)
    if since is None or git(root, "rev-parse", "--verify", "-q", since + "^{commit}") is None:
        why = "первая итерация" if since is None else f"метки {since} нет — весь набор"
        for c in order:
            reasons[c].append(why)
        out()

    register = "\n".join(p.read_text(errors="replace") for p in root.glob("documentation/ui/**/frames-register.md"))
    node_screen, modal_screen = {}, {}
    for row in re.findall(r"^\|\s*(S-\d+)\s*\|(.*)$", register, re.M):
        for n in NODE.findall(row[1]):
            node_screen.setdefault(n, set()).add(row[0])
        for m in MID.findall(row[1]):
            modal_screen.setdefault(m, set()).add(row[0])
    for p in root.glob("documentation/ui/**/screen-specs/S-*.md"):
        fm = re.search(r"^figma:.*?/\s*(\S+)", p.read_text(errors="replace"), re.M)
        if fm:
            node_screen.setdefault(fm.group(1), set()).add(SID.match(p.name).group(0))

    screens: dict[str, str] = {}  # S-n -> why
    ops: dict[str, str] = {}
    reqs: dict[str, str] = {}
    for f in (git(root, "diff", "--name-only", f"{since}..HEAD", "--", "documentation") or "").splitlines():
        name = Path(f).name
        if "/screen-specs/" in f and SID.match(name):
            screens.setdefault(SID.match(name).group(0), "ТЗ изменено")
        elif name == "frames-register.md":
            for _, text in changed(root, since, f):
                m = re.match(r"\|\s*(S-\d+)\s*\|", text)
                if m:
                    screens.setdefault(m.group(1), "реестр кадров изменён")
        elif "/requirements/srs/" in f and (root / f).exists():
            lines = (root / f).read_text(errors="replace").splitlines()
            for n, text in changed(root, since, f):
                head = next((lines[i] for i in range(min(n, len(lines)) - 1, -1, -1) if lines[i].startswith("#")), "")
                for r in REQ.findall(text + " " + head):
                    reqs.setdefault(r, "требование изменено")
    for o in touched_ops(root, since):
        ops.setdefault(o, "OpenAPI изменён")
    known_ops = {o for c in cases.values() for o, _ in OP.findall(c[0])}
    if a.plan and Path(a.plan).exists():
        units = re.split(r"^###\s+(?=U\d+\.)", Path(a.plan).read_text(errors="replace"), flags=re.M)[1:]
        for u in units:
            uid = u.split(".", 1)[0]
            part = "\n".join(re.findall(r"^\|\s*\*\*(?:Документы|Файлы)\*\*\s*\|.*$|^\*\*Цель\*\*.*$", u, re.M))
            for s in SID.findall(part):
                screens.setdefault(s, f"в плане: {uid}")
            for o in known_ops & set(re.findall(r"`([A-Za-z_]\w*)`", part)):
                ops.setdefault(o, f"в плане: {uid}")
    for t in (a.touch or "").split(","):
        t = t.strip()
        if t:
            (screens if SID.fullmatch(t) else ops)[t] = "названо вручную"
    failed = {c for c, s in last_run(Path(a.failed)).items() if "❌" in s or "⛔" in s} if a.failed else set()

    old = cases_of(case_files(root, since))
    for c in order:
        text, head = cases[c]
        trace = text[len(head):]
        own = set(SID.findall(head.split("|", 1)[0]))  # named screens win: a shared modal (M2) is not every owner's
        if not own:
            own = {s for m in MID.findall(head.split("|", 1)[0] + trace) for s in modal_screen.get(m, ())}
            own |= {s for n in NODE.findall(trace) for s in node_screen.get(n, ())}
        if c not in old:
            reasons[c].append("новый кейс")
        elif old[c][0] != text:
            reasons[c].append("кейс изменён")
        for s in sorted(own & screens.keys()):
            reasons[c].append(f"экран {s} ({screens[s]})")
        for o, _ in OP.findall(trace):
            if o in ops:
                reasons[c].append(f"операция {o} ({ops[o]})")
        checks = re.search(r"Проверяет:\**(.*)", head)
        for r in sorted(set(REQ.findall(checks.group(1) if checks else "")) & reqs.keys()):
            reasons[c].append(f"{r} ({reqs[r]})")
        if c in failed:
            reasons[c].append("упал в прошлом прогоне")
    surface += [f"экран {s}" for s in sorted(screens)] + [f"операция {o}" for o in sorted(ops)]
    surface += [f"{r} изменено" for r in sorted(reqs)] + ([f"упали в прошлый раз: {len(failed)}"] if failed else [])
    out()


if __name__ == "__main__":
    main()
