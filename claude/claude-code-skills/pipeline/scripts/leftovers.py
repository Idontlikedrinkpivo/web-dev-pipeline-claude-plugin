"""What a stage left running: containers, volumes, worktrees and temporary test databases of the project.

    python3 leftovers.py [<project dir>]

Run before «ЭТАП … ЗАКРЫТ» (pipeline → references/handover-check.md → Before the close) and at a stop. It removes
nothing: the stage removes what it started — its lines in resume.md → «Запущено» — and runs this again. What
counts as left over:

  - a container or volume whose name or compose project starts with the project's name, other than the main stand
    (the compose project named exactly as the project, or `<project>-dev`, `-demo`, `-test`): stream databases
    (`<project>-s<k>-pg`), stand copies (`<project>-e2e-<n>`) and the like;
  - a git worktree other than the main one;
  - a database on a running postgres container of the project whose name ends in a uuid or a hex run id, or starts
    with `tmp_test_` — a test that died before its afterAll.

The last line is the report's line: «стенды удалены: …» when nothing is left, «осталось: …» otherwise (exit 1).
Docker not running is said, not guessed. Standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MAIN_SUFFIXES = ("", "-dev", "-demo", "-test")
TEMP_DB = re.compile(r"^tmp_test_|[_-][0-9a-f]{8}(?:[_-]?[0-9a-f]{4}){3}[_-]?[0-9a-f]{12}$|[_-][0-9a-f]{10,}$")


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return p.returncode, p.stdout


def project_name(root: Path) -> str:
    """The compose default: the folder's name, lower case, only [a-z0-9_-]."""
    return re.sub(r"[^a-z0-9_-]", "", root.name.lower())


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    name = project_name(root)
    left: list[str] = []
    notes: list[str] = []

    code, out = run(["docker", "ps", "-a", "--format",
                     '{{.Names}}\t{{.Status}}\t{{.Label "com.docker.compose.project"}}\t{{.Image}}'])
    pg: list[str] = []
    no_docker = bool(code)
    if code:
        notes.append("docker не отвечает — контейнеры, тома и базы не проверены")
    else:
        nameless = 0
        for row in filter(None, out.splitlines()):
            cname, status, proj, image = (row.split("\t") + ["", "", ""])[:4]
            if not cname and not proj:
                nameless += 1
                continue
            key = proj or cname
            if not key.startswith(name):
                continue
            main_stand = proj in {name + s for s in MAIN_SUFFIXES}
            if main_stand and status.startswith("Up") and "postgres" in image:
                pg.append(cname)
            if not main_stand:
                left.append(f"контейнер {cname} ({status.split(' (')[0]})")
        if nameless:
            notes.append(f"контейнеров без имени: {nameless} — чьи, не видно; удалить их может пользователь "
                         "(docker ps -a)")
        code, out = run(["docker", "volume", "ls", "--format",
                         '{{.Name}}\t{{.Label "com.docker.compose.project"}}'])
        for row in filter(None, out.splitlines()):
            vname, proj = (row.split("\t") + [""])[:2]
            main_vol = proj in {name + s for s in MAIN_SUFFIXES} if proj else \
                any(vname.startswith(f"{name}{s}_") for s in MAIN_SUFFIXES)
            if (proj or vname).startswith(name) and not main_vol:
                left.append(f"том {vname}")
        for c in pg:
            user = run(["docker", "exec", c, "printenv", "POSTGRES_USER"])[1].strip() or "postgres"
            code, dbs = run(["docker", "exec", c, "psql", "-U", user, "-Atc",
                             "select datname from pg_database where not datistemplate"])
            if code:
                notes.append(f"базы в {c} не прочитаны")
                continue
            temp = [d for d in dbs.split() if TEMP_DB.search(d)]
            if temp:
                left.append(f"временных баз в {c}: {len(temp)} ({', '.join(temp[:3])}{' …' if len(temp) > 3 else ''})")

    code, out = run(["git", "worktree", "list", "--porcelain"], cwd=root)
    trees = [ln[9:] for ln in out.splitlines() if ln.startswith("worktree ")]
    for t in trees[1:]:
        left.append(f"worktree {t}")

    for n in notes:
        print(f"⚠ {n}")
    for item in left:
        print(f"  · {item}")
    if left:
        print(f"осталось: {len(left)} — убрать своё (resume.md → «Запущено») и запустить снова")
        sys.exit(1)
    print("стенды удалены: контейнеров, томов, worktree и временных баз этапа не осталось"
          + (" (docker не проверен)" if no_docker else ""))


if __name__ == "__main__":
    main()
