# Changing the pipeline

Read only when the stage order, a gate, or a stage itself is being changed
— not during a run.

## One place for the order

Stages name their **successor** in `pipeline`'s chain table and nowhere
else. Reordering or retiring a *stage* is a one-table edit. Gates are not:
`grill-me` and `doc-review` are still invoked from the writer skills that
own the artifact, so inserting or retiring a gate is the table **plus**
those calls. Do not claim a single-file gate edit.

This is the discipline `executor-catalog` applies to models: a finished
stage resolves to the next stage and its gates in one table. A stage that
hardcodes "now run X" is a second source of truth, and the two drift the
first time the order changes.

## Rules for an edit

- **Reorder or insert a stage** — edit the chain table only. No stage skill
  changes, because none of them names its successor.
- **A new stage needs a row and a reason** — what it consumes, what it
  produces, and which gates close it. A stage nobody offers is unreachable;
  a stage with no gate has to say why none applies.
- **A new gate is a cost decision.** Say what it costs per run in the same
  sentence you add it, the way the `doc-review` note in "Asking before a
  transition" does.
- **Retiring a stage** — remove its row and re-point the neighbours' `Then
  offer` cells in the same edit, otherwise the chain has a hole that reads
  as a dead end.
- **Do not encode content rules in `pipeline`.** What a document must
  contain belongs to its stage; `pipeline` only says which stage runs when.
- **A state the pipeline reads** (a gate mark, a verdict line, a stamp
  commit's wording) is read by `scripts/where_am_i.py` too: change both.

## Asymmetries, on purpose

Each of these looks like an omission and is not. Do not "fix" one without
changing `pipeline`:

| Looks missing | Why it is not |
|---|---|
| No `doc-review` on business requirements | Stage 1's artifact is the least formal in the pipeline and every line of it is re-examined when `srs-writer` reads it. The grill is the stronger instrument there, and it runs. |
| No `grill-me` on mockups | The user judges mockups by looking at them in Figma; a grill interrogates written decisions, and the decisions the frames embody are written down by `screen-spec`, whose `doc-review` checks them. |
| No `grill-me` on architecture, DB, or API | Those decisions are technical, not product, and the user is not the one who settles them. `doc-review` already carries the right instruments: `adversarial-document-reviewer` challenges the premise and `security-lens-reviewer` the security decisions. |
| No gate on the Figma file | Frames are not a document. `ui-design` checks the returned `nodeId`s and its completeness checklist; `screen-spec`'s sync check (frame ↔ action ↔ API) and `doc-review` cover the rest. |
| No whole-codebase quality audit | Security has one — stage 14, once per iteration, because a hole anywhere in the application is a hole in the release. Quality does not: `code-review-full`'s `Drift` and `Superseded code` lenses cover the debt a plan introduced, and a standing audit of code no plan touched is a different activity on its own cadence that no stage depends on. |
