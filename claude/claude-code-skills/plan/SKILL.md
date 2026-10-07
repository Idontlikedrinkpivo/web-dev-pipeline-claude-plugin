---
name: plan
description: >-
  Turns settled design documents, or existing code for brownfield work, into
  an implementation plan in the version folder documentation/plans/: atomic one-commit
  units, a complexity grade, and a named executor per unit. Use when the
  design is done and the user asks for a plan, tickets, or an order of work
  — «составь план», «разбей на задачи». Not for product behaviour, choosing
  a stack, document versions, or writing code — `work` executes the plan.
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
| Document `version` fields and changelog rows | `doc-versioning`, invoked by the user. This skill does not call it. The service version is read from the open folder and its level re-checked here, per `pipeline` → Service version |
| Writing code, running tests, committing code | `work` |

If a design gap surfaces while planning, it goes to this plan's **Open
questions** file beside the plan, `open-questions.md`. Never close a design
gap by guessing inside a unit, and never add an open-questions section to the
plan. A finding the user asked to defer after review goes in that same file.

## Inputs

| Input (path under `documentation/`) | Required | Read for |
|---|---|---|
| Architecture foundation `architecture/architecture.md` | **yes** | stack (§1), «Решения по NFR» (§1 — each row is applied by some unit), modules and areas (§2), ports and adapters and the configuration table (§4 — each variable is read and used by some unit), file tree (§5), lint and test plan (§6) |
| Domain model `architecture/domain.md` | **yes** | entities, value objects, named errors, the invariant table (§4) — every rule a unit enforces is cited from here |
| Scenarios of the areas in scope `architecture/scenarios/<area>/<area>.md` | **yes** | one unit per state-changing scenario; its steps, ports, transaction boundary and errors |
| SRS `requirements/srs/srs.md` | **yes** | UC / AC / BR / NFR ids the units must cite |
| OpenAPI `api/openapi.yaml` | when the surface is HTTP | one unit per operation group; `operationId` names the unit |
| DB schema `db/schema.md` + `db/migrations/` | when there is storage | migration units and their ordering: a schema change in scope is a unit that adds the next numbered file `db-schema-design` wrote to the app's migration run — never an edit of a committed file |
| Screen specs `ui/screen-specs/` (+ `ui/frames-register.md`) | when there are screens | one unit per screen: its elements, states, response outcomes and the Figma `nodeId` the unit cites; after a restyle, the register's «Визуальное направление» line and the `🎨 Tokens` page for the theme unit |
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
(brownfield, no docs): then the code stands in for the docs — inventoried by
`code-explorer` in the orchestrator, not read into this session — and mark
every unit's `Docs` cell `code:<path>` so execution knows the citation is
inferred, not specified.

## Orchestrator (session)

The session writes no plan file. It grades which writer settles the plan,
asks, and dispatches. It does not slice units.

This skill does not call `doc-versioning`, does not stamp a document, and
does not commit documentation. Pin `sources:` to the version already
written in each source file.

1. Stop when a greenfield plan has no architecture foundation, domain model,
   or scenarios document for an area in scope. Brownfield
   with no docs is allowed. Read the inputs far enough to run the grade
   below: level, risk, and the counts in the cascade. Do not slice.
2. **Read the iteration's version** from the open
   `documentation/plans/<version>/` (no `summary.md`); none open — open it
   per `pipeline` → Service version. Then **re-check the level** there
   against the iteration's typed changes: the rows of this version, plus
   unstamped changes typed from the diff since the last tag. A changed
   level is asked again. VERSION in the packet: number, level, reason.
3. **Brownfield only.** Resolve the `code-explorer` row and dispatch it
   under `executor-catalog` → Dispatch contract. Read that section's
   bullets and stop before its example. Ask for entry points, patterns a
   new unit would mirror, the storage access shape, and the test
   conventions. Take back paths and shapes only.
