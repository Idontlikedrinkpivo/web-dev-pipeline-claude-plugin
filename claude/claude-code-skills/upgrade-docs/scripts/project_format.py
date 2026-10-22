"""Which of the plugin's format changes a project still lacks, and the project's stamp of the plugin version.

    python3 project_format.py hook  <project dir>        # the session-start line; prints nothing when the project is in line
    python3 project_format.py list  <project dir>        # every pending change in full (--json for a machine)
    python3 project_format.py check <project dir> <id>   # exit 0 when this change is no longer pending
    python3 project_format.py skip  <project dir> <id>   # the user declined it for good: never offered again
    python3 project_format.py stamp <project dir>        # record the installed version — only when nothing is pending
    python3 project_format.py born  <project dir>        # a new project's first document: record the installed version
                                                         # at once (its stages produce today's formats); no-op when stamped

The changes are ../changes.json: each names the plugin version that brought it, a check that it applies to the
project (`applies`) and a check that the project is still behind (`behind`). A check is one of
{"exists": path}, {"missing": path} (a path with * is a glob), {"grep": {"path": file or folder, "pattern": regex}} (text files under a
folder, multiline), {"all": [...]}, {"any": [...]}, {"not": check}; paths are relative to the project.
The stamp is documentation/.dev-pipeline.json — {"plugin": "<version>", "skipped": [ids]}, committed with the
documents. Changes up to the stamped version count as done; a project without a stamp is checked against all.
Read-only except skip and stamp. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANGES = HERE.parent / "changes.json"
STAMP = "documentation/.dev-pipeline.json"
TEXT = {".md", ".yaml", ".yml", ".json", ".txt", ".sql", ".dbml", ".html"}


def ver(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v))


def installed() -> str:
    for d in [HERE, *HERE.parents]:
        for p in (d / ".claude-plugin" / "plugin.json", d / "plugin.json"):
            if p.is_file():
                try:
                    return json.loads(p.read_text(encoding="utf-8"))["version"]
                except (ValueError, KeyError):
                    pass
    return "0"


def stamp_of(root: Path) -> dict:
    try:
        return json.loads((root / STAMP).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def grep(root: Path, path: str, pattern: str) -> bool:
    rx = re.compile(pattern, re.M)
    p = root / path
    files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file() and f.suffix in TEXT] if p.is_dir() else []
    for f in files:
        try:
            if rx.search(f.read_text(encoding="utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


def present(root: Path, path: str) -> bool:
    return any(root.glob(path)) if "*" in path else (root / path).exists()


def holds(root: Path, c: dict) -> bool:
    if "exists" in c:
        return present(root, c["exists"])
    if "missing" in c:
        return not present(root, c["missing"])
    if "grep" in c:
        return grep(root, c["grep"]["path"], c["grep"]["pattern"])
    if "all" in c:
        return all(holds(root, x) for x in c["all"])
    if "any" in c:
        return any(holds(root, x) for x in c["any"])
    if "not" in c:
        return not holds(root, c["not"])
    raise ValueError(f"unknown check {c}")


def pending(root: Path) -> list[dict]:
    st = stamp_of(root)
    since, skipped = ver(st.get("plugin", "0")), set(st.get("skipped", []))
    changes = json.loads(CHANGES.read_text(encoding="utf-8"))
    return [c for c in changes if ver(c["version"]) > since and c["id"] not in skipped
            and holds(root, c["applies"]) and holds(root, c["behind"])]


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, root = sys.argv[1], Path(sys.argv[2]).resolve()
    if cmd == "hook":
        if not (root / "documentation").is_dir():
            return
        todo = pending(root)
        if not todo:
            return
        st, now = stamp_of(root).get("plugin"), installed()
        head = (f"The dev-pipeline plugin is {now}; this project was brought in line with {st}." if st else
                f"The dev-pipeline plugin is {now}; this project has no stamp of the plugin version.")
        print(f"{head} {len(todo)} change(s) of the plugin's formats are not in the project yet: "
              + "; ".join(f"«{c['title']}» ({c['version']})" for c in todo) + ".")
        print("Tell the user in one or two plain sentences and offer the dev-pipeline:upgrade-docs skill; change nothing "
              "without their answer.")
        return
    if cmd == "list":
        todo = pending(root)
        if "--json" in sys.argv:
            print(json.dumps(todo, ensure_ascii=False, indent=1))
            return
        st = stamp_of(root)
        print(f"plugin {installed()}; project stamp {st.get('plugin', 'none')}; skipped {st.get('skipped', [])}")
        if not todo:
            print("nothing pending")
        for c in todo:
            print(f"\n[{c['id']}] {c['title']} — {c['version']}\n  Что: {c['what']}\n  Чем исправить: {c['fix']}")
        return
    if cmd == "check":
        cid = sys.argv[3]
        c = next((c for c in json.loads(CHANGES.read_text(encoding="utf-8")) if c["id"] == cid), None)
        if c is None:
            sys.exit(f"no change {cid}")
        behind = holds(root, c["applies"]) and holds(root, c["behind"])
        print("still behind" if behind else "done")
        sys.exit(1 if behind else 0)
    if cmd == "born":
        if (root / STAMP).exists():
            print(f"{STAMP}: already stamped — left as it is")
            return
        (root / STAMP).parent.mkdir(parents=True, exist_ok=True)
        (root / STAMP).write_text(json.dumps({"plugin": installed()}, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"{STAMP}: born at {installed()}")
        return
    if cmd in ("skip", "stamp"):
        st = stamp_of(root)
        if cmd == "skip":
            st["skipped"] = sorted(set(st.get("skipped", [])) | {sys.argv[3]})
        else:
            todo = pending(root)
            if todo:
                print("not stamped — pending: " + ", ".join(c["id"] for c in todo))
                sys.exit(1)
            st["plugin"] = installed()
        (root / STAMP).parent.mkdir(parents=True, exist_ok=True)
        (root / STAMP).write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{STAMP}: {json.dumps(st, ensure_ascii=False)}")
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
