"""Send the iteration branch once a document is final — after its reviews and their fixes, never a draft.

    python3 push_branch.py [<project dir>]

Pushes the current branch to `origin` only when all of these hold, and says in one line what it did:
- the branch is an iteration branch, `iteration/<version>` — never `main`, never another branch;
- the project has a remote named `origin`.
What is not committed (a site rebuilt after the edit, files out of git) does not stop it: it is set aside while the
others' commits are taken (`--autostash`) and put back.

When `origin` already has the branch, it first takes the others' commits (`git pull --rebase`); a rebase that stops
on a conflict is undone (`git rebase --abort`) and the script stops with exit 2 — the session asks the user. A push
the remote refuses (no access, no network, a branch moved meanwhile) is exit 1 with the reason and the command to
run by hand; the stage goes on, it is not a stop. Exit 3: a contract document the push carries fails
doc-versioning/scripts/doc_check.py (its lines are printed) — nothing is pushed until it is fixed. Never `--force`,
never a tag. Exit 0: pushed, or nothing to push.
Standard library only.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def git(root: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def form_problems(root: str, upstream: str | None) -> str:
    """doc_check.py over the contract documents this push carries: a document with a broken form is not final."""
    base = upstream or next((b for b in ("origin/main", "main", "origin/master", "master")
                             if git(root, "rev-parse", "-q", "--verify", b)[0] == 0), None)
    if not base:
        return ""
    _, names = git(root, "diff", "--name-only", f"{base}...HEAD", "--", "documentation")
    docs = sorted({n for n in names.splitlines() if not n.startswith(("documentation/plans/", "documentation/_web-docs/"))})
    if not docs:
        return ""
    check = Path(__file__).resolve().parents[2] / "doc-versioning" / "scripts" / "doc_check.py"
    args = [sys.executable, str(check), root]
    for d in docs:
        args += ["--only", d]
    r = subprocess.run(args, capture_output=True, text=True)
    return "" if r.returncode == 0 else r.stdout.strip()


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    _, branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if not branch.startswith("iteration/"):
        print(f"push: не отправляю — ветка {branch or '?'}, а отправляется только iteration/<версия>")
        sys.exit(0)
    code, url = git(root, "remote", "get-url", "origin")
    if code:
        print("push: удалённого репозитория (origin) нет — отправлять некуда")
        sys.exit(0)
    manual = f"git pull --rebase origin {branch} && git push -u origin {branch}"
    fetched, out = git(root, "fetch", "origin", branch)
    if fetched == 0:
        code, out = git(root, "rebase", "--autostash", f"origin/{branch}")
        if code:
            git(root, "rebase", "--abort")
            clash = "\n".join(l for l in out.splitlines() if l.startswith("CONFLICT"))
            print(f"push: в origin/{branch} есть чужие коммиты, и они конфликтуют с этими — ничего не отправлено, "
                  f"ребейз отменён. Нужно решение пользователя.\n{clash}")
            sys.exit(2)
    ahead = git(root, "rev-list", "--count", f"origin/{branch}..HEAD")[1] if fetched == 0 else "?"
    if ahead == "0":
        print(f"push: origin/{branch} уже содержит всё — отправлять нечего")
        sys.exit(0)
    bad = form_problems(root, f"origin/{branch}" if fetched == 0 else None)
    if bad:
        print("push: не отправлено — у отправляемых документов ошибки формы (doc_check.py); исправьте, закоммитьте "
              "и отправьте снова:\n" + bad)
        sys.exit(3)
    code, out = git(root, "push", "-u", "origin", branch)
    if code:
        print(f"push: не отправлено — {out.splitlines()[-1] if out else 'ошибка'}. Вручную: {manual}")
        sys.exit(1)
    _, sha = git(root, "rev-parse", "--short", "HEAD")
    print(f"push: отправлено — {sha} в origin/{branch}")


if __name__ == "__main__":
    main()
