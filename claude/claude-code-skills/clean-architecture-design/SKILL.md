---
name: clean-architecture-design
description: >-
  Writes the architecture as three documents from the settled SRS, schema
  and OpenAPI: a foundation (stack, modules, ports, file tree, lint rules,
  D2 diagrams), a domain model (rich entities and the invariant table that
  homes every rule), and one living scenarios document per functional area
  (use cases, queries, sequence diagrams for key ones). Use after the
  schema and OpenAPI, or for «спроектируй архитектуру», «доменная модель»,
  «сценарии», Clean / hexagonal / DDD layering. Not for inventing tables,
  operations or scope, screens, plan units, or code.
---

# Clean Architecture Design from Requirements

The architecture is three documents under `documentation/architecture/`
(paths below are relative to it). Each has its own mode, its own version
and changelog. They are split by how often they change, so that a new
use case does not reopen the stack and a new rule does not reopen the
file tree. They are split as documents, not as writers: one writer
settles every document a sitting touches, because the three share names
(ports, errors, types) that only stay one name when one head holds them.

| Mode | Document | Owns | Changes when |
|---|---|---|---|
| `foundation` | `architecture.md` + its D2 views in `diagrams/` (`.d2` / `.svg`), each embedded in the section it illustrates | §1 Состав системы (actors, stores, externals, API, security, NFR, «Ключевые решения» with «Уровень» and «Стек») · §2 Модули и функциональные области · §3 Границы и поток данных · §4 Порты и адаптеры · §5 Дерево файлов · §6 Проверки и тесты | a fundamental decision changes: a new port, external system, store, area, transaction model, or stack |
| `domain` | `domain.md` | value objects, entities, named errors, **the invariant table** (the only home of every business rule), boundary checks, what is not an entity, glossary → types | a rule or an entity is added or changed |
| `scenarios:<area>` | `scenarios/<area>/<area>.md` + `scenarios/<area>/diagrams/<use-case-kebab>.puml` / `.svg` (PlantUML) for key scenarios | the area's use cases (input, access, steps → port / entity method, transaction boundary, output, errors, `operationId`) and its queries | a use case of that area is added or changed |

`<area>` is a functional area: a capability group of the SRS (its bold FR
sub-headers), which is also a module of the file tree, in kebab-case
English (`bookings`, `maintenance`). One living document per area,
edited in place; a new area gets a new folder `scenarios/<area>/`.

## Orchestrator (session)

The session writes no architecture document. Same reason `work` writes no
code: the grade is worthless if the chat model does the expensive part.
The dispatched writer settles the sitting's documents and nests
`doc-typist` to print them, including their diagrams. A report whose
`DELEGATED` is not `doc-typist` comes back until it is. The session does not
dispatch the typist.

1. **Gather inputs.** Stop without
   `documentation/requirements/srs/srs.md`; when the product stores
   data, without `documentation/db/schema.md` (name `db-schema-design`);
   when it has HTTP, without `documentation/api/openapi.yaml` (name
   `openapi-spec-generator`). A stop ends with one question: whether to
   run the named stage. Screens are not an input: the architecture
   places use cases, rules and ports, and none of those depends on how a
   screen looks. When any of the three documents already exists, read
   `doc-versioning`, read every existing one and its diagrams (`.d2`,
   `.puml`), and treat this as an increment. If the user edited a `.d2`
   and asked to apply it, follow `references/architecture-diagram.md`
   (diagram → architecture) in the foundation packet. If a `.d2` and its
   document disagree and the user did not say which is newer, ask once.
2. **Pick the modes.** Greenfield runs all three in this stage, in
   order: `foundation` → `domain` → `scenarios:<area>` for every area
   the SRS groups name. An increment picks only the documents what
   changed reaches (the table's «Changes when» column; detail in
   `references/increment.md` → "Which modes run"). Write down which
   documents are untouched and why; that line goes into the report.
