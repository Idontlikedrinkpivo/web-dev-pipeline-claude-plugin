"""Open (or re-enter) an iteration: the branch, the plans folder, .gitignore — every stage that opens one runs this.

    python3 open_iteration.py <version> [<project dir>]
        [--init]                # not a git repository yet: create one (git init, branch main) — the user said yes
        [--allow-unmerged]      # the user chose to start from main although an earlier iteration is not merged
        [--base <branch>]       # the user chose to start from that branch (an earlier iteration not merged yet)
        [--allow-open]          # the user wants a second open iteration beside the one already open

What it does, in order (pipeline → references/service-version.md):
1. With a remote: fetch it and fast-forward the local main branch (main, else master) from it.
2. The branch iteration/<version> exists here or on the remote: switch to it (a teammate's iteration is tracked).
   Otherwise: an earlier iteration/* branch whose content is not in main stops the run with exit 2 — the new
   iteration would start without it; ask the user, then rerun with --allow-unmerged or --base. Then create the
   branch from main (the working tree's uncommitted changes come along) and switch to it.
3. Creates documentation/plans/<version>/; puts documentation/plans/ into .gitignore (untracking it when it was
   tracked) and commits that alone on the iteration branch when nothing else is staged.
4. Prints what the opening stage says next: who runs the design (products with screens, asked once —
   pipeline → references/design-owner.md) and the plugin's code changes still pending (upgrade-code).

Exit codes: 0 done; 1 error (message says why); 2 a decision for the user (message names the options, nothing
changed); 3 not a git repository (rerun with --init after the user's yes). Python 3.9+, standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANS_RX = re.compile(r"^/?documentation/plans/?(\*\*?)?\s*$")
SCREEN_RX = re.compile(r"экран|интерфейс|страниц|макет|веб-приложен|мобильн|\bUI\b|frontend|фронт", re.I)


def git(root: Path, *args: str, check: bool = False, timeout: int = 120) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        fail(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()}")
    return r


def out(root: Path, *args: str) -> str:
    return git(root, *args).stdout.strip()


def fail(msg: str, code: int = 1) -> None:
    print(f"open_iteration: {msg}")
    sys.exit(code)


def has_ref(root: Path, ref: str) -> bool:
    return git(root, "rev-parse", "-q", "--verify", ref + "^{commit}").returncode == 0


def vkey(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def main_branch(root: Path, remote: bool) -> str | None:
    for b in ("main", "master"):
        if has_ref(root, f"refs/heads/{b}"):
            return b
    if remote:
        head = out(root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
        if head.startswith("origin/"):
            return head[len("origin/"):]
        for b in ("main", "master"):
            if has_ref(root, f"refs/remotes/origin/{b}"):
                return b
    return None


def merged(root: Path, ref: str, into: str) -> bool:
    """True when ref's content is in `into`: an ancestor, or merging it would change nothing (a squash merge)."""
    if git(root, "merge-base", "--is-ancestor", ref, into).returncode == 0:
        return True
    r = git(root, "merge-tree", "--write-tree", into, ref)
    if r.returncode != 0:
        return False  # a conflict, or a git without --write-tree: not provably merged
    return r.stdout.split()[0] == out(root, "rev-parse", f"{into}^{{tree}}")


def gitignore(root: Path) -> bool:
    """documentation/plans/ in .gitignore; True when the file changed."""
    p = root / ".gitignore"
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if any(PLANS_RX.match(l.strip()) for l in text.splitlines()):
        return False
    p.write_text(text + ("" if not text or text.endswith("\n") else "\n") + "documentation/plans/\n", encoding="utf-8")
    return True


def commit_gitignore(root: Path, changed: bool, notes: list) -> None:
    tracked = bool(out(root, "ls-files", "documentation/plans"))
    if not changed and not tracked:
        return
    if git(root, "rev-parse", "-q", "--verify", "HEAD").returncode == 0 and \
            git(root, "diff", "--cached", "--quiet").returncode != 0:
        notes.append("other changes are staged, so .gitignore was left uncommitted: commit it on its own "
                     "(«chore: documentation/plans/ вне git») before the stage's commit")
        if tracked:
            notes.append("documentation/plans/ is still tracked: `git rm -r --cached documentation/plans` in that commit")
        return
    if tracked:
        git(root, "rm", "-r", "--cached", "-q", "documentation/plans", check=True)
    git(root, "add", ".gitignore", check=True)
    git(root, "commit", "-q", "-m", "chore: documentation/plans/ вне git", check=True)
    notes.append("committed .gitignore: documentation/plans/ is out of git" + (" (untracked, files kept)" if tracked else ""))


