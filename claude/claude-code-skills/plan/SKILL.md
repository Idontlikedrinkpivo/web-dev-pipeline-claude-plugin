---
name: plan
description: >-
  Turns design documents or code into the implementation plan (one-commit units, grade, executor), or a fix plan from
  a test or audit report. Use for «составь план», «разбей на задачи», «исправь баги из отчёта».
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
`references/modes.md`. The writer reads its MODE's section before its Step 1.

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
asks, and dispatches. It does not slice units. Cite these steps as `plan` →
Orchestrator step <n>; the writer's own Steps 1–7 are another sequence
(`references/writer.md`).

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
6. Inspect the report. A `DELEGATED` that is not `doc-typist` (the writer
   typed the plan itself) comes back, until it is right; model slugs and
   executor names are `plan_lint.py`'s, in step 7. A `BLOCKED` with a
   question for the user is asked and sent back to the same row; any
   other `BLOCKED` / `HARDER_THAN_EXPECTED` escalates one tier per failure
   (lite → medium → hard), and that dispatch asks again; the rounds go on
   while each makes progress (`pipeline` → `references/convergence.md`).
7. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/plan_lint.py" <plan>`: each error goes back to the writer
   (`revise`, those lines) until it exits 0. Report the plan path and the writer's counts. Then run `plan-review` at
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

The writer half — Steps 1–7 (digest, slicing, order, unit fields, grading, executors, the hand-off to
`doc-typist`), the output template, the quality gate and the report — is `references/writer.md`. The dispatched
`plan-*` writer reads it whole (its packet's SKILL slot names it), and so does `doc-typist` for the plan's shape,
headings and ids. The session does not read it.

## References

- `references/modes.md` — what greenfield, increment, fix and revise
  change; a path this version retired; brownfield without documents. The
  writer reads its MODE's section.
- `references/writer.md` — the writer half: Steps 1–7, the output
  template, the quality gate, the report. The writer reads it; the session
  does not.
- `references/plan-template.md` — the document template and its pins
  (writer Step 7).
- `references/unit-example.md` — one filled unit, for calibration (writer
  Step 4).
- `references/files-field.md` — the five cases of «Файлы» (writer Step 4).
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
  session runs it at once, without asking, after the file exists
  (Orchestrator step 7).
  It reports; every fix it names is applied by a new dispatch of the
  writer, not by the session.
- `pipeline` (skill) — where this stage sits, its gate, and what follows.
  The session asks. The writer does not.
