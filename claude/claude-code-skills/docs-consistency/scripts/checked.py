"""The `checked:` block of docs-consistency.md: every file of the document set with its git blob hash.

    python3 checked.py [<project dir>]                          # print the block for the set as it is now
    python3 checked.py [<project dir>] --verify <report.md>     # exit 0 when the report's block still matches

A contract split into files is one document in several files (the SRS's areas/, the OpenAPI paths/ and
components/, the migrations beside the schema): an edit in any of them is an edit of the document, so the block
pins every file, not the index alone. --verify lists what changed since the check — a file edited, gone, or new
in the set (a report written before every file was pinned lists only the index files, so its parts come out as
new) — and exits 1 when anything did. The hash is the one `git hash-object <path>` prints, from the working tree,
first 7 characters. Standard library only.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# the set docs-consistency reads (docs-consistency → Inputs; doc-versioning → Registry), in chain order
PATTERNS = [
    "requirements/srs/srs.md", "requirements/srs/areas/*.md",
    "db/schema.md", "db/migrations/*.sql",
    "api/openapi.yaml", "api/paths/**/*", "api/components/**/*",
    "architecture/architecture.md", "architecture/domain.md", "architecture/scenarios/*/*.md",
    "ui/frames-register.md", "ui/screen-specs/S-*.md",
    "ui/*/frames-register.md", "ui/*/screen-specs/S-*.md",
]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()[:7]


def doc_set(root: Path) -> dict:
    """{repo-relative path: hash} for every file of the set present now."""
    doc = root / "documentation"
    files: dict = {}
    for pat in PATTERNS:
        for p in sorted(doc.glob(pat)):
            if p.is_file() and not p.name.startswith("."):
                files.setdefault(p.relative_to(root).as_posix(), blob(p))
    return files


def block(files: dict) -> str:
    return "checked:\n" + "".join(f"- {path} {h}\n" for path, h in files.items())


def recorded(report: Path) -> dict:
    """The report's `checked:` block as {path: hash}."""
    files, inside = {}, False
    for line in report.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip() == "checked:":
            inside = True
            continue
        if inside:
            parts = line.strip().split()
            if len(parts) == 3 and parts[0] == "-":
                files[parts[1]] = parts[2]
            elif line.strip():
                break
    return files


def diff(root: Path, report: Path) -> list:
    """What moved since the report: (kind, path) with kind changed | gone | new."""
    then, now = recorded(report), doc_set(root)
    out = [("changed", p) for p, h in then.items() if p in now and not now[p].startswith(h[:7]) and not h.startswith(now[p])]
    out += [("gone", p) for p in then if p not in now]
    out += [("new", p) for p in now if p not in then]
    return out


def main() -> None:
    args = sys.argv[1:]
    report = Path(args[args.index("--verify") + 1]) if "--verify" in args else None
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--verify")]
    root = Path(pos[0] if pos else ".").resolve()
    if report is None:
        sys.stdout.write(block(doc_set(root)))
        return
    if not report.is_file():
        sys.exit(f"no report {report}")
    moved = diff(root, report)
    if not moved:
        print("checked: every file matches")
        return
    names = {"changed": "changed since the check", "gone": "gone since the check", "new": "new in the set, not checked"}
    for kind, path in moved:
        print(f"{names[kind]}: {path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
