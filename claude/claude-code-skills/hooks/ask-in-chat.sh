#!/bin/sh
# dev-pipeline: PreToolUse on AskUserQuestion — refuse the choice card in a dev-pipeline project and send the
# question back to the chat.
#
# Why: every question of the pipeline is a chat message the user answers with a message (pipeline →
# references/question-format.md). A card closed without a pick came back to the model as «no choice made», and it
# went on with the first option — «Вы не выбрали вариант, поэтому ставлю первый» (ai-initiatives, 2026-10-21,
# upgrade-docs) — and changed documents nobody had agreed to. The rule was already in the skills and was broken, so
# it is held here, outside the model.
#
# Narrow on purpose: it acts only where documentation/.dev-pipeline.json exists — the plugin's stamp, written when
# a project's first document is born (brainstorm, srs-writer) and by upgrade-docs / upgrade-code — so another
# project's questions, and every other tool, are left alone. Silent otherwise; never fails the session.
cat >/dev/null 2>&1
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$dir/documentation/.dev-pipeline.json" ] || exit 0
root="$(cd "$(dirname "$0")/.." && pwd)"
fmt="$root/pipeline/references/question-format.md"
[ -f "$fmt" ] || fmt="$root/grill-me/SKILL.md, section «How a question is shown»"
reason="dev-pipeline: this project asks its questions in the chat, not in a choice card — a card closed without a pick has been read as the first option. Ask the same question as one chat message, as $fmt says: what is being decided in plain words with an example, the options as letters with the one you recommend, «Ответьте сообщением», then end the turn and wait. Until the user answers, change nothing; no answer is not a choice."
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json, sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": sys.argv[1]}}, ensure_ascii=False))' "$reason"
  exit 0
fi
printf '%s\n' "$reason" >&2   # without python3: exit code 2 blocks the call and hands this text to the model
exit 2
