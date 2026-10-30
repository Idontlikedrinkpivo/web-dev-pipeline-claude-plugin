---
name: plan
description: >-
  Turns design documents or existing code into the implementation plan: one-commit units, each with a grade and an
  executor; or a fix plan from a test or audit report. Use for «составь план», «разбей на задачи», «план исправлений»,
  «исправь дефекты по отчёту».
---

# Implementation Plan with Executor Routing

Design documents say **what** and **how it is shaped**. This plan says **in
what order it gets built, in what commits, and by whom**. Its one distinctive
job: every unit carries a complexity grade and a named executor, so a rename
is told to apply a shape and a state machine is told to design the missing
part — and each gets the review roster that grade names.

This skill decides nothing the design already decided. It cites. Write the
plan in Russian. Do not translate U-ids, file paths, or executor names.
Template headings stay as this skill specifies.

## Not this skill's job

| Not here | Owner |
|---|---|
| Product behavior, actors, acceptance criteria | `srs-writer` |
| Stack, layers, ports · rules · use-case flow | `clean-architecture-design` (foundation · domain model · scenarios) |
| Endpoint contracts · table shapes · screen behaviour | `openapi-spec-generator` · `db-schema-design` · `screen-spec` |
| Look of a screen | the Figma frame cited by `fileKey` / `nodeId` in the screen spec. A screen unit cites that id and does not restyle the product; a new look arrives only as the theme unit after a `ui-design` restyle |
| Directory tree, lint config, composition root | `repo-scaffold` |
| Compose topology · CI workflow | `deploy-topology` · `ci-pipeline` |
| Document `version` fields and changelog rows | `doc-versioning`, whose stamp is written automatically when a design stage closes; this skill does not call it. The service version is read from the open folder and its level re-checked here, per `pipeline` → Service version |
| Writing code, running tests, committing code | `work` |

If a design gap surfaces while planning, it goes to this plan's **Open
questions** file beside the plan, `open-questions.md`. Never close a design
gap by guessing inside a unit, and never add an open-questions section to the
plan. A finding the user asked to defer after review goes in that same file.
A gap the user settles instead — or a decision the user changes while the
plan is written or reviewed — goes into the design document first,
committed with no version change, and the plan is written or revised
against the fixed text (`pipeline` → `references/decision-changes.md`).

## Modes

| MODE | When | The writer |
|---|---|---|
| `greenfield` | the product's first plan: the code is what `repo-scaffold` made | slices everything the documents hold |
| `increment` | a version over code that runs — its documents changed; also a brownfield repo whose code is the design (no documents) | slices only what this version added or changed, against the inventory of the code it reaches |
| `fix` | a UI acceptance run returned `DEFECTS`, a security audit `FIX`, or a code audit's rows: the report rows the user chose to fix | appends fix units to this version's `plan.md`, no bump unit; a code audit's fix plan is born in its own iteration, with one |
| `revise` | `plan-review` returned `FIX_THEN_PROCEED` or `RETURN_TO_PLAN` | settles the blocking findings only |

What each mode changes — scope, inventory, citations, coverage:
`references/modes.md`. The writer reads its MODE's section before Step 1.

## Inputs