3. **Stack.** If the stack is not already a fact, run Step 2b **in this
   chat** before the foundation dispatch: propose cards per
   `references/stack-proposal.md`, wait for the pick. Do not dispatch a
   writer to guess a framework. A named stack is a fact only for the parts
   it names: when the SRS has a human-facing interface and the user named
   only a backend, propose the Frontend card alone. On an increment the
   stack is the «Стек» row of foundation §1.
4. **Level.** Decide the level (Step 2) far enough to grade. The
   foundation writer records it as the «Уровень» row of §1 «Ключевые
   решения»; domain and scenarios writers read it from there.
5. **Dispatch one writer for the sitting.** First create
   `documentation/plans/<version>/progress-architecture.md` per
   `pipeline` → `references/progress-files.md` — one row per document in `MODE`, all `⏳ ждёт` —
   post its link in the chat, and put its path in the packet's
   `PROGRESS FILE`: one dispatch writes every document, and the file is
   where the user sees which one it is on. Each document the session
   inspects or reviews puts the count with the link in the chat. Read `executor-catalog` and
   `executor-catalog/references/design-complexity.md`. Grade each picked
   document by its mode's rules there, and dispatch the highest grade
   once for all of them. Why one: every writer re-reads the SRS, the
   schema and the API, and a writer that never saw the scenarios leaves
   the ports, errors and import rules they need as gaps for another
   round. Fill the packet in
   `executor-catalog/references/design-writer-prompt.md`: `MODE`
   (greenfield or increment, plus the documents in order, e.g.
   `greenfield · foundation, domain, scenarios:top-ups,
   scenarios:refunds`), one `OUTPUT PATH` and `DIAGRAM PATH` per
   document. Before the `Agent` call, write one line per document
   `Document | Grade` and then `Dispatch | Executor | subagent_type`,
   then dispatch without asking which model. Follow the catalog dispatch
   contract: `subagent_type` is the row's name and the call passes no
   `model` (the agent file holds it) unless the user named one. A
   missing agent or a rejected alias is a stop. **Split only for size:**
   a greenfield with more than six areas goes in two dispatches,
   `foundation, domain` and then every `scenarios:<area>`; the second
   reads the first from disk.
6. **Inspect each document** as it lands (its progress row `🔍
   проверка`, then `✅ готово`): the file; for `foundation`,
   each `.d2` in `diagrams/` it requires and its embed in the section;
   for `scenarios`, a `.puml` in the area's `diagrams/` for every
   scenario its «Последовательность» row links. A missing file is an
   incomplete write. When a `.svg` is missing, run the render command in
   `references/architecture-diagram.md` once. Do not edit a `.d2` or a
   `.puml`. A `BLOCKED` / `HARDER_THAN_EXPECTED` return escalates one
   tier per failure (lite → medium → hard); every round goes on while it
   makes progress (`pipeline` → `references/convergence.md`). A document the
   report lists under `ALSO CHANGED` (the writer added a name to it, see
   Writer) joins the documents of this sitting: it is reported as
   changed and goes to the same `doc-review` question.
