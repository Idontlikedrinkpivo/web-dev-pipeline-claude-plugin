# Assignable implementer names

The plan writer loads **this file only** when it names a unit's
`Implementer` or `Nested`. It does not load the rest of
`executor-catalog`. The session that dispatches the writer loads the
`plan-writer` rows separately. `plan-review` uses this list for the
executor-validity lens.

## Implementer

Copy one of these names into a unit's `Implementer`. Nothing else is legal there
— not a review row, not a plan-review row, not a plan-writer row, not a
doc-review row, not a design-writer row, not `code-explorer`, not a
model slug.

| Name | When |
|---|---|
| `mechanical-worker` | Grade 0: rename, move, config, apply a settled shape to N sites; the plan's last unit, the manifest `version` bump |
| `impl-lite` | Low: transcribe a fully specified artifact against a local pattern |
| `impl-medium` | Mid: close local decisions, then prove them |
| `impl-hard` | High: design the missing part inside given boundaries |
| `impl-ui` | Frontend whose `Docs` cite a screen spec and a Figma `nodeId`: the screen and its states, or a component whose shape comes from that frame. Any grade |

The grade's row and `impl-ui` do not combine. A unit that cites the frame is
`impl-ui` even when the cascade says 0 or Low. A unit that does not cite one
never takes `impl-ui`. Drawing or editing the Figma file is `figma-sonnet` or
`figma-opus`, and those names are not legal in a plan.

`impl-critical` is **not** an Implementer. `work` may escalate to it after a
High unit returns `BLOCKED` or `HARDER_THAN_EXPECTED`. A plan that writes it
is invalid. An `impl-ui` unit does not escalate onto it.

## Nested

`Nested` is either `—` or `mechanical-worker`. No other name. Nested never
raises capability. An `impl-ui` unit does not nest: `Nested` is `—`.

## Not assignable as Implementer or Nested

These names exist in the catalog for other dispatchers. Writing any of them
into a plan unit is a P0 for `plan-review`:

`impl-critical` · `review-medium` · `review-hard` · `review-full-plan` ·
`plan-review-medium` · `plan-review-hard` ·
`doc-review-low` · `doc-review-medium` · `doc-review-hard` ·
`docs-consistency-checker` · `ui-test-writer` · `ui-test-runner` · `screen-writer` ·
`figma-opus` · `figma-sonnet` · `design-lite` ·
`design-medium` · `design-hard` · `srs-author` · `doc-typist` ·
`plan-lite` · `plan-medium` · `plan-hard` · `code-explorer`

Slugs (`sonnet`, `gpt-*`, …) are never plan fields.