4. Read `executor-catalog` and
   `executor-catalog/references/plan-complexity.md`. The cascade there
   grades the plan, not a unit. Before the `Agent` call, write
   `Grade | Executor | subagent_type` for the `plan-writer` row the
   grade picked (`plan-lite`, `plan-medium`, or `plan-hard`), and dispatch
   it without asking which model, with `executor-catalog/references/plan-writer-prompt.md`
   as `subagent_type: "<row>"` with no `model` — the agent file holds
   it; pass `model` only for an explicit user model pick. A missing
   agent is a stop per the Dispatch contract, a rejected alias per Slug
   hygiene. Do not write the plan on the session model. Do not dispatch
   `doc-typist`.
5. Inspect the file. A model slug in the body, an `Implementer` outside
   `assignable-implementers.md`, or a report whose `DELEGATED` is not
   `doc-typist` comes back once. `BLOCKED` / `HARDER_THAN_EXPECTED`
   escalates once (lite → medium → hard), and that dispatch asks again.
   A second failure is a stop.
6. Report the plan path and the writer's counts. Then follow `pipeline`
   → "Asking before a transition". Ask about `plan-review` first. On a
   no, stop. On a yes, run that gate; it returns without asking the next
   stage. Branch on its verdict:
   - `FIX_THEN_PROCEED` or `RETURN_TO_PLAN` — grade the revise on its
     own, not by the plan (`plan-complexity.md` → Grading a revise: the
     `Fix kind` of the blocking rows). Before the `Agent` call write
     `Revise grade | Executor | subagent_type`. Dispatch that `plan-*`
     row with MODE `revise`, the revise grade in COMPLEXITY, and the
     blocking rows pasted into FINDINGS, then re-run `plan-review` over
     the changed units only. At most one revise round; a second blocking verdict is a stop
     to the user.
   - `STOP` — stop and take it to the user.
   - `PASS` — only then ask about the stage the table names after this
     one. Do not name a next step from memory.

## Writer (dispatched)

You settle the plan. You do not print it. When every unit decision the
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. Read
the file back. One correction dispatch, then the report. Do not type the
correction, and do not paste the finished plan into the typist's prompt.
Do not run `plan-review` or `pipeline`.

Pin `sources:` to the version already written in each source file. Do
not call `doc-versioning`.

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

**Brownfield inventory is already in the packet.** Paths and shapes only.
Do not dispatch `code-explorer` and do not read the repo unit by unit. A
brownfield packet with no inventory is `STATUS BLOCKED`. A greenfield
packet says `none`: the design documents already say everything the
digest needs. `Docs` cells in a brownfield plan read `code:<path>`.

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
| Screen | one unit per screen with all its states, citing its screen spec and the `nodeId` |
| Theme (after a `ui-design` restyle) | one unit: the project's theme file — colours light and dark, radius, shadows, density, fonts with their Cyrillic subset — from the Figma variables, and the values screens hardcode moved into it; `Docs` cite the register's «Визуальное направление» line and the `🎨 Tokens` `nodeId`; `impl-ui`; screen units that fix the look depend on it |
| Mechanical batch | one unit for a repo-wide rename, codemod, or config sweep |
| Version bump | the last unit: sets the manifest's `version` to VERSION; grade 0, `mechanical-worker`, `Depends on` every other unit |

Split a unit when it crosses a ring (domain **and** adapter), when it mixes a
decision with mechanics, or when two halves would land in separate commits
anyway. Merge two units when neither can land green alone.

Never produce: a 5-minute micro-step, a unit spanning unrelated concerns, a
layer batch ("all entities", "all adapters", "wire everything" — it cannot
land as one reviewable green commit), a unit so vague the executor has to
re-derive the design.

**A path this version retired.** List every id this iteration marked
`[deprecated in <version>]` or removed (a «ломает» row of this version,
`удалён:`). Marks from older versions are not this plan's job. For each id whose code is still in the
repo, add one unit. `Docs` cites the retired id and what replaced it. `Files`
names the old path. The goal says that path is gone and the replacement covers
it. A test says the old call is absent and the replacement scenario passes.
The unit does not delete the specification row.

Three exceptions, each one sentence in that unit:

