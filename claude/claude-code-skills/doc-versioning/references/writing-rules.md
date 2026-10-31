# Writing rules

Read before writing, reviewing or checking any document or report of the pipeline: the language every artifact
is written in, the headings and report shapes that stay frozen, and what a contract may not say about the look.
Writers, gates and reviewers follow it; `doc-review` and `docs-consistency` check it.

## Document language

Every artifact this collection writes is in **Russian**: prose, titles,
explanatory table cells, changelog bodies, grill questions, review
findings, architecture rationale, OpenAPI `description` / `summary` /
`example`, DBML `Note` / `COMMENT ON`.

Do not translate **cited tokens**: ids (`UC-1`, `FR-2`, `ДП-3`), table and
column names, `operationId`, paths, type names, file paths, stack
identifiers. They stay as the design named them.

**Every document reads at a glance** — a table cell is one fact, a run of cases is a table, a sequence is a
numbered list, no history in the body: `references/readable.md`, with `scripts/facts_check.py` to prove a rewrite
kept its facts.

**Frozen headings stay as the stage skill names them.** Frontmatter keys
(`version`, `migration`, `sources`, `grilled`) stay English. Every versioned
document, the DB schema included, has `## Журнал изменений` with the same
five Russian columns; a plan has none. Headings and table columns are
Russian unless the word is a term of the trade (`DBML`, `ER`, `API`, `SRS`,
ids). SRS
and architecture freeze their Russian headings in `srs-writer` and
`clean-architecture-design` (`## 1. Кратко`, `## 1. Состав системы`, …).
Translating a frozen heading breaks parsers and citations.

**Report shapes are frozen the same way.** Review and run reports print a
template. Its headings, verdict tokens, and fixed lines stay exactly as the
template writes them: `Verdict: PASS`, `## Ревью плана — <path> — <verdict>`,
`### Ревью U<n> — <verdict>`, `## Ревью всего прогона — <path> — <verdict>`,
`## Результаты ревью документа`, `### Охват`, `Review complete.` The
verdict tokens and the `Verdict:` and `Review complete.` lines are machine
markers and stay English. A report written before plugin 1.2.152 carries
the English heading of its time (`## Plan review — …`, `### Review U<n>`,
`## Full-plan review — …`, `## Document Review Results`) — the same report. This matters for two reasons. `work` and `pipeline`
read `Verdict:` as a gate, and a missing line means the gate did not pass. Later
stages and the user find a report by its heading, so a translated heading
reads as a missing report.

This rule is the artifact, not the skill file and not the source code.

## What, not how it looks

Every contract written before the mockups — SRS, DB schema, OpenAPI, the
architecture foundation, the domain model, the scenarios —
describes **what** the product does and holds: actions, data, rules,
states, outcomes, and what each text must convey. None of them records a
visual or UX-pattern decision, or the exact wording of a label or a
message: a widget (button, dropdown, context menu,
tabs), a presentation (modal, side panel, own page, toast, banner),
layout, density, colour, icon, size, or how a layout changes at a narrow
width. Those are decided on the Figma frames by `ux-patterns`, by the
skill or by a designer, and they change often. A contract that names
one has to be edited every time the designer decides differently, and
it silently overrules the designer until it is.

| In the contract | On the frame only |
|---|---|
| «резидент отменяет свою бронь» — an action | a button, a menu item, a swipe; its label «Отменить» |
| «выбор одной переговорной из списка» — input of a kind | dropdown, radio group, segmented control |
| «вложенный шаг M1 «Отмена брони»» | modal, side panel, separate page |
| «сообщение об успехе (смысл: бронь отменена)», «ошибка у поля» | toast, banner, inline line above the table; the wording «Бронь отменена» |
| «для каждой брони: переговорная, дата, время» | table, cards, list rows |
| «поддерживаемые ширины: 1280+ и 375» | table → cards at 375 |

Each writer names this rule in its own terms; `doc-review` checks it on
every type; a binding found later is rewritten as behaviour, and the
visual choice stays on the frame.

Two documents are exempt because they are written **after** the mockups
and describe them: the frames register and the screen specs (`screen-spec`).
They cite frames, variants and the wording from the frame's «Тексты»
table — by reference, never by describing colours or sizes in words.
`ui-wishes.md` is input to the design, never a contract: a frame or a
document that departs from a wish is not a discrepancy anywhere.