def design_line(root: Path) -> str:
    doc = root / "documentation"
    regs = sorted(doc.glob("ui/frames-register.md")) + sorted(doc.glob("ui/*/frames-register.md"))
    for reg in regs:
        m = re.search(r"Дизайн ведёт:?\**:?\s*([^\n|]+)", reg.read_text(encoding="utf-8", errors="replace"))
        if m and m.group(1).strip(" *`"):
            return (f"Design: «{m.group(1).strip(' *`')}» per {reg.relative_to(root)} — say it in one line, no "
                    "question (pipeline → references/design-owner.md).")
    if regs:
        return ("Design: the product has screens and the frames register names no owner — ask once who runs the "
                "design (pipeline → references/design-owner.md).")
    srcs = [doc / "requirements/business-requirements/business-requirements.md", doc / "requirements/srs/srs.md"]
    srcs += sorted((doc / "requirements/srs/areas").glob("*.md")) if (doc / "requirements/srs/areas").is_dir() else []
    if any(p.is_file() and SCREEN_RX.search(p.read_text(encoding="utf-8", errors="replace")) for p in srcs):
        return ("Design: the documents speak of screens — ask once who runs the design, right after the version "
                "(pipeline → references/design-owner.md).")
    return ("Design: no sign of screens in the documents yet — if the request has them, ask who runs the design now; "
            "otherwise at the fork after the SRS (pipeline → references/design-owner.md).")


def code_changes(root: Path) -> str | None:
    fmt = HERE.parent.parent / "upgrade-docs" / "scripts"
    if not (root / "documentation").is_dir() or not (fmt / "project_format.py").is_file():
        return None
    try:
        sys.path.insert(0, str(fmt))
        import project_format
        todo = project_format.pending(root, "code")
    except Exception:
        return None
    if not todo:
        return None
    return ("Plugin code changes still pending (upgrade-code): " + "; ".join(f"{c['id']} «{c['title']}»" for c in todo)
            + " — offer /dev-pipeline:upgrade-code, or `plan` makes them this iteration's first unit.")


