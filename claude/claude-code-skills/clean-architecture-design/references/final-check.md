# Before you finish

Read this after your document and its diagrams are on disk, before the
write is reported. Check the section for your MODE and the "Every mode"
section. Each item names the place (SKILL.md section or reference) that
states the rule; fix the document there, not here.

## Every mode

- Each fact sits in its one home (SKILL.md → One home per fact). Nothing
  owned by another document is restated; it is cited by name, rule id,
  or section — a rule's value too («до 4 ч» in a test plan is a second
  copy of BR-3). A fact a document lacks was added in its home and the
  report lists that document under `ALSO CHANGED`.
- Every type, id or result that appears in two documents (or two areas)
  has the same name and the same shape in both — grep each such name
  across the set before the report.
- No widget, layout, colour, icon, or exact UI wording anywhere —
  `doc-versioning` → What, not how it looks.
- The design stays inside the level's limits (no ceremony of the level
  above). Nothing was cut to make the document shorter — Step 2.
- Read the document as if its previous version did not exist: every
  section states its design, and nothing under a live heading is empty —
  `increment.md`.
- Russian prose and the Russian headings of the mode's template; English
  identifiers. `A-n` entries live only in
  `documentation/architecture/open-questions.md`.
- Every state the documents name is named by the requirements or tagged
  as an assumption — Guardrails → Invented model.

## Mode `foundation`

- The H1 is followed by `## Описание системы`, then `## Журнал
  изменений`. §1 is the Russian table set, one fact per row; no entity,
  use-case or read tables — `output-template-foundation.md`.
- «Ключевые решения» opens with the «Уровень» and «Стек» rows; every
  other row names a real alternative. The level is Modest unless a Full
  trigger fired, or the user / SRS named the system a throwaway
  prototype — Step 2.
- §1 Стек names the runtime with major versions; the file tree and lint
  table match it. The stack was already a fact, or the user picked it in
  chat — Step 2b.
- The security table covers all eleven sub-items: a concrete decision,
  or `Не применимо` with a reason naming the absent surface. Every NFR-ID
  is the `NFR-<n>` from the SRS named in `sources`. Schema and OpenAPI
  decisions are not reopened — `nfr-decisions.md`.
- With a human-facing interface in the SRS, the client is placed: its
  stack in §1, a §2 row, its folder and generated API client in §5, its
  lint and test rows in §6 — never «вне документа».
- §2 has one row per SRS capability group, each with its module folder,
  scenarios document path, and what it takes from other areas by name;
  area names match §5 folders. Every cross-area type or call the
  scenarios use is named there. A shared module (one several areas take
  from) takes nothing from an area.
- §3 opens with the layer roster; its cells are counts and pointers.
- §4: every port is signatures, with fields for every named type it
  defines; with several tenants every method over tenant-owned rows takes
  `TenantId`; wire and storage-record types are derived by a named tool;
  the configuration table, the service-channel table, and one named-error
  → HTTP table with the route-guard paragraph exist; every named error of
  the domain model has an HTTP row — `configuration-and-http.md`.
- §5 is real file names for what this document owns, with `domain/` and
  `application/` folders pointing at the document that names their files;
  every port, adapter, mapper and storage model from §4 has a line.
- §6: the lint rule table (not a pasted config) names every production
  layer of §5, exempts Host/bootstrap, forbids cycles and every
  cross-area import §2 does not name (and allows each one it names) when
  there are two or more areas, and uses a named tool for *this* stack.
  Walk every entity and value-object signature of the domain model and
  every scenario step: each type it names is importable from its file
  under §6. Where the allowed set differs by area, the row names the
  areas, so §6 allows no more than §2. The test plan covers one entity test per invariant
  row, use-case tests, a round-trip test per mapper, the cross-tenant
  test when there are several tenants, and one end-to-end path, sized to
  the level.
- Diagrams: `diagrams/context.d2`, `layers.d2`, `stores.d2` exist, plus
  `containers.d2` (or the skip sentence in §1) and `modules.d2` (or the
  skip sentence in §2); no separate diagram index file. Each view is
  embedded in its section — Контекст and Контейнеры in §1, Хранилища
  under §1 «Хранилища», Модули in §2, Слои in §3 — as
  `![<view>](diagrams/<view>.svg)`, with its `.svg` beside the `.d2` (or
  the report says `d2` was missing). Token labels resolve in §1 / §4 /
  §5. Edges in Контекст and Контейнеры carry labels; «Слои» has the
  legend. Nothing invented. No Mermaid — `architecture-diagram.md`.

