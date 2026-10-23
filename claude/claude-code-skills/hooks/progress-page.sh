#!/bin/sh
# dev-pipeline: after an edit of a progress file (documentation/plans/<version>/progress*.md, test-run.md,
# security-audit.md) rebuild its page beside it — progress-design.md -> progress-design.html — which reloads itself
# in the browser. Fires for subagents' edits too. Silent and never fails the tool call.
input=$(cat 2>/dev/null)
case "$input" in
  *documentation/plans/*progress*.md*|*documentation/plans/*test-run.md*|*documentation/plans/*security-audit.md*) ;;
  *) exit 0 ;;
esac
root="$(cd "$(dirname "$0")/.." && pwd)"
script="$root/pipeline/scripts/progress_page.py"
[ -f "$script" ] || script="$root/skills/pipeline/scripts/progress_page.py"   # the Codex layout
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
# every progress file the tool changed (an apply_patch can touch several), relative to the project: only the
# changed files' paths — tool_input.file_path, or the patch's file headers — not paths named inside the edit's text
printf '%s' "$input" | python3 -c '
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
    rel = os.path.relpath(full, root).replace(os.sep, "/")
    if re.fullmatch(r"documentation/plans/[0-9][0-9.]*/(progress[a-z0-9-]*|test-run|security-audit)\.md", rel):
        print(rel)
' "$dir" 2>/dev/null | sort -u | while read -r rel; do
  python3 "$script" "$dir/$rel" >/dev/null 2>&1 || true
done
exit 0
