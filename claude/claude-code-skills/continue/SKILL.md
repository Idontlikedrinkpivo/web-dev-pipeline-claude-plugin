---
name: continue
description: >-
  User command: says where the project stopped, from its files, and asks the next step. In chat, «где я» is pipeline.
disable-model-invocation: true
---

# Continue the project

A new session remembers nothing of the last one; the project's files do. This command reads them and puts the user
back at the right stage.

1. Run `python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/where_am_i.py"` from the project's root. Its output is the
   evidence — never what an earlier session seemed to say. When it names an iteration open only by its branch
   («Итерация … открыта по ветке» — a fresh clone, or a colleague's pushed work), run the `open_iteration.py` command
   it prints and the script again: switching to that branch and creating the ignored `plans/` folder is part of
   reading where the project is, and the documents live on that branch. The only commit it can make is the
   `.gitignore` line for `plans/` when that branch still lacks it; its output says so.
2. Read the output by `pipeline` → `references/where-am-i.md` (`${CLAUDE_SKILL_DIR}/../pipeline/references/where-am-i.md`):
   it owns which open point comes first.
3. Answer in plain Russian: where the project is, what is done, what is stale or waiting, and the next step — asked as
   `pipeline` → «Asking before a transition» asks it (run, skip, or stop). Start nothing before the answer.
