---
name: upgrade-docs
description: >-
  Brings a project's documents up to a newer dev-pipeline plugin: lists the document format changes the project
  lacks, asks which to make, makes them one commit each. Use when the session-start hook names document changes,
  after a plugin update, or for «обнови документы под плагин», «что поменялось в плагине». Code and project
  settings go to `upgrade-code`; not writing documents from scratch.
---

# Upgrade a project's documents to the installed plugin

A plugin release can change what a project's files should look like: a new document, a new section of one, a new
rule for text the pipeline already wrote. Projects written under an older release do not change by themselves.
`changes.json` beside this file lists every such change with a check that it applies to a project and a check
that the project still lacks it; `scripts/project_format.py` runs the checks. The session-start hook runs the same
checks and names what is pending, so the user hears about it in any project after an update.

The list has two kinds. Rows with `"kind": "code"` change the project's code and settings — quality gates, the
project's verify skill, the plugin's team settings — and belong to `upgrade-code`, which follows these steps with
its own differences. The rows without a kind are documents, and they are this skill's.

## Steps

1. **List.** Run `python3 <this skill's folder>/scripts/project_format.py list . --kind docs` from the project's
   root. Nothing pending — say so in one sentence, run `stamp` (step 6) and stop. When the output also names
   changes for `upgrade-code`, say in one line that they are the code's and `/dev-pipeline:upgrade-code` makes
   them; do not make them here.

2. **Explain.** For each pending change tell the user, in plain Russian, one short paragraph: what the plugin does
   differently now, what it means in this project (which files, roughly how much work: a whole new document and a
   check on the test stand, or a rewrite of existing text), and what will not change. The `what` and `fix` fields
   are the source; look at the project's files before estimating the size, never guess.

3. **Ask.** One question per change, one at a time, per `grill-me` → "How a question is shown": the change
   explained in the chat, then the options «сделать сейчас», «не нужно этому проекту» (skipped for good), «позже»
   (asked again next time), then stop until the user answers. Nothing is changed before the answer.

4. **Branch.** The working tree must be clean — if not, ask how to handle it, do not stash on your own. During an
   open iteration (an open `documentation/plans/<version>/` with no `summary.md`) the commits go on that
   iteration's branch `iteration/<version>` (`pipeline` → Service version, «One branch per iteration»). Otherwise make a branch
   `docs/plugin-<installed version>` from the current one, unless the user wants the current branch.

5. **Make each chosen change**, one at a time:
   - Read the skill the `fix` names and do what the `fix` says — only that. A row that names one step of a stage
     runs that step, not the stage; a row that names a whole stage (a new document) runs the stage with its gates.
   - Check it: `python3 <…>/project_format.py check . <id>` must print `done`. If it still says `still behind`,
     the change is not finished — finish it or tell the user what stopped it.
   - Commit it alone: `docs: <title of the change> (плагин <version>)`, with the documents it touched; when the
     project has a documentation site, wait for its rebuild first (`docs-site` → `rebuild.py . --wait`) and stage
     `documentation/_web-docs` too.
   - «Не нужно этому проекту»: `python3 <…>/project_format.py skip . <id>`.

6. **Stamp.** `python3 <…>/project_format.py stamp .` writes the installed version into
   `documentation/.dev-pipeline.json` — only when nothing of either kind is pending (skipped changes do not count),
   otherwise it lists what is left and writes nothing. Code changes left for `upgrade-code` keep the stamp off too:
   say so, and that the stamp comes with the last of them. Commit the file: `docs: проект приведён к плагину <version>`.

7. **Report**: what was made (with commits), what was skipped for good, what was left for later, what is left
   for `upgrade-code`, the branch. On a
   `docs/plugin-<version>` branch the user merges and pushes it; on an iteration's branch the changes reach `main`
   with the iteration.

## Rules

- The user decides every change; a hook line or a pending list is never a reason to start one.
- One change, one commit; never mix a format change with other work.
- A change is finished when its check passes, not when the text looks done.
- Never edit `changes.json` from a project session: it belongs to the plugin. A pending change that is wrong for
  this project is skipped, and the user may report it.

## For the plugin's maintainer

A release that changes the format of files projects already have adds a row to `changes.json`:
`references/adding-a-change.md`.