- A client still calls the HTTP operation. Remove this product's callers
  and the screen. Leave the operation `deprecated: true`.
- The code still serves a live requirement. Name that requirement.
- The code cannot be found. Put «где живёт <id>» in `open-questions.md`,
  class `Блокирует старт`. The plan is not done while that row is open.

A repo with no such code skips this.

### Step 3. Order and mark parallelism

Order by dependency, not by layer aesthetics: a unit ships only after every
unit it imports from. Two units are **parallel-safe** only when their `Files`
sets are disjoint *and* they share no type, migration, registry, config,
generated client, lockfile, or runtime resource their tests need (a local
database, a port, a dev server, a package install). Declared file
disjointness is necessary and not sufficient — an unmarked shared contract is
what turns a parallel wave into a merge fight, and two workers running
integration tests against one local database corrupt each other even in
isolated worktrees. Default to `no` under any doubt. **UI units are always
`Parallel-safe: no`** and run one after another: the first one (in plan
order) carries the API client generation and the app-wide error handler in
its `Files`; later screens depend on it and only use them.

Among units that are equally ready, order first the one that completes the
earliest use case's path end-to-end. A run stopped mid-way then leaves a
working slice rather than one layer of everything.

### Step 4. Fill each unit

`U-IDs` are stable: `U1`, `U2`, … Assigned once, never renumbered. Splitting
keeps the original id on the original concept and gives the new part the next
unused number. Deletion leaves a gap; gaps are fine.

```markdown
### U<n>. <Verb phrase>

| | |
|---|---|
| **Docs** | scenarios/orders `<UseCase>` · domain §4 <rule row> · SRS UC-2 / AC-Exc-1 · BR-3 · api `POST /orders` |
| **Files** | repo-relative paths, including the test file |
| **Pattern** | repo-relative path(s) whose conventions this unit mirrors (`path (U<n>)` when a unit in `Depends on` creates it, or the arch section that fixes the shape), or `— first of its kind` |
| **Depends on** | U-ids, or `—` |
| **Parallel-safe** | yes / no — and with what it contends when no |
| **Complexity** | 0 / Low / Mid / High |
| **Why** | the one signal that set the grade (see `references/complexity.md`) |
| **Implementer** | executor name from `executor-catalog` |
| **Nested** | executor name, or `—` |
| **Nested does** | the mechanics to delegate, or `—` |

**Goal** — one sentence: what is true after this commit. A new path says
what exists that did not before. A retired path says the old path is gone
and what covers it.

**Approach** — the decisions already made, cited not restated: which entity
method the use case calls, which port signature the adapter implements, which
error maps to which status. No code, no imports, no signatures invented here.

**Test scenarios** — one per line, each naming input, action, expected
outcome. Cover every invariant row this unit enforces (`covers BR-3`), the
AC of each flow it serves, its error paths, and its boundary crossings.
A unit with no behavior writes `none — <reason>` instead.

**Verification** — the observable outcome that proves the unit done, as an
outcome, not a shell recipe.

**Commit** — the conventional message this unit lands under.
```

A filled unit, for calibration — match its density, not its domain:
`references/unit-example.md`.

Every behavior-bearing unit names its test file in `Files`. A unit with a
blank `Test scenarios` and real behavior is an unfinished unit, not a fast one.

