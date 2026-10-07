# SRS-writer packet and report

A subagent gets one SRS and no conversation history. What is not in the
packet does not exist for it.

The orchestrator fills every slot. The writer follows the **Writer** half
of `srs-writer`, not the Orchestrator half.

## The packet

```
You settle the SRS. You do not print it, and you do not write production
code, a schema, or an API. When every decision the template needs is
settled, nest `doc-typist` with
`executor-catalog/references/doc-typist-prompt.md`. A gap the skill calls
BLOCKED returns before that dispatch. Read the file back. One correction
dispatch, then the report. Do not type the correction. Do not paste the
finished SRS into the typist's prompt. Writing OUTPUT PATH yourself is
a failed print.

SKILL           <repo-relative path to srs-writer/SKILL.md>
                Follow the Writer half and the `srs-writer` skill's references/security-checklist.md.
                Skip the Orchestrator half. Do not run grill-me, doc-review,
                or pipeline. Do not commit.

EXECUTOR        srs-author

OUTPUT PATH     documentation/requirements/srs/srs.md and its areas/
                files (srs-writer → Document Structure → Layout)
MODE            greenfield | increment | grill-reversal

INPUTS YOU MUST FOLLOW (pasted, not linked)
  <the source: a business-requirements file, a note, or the chat text.
   On increment or grill-reversal, also paste the current SRS.>

REVERSALS       <grill-reversal only: each decision the user reversed —
                in a grill, or after the SRS was finished (pipeline →
                references/decision-changes.md) — with the line it
                replaces. Otherwise: none>

LANGUAGE        Russian prose, including section headings and table
                columns from the skill template. Do not translate ids
                (A-, FR-, NFR-, BR-, UC-, AC-, Alt-, Exc-) or the
                priority tokens must / should / could. Frontmatter keys
                stay English.

RULES
- `doc-typist` writes OUTPUT PATH and any `open-questions.md` row or
  `ui-wishes.md` line the settlement named. You write none of them.
- Do not invent a product decision. A gap is a row in `open-questions.md`
  beside the SRS. Do not add an open-questions section to the SRS.
  A generic actor, or any question the skill says to ask before writing
  the row, is STATUS BLOCKED — do not guess and do not ask the user
  yourself.
- On grill-reversal: the settlement lists each contradicted line and
  its replacement. The typist replaces it in place. Do not bump version.
  Do not add a changelog row.
- Frontmatter is only `title`, `date`, `updated`, `version`. Do not
  write `status`, `grilled`, `reviewed`, or `sources`.
- On increment: follow srs-writer → Resume and doc-versioning. Do not
  change `version`, `updated`, or `## Журнал изменений`. Never renumber:
  a row inserted between two rows takes a dotted id after the row above
  (`FR-10.1`), a row at a section's end the next whole number.
- Behaviour, not interface (srs-writer → Behaviour, not interface): no
  screen, control, gesture, message wording, or visual in the SRS.
  Interface wishes from the source go to `ui-wishes.md` beside the SRS.
- Do not invoke grill-me, doc-review, or pipeline.
- Do not commit, do not stage.
```

## The report

Last message, exactly these fields:

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILE WRITTEN      the output path, or none
COUNTS            FR range, UC range, N rows in open-questions.md,
                  N wishes in ui-wishes.md
SOURCE            покрыто N из M пунктов источника
DOWNSTREAM        increment only: one line per consumer, must bump or
                  unaffected with the reason. Omit on greenfield.
CONCERNS          only for DONE_WITH_CONCERNS
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED
DELEGATED         doc-typist, or none
```
