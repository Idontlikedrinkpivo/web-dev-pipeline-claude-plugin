---
name: upgrade-code
description: >-
  Brings a project's code and settings (quality gates, linters, CI) up to a newer dev-pipeline plugin, a commit each.
  Use when the session-start hook names code changes, or «обнови линтеры и CI под плагин». Documents: upgrade-docs.
---

# Upgrade a project's code to the installed plugin

The same list and script as `upgrade-docs`: `../upgrade-docs/changes.json`, the rows with `"kind": "code"`, and
`../upgrade-docs/scripts/project_format.py`. These changes touch the project's code and settings, not its
documents, so they are kept apart: the person who brings the documents up need not be the one who changes
linters and CI, and a code change wants the project's checks around it.

## Steps

Follow `upgrade-docs` → Steps — one change per message, no answer is «позже» — with these differences.

1. **What is pending.** `python3 "${CLAUDE_SKILL_DIR}/../upgrade-docs/scripts/project_format.py" list . --kind
   code`. Document changes it names as also pending belong to `/dev-pipeline:upgrade-docs`: say so in one line, do
   not make them.

2. **The queue.** `project_format.py next . --kind code`, then `--after <id>` of the change just settled, as there. Say also what in the
   code or settings changes, how many files (count them in the project, never guess) and that the app's behaviour
   does not change. A row whose `fix` names its own question asks it — the quality gates ask whether to make them
   now on a separate branch or as the first unit of the next iteration. «Первой задачей итерации» is «позже»
   here: nothing is made and nothing recorded. When that iteration opens, `open_iteration.py` names the change
   again, and `plan` makes it the iteration's first unit — or the user runs this skill then.

3. **Make the chosen change.** The branch as there, but outside an open iteration it is
   `chore/plugin-<installed version>`. Before the first change, run the project's own checks — the `lint`,
   `typecheck` and `test` commands its manifests name — and keep the result. Then per change:
   - Do what the `fix` says, with the skill it names, and only that: configuration and tooling, never the app's
     behaviour.
   - Run the same checks again. A check that was red before stays as it was and goes into the report; a check this
     change turned red is the change's defect — fix it within the change, or undo the change and tell the user.
   - `project_format.py check . <id>` must print `done`.
   - Commit it alone: `chore: <title of the change> (плагин <version>)`, only that change's files.

4. **Stamp.** As there: the stamp needs nothing of either kind pending, so document changes left for
   `upgrade-docs` keep it off — say so.

5. **Report.** As there, plus the checks before and after.

## Rules

`upgrade-docs` → Rules hold here too.
