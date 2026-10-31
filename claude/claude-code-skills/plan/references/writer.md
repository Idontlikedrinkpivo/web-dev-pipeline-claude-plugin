# Plan writer — the Writer half of `plan`

Read by the dispatched `plan-*` writer, never by the session: the session's half is `plan/SKILL.md` →
Orchestrator. The inputs and modes are `plan/SKILL.md` → Modes and Inputs. Cite a step here as
`plan/references/writer.md` → Step <n>, never as «plan step <n>»: the orchestrator's numbered steps are a
different sequence.

## Start

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

The two floors — risk (auth, authorization, money, migrations on existing data, secrets, a published contract)
and spec (`Документы` that do not fully determine the outcome) — are `references/complexity.md` → The cascade,
rules 1 and 4, worded only there so the two texts cannot drift; no file count argues either down.

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
   reason, none recreates what the scaffold already has — Step 2, `plan/SKILL.md` → Inputs.
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