`Pattern` is the evidence for complexity signal 4: a path means precedent
exists, and it has to exist in the tree or be created by an earlier unit
reachable via `Depends on` (write `path (U<n>)`); an architecture section
whose file tree / snippet fixes the shape counts too. `— first of its kind`
puts signal 4 at the expensive end, and the anti-deflation gate keeps the unit
at Mid or above. `work` pastes this field into the worker's `PATTERN TO
MIRROR` verbatim, so a pattern left out here gets picked at execution time
with nobody reviewing it. In a brownfield plan, take the paths from the
`code-explorer` inventory.

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
vibe: `Files` count and ring spread, whether `Approach` still contains a
decision, whether `Pattern` names a precedent, whether `Test scenarios` has
error and integration rows, whether `Docs` fully specifies the outcome.

**The risk floor is not the only route to High.** The cascade's compound gate
(rule 2) exists for work that is hard without being dangerous: an open
mechanism, a first-of-its-kind cross-ring shape, an outcome that needs time
control or a second worker to prove. A plan whose only High units touch auth or
money is usually a plan where that gate was skipped, and its hardest unit was
handed to the Mid implementer.

Two rules override everything else in that file:

- **Risk floor.** A unit touching auth, authorization, money, migrations on
  existing data, secrets, or an external contract is never below **Mid**.
- **Spec floor.** A unit whose `Docs` do not fully determine the outcome is
  never below **Mid**, regardless of how few files it touches — undecided
  work is expensive work.

Put the deciding signal in `Why` in under twelve words. If `Why` reads
"seems complex" or restates the goal, the cascade was not run. The same holds
for the plan as a whole: every unit Mid, or every unit High, means Step 5 was
skipped — grades that do not spread defeat the routing.

### Step 6. Assign executors from the assignable list

Read `executor-catalog/references/assignable-implementers.md` only — not the
rest of the catalog. `Implementer` is one of `mechanical-worker`, `impl-lite`,
`impl-medium`, `impl-hard`, `impl-ui`. `Nested` is `—` or `mechanical-worker`.
Review, plan-review, doc-review, `code-explorer`, and `impl-critical` names
are illegal here. A frontend unit whose `Docs` cite a screen spec and a Figma
`nodeId` is `impl-ui` at every grade, and it does not nest. Never write a
model slug into the plan: the catalog and its agent files own the mapping, so
a model rename touches one agent file instead of every plan ever written.

Fill `Nested` only when the unit genuinely contains mechanics separable from
its decision — apply a settled shape across many files, generate fixtures,
port a pattern to N call sites. Then `Nested does` states exactly that
delegation and, implicitly, that the implementer keeps the decision. A unit
whose whole content is mechanical does not nest; it *is* the mechanical tier.
Nesting is never escalation: more horsepower is a higher `Implementer`.

### Step 7. Hand the plan to `doc-typist`

The file lands at `documentation/plans/<version>/plan.md`. Questions go in
`open-questions.md` in the same folder. Repo-relative paths everywhere in the
body — absolute paths do not survive a worktree. You do not write this file.
The settlement is one line per unit field, not the template below filled in.
`doc-typist` renders that template.

When the file already exists **for this same version** — a plan you are
revising, or an open version a new change joins — edit it in place: keep the
existing U-ids, append new units with unused numbers, keep the bump unit last,
and update grades only with a reason in `Why`. The plan carries no progress
state — no checkboxes, no `status:` field. Progress lives in git, and the
`work` skill reads it there.

**A new version gets a new plan folder.** Specs version in place; plans do
not. A plan is a work order for one service version, so it starts a fresh U-id
namespace at U1 and never rewrites a closed version's plan (its folder has
`summary.md`) to describe new work — old plans must stay readable against the
commits that came out of them. See the `doc-versioning` skill for the split.

Pin what the plan was built from as `path@<version>`, the version already
written in each source file. Do not mint a version to make the pin current:

```yaml
sources:
  - documentation/architecture/architecture.md@1.1.0
  - documentation/architecture/domain.md@1.3.0
  - documentation/architecture/scenarios/invoices/invoices.md@1.3.0
  - documentation/requirements/srs/srs.md@1.3.0
```

If a source's `version` is ahead of what an existing plan pinned and its
rows after the pin hold a «ломает», say so before planning further: the
units may cite decisions that changed. And
if a source document carries a stale banner of its own, do not plan on top of it
silently — name the gap in `open-questions.md` beside the plan.

## Output document template

```markdown
---
name: implementation plan <version>
date: YYYY-MM-DD
sources:
  - documentation/architecture/architecture.md@<version>
  - documentation/architecture/domain.md@<version>
  - documentation/architecture/scenarios/<area>/<area>.md@<version>   # one per area in scope
  - documentation/ui/screen-specs/S-1-<screen>.md@<version>           # one per screen in scope
  - documentation/requirements/srs/srs.md@<version>
