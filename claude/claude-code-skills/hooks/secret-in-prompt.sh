#!/bin/sh
# dev-pipeline: UserPromptSubmit — a message that carries what looks like a key, token, password or connection
# string gets one instruction for the model: never store or repeat the value, name its variable, tell the user it
# was not saved and is worth revoking (pipeline → Secrets).
#
# Why a hook: the pipeline copies the user's words into documents and agents' packets (the business requirements,
# the SRS, every SOURCE TEXT), so a pasted key would travel into files and commits before any rule was read. The
# shapes live in secret_scan.py; the value itself is never printed.
#
# Narrow on purpose: it acts only where documentation/.dev-pipeline.json exists (the plugin's stamp, as in
# ask-in-chat.sh), and only when a shape matches. Silent otherwise; without python3 it does nothing; never fails the
# session.
input=$(cat 2>/dev/null)
dir="${CLAUDE_PROJECT_DIR:-}"
[ -n "$dir" ] || dir=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd") or "")' 2>/dev/null)
[ -n "$dir" ] || dir="$PWD"
if [ ! -f "$dir/documentation/.dev-pipeline.json" ] || ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi
printf '%s' "$input" | python3 "$(dirname "$0")/secret_scan.py" 2>/dev/null
exit 0
