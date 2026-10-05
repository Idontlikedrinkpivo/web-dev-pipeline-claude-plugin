# Increment: when the architecture documents already exist

Read this when any of the three documents (foundation, domain model,
scenarios of an area) already exists — a feature added to a designed
system. The orchestrator reads "Which modes run"; each writer reads the
rest. Each output is the same document, edited in place, not a second
file and not a new version number. Read the `doc-versioning` skill and
follow it. A write touches neither `version` nor the changelog: the
stamping commit writes the version and one typed row per changed name.

## Which modes run

Pick from what changed in the inputs (SRS diff, schema diff, OpenAPI
diff, the user's request). Run the picked modes in the greenfield order:
foundation → domain → scenarios.

| What changed | Mode | Why only this |
|---|---|---|
| a new or changed business rule, a new entity or value object, a new state | `domain` | rules have one home; a scenario that only cites the rule id does not change |
| a new or changed use case or query | `scenarios:<area>` of each touched area | one living document per area; other areas are not re-read |
| a use case in a new SRS group | `foundation` (§2 row, §5 folder, lint) + a new `scenarios:<area>`, which creates `scenarios/<area>/` | an area is a module; the tree and lint must know it |
| a new port, external system, store, transaction model (outbox vs in-request), stack, or level | `foundation` | these are the fundamental decisions it owns |
| a new method on an existing port, a new named error's HTTP row, a new config variable | `foundation`, graded as a mechanical increment | a signature and a mapping have one home; usually added by the writer of a scenario that needs it (`ALSO CHANGED`) |
| a field added to an entity | `domain` (sketch, «Поля также в:»); the scenarios whose read models show it | — |

A document no row picks is **untouched**. Name each untouched document in
the report with its reason («фундамент не тронут: новых портов, хранилищ
и внешних систем нет»). Those lines are the evidence that the increment
does not contradict an earlier decision.

One writer settles every picked document. When a picked document needs
a name another document lacks (a port method, a named error and its
HTTP row, an entity method), the writer adds it there and lists that
document under `ALSO CHANGED` (SKILL.md → Writer); it becomes a changed
document of this increment like the picked ones.

## What changes in each document

- **Steps 2 and 2b are already answered** — read them from foundation
  §1 «Ключевые решения». Do not re-propose either. Promote the level
  only when this feature is itself a Full trigger; then the foundation
  edits the «Уровень» row and the report names the promotion. A
  promotion reaches the domain model and every scenarios document
  (input and output types, query ports per audience), so it runs all
  modes.
- **The invariant table grows, it does not get rewritten.** New rows for
  the new rules; an existing row changes only when the feature genuinely
  changes that rule. Name the reason in the report; the commit's
  changelog row carries it.
- **A scenarios document gains or changes only the touched use cases.**
  Other use cases of the area keep their text verbatim. A scenario that
  cites a changed rule id is re-read; it changes only if its steps or
  errors change.
- **Re-read the sections the feature touches even when they look
  unaffected** — an entity gaining a state, a port gaining a method, a
  query whose audience now sees a new field. Record what you confirmed
  unchanged in the report.
- **When code already exists, the code is the source for signatures.**
  Copy an entity's or a port's signature from the file the documents
  name, not from the old document; a line that disagrees with the code
  is corrected to the code (unless this feature changes it) and listed
  in the report. Otherwise the document turns into a second, stale
  contract the next agent trusts.
- **Only affected sections appear in the diff.** No re-wording, no
  re-ordering, no renumbered assumptions.
- **Every version is still the whole document.** The changelog carries
  the diff; the body carries the portrait. A section that did not change
  keeps its previous text verbatim — it is never replaced by a pointer.
  Banned in the body: "как в 1.1.0", "без изменений", "см. историю git",
  "описано выше", an empty section under a live heading. A reader who
  opens only this version must be able to name everything the document
  owns without opening an older one.
- **Name a downstream verdict per consumer in the report** — the other
  two architecture documents, DB schema, OpenAPI, plan, scaffold: must
  change, or unaffected with the reason. Give each changed name the
  change type it implies — `ломает` (a port, method, named error, rule or
  field others cite removed, renamed, or changed in meaning or shape),
  `добавляет` (a new one), `уточняет` (same meaning, new wording) — so the
  stamp can type its rows. Do not write either into the changelog; the
  commit copies them. Name `repo-scaffold` when foundation
  §5 gained a folder or §1 Стек changed; it adds folders and lint rules
  to the live repo in its increment mode.
- **Rebuild the diagrams of the document you changed.** Foundation: the
  D2 views in `diagrams/` and their embeds from §1 / §2 / §4 / §5 (a
  second area adds `modules.*` and its embed in §2), unless this
  increment is applying a newer diagram (then apply first, then
  rebuild). Scenarios: the
  sequence diagram of every key scenario whose steps changed; a scenario
  that became key gains `scenarios/<area>/diagrams/<use-case-kebab>.puml`
  / `.svg` and its «Последовательность» row, one that stopped being key
  loses its `diagrams/<use-case-kebab>.*` and the row (an emptied
  `diagrams/` folder goes too). See `architecture-diagram.md`.
