---
name: upgrade-docs
description: >-
  Brings a project's documents up to a newer dev-pipeline plugin, a commit per change. Use when the session-start hook
  names document changes, or «обнови документы под новую версию плагина». Not «обнови документацию» after a product
  change (the document's own stage).
---

# Upgrade a project's documents to the installed plugin

A plugin release can change what a project's files should look like: a new document, a new section of one, a new
rule for text the pipeline already wrote. Projects written under an older release do not change by themselves.
`changes.json` beside this file lists every such change with a check that it applies to a project and a check
that the project still lacks it; `scripts/project_format.py` runs the checks. The session-start hook runs the same
checks and names what is pending, so the user hears about it in any project after an update.

The list has two kinds. Rows with `"kind": "code"` change the project's code and settings — quality gates, the
project's verify skill — and belong to `upgrade-code`, which follows these steps with its own differences. The rows without a kind are documents, and they are this skill's.

## Steps

The changes are shown **one at a time**: a list of every change explained at once got edited before anyone
answered, and a question left unanswered was answered by the model itself («Вы не выбрали вариант, поэтому ставлю
первый»). The script hands out one change per call, so the next one is not on screen until this one is settled.

1. **What is pending.** `python3 "${CLAUDE_SKILL_DIR}/scripts/project_format.py" list . --kind docs` from the
   project's root, for the count only — say in one line how many document changes the project lacks, and, when the
   output also names changes for `upgrade-code`, that they are the code's and `/dev-pipeline:upgrade-code` makes
   them; do not make them here. Do not explain them here. Nothing pending — go to step 4 (the stamp still lands
   in a commit).

2. **The queue, one change per message.** `python3 "${CLAUDE_SKILL_DIR}/scripts/project_format.py" next . --kind
   docs` prints the next change only. For it, one message, shown as `pipeline` → `references/question-format.md`
   says: «Изменение N из M», then in plain Russian what the plugin does differently now, what it means in this
   project — which files, roughly how much work (a whole new document and a check on the test stand, or a rewrite
   of existing text), and what will not change; the `what` and `fix` fields are the source; look at the project's
   files before estimating the size, never guess. Then the options and stop:
   - `A. Сделать сейчас` — step 3;
   - `B. Не нужно этому проекту` — never offered again: `project_format.py skip . <id>`;
   - `C. Позже` — nothing recorded, nothing changed; it comes back the next time this skill runs.

   After the answer, the next change: `next . --kind docs --after <id of the change just settled>` — always with
   `--after`, so a change left for later is not shown twice in one sitting.

   **No answer is «позже».** A reply about something else, a reply that fits no option, silence, a closed picker
   — the change is C: no file is touched, nothing is recorded, and the first option is never assumed. Answer the
   other message; go on with the queue when the user comes back to it. The queue ends when `next` prints
   «nothing pending».

3. **Make the chosen change**, before the next one is shown:
   - **The branch, before the first commit.** The working tree must be clean — if not, ask how to handle it, do not
     stash on your own. During an open iteration (an open `documentation/plans/<version>/` with no `summary.md`) the
     commits go on `iteration/<version>` — run `python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/open_iteration.py"
     <version>` when on another branch; it only switches. Otherwise make a branch `docs/plugin-<installed version>`
     from the current one, unless the user wants the current branch.
   - Read the skill the `fix` names and do what the `fix` says — only that. A row that names one step of a stage
     runs that step, not the stage. A row that names a whole stage (a new document) runs the stage with its gates;
     when it returns, come back here — that stage does not offer the next pipeline stage and does not end the
     sitting, because the user is inside this queue.
   - **Form goes with the change; meaning is asked.** What the change's format prescribes is part of it, made
     without a separate question: moving journal rows and closed questions to where the format keeps them, removing
     history notes from the body («Правка от <даты>» paragraphs, «было → стало» remarks), the version on a
     `[deprecated]` mark, a duplicate of a row that lives elsewhere, headings, table shapes and file layout. A change
     of meaning is never made under the change's cover: a requirement, a field, an operation, a status, a number, a
     rule, a removed row. When the fix seems to need one, one question about that item alone; the rest of the
     change goes on. Never decline the whole change because one item looks like meaning.
   - Check it: `python3 "${CLAUDE_SKILL_DIR}/scripts/project_format.py" check . <id>` must print `done`. If it still
     says `still behind`, the change is not finished — finish it or tell the user what stopped it.
   - Commit it alone: `docs: <title of the change> (плагин <version>)`, with the documents it touched; when the
     project has a documentation site, wait for its rebuild first (`docs-site` → `rebuild.py . --wait`) and stage
     `documentation/_web-docs` too. This commit is not a stamp, and its hunks get no changelog row
     (`doc-versioning` → Commits that are not stamps).

4. **Stamp.** `python3 "${CLAUDE_SKILL_DIR}/scripts/project_format.py" stamp .` writes the installed version into
   `documentation/.dev-pipeline.json` — only when nothing of either kind is pending (skipped changes do not count),
   otherwise it lists what is left and writes nothing. Code changes left for `upgrade-code` keep the stamp off too:
   say so, and that the stamp comes with the last of them. When it wrote the file, commit it on the branch of
   step 3 (made now, when no change was made before): `docs: проект приведён к плагину <version>`.

5. **Report**: what was made (with commits), what was skipped for good, what was left for later, what is left for
   `upgrade-code`, the branch. On a `docs/plugin-<version>` branch the user merges and pushes it; on an
   iteration's branch the changes reach `main` with the iteration.

## Rules

- The user decides every change; a hook line or a pending list is never a reason to start one.
- One change per message, one change per commit; never mix a format change with other work.
- A change is finished when its check passes, not when the text looks done.
- Never edit `changes.json` from a project session: it belongs to the plugin. A pending change that is wrong for
  this project is skipped, and the user may report it.
