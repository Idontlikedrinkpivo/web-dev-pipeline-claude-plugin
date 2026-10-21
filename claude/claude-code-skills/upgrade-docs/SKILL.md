---
name: upgrade-docs
description: >-
  Brings a project in line with a newer dev-pipeline plugin: lists the plugin's format changes the project's files
  do not have yet (a new document, a new section, a new rule for an existing document, the documentation site),
  explains each in plain words, asks the user which to make now, makes the chosen ones through the skill that owns
  them on a branch — one commit per change — and stamps the plugin version in documentation/.dev-pipeline.json. Use
  when the session-start hook says the project is behind the plugin, after `claude plugin update`, or when the user
  asks «обнови проект под плагин», «что поменялось в плагине», «приведи документы к новой версии». Not for writing
  a project's documents from scratch (the pipeline's stages) or updating the plugin itself.
---

# Upgrade a project to the installed plugin

A plugin release can change what a project's files should look like: a new document, a new section of one, a new
rule for text the pipeline already wrote. Projects written under an older release do not change by themselves.
`changes.json` beside this file lists every such change with a check that it applies to a project and a check
that the project still lacks it; `scripts/project_format.py` runs the checks. The session-start hook runs the same
checks and names what is pending, so the user hears about it in any project after an update.

## Steps

1. **List.** Run `python3 <this skill's folder>/scripts/project_format.py list .` from the project's root. Nothing
   pending — say so in one sentence, run `stamp` (step 6) and stop.

2. **Explain.** For each pending change tell the user, in plain Russian, one short paragraph: what the plugin does
   differently now, what it means in this project (which files, roughly how much work: a whole new document and a
   check on the test stand, or a rewrite of existing text), and what will not change. The `what` and `fix` fields
   are the source; look at the project's files before estimating the size, never guess.

3. **Ask.** One question per change, or one multi-select question when there are several: «сделать сейчас»,
   «не нужно этому проекту» (skipped for good), «позже» (asked again next time). Nothing is changed before the
   answer.

4. **Branch.** The working tree must be clean — if not, ask how to handle it, do not stash on your own. Make a
   branch `docs/plugin-<installed version>` from the current one, unless the user wants the current branch.

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
   `documentation/.dev-pipeline.json` — only when nothing is pending (skipped changes do not count), otherwise it
   lists what is left and writes nothing. Commit the file: `docs: проект приведён к плагину <version>`.

7. **Report**: what was made (with commits), what was skipped for good, what was left for later, the branch. The
   user merges and pushes.

## Rules

- The user decides every change; a hook line or a pending list is never a reason to start one.
- One change, one commit; never mix a format change with other work.
- A change is finished when its check passes, not when the text looks done.
- Never edit `changes.json` from a project session: it belongs to the plugin. A pending change that is wrong for
  this project is skipped, and the user may report it.

## For the plugin's maintainer

A release that changes the format of files projects already have adds a row to `changes.json`:
`references/adding-a-change.md`.