routing: executor-catalog
---

# Implementation plan: <version>

## 1. Digest
Version · level · reason (Step 1) · the changes, when several · architecture
level and budget · stack · the unit spine this produced · what the scaffold
already provides.

## 2. Unit map
| U | Unit | Complexity | Implementer | Nested | Depends on | Parallel-safe |
|---|---|---|---|---|---|---|

Then, when useful, a D2 dependency graph of the same table
(`diagrams/deps.d2` plus the rendered `.svg`).

## 3. Units
One `### U<n>.` block per unit, per Step 4.

## 4. Waves
Which units may run together, derived from Depends on + Parallel-safe. A wave
is a claim about contention, so name the contention that keeps units apart.
For each wave, also name which use case (UC id) first runs end-to-end after
it, or `—`.

## 5. Definition of done
The plan-wide gate: lint contracts from the foundation §6 pass, the end-to-end path
runs, every quoted invariant row has a test, every AC is covered.
```

## Quality gate

1. Every unit lands as one green commit; none crosses a ring without a stated
   reason, none recreates what the scaffold already has — Step 2, Inputs.
2. Every `Docs` citation resolves to a real section or id; no unit invents a
   method, signature, status, or column the design never named — Step 4.
3. Every quoted invariant row and every AC appears in some unit's
   `Test scenarios` — Step 4. Every foundation «Решения по NFR» row and
   every §4 configuration variable belongs to a unit that applies it (a
   body limit set, a pool sized from its variable, workers started from
   theirs) — a decision that only lives in the document is not built.
4. Every unit has `Complexity`, a one-signal `Why`, and an assignable
   `Implementer` — Steps 5–6.
5. Risk floor and spec floor hold — Step 5.
6. Grades spread across at least two tiers, unless the plan is honestly one
   kind of work and says so — Step 5.
7. `Depends on` is a DAG; every `Parallel-safe: yes` pair is disjoint in
   files, contracts, *and* runtime resources — Step 3.
8. Every `Pattern` path exists or is created by a unit in its `Depends on`
   chain; every `— first of its kind` unit is Mid or above — Step 4.
9. U-ids unique and never renumbered; no model slug and no progress state in
   the body — Steps 4, 6, 7.
10. Rows in `open-questions.md` block named units instead of being absorbed as guesses.
11. Every id this version retired has a unit whose test says the old path
    is gone, or that unit names one exception: a client still calls the
    operation, the code still serves a named live requirement, or the code
    was not found and `open-questions.md` blocks the start — Step 2.
12. §1 states the version, its level and reason, the level re-checked
    against the iteration's typed changes; the last unit bumps the
    manifest's `version` to it — Steps 1–2.

Fix failures in place. A failure that needs a design decision goes to
`open-questions.md` and to the user — not into a unit.

## Report

The writer's last message is the report in
`executor-catalog/references/plan-writer-prompt.md`. Counts include the
grade spread (`0:2 Low:5 Mid:4 High:1`), the wave count, and any blocking
questions. The writer does not ask the next stage.

## References

- `references/complexity.md` — the unit grading cascade, the six signals,
  the anti-inflation and anti-deflation gates, the split rule, and
  calibrated examples per grade. The writer runs this. The session does
  not.
- `executor-catalog/references/plan-complexity.md` — the cascade that
  picks `plan-lite` / `plan-medium` / `plan-hard`. The session runs this
  before the dispatch.
- `executor-catalog/references/assignable-implementers.md` — the only
  legal `Implementer` and `Nested` names.
- `executor-catalog` (skill) — the `plan-writer` rows, the `code-explorer`
  row for the brownfield inventory, and the Dispatch contract.
- `plan-review` (skill) — the independent gate over this plan. The
  session asks about it after the file exists. It reports; every fix it
  names is applied by a new dispatch of the writer, not by the session.
- `pipeline` (skill) — where this stage sits, its gate, and what follows.
  The session asks. The writer does not.