def main() -> None:
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    base_arg = args[args.index("--base") + 1] if "--base" in args else None
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--base")]
    if not pos or not re.fullmatch(r"\d+\.\d+\.\d+", pos[0]):
        sys.exit(__doc__)
    version = pos[0]
    root = Path(pos[1] if len(pos) > 1 else ".").resolve()
    branch = f"iteration/{version}"
    notes: list = []

    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        if "--init" not in flags:
            fail(f"{root} is not a git repository. The pipeline commits every stage on an iteration branch: ask the "
                 "user, then rerun with --init (git init, branch main).", 3)
        if git(root, "init", "-q", "-b", "main").returncode != 0:
            git(root, "init", "-q", check=True)
            git(root, "symbolic-ref", "HEAD", "refs/heads/main", check=True)
        notes.append("created a git repository (branch main)")
        top = git(root, "rev-parse", "--show-toplevel")
    if not (root / "documentation").is_dir():  # a system in a subfolder keeps its own documentation/ there
        root = Path(top.stdout.strip())

    plans = root / "documentation" / "plans"
    folder = plans / version
    if (folder / "summary.md").exists():
        fail(f"iteration {version} is closed (documentation/plans/{version}/summary.md): the next iteration takes the "
             "next number (pipeline → references/service-version.md).")
    others = sorted((p.name for p in plans.iterdir() if p.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", p.name)
                     and p.name != version and not (p / "summary.md").exists()), key=vkey) if plans.is_dir() else []
    if others and "--allow-open" not in flags:
        fail(f"iteration {', '.join(others)} is open (no summary.md): it is the current iteration — reuse it. "
             f"Open {version} beside it only on the user's yes: rerun with --allow-open.", 2)

    has_origin = "origin" in out(root, "remote").split()
    remote = has_origin
    if remote:
        r = git(root, "fetch", "-q", "--prune", "origin", timeout=90)
        if r.returncode != 0:
            why = ((r.stderr or r.stdout).strip().splitlines() or ["?"])[-1]
            notes.append(f"fetch from origin failed ({why}): main is as it is on this machine")
            remote = False
    unborn = git(root, "rev-parse", "-q", "--verify", "HEAD").returncode != 0
    current = out(root, "symbolic-ref", "-q", "--short", "HEAD")
    main_ref = main_branch(root, remote) or (current if unborn else None)

    if current == branch:
        notes.append(f"already on {branch}")
    elif has_ref(root, f"refs/heads/{branch}"):
        git(root, "switch", "-q", branch, check=True)
        notes.append(f"switched to the existing branch {branch}")
    elif remote and has_ref(root, f"refs/remotes/origin/{branch}"):
        git(root, "switch", "-q", "-c", branch, "--track", f"origin/{branch}", check=True)
        notes.append(f"switched to {branch} from origin (someone else opened it)")
    else:
        if unborn:
            # no commit yet: main gets its first commit (.gitignore), so the iteration has something to branch from
            gitignore(root)
            git(root, "add", ".gitignore", check=True)
            git(root, "commit", "-q", "-m", "chore: начало репозитория", "--", ".gitignore", check=True)
            main_ref = out(root, "symbolic-ref", "-q", "--short", "HEAD")
            notes.append(f"first commit on {main_ref}: .gitignore with documentation/plans/")
        elif remote and main_ref and has_ref(root, f"refs/remotes/origin/{main_ref}"):
            if current == main_ref:
                r = git(root, "merge", "-q", "--ff-only", f"origin/{main_ref}")
            else:
                r = git(root, "fetch", "-q", ".", f"refs/remotes/origin/{main_ref}:refs/heads/{main_ref}")
            if r.returncode == 0:
                notes.append(f"{main_ref} updated from origin")
            else:
                notes.append(f"{main_ref} not fast-forwarded from origin (diverged or blocked): "
                             f"{(r.stderr or r.stdout).strip().splitlines()[-1:]}")
        if not main_ref and not base_arg:
            fail("no main branch (main or master) to start from — a question for the user: which branch the iteration "
                 "starts from; rerun with --base <branch>. The branch was not created.", 2)
        if not base_arg and not unborn:
            refs = [r for r in out(root, "for-each-ref", "--format=%(refname:short)", "refs/heads/iteration/",
                                   "refs/remotes/origin/iteration/").split() if r not in (branch, f"origin/{branch}")]
            unmerged = []
            for ref in refs:
                into = f"origin/{main_ref}" if ref.startswith("origin/") and has_ref(
                    root, f"refs/remotes/origin/{main_ref}") else main_ref
                name = ref[len("origin/"):] if ref.startswith("origin/") and ref[len("origin/"):] in refs else ref
                if name not in unmerged and not merged(root, ref, into):
                    unmerged.append(name)
            if unmerged and "--allow-unmerged" not in flags:
                names = ", ".join(unmerged)
                fail(f"not merged into {main_ref}: {names}. A new iteration from {main_ref} would start without that "
                     f"work. Ask the user (one question): A. merge it first (on GitHub), then rerun; B. start from "
                     f"{main_ref} anyway — rerun with --allow-unmerged; C. start on top of it — rerun with "
                     f"--base {unmerged[-1]}. The branch was not created.", 2)
            if unmerged:
                notes.append(f"started from {main_ref} although {', '.join(unmerged)} is not merged (the user's choice)")
        start = base_arg or main_ref
        if not has_ref(root, start):
            fail(f"no branch {start} to start from")
        r = git(root, "switch", "-q", "-c", branch, start)
        if r.returncode != 0:
            fail(f"could not create {branch} from {start}: {(r.stderr or r.stdout).strip()} — the working tree has "
                 "changes that conflict with it; ask the user how to handle them (never stash on your own).")
        notes.append(f"created {branch} from {start} and switched to it")

    folder.mkdir(parents=True, exist_ok=True)
    commit_gitignore(root, gitignore(root), notes)

    print(f"Iteration {version}: branch {branch}, folder documentation/plans/{version}/"
          + (" (another open iteration: " + ", ".join(others) + ")" if others else ""))
    for n in notes:
        print(f"- {n}")
    print(design_line(root))
    line = code_changes(root)
    if line:
        print(line)
    if not has_origin:
        print("No remote (origin): everything stays local; the push command at the end needs one.")


if __name__ == "__main__":
    main()
