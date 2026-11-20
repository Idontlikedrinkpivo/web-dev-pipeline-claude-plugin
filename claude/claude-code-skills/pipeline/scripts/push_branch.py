"""Send the iteration branch once a document is final — after its reviews and their fixes, never a draft.

    python3 push_branch.py [<project dir>]

Pushes the current branch to `origin` only when all of these hold, and says in one line what it did:
- the branch is an iteration branch, `iteration/<version>` — never `main`, never another branch;
- the project has a remote named `origin`.
It sends only what is committed and commits nothing itself: in 2.3.0 it committed 336 files of documentation/plans
on its own — older versions' reports, archive/, docx, json — and pushed them (the user: send only what is committed,
stop on a dirty tree and show the list). So anything not committed under documentation/ stops it, exit 4, nothing
sent: it lists the files and prints the command that commits this iteration's own reports — the `.md` files of
documentation/plans/<version>/, «chore: отчёты итерации <version>», by their paths (pipeline →
references/service-version.md → The iteration's files in git) — for the session to run; the rest it names for
whoever owns them. Changes outside documentation/ (another session's code in the same checkout) do not stop it and
are never stashed: the rebase is then skipped (it would need `--autostash`, which would move another session's files)
and the push is tried as it is; a clean tree is rebased without `--autostash`.

When `origin` already has the branch, it first takes the others' commits (`git pull --rebase`); a rebase that stops
on a conflict is undone (`git rebase --abort`) and the script stops with exit 2 — the session asks the user. A conflict
only in the generated site documentation/_web-docs/ is not the user's: the upstream version of those files is taken, the
rebase goes on, the site is rebuilt once (docs-site/scripts/rebuild.py) and committed alone; other conflicts are the
user's. A push
the remote refuses (no access, no network, a branch moved meanwhile) is exit 1 with the reason and the command to
run by hand; the stage goes on, it is not a stop. Exit 3: a contract document the push carries fails
doc-versioning/scripts/doc_check.py (its lines are printed) — nothing is pushed until it is fixed. Never `--force`,
never a tag. Exit 4: something under documentation/ not committed (above). Exit 0: pushed and confirmed, or nothing
to push.
A push counts as sent only when `git ls-remote origin refs/heads/<branch>` afterwards returns the sha of HEAD (exit 1
with the command to check otherwise, also when git printed «Everything up-to-date» although commits were ahead):
a push's own output proves nothing — the 2.2.1 run took «Everything up-to-date» for success and the commit was not there.
Standard library only.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


SITE = "documentation/_web-docs"


def git(root: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                       env={**os.environ, "GIT_EDITOR": "true"})
    return p.returncode, (p.stdout + p.stderr).strip()


def rebase_onto(root: str, upstream: str) -> tuple[int, str, bool]:
    """Rebase; a stop with conflicts only under the generated site takes the upstream side and goes on.

    Returns (code, output, site_resolved). During a rebase «ours» is the upstream being replayed onto."""
    code, out = git(root, "rebase", upstream)
    resolved = False
    while code:
        paths = git(root, "diff", "--name-only", "--diff-filter=U")[1].splitlines()
        if not paths or not all(x.startswith(SITE + "/") for x in paths):
            return code, out, resolved
        for x in paths:
            if git(root, "checkout", "--ours", "--", x)[0]:
                git(root, "rm", "-q", "--", x)  # the upstream deleted the page
        git(root, "add", "-A", "--", SITE)
        resolved = True
        code, out = git(root, "rebase", "--continue")
        if code and not git(root, "diff", "--name-only", "--diff-filter=U")[1]:
            code, out = git(root, "rebase", "--skip")  # the commit held only the site and is now empty
    return 0, out, resolved


def rebuild_site(root: str) -> None:
    """After a site conflict: one rebuild of the site and a commit of it alone; a failure is said, the push goes on."""
    script = Path(__file__).resolve().parents[2] / "docs-site" / "scripts" / "rebuild.py"
    note = "push: конфликт только в сайте документации — взят вариант с сервера, сайт пересобран"
    if not script.exists():
        print(note.replace("сайт пересобран", "сайт НЕ пересобран: rebuild.py не найден; пересоберётся при следующем документе"))
        return
    ok = True
    for extra in ([], ["--wait"]):
        r = subprocess.run([sys.executable, str(script), root, *extra], capture_output=True, text=True)
        ok = ok and r.returncode == 0
    if not ok:
        print(note.replace("сайт пересобран", "сайт НЕ пересобран: rebuild.py завершился с ошибкой; пересоберётся при "
                           "следующем документе"))
    else:
        print(note)
    if git(root, "status", "--porcelain", "--", SITE)[1]:
        git(root, "add", "-A", "--", SITE)
        git(root, "commit", "-q", "-m", "docs: сайт документации (после слияния)", "--", SITE)


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


def uncommitted_docs(root: str, branch: str) -> None:
    """Stop, exit 4, when anything under documentation/ is not committed: list it, and print the command for this
    iteration's own reports — the session runs it, this script commits nothing."""
    rows = [l for l in git(root, "status", "--porcelain", "--untracked-files=all", "--", "documentation")[1].splitlines()
            if l.strip()]
    if not rows:
        return
    version = branch.split("/", 1)[1]
    paths = [l.split(maxsplit=1)[1].split(" -> ")[-1].strip('"') for l in rows]   # git() strips the first space
    mine = [p for p in paths if p.startswith(f"documentation/plans/{version}/") and p.endswith(".md")]
    other = [p for p in paths if p not in mine]
    print(f"push: не отправлено — в documentation/ не закоммичено {len(paths)} файл(ов); отправляется только "
          "закоммиченное.")
    if mine:
        q = " ".join(f"'{p}'" for p in mine)
        print(f"Отчёты итерации {version} ({len(mine)}) — закоммитьте их и запустите снова:\n"
              f"  git add -- {q} && git commit -q -m \"chore: отчёты итерации {version}\" -- {q}")
    if other:
        print("Не отчёты этой итерации — коммитит тот, чьи они (документ — его этап; чужое — пользователь):")
        for p in other[:40]:
            print(f"  · {p}")
        if len(other) > 40:
            print(f"  … и ещё {len(other) - 40}")
    sys.exit(4)


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    _, branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if not branch.startswith("iteration/"):
        print(f"push: не отправляю — ветка {branch or '?'}, а отправляется только iteration/<версия>")
        sys.exit(0)
    uncommitted_docs(root, branch)
    code, url = git(root, "remote", "get-url", "origin")
    if code:
        print("push: удалённого репозитория (origin) нет — отправлять некуда")
        sys.exit(0)
    manual = f"git pull --rebase origin {branch} && git push -u origin {branch}"
    fetched, out = git(root, "fetch", "origin", branch)
    # Changes outside documentation/ may be another session's work in this checkout: never stash them, skip the rebase.
    dirty = [l for l in git(root, "status", "--porcelain")[1].splitlines() if l.strip()]
    if fetched == 0 and dirty:
        print("push: в дереве незакоммиченные правки вне documentation/ — ребейз пропущен, пробую отправить как есть")
    if fetched == 0 and not dirty:
        code, out, site_fixed = rebase_onto(root, f"origin/{branch}")
        if code:
            git(root, "rebase", "--abort")
            clash = "\n".join(l for l in out.splitlines() if l.startswith("CONFLICT"))
            print(f"push: в origin/{branch} есть чужие коммиты, и они конфликтуют с этими — ничего не отправлено, "
                  f"ребейз отменён. Нужно решение пользователя.\n{clash}")
            sys.exit(2)
        if site_fixed:
            rebuild_site(root)
    ahead = git(root, "rev-list", "--count", f"origin/{branch}..HEAD")[1] if fetched == 0 else "?"
    if ahead == "0" and dirty and git(root, "rev-parse", "HEAD")[1] != git(root, "rev-parse", f"origin/{branch}")[1]:
        ahead = "?"  # not rebased and behind origin: let the push be refused, with the manual command
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
    _, head = git(root, "rev-parse", "HEAD")
    _, sha = git(root, "rev-parse", "--short", "HEAD")
    lc, ls = git(root, "ls-remote", "origin", f"refs/heads/{branch}")
    remote = ls.split()[0] if lc == 0 and ls.split() else ""
    if "Everything up-to-date" in out or remote != head:
        got = remote or "нет ответа"
        print(f"push: НЕ ПОДТВЕРЖДЕНО — origin/{branch} = {got}, HEAD = {head}; проверьте: "
              f"git ls-remote origin refs/heads/{branch}")
        sys.exit(1)
    print(f"push: отправлено — {sha} в origin/{branch}, подтверждено ls-remote")


if __name__ == "__main__":
    main()
