#!/bin/sh
# dev-pipeline: after an edit of a document under documentation/ (plans/ and the site itself left out), regenerate the
# table documents when the schema changed (db-schema-design/scripts/table_docs.py), then rebuild the project's
# documentation site in the background — or build it, at the project's first document (rebuild.py decides, and leaves
# out a project that declined the site). Fires for subagents' edits too. Silent, returns at once, never fails the
# tool call.
input=$(cat 2>/dev/null)
case "$input" in
  *documentation/*) ;;
  *) exit 0 ;;
esac
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
# Only the paths of the files the tool changed — tool_input.file_path of Edit, Write and MultiEdit, or the file
# headers of an apply_patch (the Codex build) — never the rest of the input: the old and new text of an edit may
# name a documentation/ path, and a code edit that mentions one must not start a rebuild with --api and npx.
paths=$(printf '%s' "$input" | python3 -c '
import json, os, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
root = os.path.realpath(sys.argv[1])
ti = data.get("tool_input") if isinstance(data, dict) else None
found, texts = [], []
if isinstance(ti, dict):
    for key in ("file_path", "path"):
        if isinstance(ti.get(key), str):
            found.append(ti[key])
    texts = [v for v in ti.values() if isinstance(v, str)]
elif isinstance(ti, str):
    texts = [ti]
for t in texts:
    found += re.findall(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+?)\s*$", t, re.M)
for p in found:
    full = os.path.realpath(p if os.path.isabs(p) else os.path.join(root, p))
    rel = os.path.relpath(full, root)
    if rel.startswith("documentation" + os.sep):
        print(rel.replace(os.sep, "/"))
' "$dir" 2>/dev/null | grep -v -e '^documentation/plans/' -e '^documentation/_web-docs/' -e '^documentation/_site/' -e '^documentation/\.' | sort -u)
[ -n "$paths" ] || exit 0
root="$(cd "$(dirname "$0")/.." && pwd)"
# The schema changed: regenerate its table documents first (db-schema-design), so the site gets them too.
case "$paths" in
  *documentation/db/*)
    if printf '%s\n' "$paths" | grep '^documentation/db/' | grep -v -q '^documentation/db/tables/'; then
      tables="$root/db-schema-design/scripts/table_docs.py"
      [ -f "$tables" ] || tables="$root/skills/db-schema-design/scripts/table_docs.py"   # the Codex layout
      python3 "$tables" "$dir" >/dev/null 2>&1
    fi ;;
esac
script="$root/docs-site/scripts/rebuild.py"
[ -f "$script" ] || script="$root/skills/docs-site/scripts/rebuild.py"   # the Codex layout
case "$paths" in
  *documentation/api/*) python3 "$script" "$dir" --api >/dev/null 2>&1 ;;
  *) python3 "$script" "$dir" >/dev/null 2>&1 ;;
esac
exit 0
