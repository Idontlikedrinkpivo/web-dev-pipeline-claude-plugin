#!/bin/sh
# dev-pipeline: after an edit of a document under documentation/ (plans/ and the site itself left out), rebuild the
# project's documentation site in the background — only when the project already has one. Fires for subagents'
# edits too. Silent, returns at once, never fails the tool call.
input=$(cat 2>/dev/null)
case "$input" in
  *documentation/*) ;;
  *) exit 0 ;;
esac
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$dir/documentation/site/index.html" ] || exit 0
paths=$(printf '%s' "$input" | grep -o 'documentation/[^"[:space:]\\]*' | grep -v -e '^documentation/plans/' -e '^documentation/site/' -e '^documentation/\.' | sort -u)
[ -n "$paths" ] || exit 0
root="$(cd "$(dirname "$0")/.." && pwd)"
script="$root/docs-site/scripts/rebuild.py"
[ -f "$script" ] || script="$root/skills/docs-site/scripts/rebuild.py"   # the Codex layout
case "$paths" in
  *documentation/api/*) python3 "$script" "$dir" --api >/dev/null 2>&1 ;;
  *) python3 "$script" "$dir" >/dev/null 2>&1 ;;
esac
exit 0
