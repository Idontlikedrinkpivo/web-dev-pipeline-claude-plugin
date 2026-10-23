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
`<SKILLS ROOT>/executor-catalog/references/doc-typist-prompt.md`. A gap the skill calls
BLOCKED returns before that dispatch. Read the file back. One correction
dispatch, then the report. Do not type the correction. Do not paste the
finished SRS into the typist's prompt. Writing OUTPUT PATH yourself is
a failed print.

SKILLS ROOT     <absolute folder holding the plugin's skills
                (executor-catalog → Dispatch contract)>
SKILL           <SKILLS ROOT>/srs-writer/SKILL.md
                Follow the Writer half and the `srs-writer` skill's references/security-checklist.md.
                Skip the Orchestrator half. Do not run grill-me, doc-review,
                or pipeline. Do not commit.

EXECUTOR        srs-author

OUTPUT PATH     documentation/requirements/srs/srs.md and its areas/
                files (srs-writer → Document Structure → Layout)
MODE            greenfield | increment | grill-reversal | as-is
                as-is: the system exists and the SRS does not — write it
                from the code and the project's own documents named in
                READ FROM DISK, per <SKILLS ROOT>/upgrade-docs/references/
                as-is.md (describe, never design; a guess is an open
                question)
VERSION         <x.y.z — the open iteration's version (srs-writer, step 2);
                as-is: the service's current version (upgrade-docs/
                references/as-is.md §9)>

READ FROM DISK  <the source when it is a file (the business-requirements
                document, a note); on increment or grill-reversal also the
                current SRS — documentation/requirements/srs/srs.md and every
                areas/*.md; on as-is the code that shows the behaviour (routes,
                screens, jobs, the tests) and the project's own documents>
SOURCE TEXT     <pasted: the source when it exists only in the chat, and the
                user's answers of this session; or: none>

REVERSALS       <grill-reversal only: each decision the user reversed —
                in a grill, or after the SRS was finished (pipeline →
                references/decision-changes.md) — with the line it
                replaces. A grill sends its whole ledger here once, at
                its close, never one dispatch per round. Otherwise: none>
DEFERRED        <grill-reversal only: each question the grill deferred
                («потом», «отложим»), one line each, from the ledger.
                Otherwise: none>

LANGUAGE        Russian prose, including section headings and table
                columns from the skill template. Do not translate ids
                (A-, FR-, NFR-, BR-, UC-, AC-, Alt-, Exc-). Frontmatter
                keys stay English.

RULES
- `doc-typist` writes OUTPUT PATH and any `open-questions.md` row or
  `ui-wishes.md` line the settlement named. You write none of them.
- Do not invent a product decision. A gap is a row in `open-questions.md`
  beside the SRS. Do not add an open-questions section to the SRS.
  A generic actor, or any question the skill says to ask before writing
  the row, is STATUS BLOCKED with that one question in BLOCKER — do not
  guess and do not ask the user yourself; the session asks it and sends
  the answer back to you.
- On grill-reversal: the settlement lists each contradicted line and
  its replacement. The typist replaces it in place. Each DEFERRED line
  becomes one `open-questions.md` row beside the SRS, class `Отложено`,
  source `(допрос, YYYY-MM-DD)` — a deferred question is kept, not lost
  with the ledger. Do not bump version. Do not add a changelog row.
- Frontmatter is only `title`, `date`, `updated`, `version`. Do not
  write `status`, `grilled`, `reviewed`, or `sources`.
- On increment: follow srs-writer → Resume and doc-versioning. Do not
  change `version`, `updated`, or `## Журнал изменений`. Never renumber:
  a row inserted between two rows takes a dotted id after the row above
  (`FR-10.1`), a row at a section's end the next whole number.
- Behaviour, not interface (srs-writer → Behaviour, not interface): no
  screen, control, gesture, message wording, or visual in the SRS.
  Interface wishes from the source go to `ui-wishes.md` beside the SRS,
  by SRS group, a table «Где · Пожелание · Требования» (srs-writer → Behaviour, not interface).
- Do not invoke grill-me, doc-review, or pipeline.
- Do not commit, do not stage.
```

## The report

Last message, exactly these fields:

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILE WRITTEN      the output path, or none
COUNTS            FR range, UC range, N rows in open-questions.md
                  (N of them `Отложено` from DEFERRED), N wishes in
                  ui-wishes.md
SOURCE            покрыто N из M пунктов источника
CHANGES           every new or changed id with its change type —
                  `FR-10.1 добавляет`, `BR-3 ломает`, `UC-4 уточняет`
                  (srs-writer → Artifact Root and Resume, step 4); the
                  stamp types its changelog rows from this list. Omit on
                  greenfield.
DOWNSTREAM        increment only: one line per consumer, must bump or
                  unaffected with the reason. Omit on greenfield.
CONCERNS          only for DONE_WITH_CONCERNS
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED
DELEGATED         doc-typist, or none
```
