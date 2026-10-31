#!/bin/sh
# dev-pipeline: PreToolUse guard — refuses the few commands that broke real runs again and again although the rules
# said not to: a commit chained to a test run, a commit on main during an iteration, a `Plan-Unit:` trailer git
# cannot read, GNU-style `sed -i`, a progress file written from the shell, `git stash` / `reset --hard` / `clean`
# in the shared tree, an agent's edit outside its worktree. The rules and the reasons are in guard.py.
#
# Narrow on purpose: it acts only where documentation/.dev-pipeline.json exists (as ask-in-chat.sh); without
# python3 it does nothing; it never fails the tool call on its own error.
command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1; exit 0; }
python3 "$(dirname "$0")/guard.py" 2>/dev/null
exit 0
