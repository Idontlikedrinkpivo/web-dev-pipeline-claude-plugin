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
# every progress file the edit names (an apply_patch can touch several), relative to the project
printf '%s' "$input" | grep -o 'documentation/plans/[0-9][0-9.]*/[a-z0-9-]*\.md' | sort -u | while read -r rel; do
  python3 "$script" "$dir/$rel" >/dev/null 2>&1 || true
done
exit 0
