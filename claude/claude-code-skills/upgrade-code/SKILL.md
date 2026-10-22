---
name: upgrade-code
description: >-
  Brings a project's code and settings up to a newer dev-pipeline plugin — quality gates in linters and CI, the
  project's verify skill: lists what the project lacks, asks which to make, makes them one commit each with the
  checks green before and after. Use when the session-start hook names code changes, or
  for «обнови код проекта под плагин». Documents go to `upgrade-docs`.
---

# Upgrade a project's code to the installed plugin

The same list and script as `upgrade-docs`: `../upgrade-docs/changes.json`, the rows with `"kind": "code"`, and
`../upgrade-docs/scripts/project_format.py`. These changes touch the project's code and settings, not its
documents, so they are kept apart: the person who brings the documents up need not be the one who changes
linters and CI, and a code change wants the project's checks around it.

## Steps

Follow `upgrade-docs` → Steps, with these differences.

1. **List.** `python3 <this skill's folder>/../upgrade-docs/scripts/project_format.py list . --kind code`. Document
   changes it names as also pending belong to `/dev-pipeline:upgrade-docs`: say so in one line, do not make them.

2. **Explain.** Say also what in the code or settings changes, how many files (count them in the project, never
   guess) and that the app's behaviour does not change.

3. **Ask.** As there. A row whose `fix` names its own question asks it — the quality gates ask whether to make them
   now on a separate branch or as the first unit of the next iteration. «Первой задачей итерации» is «позже»
   here: nothing is made, the session-start line names the change again, and the user runs this skill when that
   iteration opens.

4. **Branch.** As there, but outside an open iteration the branch is `chore/plugin-<installed version>`.

5. **Make each chosen change.** Before the first one, run the project's own checks — the `lint`, `typecheck` and
   `test` commands its manifests name — and keep the result. Then per change:
   - Do what the `fix` says, with the skill it names, and only that: configuration and tooling, never the app's
     behaviour.
   - Run the same checks again. A check that was red before stays as it was and goes into the report; a check this
     change turned red is the change's defect — fix it within the change, or undo the change and tell the user.
   - `project_format.py check . <id>` must print `done`.
   - Commit it alone: `chore: <title of the change> (плагин <version>)`, only that change's files.

6. **Stamp.** As there: the stamp needs nothing of either kind pending, so document changes left for
   `upgrade-docs` keep it off — say so.

7. **Report.** As there, plus the checks before and after.

## Rules

`upgrade-docs` → Rules hold here too.