| Input (path under `documentation/`) | Required | Read for |
|---|---|---|
| Architecture foundation `architecture/architecture.md` | **yes** | stack (§1), «Решения по NFR» (§1 — each row is applied by some unit), modules and areas (§2), ports and adapters and the configuration table (§4 — each variable is read and used by some unit), file tree (§5), lint and test plan (§6) |
| Domain model `architecture/domain.md` | **yes** | entities, value objects, named errors, the invariant table (§4) — every rule a unit enforces is cited from here |
| Scenarios of the areas in scope `architecture/scenarios/<area>/<group>.md` | **yes** | one unit per state-changing scenario; its steps, ports, transaction boundary and errors |
| SRS `requirements/srs/srs.md` and every `areas/*.md` | **yes** | UC / AC / BR / NFR ids the units must cite |
| OpenAPI `api/openapi.yaml` with `paths/` and `components/` | when the surface is HTTP | one unit per operation group; `operationId` names the unit |
| DB schema `db/schema.md` + `db/migrations/` | when there is storage | migration units and their ordering: a schema change in scope is a unit that adds the next numbered file `db-schema-design` wrote to the app's migration run — never an edit of a committed file |
| Screen specs `ui/screen-specs/` (+ `ui/frames-register.md`) | when there are screens | one unit per screen (a large screen: one per part, see Screen below): its elements, states, response outcomes and the Figma `nodeId` the unit cites; after a restyle, the register's «Визуальное направление» line and the `🎨 Tokens` page for the theme unit |
| A report — `plans/<version>/test-run.md` (`DEFECTS`), `security-audit.md` (`FIX`) or `plans/code-audit-<date>.md` | `MODE fix` | the rows the user chose to fix, by id (`TC-n`, `F<n>`, `A<n>`) |
| Scaffold state (the repo itself) | always | what already exists — never plan a unit that recreates it |

`docs-consistency.md` in the version folder is read for its first line and its
`checked:` hashes. Missing, not `Verdict: PASS`, or a hash that no longer
matches its file: say in the opening that the document set was not checked
as a whole since its last change, and ask about `docs-consistency` before
planning, per `pipeline`. A declined check is not a stop; name it in the
plan's §1 digest.

**Missing a required input: stop and say which one.** A plan built on a
guessed architecture routes work confidently in the wrong direction, which is
worse than no plan. The one exception is a repo whose code *is* the design
(brownfield, no docs, `MODE increment`): then the code stands in for the
docs — inventoried by `code-explorer` in the orchestrator, not read into
this session — and every unit's `Документы` cell reads `code:<path>` so
execution knows the citation is inferred, not specified. A code audit's fix plan
(`MODE fix`, rows `A<n>`) is the same case: its rows, the documents they revised and the code stand in.

## Orchestrator (session)

The session writes no plan file. It grades which writer settles the plan,
asks, and dispatches. It does not slice units.

This skill does not call `doc-versioning`, does not stamp a document, and
does not commit documentation. Pin `sources:` to the version already
written in each source file.

1. Stop when a greenfield or increment plan has no architecture
   foundation, domain model, or scenarios document for an area in scope.
   Brownfield with no docs is allowed. Pick MODE (Modes). Read the inputs
   far enough to run the grade below: level, risk, and the counts in the
   cascade. Do not slice.
2. **Read the iteration's version** from the open
   `documentation/plans/<version>/` (no `summary.md`), or from the
   iteration branch `where_am_i.py` names when the folder is not here (a
   fresh clone: `open_iteration.py <version>` only creates it). None open —
   fix the number per `pipeline` → Service version and open it:
   `python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/open_iteration.py" <version>`.
   Then **re-check the level** against the iteration's typed changes: the
   rows of this version, plus unstamped changes typed from the diff since
   the last tag. A changed level is asked again. VERSION in the packet:
   number, level, reason; MANIFEST: the manifest's current `version`.