## Mode `domain`

- Every quoted **domain** rule is in the invariant table with an entity
  or value-object owner; every **boundary** rule is in §5 (shape +
  proof). The invariant table exists in this document only.
- Every `BR-n` of the SRS is in exactly one place — invariant row,
  boundary row, or a scenario's «Доступ» row — with its id first;
  immutability and at-most-once rules are invariant rows.
- Every «Где проверяется» cell names a method that also appears in an
  entity or value-object sketch, with the same signature. Every row has
  «Ограничение в схеме» `none` / `CHECK` / `UNIQUE` / `FK`, copied from
  the schema.
- Every entity heading carries its file path, and every sketch is
  followed by `Поля также в:` naming each storage model, mapper, read
  model, and wire schema that repeats its fields.
- §3 lists every named error a scenario may return, with who raises it,
  and no HTTP status; each name has its row in foundation §4.
- Every SRS term that became a type has a glossary row; every noun that
  did not become an entity has a «Что не сущность» row.

## Mode `scenarios:<area>`

- The «Область» table names the area, its SRS group, module and
  entities; the area matches a foundation §2 row.
- Every state-changing action of the SRS group has a use case with its
  file path in the heading, and the Вход / Доступ / Выход / Операция API,
  Шаги, and Ошибки tables. No read is a use case; no query returns an
  entity. Queries are a table, not a code fence.
- Every step names a port method that exists in foundation §4 or an
  entity method that exists in the domain model; every rule is cited by
  id, never restated; the transaction boundary is marked.
- Every error is a name from domain model §3, with a state policy and no
  HTTP status; every external call has a side-effect policy consistent
  with the foundation's transaction-model row.
- Every `operationId` exists in `documentation/api/openapi.yaml`; every
  query names its operation and «Источник строк».
- Every key scenario (≥ 3 ports or external calls, parallel calls, a
  transaction spanning an external call, retries / idempotency, a
  long-running operation) has
  `scenarios/<area>/diagrams/<use-case-kebab>.puml` (PlantUML) and `.svg`, linked by a Markdown link
  `[<use-case-kebab>](diagrams/<use-case-kebab>.svg)` in its
  «Последовательность» row, whose steps match its Шаги table; no plain
  scenario has one, and no `diagrams/` folder is left empty —
  `output-template-scenarios.md`.

## Step-level defects

Each is spelled out where it arises; look for all of them:

- The orchestrator wrote a document, or a writer ran a gate — Orchestrator.
- A name written in the wrong home, or an added name not listed under
  `ALSO CHANGED` — Guardrails, Writer.
- No reader entrance, a lost NFR, a silently resolved ambiguity — Step 1.
- A document written as a diff — Step 1b.
- A label without its limits: writing "Modest" and delivering a Full
  design — Step 2.
- A silent stack; the level or the stack as a heading — Step 2b.
- Ports as a name list, an environment variable without a row, a service
  path without an owner, a route table — mode `foundation`, §4.
- A tree of shapes, `utils/` / `helpers/` / `common/`, or a
  stdlib-colliding name — mode `foundation`, §5.
- Boundaries without a linter, or a lint table that omits a layer or
  binds Host — mode `foundation`, §6.
- A rule in a scenario step, an invariant table outside the domain
  model — modes `domain`, `scenarios`.
- A missing or inventive diagram — `architecture-diagram.md`.

## Banned headings and terms

Examples of the Guardrail «A heading or term outside the template» —
each was rejected in a past document. They illustrate the rule; they are
not the whole list.

- writer scratchpad — «Правила по виду», «DTO или сущность», «Путь
  одного запроса», «Кольцо», `## Сокращения`, a gloss of the
  invariant-table columns, a `from(raw)` definition;
- a decision promoted to a section instead of a «Ключевые решения»
  row — «Решение о глубине», «Решение о стеке»;
- another document's job — an assumptions section (`open-questions.md`),
  «Порядок реализации» (`plan`), a route table (OpenAPI), a table
  catalog (schema), an invariant table outside the domain model, a
  rule restated in a scenario;
- a second table for a fact the foundation §1 already homes —
  «Данные» beside Хранилища, «Каналы», «Ограничения»;
- a second name for one concept — the word «агрегат», or any «агрегат
  = сущность» equation; the documents say «сущность».