7. **Close.** Report which documents were written or changed, which
   were untouched and why, and the level. Then ask, per `pipeline` →
   "Asking before a transition": first about `doc-review` on each
   document written or changed in this sitting (one gate question that
   names them; a run reviews each, and each verdict goes into the
   progress file's «Ревью» cell), then the one next stage the
   `pipeline` table names. The writers do not run those. `doc-review`
   edits the body and does not bump. See `doc-versioning`.

## Writer (dispatched)

You settle the documents MODE names, in order: foundation → domain →
each area's scenarios. You do not print them. Settle all of them before
printing any: the scenarios tell you which port methods, named errors
and cross-area types the foundation and the domain model must hold, so
those two are final only after the scenarios are sketched. Then nest
`doc-typist` per `executor-catalog` → Nesting, packet
`executor-catalog/references/doc-typist-prompt.md`, one typist per
document, in parallel; each gets only its document's decisions and
diagrams. A gap this skill calls BLOCKED returns before that dispatch.
Read the files back. One correction dispatch per document, then the
report. Do not type the correction, and do not paste a finished
document into the typist's prompt.

A document outside MODE that lacks a name your documents need — a port
method, a named error and its HTTP row, a config variable, a file line,
an entity method or an invariant row for a rule the SRS states — joins
your sitting: settle the added lines, print it with its own typist, and
list it under `ALSO CHANGED`. A fundamental change it would need (a new
port, external system, store, transaction model, or stack) is not a
name: return `HARDER_THAN_EXPECTED` with it.

You are a software architect turning development requirements into an
architecture an AI coding agent (or a human) can implement without
losing control of the system. The design follows Clean Architecture with
**rich domain models**: business rules live inside entities, use cases
only orchestrate, frameworks stay at the edge, and every boundary is
written down in a form a machine can check.

The deliverable is Markdown (plus D2 and PlantUML diagrams), not code.
Short sketches (signatures, interfaces, a lint rule, a DDL constraint)
are welcome when they make a boundary concrete. Write in Russian; keep
identifiers, paths, and type names in English. Headings are the Russian
ones of the mode's template (`references/output-template-<mode>.md`),
not the English outline of this skill. **There is no length limit**:
these documents are the contract every later stage builds on, so each is
as detailed as the system needs. What keeps them readable is that each
fact has one home (the table below), not a line count.

**What, not how it looks** (`doc-versioning`). None of the three
documents names a widget, a layout, a colour, an icon, or exact UI
wording — not in a row, a note, or prose. A use case is cited by its
action, its data and its outcome.

### One home per fact

| Fact | Home |
|---|---|
| actors, stores, externals, API inputs, security and NFR decisions, level, stack | foundation §1 |
| area → module → SRS group → scenarios document | foundation §2 |
| layer roster, import direction | foundation §3 |
| port signatures, adapters, composition root, configuration, service paths, named error → HTTP, route-guard mechanism | foundation §4 |
| file paths of ports, adapters, mappers, storage models, `bootstrap/` | foundation §5 |
| lint rules, structural tests, test plan | foundation §6 |
| value objects, entities (with their file path), named errors | domain model §1–§3 |
| every domain rule (BR id, owner, method, schema constraint, outcome) | domain model §4 — nowhere else |
| boundary rules (what may cross which boundary) | domain model §5 |
| a use case: input, access policy, steps, transaction, output, errors, `operationId`, its file path | scenarios of its area |
| queries and read-model fields | scenarios of the area that reads |
| methods, paths, success codes, bodies | `documentation/api/openapi.yaml` — never here |
| tables, columns, constraints | `documentation/db/schema.md` and its migrations — never here |

A fact written in two homes drifts, and the reader must guess which copy
is the contract. A later document cites an earlier one by name (rule id,
NFR id, port method, error name, section), never by restating it — not
even a value: «до 4 ч» in a test plan or a purge step is a second copy
of BR-3. A type two areas use (a result, an id, a read model) is defined
once, in the area or document that owns it, and cited with the same
name and shape everywhere else. A fact the earlier document lacks is
added there, in its home (Writer → `ALSO CHANGED`), never written here.

## Why this shape

AI generates code that works today but cannot evolve: rules end up
scattered across services, controllers, and helpers, and the next
generation has to reassemble the domain from ten files before it can
change one rule. A rich entity puts the rule where the model expects
it — one file, full picture. A use case is a stable unit of work ("build
the Refund use case") that keeps the model inside orchestration instead
of inventing rules. Because an agent copies whatever pattern it finds in
the repo, a boundary that exists only in prose is not a boundary — a
linter or a structural test enforces it. Design for the reader with the
smallest context window: meaningful paths, small files, named types —
and small documents: an agent building one use case opens one scenarios
document and the domain model, not the whole architecture.

## Shared steps (every mode)

### Step 1. Digest the requirements

**The schema and OpenAPI already exist** when the product stores data or
has HTTP. The schema (`documentation/db/schema.md`, migrations in
`documentation/db/migrations/`) says which constraints SQL already
enforces; OpenAPI says the `operationId`s and declared error codes. Read
them. Do not invent a table, a column, or an operation. A use case whose
operation is missing is a gap to send back to `openapi-spec-generator`,
not a route this document adds.

Extract from the inputs, and put each into its home:

| Extract | Becomes |
|---------|---------|
| Actors and roles | foundation §1 Акторы; access policy per operation in the scenario's «Доступ» row; a domain role rule in the domain model |
| User actions | one use case per action that changes state, in the scenarios of its area; reads are queries |
| SRS capability groups | areas: foundation §2 rows, one scenarios document each |
| Business rules and invariants | entity / value-object behavior and an invariant row (domain model) |
| States and lifecycle | which method may set which status (domain model §2). The closed list of codes is a schema column's allowed values |
| External systems | gateway ports + adapters (foundation §4); side-effect policy in the scenario's Ошибки. Partners we do not own — not our Postgres or object store |
| Data that must survive restarts | named stores in foundation §1 Хранилища (postgres / S3 / files — **not** tables); repository ports follow |
| Delivery channels (REST, GraphQL, CLI, queue, cron) | foundation §1 API rows; controllers / handlers in adapters |
| Security NFRs | foundation §1 Решения по безопасности |
| Other NFRs: performance, reliability, scalability, observability | foundation §1 Решения по NFR |
| Constraints: versioned API, sensitive data, several clients, team size, lifespan, hosting limits, existing repo | scope (Step 2), stack proposal (Step 2b), DTO decision (foundation «Ключевые решения») |
| Anything you had to assume | `documentation/architecture/open-questions.md` (shared by the three documents), and tagged `(A-n)` rows wherever it matters |

Sort every extracted rule into one of four kinds **while writing**. The
kind decides its home. The sort is a writer's scratchpad; the reader
sees only the result.

| Kind | Test | Home |
|---|---|---|
| **Domain rule** | Would a clerk with a paper ledger and a rulebook check it? Limits, thresholds, eligibility, consequences, what a state permits, **who may complete a named transition** (override, lift, sign-off) | entity or value object; one invariant row. A named-transition role arrives as a typed actor; the entity decides whether that kind of actor may complete it |
| **Application flow** | Is it about the order of steps in *this* app rather than about what is allowed? | scenario steps |
| **Access policy** | Who may *invoke this endpoint or job at all*? | the scenario's «Доступ» row (with its BR id); the guard mechanism is foundation §4. A check that needs the loaded record (ownership) → step 1 of the use case. Tenancy → the ports. Never inside the entity |
| **Boundary rule** | Is it about which data may cross which boundary? | a read model / payload type per audience that has no such member, plus a structural test; a row of domain model §5, not the invariant table |

A typed actor on a transition and a guard on the same role are **two
questions, not duplication**: the guard stops an unsigned caller; the
entity stops an illegal transition even if a job or another adapter
calls it. Do not invent requirements. When a rule is ambiguous, pick the
reading that keeps the domain simplest, tag it as an assumption, and
list the question. Open questions are closed before publish; a published
document does not explain `OQ-N` / grill links.

### Step 1b. When the documents already exist — increment, do not restart

A feature added to a designed system runs the same modes, but each
output is the same document, edited in place, not a second file and not
a new version number: the stamping commit (`doc-versioning`) writes the
version and the typed rows. Read `references/increment.md` before
editing. Every version is still the whole document (no "как в 1.1.0", no
"без изменений"): downstream stages pin these files as `path@<version>`,
so a diff-only version leaves them reading half a design.

### Step 2. Decide how much architecture is justified

Read `references/architecture-level.md`: the levels (Framework-first,
Modest, Full), the triggers for each, and how the level is recorded.

### Step 2b. Propose the stack — then write only what the user picked

The tree, wiring and linter are stack-shaped, so the stack is never a
silent default. A fact (a manifest, or named by the user / SRS) or the
pick from INPUTS goes into §1 Стек with majors and the «Стек» row; the
tree and the lint table match it. A missing part (backend or client) →
`STATUS BLOCKED`: the orchestrator proposes cards (`references/stack-proposal.md`).

## Mode `foundation`

Template and per-section notes: `references/output-template-foundation.md`
— read it before writing or editing the file.

**The client is part of the system.** When the SRS has a human-facing
interface, the foundation places it like any other container: its stack
in §1, its module in §2, its folder, generated API client and layout (the
`frontend` skill's profile for the stack) in §5, its lint rules and test
rows in §6. Screens are not needed for that — the structure does not
depend on how a screen looks. «Клиент вне документа» leaves `plan` with
screens and nowhere to put them.

- **§1 Состав системы is tables, one fact per row.** «Решения по
  безопасности» (always — eleven sub-items) and «Решения по NFR»:
  `references/nfr-decisions.md`. «Ключевые решения» opens with
  «Уровень» and «Стек». Why: `plan`, `code-review-full`, and later
  increments each read one row here, so a fact left in prose reaches
  nobody. After the H1 comes `## Описание системы` (one or two
  sentences: what the system is, who writes and who reads, what is out
  of scope), then `## Журнал изменений`.
- **§2 Модули и функциональные области** — one row per area, always:
  area, module folder, SRS group, scenarios document path, which
  entities own its state, what it takes from other areas (types, ports,
  use cases — by name), who consumes its contract. A cross-area import or
  call is allowed only when this table names it, and §6 turns each named
  one into an allowed lint row. Fill this column from the sketched
  scenarios and entity signatures, not from guesswork. A shared module
  takes nothing from an area: a type its methods accept lives in it or
  in `shared/domain`, or the dependency points the wrong way.
- **§3 Границы и поток данных** — the layer roster first (shape:
  `references/use-cases-and-boundaries.md` → layer roster), artifacts as
  counts and pointers, never names; then who imports whom.
- **§4 Порты и адаптеры**, in this order: port signatures (a type the
  signature names is defined here unless the domain model defines it;
  with several tenants every port method over tenant-owned rows takes
  `TenantId` first and its adapter filters by it — row-level security is
  the second line, not the only one); Port → Adapter table (**one
  hand-written source per shape**: wire types generated from
  `documentation/api/openapi.yaml`, storage records inferred from the ORM's table
  definitions; name the tool and check its current usage against the
  installed version with Context7; the mapper is hand-written and pinned
  by a round-trip test); external-call failure; file formats; Сборка
  (wiring per framework: `references/layers-and-dependency-rule.md`);
  Конфигурация; Служебные каналы; named error → HTTP with the route-guard
  paragraph (`references/configuration-and-http.md`). No route
  inventory — OpenAPI owns it; no schema design — the schema document
  owns it.
- **§5 Дерево файлов** — concrete names, area-first then layer:
  `domain/` · `application/` · `adapters/` · `bootstrap/`. Real file
  names for what this document owns (ports, adapters, mappers, storage
  models, `bootstrap/`); `domain/` and `application/` of each area as a
  folder line pointing at the document that names their files. No `…`,
  no `<entity>.<ext>`, no `adapters/a|b|c/`, no `utils/` / `helpers/` /
  `common/`, no folder that collides with the stack's standard library.
  Why: the path is the first thing an agent reads, and `repo-scaffold`
  creates exactly this tree. Layout sketch:
  `references/machine-checkable-boundaries.md` → File layout.
- **§6 Проверки и тесты** — name the enforcer (TS → dependency-cruiser;
  Python → import-linter; Java → ArchUnit; C# → NetArchTest + csproj; Go
  → go-arch-lint) and its rules as a table (from → must not import)
  covering every production layer of §5. Not the config file:
  `repo-scaffold` writes it from these rows, and a pasted config is a
  second copy that drifts. Host/bootstrap is exempt from inward-only.
  With two or more areas, also forbid cycles and every cross-area import
  except the ones §2 names. The test plan is one row per test file or
  per layer group, citing rule ids, never their values:
  one entity test per invariant row of the domain model, use-case tests
  with in-memory fakes, one round-trip test per mapper, one cross-tenant
  adapter test when there are several tenants, one automated end-to-end
  path. Configs and shapes: `references/machine-checkable-boundaries.md`.
- **Diagrams** — D2 views in `diagrams/`, each embedded in the section
  it illustrates (`references/architecture-diagram.md`): Контекст and
  Контейнеры (processes on the network, not layers; a sentence instead
  for a single process) in §1, Хранилища и интеграции under §1
  «Хранилища», Модули in §2 (a sentence instead for one area), Слои in
  §3. No index file, no ER, no entity catalog.

On greenfield the foundation comes first, so it names ports, port
methods and named errors from the SRS, the schema and the OpenAPI
declared errors; the domain and scenarios writers then use exactly those
names, and report a gap when one is missing.

## Mode `domain`

Template: `references/output-template-domain.md`. How to design an
entity, row shapes, value objects: `references/rich-entities.md`. Read
both before writing. Inputs include the foundation (level, ports, named
errors already mapped to HTTP).

- **Entities** — `### <Name> (сущность) — \`<root>/<area>/domain/<file>.<ext>\``, a
  one-line «что это», then a sketch whose methods are named after the
  requirement's verbs and refuse what the rules forbid. Never a status
  setter. Under each sketch one line `Поля также в:` listing every other
  place that repeats its fields — storage model, mapper, read models,
  wire schema — by path, each derived one marked `(генерируется)`. It is
  the list an agent edits when a field changes; a place missing from it
  is where a stale field survives.
- **Invariant table (§4)** — domain rules only, one row per rule, no
  prose in the cells, no paragraph under the heading: `Правило |
  Владелец | Где проверяется | Ограничение в схеме | Исход`. «Правило»
  starts with the SRS id. «Где проверяется» is always an entity or
  value-object method with the same signature as in the sketch — never a
  use case, controller, adapter, `Clock`, or the word `database`.
  «Ограничение в схеме» copies the schema document (`CHECK` / `UNIQUE` /
  `FK`, or `none` when it left the rule to the entity); do not add a
  constraint the schema lacks. Why: tests are written from «Где
  проверяется» and the schema is checked against «Ограничение в схеме»,
  so each rule needs exactly one owner and one row. Immutability and
  at-most-once rules are rows too.
- **Every `BR-n`** of the SRS lands in exactly one place, id first: an
  invariant row, a boundary-checks row (§5), or the «Доступ» row of the
  scenario that guards it (access policy). A BR left only in prose is
  lost to the tests.
- **Named errors (§3)** — every name a scenario may return, including
  application errors such as `…NotFound` and `Forbidden`, with who raises
  it. No HTTP status here; every name has its row in foundation §4.
- Calendar math lives on a value object; `Clock` only supplies `Now` and
  zone. Entity headings say «сущность», never «агрегат».

## Mode `scenarios:<area>`

Template: `references/output-template-scenarios.md`. Why use cases and
queries take this shape, side effects, idempotency, typed boundaries:
`references/use-cases-and-boundaries.md`. Inputs include the foundation
and the domain model; this document cites both and restates neither.

- **One use case per state-changing action** — the unit an agent is
  asked to build, so it is complete on its own. Heading
  `### <UseCaseName> — \`<root>/<area>/application/<file>.<ext>\`` with
  the stack's real path and extension. Tables: Вход / Доступ / Выход /
  Операция API · Шаги (шаг → порт или метод сущности, the transaction
  boundary marked) · Ошибки. More than four use cases → an index table
  first.
- **The use case orchestrates; it owns no rule.** A step that asks the
  entity cites the invariant row by its rule id (`BR-3`); the rule's
  words stay in the domain model. Errors are names from domain model §3,
  never redefined, with no HTTP status. Port methods are names; their
  signatures stay in foundation §4.
- **Side-effect policy** ("must" → outbox in the same transaction, or
  in-request) lives in Ошибки, consistent with the foundation's
  transaction-model row in «Ключевые решения».
- **Queries** — reads are not use cases and never return the entity. A
  table: Запрос · Сигнатура · Модель · Операция API · Источник строк,
  then each read model's fields once.
- **Key scenarios** — three or more ports or external calls, parallel
  calls, a transaction spanning an external call, retries or
  idempotency, a long-running operation — also get a PlantUML sequence
  diagram `scenarios/<area>/diagrams/<use-case-kebab>.puml` + `.svg`,
  linked from the use case's «Последовательность» row as a Markdown
  link, `[<use-case-kebab>](diagrams/<use-case-kebab>.svg)`. Plain
  read-and-return or load-ask-save scenarios get none. Shape:
  `references/architecture-diagram.md` → Sequence view.

## Guardrails

- **A heading or term outside the template.** Each document uses only
  the headings of its template. Anything else is either the writer's
  working or a second copy of a fact another place owns. The user
  rejected past documents for such headings and terms, so they stay
  banned; the remembered examples are in `references/final-check.md` →
  Banned headings and terms.
- **Anemic entity + fat service.** A `…Service` holds the rules while the
  entity holds fields. Move the behavior into the entity.
- **Rules inside use cases.** A threshold, state, or count comparison in
  a scenario step. Push it down; pass the missing fact in as a type.
- **Consequences modeled as exceptions.** When the business has a word
  for the outcome, it is a state transition with a side effect, not an
  error.
- **ORM class as the entity, framework in the core, `save()` on the
  entity.** Storage models live in adapters and are mapped explicitly.
- **Ceremony by reflex.** `UnitOfWork`, `Clock`, `IdGenerator`, a use
  case per read, seven lint layers for a CRUD, DTO or entity by habit —
  each needs a named reason (a test, a rule, a risk) in «Ключевые
  решения».
- **Invented model.** A noun with no stated rule promoted to an entity,
  or a status the requirements never named (tag it `(A-n)` and ask).
- **A name written in the wrong home.** A missing port method, error or
  file line goes into the document that owns it (Writer → `ALSO
  CHANGED`), not into the scenario that needed it.

## Before you finish

Run every Guardrail above as a check, then confirm the items of your
mode in `references/final-check.md` — the one checklist for this skill.

## References

Read each file at the step named; skip the rest.

- `references/output-template-foundation.md` — foundation template, §1 table rules, «Ключевые решения». Mode `foundation`, before writing or editing.
- `references/output-template-domain.md` — domain model template, invariant-table column rules, where each BR lands. Mode `domain`, before writing or editing.
- `references/output-template-scenarios.md` — scenarios template, per-section rules, what makes a scenario key. Mode `scenarios`, before writing or editing.
- `references/final-check.md` — the final checklist, by mode. Before you finish.
- `references/increment.md` — which modes run and what changes when the documents exist (orchestrator step 2, Step 1b).
- `references/nfr-decisions.md` — the eleven security sub-items; «Решения по NFR» (foundation §1).
- `references/stack-proposal.md` — constraints, cards, chat prompt, after the pick (Step 2b).
- `references/rich-entities.md` — entity vs ORM model, invariants, value objects, when anemic is fine (mode `domain`).
- `references/use-cases-and-boundaries.md` — why use cases orchestrate, queries, side effects, typed boundaries, layer roster (mode `scenarios`; foundation §3).
- `references/layers-and-dependency-rule.md` — four layers, placement, composition-root wiring per framework (foundation §4 Сборка).
- `references/configuration-and-http.md` — Конфигурация, Служебные каналы, named error → HTTP (foundation §4).
- `references/machine-checkable-boundaries.md` — lint configs per stack, structural tests, test plan, file layout, the modules table (foundation §2, §5, §6).
- `references/architecture-diagram.md` — paths, D2 views and where each is embedded, the PlantUML sequence view for key scenarios, render commands, document ↔ diagram sync (whenever a `.d2` or `.puml` is written or changed).
- `references/architecture-diagram.example.md` — foundation sections with their views embedded and the skip sentences (when unsure where a view goes).
- `pipeline` (skill) — the **orchestrator** reads it at the close. The writers do not.
