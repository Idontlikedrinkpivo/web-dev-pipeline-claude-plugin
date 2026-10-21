#!/bin/sh
# dev-pipeline: after an edit of a progress file (documentation/plans/<version>/progress*.md, test-run.md,
# security-audit.md) rebuild documentation/plans/<version>/progress.html — the self-reloading page of the
# iteration's progress. Fires for subagents' edits too. Silent and never fails the tool call.
input=$(cat 2>/dev/null)
case "$input" in
  *documentation/plans/*progress*.md*|*documentation/plans/*test-run.md*|*documentation/plans/*security-audit.md*) ;;
  *) exit 0 ;;
esac
root="$(cd "$(dirname "$0")/.." && pwd)"
script="$root/pipeline/scripts/progress_page.py"
[ -f "$script" ] || script="$root/skills/pipeline/scripts/progress_page.py"   # the Codex layout
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
# the version folder of the edited file, so the page of that iteration is rebuilt
v=$(printf '%s' "$input" | sed -n 's#.*documentation/plans/\([0-9][0-9.]*\)/.*#\1#p' | head -n 1)
if [ -n "$v" ]; then
  python3 "$script" "$dir" --version "$v" >/dev/null 2>&1 || true
else
  python3 "$script" "$dir" >/dev/null 2>&1 || true
fi
exit 0