3. **Plugin code changes waiting** (greenfield, increment, and a code audit's fix plan — the first plan of its iteration):
   `python3 "${CLAUDE_SKILL_DIR}/../upgrade-docs/scripts/project_format.py" list . --kind code`.
   A change `upgrade-code` left for «the first unit of the next iteration»
   is lost unless this plan carries it. When the list is not empty, ask
   one question (`pipeline/references/question-format.md`): put them into
   this plan as its first units, or leave them for `upgrade-code`. A yes
   fills DEFERRED in the packet — id, title and `fix` of each.
4. **Increment, brownfield and a code audit's fix: the inventory.** Resolve the
   `code-explorer` row and dispatch it under `executor-catalog` → Dispatch
   contract. Read that section's bullets and stop before its example. Ask
   for: the entry points; the files that implement each id this version
   adds or changes; the patterns a new unit would mirror; the storage
   access shape; the test conventions; and every use — code, tests, e2e,
   CI, documents — of each symbol a change removes or renames. Take back
   paths and shapes only; they go into INVENTORY.
5. Read `executor-catalog` and
   `executor-catalog/references/plan-complexity.md`. The cascade there
   grades the plan, not a unit (`fix`: Grading a fix plan; `revise`:
   Grading a revise). Before the `Agent` call, write
   `Grade | Executor | subagent_type` for the `plan-writer` row the
   grade picked (`plan-lite`, `plan-medium`, or `plan-hard`), and dispatch
   it without asking which model, with `executor-catalog/references/plan-writer-prompt.md`
   as `subagent_type: "dev-pipeline:<row>"` with no `model` — the agent file holds
   it; pass `model` only for an explicit user model pick. A missing
   agent is a stop per the Dispatch contract, a rejected alias per Slug
   hygiene. Do not write the plan on the session model. Do not dispatch
   `doc-typist`.
6. Inspect the file. A model slug in the body, an `Исполнитель` outside
   `assignable-implementers.md`, or a report whose `DELEGATED` is not
   `doc-typist` comes back, until it is right. A `BLOCKED` with a
   question for the user is asked and sent back to the same row; any
   other `BLOCKED` / `HARDER_THAN_EXPECTED` escalates one tier per failure
   (lite → medium → hard), and that dispatch asks again; the rounds go on
   while each makes progress (`pipeline` → `references/convergence.md`).
7. Report the plan path and the writer's counts. Then run `plan-review` at
   once, without asking — on `fix`, over the appended units (the report's
   NEW UNITS): every product decision is already settled in the documents, so what the review finds is the pipeline's own work to fix (`pipeline` → `references/gates.md`).
   It returns without asking the next stage. Branch on its verdict:
   - `FIX_THEN_PROCEED` or `RETURN_TO_PLAN` — grade the revise on its
     own, not by the plan (`plan-complexity.md` → Grading a revise: the
     «Вид правки» of the blocking rows). Before the `Agent` call write
     `Revise grade | Executor | subagent_type`. Dispatch that `plan-*`
     row with MODE `revise`, the revise grade in COMPLEXITY, and the
     blocking row numbers in FINDINGS, then re-run `plan-review` over
     the changed units only. Revise and re-review repeat until the verdict
     passes, while each round makes progress; when progress stops, take it to
     the user (`pipeline` → `references/convergence.md`).
   - `STOP` — stop and take it to the user. The user's answer is a changed
     decision: it lands in its document (`pipeline` →
     `references/decision-changes.md`) before the revise round that follows.
   - `PASS` — only then ask, per `pipeline` → "Asking before a
     transition", about the stage the table names after this one. Do not
     name a next step from memory. A row of `open-questions.md` classed
     `Блокирует старт` goes into that question, each with the units it
     holds: `work` cannot start them until the user answers.

## Writer (dispatched)

You settle the plan. You do not print it. When every unit decision the
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. Read
the file back. One correction dispatch, then the report. Do not type the
correction, and do not paste the finished plan into the typist's prompt.
Do not run `plan-review` or `pipeline`.

Pin `sources:` to the version already written in each source file. Do
not call `doc-versioning`. Read your MODE's section of
`references/modes.md` first.

### Step 1. Digest the inputs into a routing table

Before slicing anything, extract only what changes unit boundaries:

- Architecture **level** (Framework-first / Modest / Full) — it sets how many
  artifacts a unit may touch and whether ports are their own units.
- The **file layout** tree — units are named by the files they own.
- The **invariant table** — each quoted row is a test scenario somewhere, and
  the rows an entity owns pull that entity's unit up in complexity.
- The **use case list** — the default unit spine.
- **Existing code** — what the scaffold already produced.

State the digest in three or four lines in the plan's §1, after the line
the packet's VERSION gives: `Версия 1.3.0 · MINOR — добавляет UC-5, UC-6;
ломает BR-3`. When the version holds several unrelated changes,
§1 lists them one line each and §3 keeps each change's units together. Do
not re-paste the architecture.

**The inventory is in the packet** (increment): paths and shapes only.
Do not dispatch `code-explorer` and do not read the repo unit by unit; the
one search allowed is for the uses of a symbol a unit changes
(`references/modes.md` → increment). An increment packet with no
inventory is `STATUS BLOCKED`. A greenfield packet says `none`.

### Step 2. Slice into atomic units

A unit is **one commit**: it lands green, alone, without a sibling unit's
work. That is the whole test — not size, not time.

Slice along the architecture's own seams:

| Seam | Unit shape |
|---|---|
| Shared domain type (id, money, span) | one unit per type cluster used by ≥2 aggregates |
| Entity / value object | one unit per aggregate root and its invariants |
| Use case | one unit per state-changing action, with its ports declared |
| Port implementation | one unit per adapter (repository, gateway, outbox) |
| Query / read model | one unit per audience-shaped read |
| HTTP surface | one unit per operation group sharing a controller |
| Migration | one unit per new file in `documentation/db/migrations/`, ordered before its adapter |
| Screen | one unit per screen with all its states, citing its screen spec and the `nodeId`. A screen of more than ~40 elements, or a spec over ~100 KB, is split by its parts — a form, a block, a dialog, a panel, as the annotation groups them: each unit cites `S-<n> эл. <from>–<to>` with the states and response errors those elements show; the first sets up the screen (route, data hook, layout) and the rest depend on it in order; together they cover every element once, and the last runs the whole screen's check |
| Theme (after a `ui-design` restyle) | one unit: the project's theme file — colours light and dark, radius, shadows, density, fonts with their Cyrillic subset — from the Figma variables, and the values screens hardcode moved into it; `Документы` cite the register's «Визуальное направление» line and the `🎨 Tokens` `nodeId`; `impl-ui`; screen units that fix the look depend on it |
| Mechanical batch | one unit for a repo-wide rename, codemod, or config sweep |
| Plugin code change (DEFERRED in the packet) | one unit per change, first in the plan: its `fix` is the approach, `Документы` cite `plugin change <id>`; graded by the cascade |
| Version bump | only when MANIFEST differs from VERSION (a new repo's scaffold already wrote it; a `fix` appended to a plan that ran never adds one): the last unit, sets the manifest's `version` to VERSION; grade 0, `mechanical-worker`, `Зависит от` every other unit |

Split a unit when it crosses a ring (domain **and** adapter), when it mixes a
decision with mechanics, when two halves would land in separate commits
anyway, or when its `Файлы` pass ~8 files of different kinds (a mechanical
sweep of one shape is exempt) — an executor's context grows with its footprint. Merge two units when neither can land green alone.

Never produce: a 5-minute micro-step, a unit spanning unrelated concerns, a
layer batch ("all entities", "all adapters", "wire everything" — it cannot
land as one reviewable green commit), a unit so vague the executor has to
re-derive the design.

**A path this version retired** (increment) — an id this iteration
deprecated or removed whose code is still in the repo — gets one unit
that removes the old path and proves the replacement covers it, or names
one of three exceptions: `references/modes.md` → A path this version
retired.

### Step 3. Order and mark parallelism

Order by dependency, not by layer aesthetics: a unit ships only after every
unit it imports from. Two units are **parallel-safe** only when their `Файлы`
sets are disjoint *and* they share no type, migration, registry, config,
generated client, lockfile, or runtime resource their tests need (a local
database, a port, a dev server, a package install). Declared file
disjointness is necessary and not sufficient — an unmarked shared contract is
what turns a parallel wave into a merge fight, and two workers running
integration tests against one local database corrupt each other even in
isolated worktrees. Default to `no` under any doubt. **UI units are always
`Параллельно: no`** and run one after another: the first one (in plan
order) carries the API client generation and the app-wide error handler in
its `Файлы`; later screens depend on it and only use them.

Among units that are equally ready, order first the one that completes the
earliest use case's path end-to-end. A run stopped mid-way then leaves a
working slice rather than one layer of everything.

### Step 4. Fill each unit

`U-IDs` are stable: `U1`, `U2`, … Assigned once, never renumbered. Splitting
keeps the original id on the original concept and gives the new part the next
unused number. Deletion leaves a gap; gaps are fine.

```markdown
### U<n>. <что делает юнит, глаголом>

| | |
|---|---|
| **Документы** | scenarios/orders/01-orders.md `<UseCase>` · domain §4 <rule row> · SRS UC-2 / AC-Exc-1 · BR-3 · api `createOrder` (fix: + `test-run.md TC-n` / `security-audit.md F<n>` / `code-audit-<date>.md A<n>`; brownfield: `code:<path>`) |
| **Файлы** | repo-relative paths, including the test file — the five cases of `references/files-field.md` |
| **Меняет символы** | each field, constant, environment variable, response shape or public symbol the unit removes or changes — or `—` |
| **Не затрагивается** | each use of those symbols the unit leaves as it is, with the reason — or `—`. With «Меняет символы» filled, search the repository for every use (code, tests, e2e, CI, documents): each hit is in `Файлы` or here |
| **Образец** | repo-relative path(s) whose conventions this unit mirrors (`path (U<n>)` when a unit in `Зависит от` creates it, or the arch section that fixes the shape), or `— first of its kind` |
| **Зависит от** | U-ids, or `—` |
| **Параллельно** | yes / no — and with what it contends when no |
| **Сложность** | 0 / Low / Mid / High |
| **Почему** | the one signal that set the grade (see `references/complexity.md`) |
| **Исполнитель** | executor name from `executor-catalog` |
| **Вложенный** | executor name, or `—` |
| **Что делает вложенный** | the mechanics to delegate, or `—` |

**Цель** — one sentence: what is true after this commit. A new path says
what exists that did not before. A retired path says the old path is gone
and what covers it.

**Подход** — the decisions already made, cited not restated: which entity
method the use case calls, which port signature the adapter implements, which
error maps to which status. No code, no imports, no signatures invented here.

**Тестовые сценарии** — an invariant row over many values (a format, a range, a round trip, a rule two layers
must agree on) gets a property scenario («для любых … верно …») beside its examples. One per line, each naming input, action, expected
outcome. Cover every invariant row this unit enforces (`covers BR-3`), the
AC of each flow it serves, its error paths, and its boundary crossings.
A unit with no behavior writes `none — <reason>` instead. A unit that splits, moves or renames code «без
изменения поведения» first pins what the code does now — a characterization scenario that stays green. Mutation runs are `work`'s close, not units; a
unit that raises mutation coverage on purpose names its line ranges and a time budget (`work/references/health.md`).

**Проверка** — the observable outcome that proves the unit done, as an
outcome, not a shell recipe.

**Коммит** — the conventional message this unit lands under.
```

A filled unit, for calibration — match its density, not its domain:
`references/unit-example.md`.

Every behavior-bearing unit names its test file in `Файлы`. A unit with a
blank `Тестовые сценарии` and real behavior is an unfinished unit, not a fast one.

`Образец` is the evidence for complexity signal 4: a path means precedent
exists, and it has to exist in the tree or be created by an earlier unit
reachable via `Зависит от` (write `path (U<n>)`); an architecture section
whose file tree / snippet fixes the shape counts too. `— first of its kind`
puts signal 4 at the expensive end, and the anti-deflation gate keeps the unit
at Mid or above unless the mechanical gate graded it 0. `work` pastes this field into the worker's `PATTERN TO
MIRROR` verbatim, so a pattern left out here gets picked at execution time
with nobody reviewing it. In an increment, take the paths from the
inventory. `work` likewise passes «Меняет символы» and «Не затрагивается»
to the worker, which then knows what it must leave alone.

**Write each scenario so its test can be written before the code.** `work`
executes units test-first: the scenarios are what the implementer turns into
failing tests before touching the implementation, so an expected outcome that
can only be filled in after reading the code has not been specified. Take the
expected value from the design — the invariant row, the error-to-status
mapping, the column constraint, the AC — and put it in the line. "Rejects an
invalid transition" is not a scenario, and neither is a category list
("happy path, edge cases, errors"); "transition Paid→Draft raises
IllegalTransition, per BR-3" is.

### Step 5. Grade complexity — after the unit is written, never before

Read `references/complexity.md` and run its cascade for each unit. Grade from
the filled fields, because the grade is a property of the work, not of a
vibe: `Файлы` count and ring spread, whether `Подход` still contains a
decision, whether `Образец` names a precedent, whether `Тестовые сценарии` has
error and integration rows, whether `Документы` fully specifies the outcome.

**The risk floor is not the only route to High.** The cascade's compound gate
(rule 2) exists for work that is hard without being dangerous: an open
mechanism, a first-of-its-kind cross-ring shape, an outcome that needs time
control or a second worker to prove. A plan whose only High units touch auth or
money is usually a plan where that gate was skipped, and its hardest unit
got the Mid packet («close local decisions») and one review pass instead
of the High packet («design the missing part») with the adversarial
review and its risk pass — the implementers share a model, the packet and
the review are what the grade buys.

Two rules override everything else in that file:

- **Risk floor.** A unit touching auth, authorization, money, migrations on
  existing data, secrets, or an external contract is never below **Mid** —
  a floor, not a verdict: it is **High** when the decision is open or the
  money or access is decided under concurrency (a row lock, a racing
  idempotency key), and the compound gate still runs after it.
- **Spec floor.** A unit whose `Документы` do not fully determine the outcome is
  never below **Mid**, regardless of how few files it touches — undecided
  work is expensive work.

Put the deciding signal in `Почему` in under twelve words. If `Почему` reads
"seems complex" or restates the goal, the cascade was not run. The same holds
for the plan as a whole: every unit Mid, or every unit High, means Step 5 was
skipped — grades that do not spread defeat the routing.

### Step 6. Assign executors from the assignable list

Read `executor-catalog/references/assignable-implementers.md` only — not the
rest of the catalog. `Исполнитель` is one of `mechanical-worker`, `impl-lite`,
`impl-medium`, `impl-hard`, `impl-ui`. `Вложенный` is `—` or `mechanical-worker`.
Review, plan-review, doc-review, `code-explorer`, and `impl-critical` names
are illegal here. A frontend unit whose `Документы` cite a screen spec and a Figma
`nodeId` is `impl-ui` at every grade, and it does not nest. Never write a
model slug into the plan: the catalog and its agent files own the mapping, so
a model rename touches one agent file instead of every plan ever written.

Fill `Вложенный` only when the unit genuinely contains mechanics separable from
its decision — apply a settled shape across many files, generate fixtures,
port a pattern to N call sites. Then `Что делает вложенный` states exactly that
delegation and, implicitly, that the implementer keeps the decision. A unit
whose whole content is mechanical does not nest; it *is* the mechanical tier.
Nesting is never escalation: more horsepower is a higher `Исполнитель`.

### Step 7. Hand the plan to `doc-typist`

The file lands at `documentation/plans/<version>/plan.md`. Questions go in
`open-questions.md` in the same folder. Repo-relative paths everywhere in the
body — absolute paths do not survive a worktree. You do not write this file.
The settlement is one line per unit field, not the template filled in.
`doc-typist` renders that template.

When the file already exists **for this same version** — a plan you are
revising, or an open version a new change joins — edit it in place: keep the
existing U-ids, append new units with unused numbers, keep a bump unit last
(a fix appends after it: the version is already set),
and update grades only with a reason in `Почему`. The plan carries no progress
state — no checkboxes, no `status:` field. Progress lives in git, and the
`work` skill reads it there.

**A new version gets a new plan folder.** Specs version in place; plans do
not. A plan is a work order for one service version, so it starts a fresh U-id
namespace at U1 and never rewrites a closed version's plan (its folder has
`summary.md`) to describe new work — old plans must stay readable against the
commits that came out of them. See the `doc-versioning` skill for the split.

Pin what the plan was built from as `path@<version>`, the version already
written in each source file — the architecture documents, the scenarios
in scope, the screen specs, the SRS, and the OpenAPI root and the schema
whenever they exist. Do not mint a version to make the pin current. The
pins and the whole document template: `references/plan-template.md`.

If a source's `version` is ahead of what an existing plan pinned and its
rows after the pin hold a «ломает», say so before planning further: the
units may cite decisions that changed. And
if a source document carries a stale banner of its own, do not plan on top of it
silently — name the gap in `open-questions.md` beside the plan.

## Output document template

`references/plan-template.md` → Template: the frontmatter with its pins,
§1 Кратко (on `fix`, one line naming the report rows), §2 Карта юнитов
with the D2 graph at DIAGRAM PATH, §3 Юниты (Step 4 blocks), §4 Волны,
§5 Критерии готовности. No other section.

## Quality gate

1. Every unit lands as one green commit; none crosses a ring without a stated
   reason, none recreates what the scaffold already has — Step 2, Inputs.
2. Every `Документы` citation resolves to a real section or id; no unit invents a
   method, signature, status, or column the design never named — Step 4.
3. Every quoted invariant row and every AC in scope appears in some
   unit's `Тестовые сценарии` — Step 4. Every foundation «Решения по NFR»
   row and every §4 configuration variable in scope belongs to a unit
   that applies it (a body limit set, a pool sized from its variable,
   workers started from theirs) — a decision that only lives in the
   document is not built. In scope: everything on greenfield; on an
   increment, the ids this version added or changed; on fix, the report
   rows (`references/modes.md`).
4. Every unit has `Сложность`, a one-signal `Почему`, and an assignable
   `Исполнитель` — Steps 5–6.
5. Risk floor and spec floor hold — Step 5.
6. Grades spread across at least two tiers, unless the plan is honestly one
   kind of work and says so — Step 5.
7. `Зависит от` is a DAG; every `Параллельно: yes` pair is disjoint in
   files, contracts, *and* runtime resources — Step 3.
8. Every `Образец` path exists or is created by a unit in its `Зависит от`
   chain; a `— first of its kind` unit is graded as `references/complexity.md`
   → Anti-deflation gates says — Step 4.
9. U-ids unique and never renumbered; no model slug and no progress state in
   the body — Steps 4, 6, 7.
10. Rows in `open-questions.md` block named units instead of being absorbed as guesses.
11. Every id this version retired has a unit whose test says the old path
    is gone, or that unit names one exception: a client still calls the
    operation, the code still serves a named live requirement, or the code
    was not found and `open-questions.md` blocks the start — Step 2,
    `references/modes.md`.
12. §1 states the version, its level and reason, the level re-checked
    against the iteration's typed changes; when MANIFEST differs from it,
    the last unit bumps the manifest's `version` to it — Steps 1–2.
13. Every unit with «Меняет символы» lists each use of those symbols in
    `Файлы` or «Не затрагивается» — Step 4.

Fix failures in place. A failure that needs a design decision goes to
`open-questions.md` and to the user — not into a unit.

## Report

The writer's last message is the report in
`executor-catalog/references/plan-writer-prompt.md`. Counts include the
grade spread (`0:2 Low:5 Mid:4 High:1`), the wave count, and any blocking
questions. The writer does not ask the next stage.

## References

- `references/modes.md` — what greenfield, increment, fix and revise
  change; a path this version retired; brownfield without documents. The
  writer reads its MODE's section.
- `references/plan-template.md` — the document template and its pins
  (Step 7).
- `references/unit-example.md` — one filled unit, for calibration (Step 4).
- `references/complexity.md` — the unit grading cascade, the six signals,
  the anti-inflation and anti-deflation gates, the split rule, and
  calibrated examples per grade. The writer runs this. The session does
  not.
- `executor-catalog/references/plan-complexity.md` — the cascade that
  picks `plan-lite` / `plan-medium` / `plan-hard`. The session runs this
  before the dispatch.
- `executor-catalog/references/assignable-implementers.md` — the only
  legal `Исполнитель` and `Вложенный` names.
- `executor-catalog` (skill) — the `plan-writer` rows, the `code-explorer`
  row for the inventory, and the Dispatch contract.
- `plan-review` (skill) — the independent gate over this plan. The
  session runs it at once, without asking, after the file exists (step 7).
  It reports; every fix it names is applied by a new dispatch of the
  writer, not by the session.
- `pipeline` (skill) — where this stage sits, its gate, and what follows.
  The session asks. The writer does not.
