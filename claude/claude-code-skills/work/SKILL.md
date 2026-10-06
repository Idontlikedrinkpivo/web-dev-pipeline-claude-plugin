---
name: work
description: >-
  Executes a finished implementation plan: dispatches each unit to the
  executor the plan named, inspects the real diff, runs the per-unit and
  whole-run reviews, and lands one commit per unit; the orchestrator writes
  no production code. Use when a plan is ready (normally after
  `plan-review`) and the user asks to execute or implement it — «выполни
  план», «запусти работу». Not for writing the feature in-session, planning,
  design, PRs or CI.
---

# Execute an Implementation Plan

The plan already decided the work, the order, and who does it. This skill's
job is to honor that routing and keep the tree green — not to re-plan, and not
to implement the work itself.

**The orchestrator writes no production code.** Every unit goes to the
executor the plan named, and a review fix goes back to that executor or to
`mechanical-worker`. The grade picks the packet and the review roster. An
orchestrator that types the fix itself skips that loop.

**Tests come from the documentation, before the code.** The design already
fixed the signatures, the states, the error mapping, and the acceptance
criteria, so a test here is not exploration — it is the transcription of a
settled contract. Every behavior-bearing unit turns its `Test scenarios` into
tests, observes them fail for the right reason, and only then gets an
implementation.

TDD is the **order inside a unit**, never a second unit and never a second
commit. A unit is still one green commit: the failing test and the code that
answers it land together. Splitting them into a `test:` commit and a `feat:`
commit doubles the dispatch and breaks the one invariant the plan is built on.
Tests are not nested either: choosing what to assert from an invariant row is
judgment, and it belongs to the unit's own implementer — `mechanical-worker`
may only replicate an assertion that implementer already wrote.

## Not this skill's job

| Not here | Owner |
|---|---|
| Slicing units, grading, assigning executors | `plan` |
| Deciding entity behavior, ports, contracts, screens | the design documents |
| Branch strategy beyond one feature branch, PRs, CI | the user's shipping flow |
| Docker/compose topology for test, dev, prod | `deploy-topology`, once the plan's units are committed |

If a unit turns out to be under-specified or the design is wrong, that is a
**stop and report**, not an improvisation.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Plan path | **yes** | or `plan.md` of the open version folder (`documentation/plans/<version>/` without `summary.md`) when the user gives none — say which file you picked |
| `executor-catalog` skill | **yes** | read before the first dispatch; it is the only source of name → agent routing (each agent's file holds its model) |
| The design documents the plan cites | on demand | read the cited section when building a worker packet, not up front |
| Context7 MCP (`resolve-library-id`, `query-docs`) | no | live library docs for the packet's `CURRENT LIB DOCS` (Step 2b). Missing MCP is a skip, not a stop |
| Language skill files the user attached | no | forwarded as `STACK SKILLS`. Do not invent a stack pack |
| `frontend` skill | for frontend units | every `impl-ui` unit, and any unit whose `Files` are browser UI code, gets it in `STACK SKILLS` without being attached: its `SKILL.md` in full plus the one `references/<profile>.md` that matches architecture §1 «Стек» (or the line `no profile — <stack>`). Backend units never get it |

### Readiness gate

Before any dispatch, check the plan carries, on **every** unit: `Complexity`,
`Implementer`, `Files`, `Pattern`, `Depends on`, `Test scenarios`, `Verification`. Also
check every `Implementer` and `Nested` name exists in
`executor-catalog/references/assignable-implementers.md` — not merely
somewhere in the catalog.

A plan missing these is not executable here. Do **not** infer a grade, and do
not pick a model yourself — name the units that are incomplete and hand back
to the `plan` skill. Inferring the routing at execution time is how a plan's
economics quietly become the session model's economics. For the same reason,
never override a named `Implementer` because the work "looks easy": the plan
graded it with the fields in front of it; you have less context, not more.

**Also confirm the plan passed `plan-review`** by reading
`documentation/plans/<version>/plan-review.md` beside the plan. That gate is
where a dependency cycle, an uncoverable invariant, a dangling citation, or a
miscalibrated grade is supposed to be caught, and each of those defects is far
more expensive once workers are running against it. A missing file, or a first
line other than `Verdict: PASS`, means the gate did not pass. Ask once, per
`pipeline` → "Asking before a transition":

- missing — run `plan-review` first, or execute without it;
- present with another verdict — name its unresolved blocking findings, then
  fix the plan first (`plan`), or execute as it stands.

Recommend the review when the plan has a High unit or a security, money, or
migration unit; for a plan of a few Low units the user may well skip it. An
execution without a passed review says so in the run report.

## Workflow

### Step 1. Set up once

Read the plan's §1 digest, §2 unit map, §4 waves, and §5 definition of done.
Read individual `### U<n>.` blocks lazily — one when you dispatch it, not all
at the start.

Branch: work on a feature branch, never the default branch without explicit
permission. If the current branch is auto-generated (`worktree-happy-otter`),
offer to rename it from the plan's version first.

Build a task list from the unit map: one task per unit, named from the unit's
goal with the U-id appended (`Add order aggregate (U3)`). Do not edit the plan
document — progress lives in commits, the task list, and the progress file
next to the plan (below).

**Say the count in the chat.** `<всего>` is the number of units in this
run's scope, taken from the unit map. The default scope is every unit in
the map. `<сделано>` is how many of those have a `Plan-Unit:` trailer in
`BASE..HEAD`. A follow-up that is not in the plan does not change either
number. After the committed set is known, and again after every Step 5
commit, write one line: `План: <сделано> из <всего>`. Take both numbers
from the map and from git, not from the previous message. A resumed or
compacted session writes the line before the next dispatch.

**Record the run base and resume from git.** Before the first dispatch, record
`BASE=$(git rev-parse HEAD)` in the run report. Every unit commit carries the
trailer `Plan-Unit: <version>/U<n>` (Step 5.5). On start — and after any
context compaction — derive the committed set from
`git log BASE..HEAD --format=%B | grep '^Plan-Unit: <version>/'`, not from
memory: a unit listed there is done and is never re-dispatched. Re-dispatching
finished units after losing your place is the single most expensive way a run
fails. Keep the run report as a file at
`$(git rev-parse --git-dir)/pipeline-work/<version>-run.md` — outside the
tree, so the plan stays byte-identical and no unit's `Files` grows — append to
it after every commit, and read it back after a compaction.

**Keep the progress file.** The user follows the run in
`documentation/plans/<version>/progress.md`, next to the plan: one row per
unit with its executor, status and review path, and — when the final review
finds problems — a section that lists every fix as its own task before the
first fix starts. It is never committed: `documentation/plans/` is out of
git (`pipeline` → Plans stay out of git). Shape and statuses:
`references/progress-file.md`. It is a view of git, never a source of truth:
the `Plan-Unit:` trailers decide what is done. Update it with the Edit tool the
moment a status changes (dispatched, in review, committed), never from the
shell: the user's file pane redraws only on edit-tool changes.

**Show the link before the first dispatch.** Once the file is created (or
rebuilt on a resumed run), and before any unit is dispatched, post it in the
chat as a clickable Markdown link with its repo-relative path, so the user
opens it with one click and watches the run live:

```text
Прогресс выполнения: [progress.md](documentation/plans/1.1.0/progress.md) — откройте, он обновляется по ходу работы.
План: 0 из 6
```

A resumed or compacted session posts the link again before its next dispatch.

### Step 2. Resolve the routing table

Read `executor-catalog` and build a small in-run table: for each distinct
`Implementer` and `Nested` name in the plan, `Name | subagent_type` — the
`subagent_type` is the name itself, since every row is its own agent; you
may append the model and effort read from that agent's file. Resolve once,
reuse for the run. Print that table in this turn before the first `Agent`
call. Every dispatch in this run — workers, reviewers, follow-ups — goes out
under the catalog's Dispatch contract; read that section with the rows.

An agent the `Agent` call does not know is not installed: stop and tell the
user to run `install.sh`, per the Dispatch contract. An alias the harness
rejects inside an agent file is handled by the catalog's Slug hygiene: stop
on that tier and report it with the tier name and the file. Neither is fixed
by adding agents or executor setup to the project.

### Step 2b. Refresh current library docs once

The worker has no chat history and may have no MCP, so you fetch library docs
once, here, and paste slices into each packet — never tell a worker to look
them up itself. When any unit calls a public library API, read
`references/context7.md` now and follow it; a missing MCP is a skip, not a
stop.

### Step 3. Pick the next unit or wave

A unit is ready when every id in `Depends on` is committed — that is, has a
`Plan-Unit:` trailer in `BASE..HEAD` (Step 1). Among ready units:

- **Serial** by default — one unit, one dispatch, one commit.
- **Parallel** only when all four hold (cap a wave at three or four):
  - the plan marks the peers `Parallel-safe: yes`;
  - their `Files` are genuinely disjoint in the current tree;
  - the harness gives each worker an isolated workspace — in Claude Code,
    pass `isolation: "worktree"` on each parallel `Agent` call;
  - their focused tests share no runtime resource (one compose database, a
    fixed port, a dev server) — isolation of files is not isolation of the
    database.
- **Never parallel** in a shared working directory: concurrent writes and
  concurrent test runs corrupt each other regardless of what the plan claims.
- **UI units are never parallel** — not with each other and not with any
  other unit: one screen at a time, in plan order, each its own dispatch,
  review, and commit. Screens share the generated API client, the app-wide
  error handler, and shared components; the first UI unit of a run sets them
  up and the next ones reuse them, so a later screen sees what the earlier
  one built.
- **Bring the wave home before Step 5.1.** Merge or cherry-pick each
  worker's worktree branch into the main tree, then integrate unit by unit.
  If that is not possible, run the wave serially instead.

Re-verify the plan's parallel claim against the tree before dispatching, then
decline parallelism under any remaining doubt. Speed is optional; a clean
history is not.

Do not re-scope the run into sessions ("phase 1 of 3 for today"). Context
pressure is handled by dispatching units and resuming from git (Step 1), not
by splitting the run.

### Step 4. Dispatch

Build the packet from `executor-catalog/references/worker-prompt.md`. Fill
every slot: paste the cited design excerpts rather than telling the worker to
go read the architecture, list the exact files, carry the unit's `Approach`,
`Test scenarios` and `Verification` verbatim, paste `STACK SKILLS` from
language skills the user attached, plus the `frontend` skill and its one
profile for a frontend unit (see Inputs), or `none — no language skills attached`,
paste `CURRENT LIB DOCS` from Step 2b, fill `FROM DEPENDENCIES` from the run
report's `Decisions` of every `Depends on` unit, and include the `DELEGATION`
block only when the unit has a `Nested` row — nesting hands typing to
`mechanical-worker` under the decision-maker, never extra horsepower; more
reasoning is a recorded escalation (Step 6). `PATTERN TO MIRROR` is the unit's
`Pattern` field verbatim; do not pick a pattern yourself — a pattern chosen at
execution time is a design decision nobody reviewed.

Dispatch with the Step 2 row: `subagent_type` is the row's name, and the
call passes no `model`. Omit any permission-mode override so the user's
own settings apply. This run does not ask which model to use. Manual model
pick in `executor-catalog` does not apply to implementers, nesting, or the
review skills this run calls.

Grade-specific expectations to state in the packet:

| Grade | What the worker is told |
|---|---|
| **0** | apply the shape exactly, touch nothing else, no design latitude |
| **Low** | mirror the named pattern; if the pattern does not fit, report rather than invent |
| **Mid** | the remaining local decisions are yours; list each one under `DECISIONS` in the report |
| **High** | design the missing part inside the cited boundaries, and prove the edge cases the scenarios name |

### Step 4b. Name the unit's evidence strategy in the packet

Pick one per unit and write it into the packet's `EVIDENCE STRATEGY` slot. The
unit's `Test scenarios` and the state of the code it touches decide this — not
the grade alone:

| Strategy | When | What the worker owes back |
|---|---|---|
| `test-first` | the unit adds or changes behavior and the surface is new | every scenario as a test, observed failing for the right reason, then the code |
| `characterization-first` | the unit changes behavior that exists and is untested | the current behavior captured as passing tests first, then which assertion changed on purpose |
| `smoke` | packaging, config, styling, wiring with no unit-level behavior | the runtime or install check it ran instead |
| `none` | the plan's scenarios say `none — <reason>` (grade 0 and similar) | nothing; the reason carries |

`test-first` is the default for any unit with real scenarios. Legacy code is
the one honest exception: demanding a red first test where none exists rewards
guessing at current behavior instead of pinning it.

**Two-phase dispatch for High and risk-floor units.** For auth, authorization,
money, migrations over live rows, secrets, or any High unit, witness the red
instead of accepting it as a claim: the same implementer is dispatched
`PHASE tests-only`, you run the tests and see them fail, then
`PHASE implementation`. Read `references/two-phase-dispatch.md` before
dispatching such a unit. Every other grade gets a single `PHASE full`
dispatch.

### Step 5. Integrate — the orchestrator's own work

Per unit, in this order, and never skip to the next unit on a broken tree:

1. **Inspect the real tree.** `git status` and the diff. The report's file list
   is a hint; what the worker actually changed is the truth. A file outside the
   unit's `Files` is a scope breach: revert it. If the unit truly needed it,
   the plan mis-listed the footprint — record why in the run report and
   re-dispatch with the corrected `Files` (Step 6), so the review sees the file
   inside the unit's scope instead of flagging it as a breach.
2. **Check the diff against the unit spec.** Does it implement the cited
   design, or something adjacent? Does it re-decide something the design
   already fixed?
3. **Run the tests** — the unit's own tests plus whatever the plan's definition
   of done names for this ring. This run is authoritative; the worker's
   self-check is not. Then check the proof, not just the green: every scenario
   the plan listed exists as a test in the diff and asserts what the scenario
   names (a test named after a scenario that asserts nothing reports coverage
   that does not exist), and the report's `EVIDENCE` matches what the diff
   shows. **A behavior-bearing unit returning `DONE` with
   no observed red and no recorded exception is not done** — send it back for
   the evidence rather than committing on the claim. `RED OBSERVED` cannot be
   reconstructed after the fact, which is exactly why an empty one is a return
   and not a note in the report.
4. **Review by grade** — the `code-review-unit` skill does the review; your
   part is its inputs and its verdict:
   1. Write the diff to a file under `$(git rev-parse --git-dir)/pipeline-work/`.
      Never paste it: pasted text stays in your context for the rest of the
      run and brings on the compaction Step 1 exists to survive.
   2. Invoke `code-review-unit` with the unit spec, that diff path, the cited
      design excerpts, the worker report, and the findings already recorded
      this run. It sizes its own roster from the grade (0 needs no dispatch,
      Low batches at the wave boundary) and returns findings plus one verdict.
   3. Before acting on `RETURN_TO_EXECUTOR`, confirm each blocking finding's
      quoted line exists in the diff (for a missing scenario test, in the
      unit's `Test scenarios`). Drop one that does not to the run report
      instead of sending it back: a false P1 costs a re-dispatch and moves the
      unit toward the second-failure stop.
   4. Honor the verdict. `COMMIT` continues to 5. `FIX_THEN_COMMIT` goes to
      `mechanical-worker`. `RETURN_TO_EXECUTOR` re-dispatches the unit's own
      implementer with the findings. `STOP` goes to the user. P2/P3 never
      hold up the commit; they land in the run report.
   5. Copy every `OPEN` cross-unit suspicion into the run report's
      **Cross-unit watch** for Step 7.
5. **Commit** one commit per unit (plus, for a Low unit, a possible fix commit
   after its batch review — see **A fix after a commit** below), with the
   unit's `Commit` message plus the
   trailer `Plan-Unit: <version>/U<n>`, staging only that unit's files —
   never `git add .`, which drags a sibling unit's half-work into this commit —
   then set the unit's row in the progress file to `✅ закоммичен` with its
   review verdict.
   Never batch several units into one commit because it was faster. Do not
   stage a contract document (SRS, OpenAPI, DB schema, architecture, UI
   spec) and do not write its changelog: that commit belongs to
   `doc-versioning`, which the user invokes. `plan` does not call it.
6. **Update the task list and the run report file** (the unit's row and the
   worker's `DECISIONS`), write `План: <сделано> из <всего>` in the chat
   (Step 1), then move on. When the run stops on a unit instead (a design
   gap, a spent attempt budget), set that row to
   `⛔ остановлен: <причина>`.

Fixing a worker's output yourself is the one thing this loop forbids, even a
one-liner. A failing test, a missed scenario, or a review finding goes back —
to the same executor with the finding, or to `mechanical-worker` when the fix
is purely mechanical.

### Step 6. Handle a bad return

| Return | Move |
|---|---|
| `DONE_WITH_CONCERNS` | route the concern to a reviewer before committing — the grade's reviewer, or a single `review-medium` pass on that unit for grade 0 and Low; commit only after the concern is closed or explicitly accepted |
| `BLOCKED` on a missing file or contract | if the plan simply mis-listed `Files`, re-dispatch with the corrected list; if a design decision is missing, **stop and ask the user** |
| `BLOCKED` / `HARDER_THAN_EXPECTED` on difficulty | escalate exactly one tier per `executor-catalog`, carrying the previous report. An `impl-ui` unit is not on that ladder: re-dispatch `impl-ui` once with the report |
| Scope breach | revert the out-of-scope part, re-dispatch the unit narrowed |
| A red test made green by editing its assertion | treat as `BLOCKED`, not a pass — it hides a real conflict between the scenario and the design |

**Attempt budget.** A unit gets its first attempt and one retry. The first
attempt is the first dispatch — a two-phase unit's tests-only and
implementation dispatches together count as one attempt. The retry is any one
of: a `RETURN_TO_EXECUTOR` re-dispatch, an escalation, or a re-dispatch with a
corrected `Files`. A `FIX_THEN_COMMIT` fix by `mechanical-worker` does not use
the budget. A unit that needs more than that means the unit or the design is
wrong: stop and say so instead of retrying.

**A fix after a commit** — from a Low batch review or from the final review —
is a new commit on top, never a rewrite of history. It goes to the executor
the verdict names (`mechanical-worker` for a mechanical finding, the unit's
own implementer for `RETURN_TO_EXECUTOR` / `RETURN_TO_UNIT`), passes
`code-review-unit` like any unit, and carries the trailer of the unit it fixes
(`Plan-Unit: <version>/U<n>`); a fix that spans units carries
`Plan-Unit: <version>/review-fix-<n>`. List every such commit in the
run report, so `code-review-full` counts it as mapped.

Escalations and grade corrections are recorded in the run report only. Never
write them back into the plan: the next run must re-derive the tier from the
unit, and a plan carrying scars stops being a decision artifact.

### Step 7. Close the run

When every unit in scope is committed, first run two checks yourself and save
each output under `$(git rev-parse --git-dir)/pipeline-work/`:

- **Definition of done** — every command in the plan's §5 (lint and
  dependency contracts, the end-to-end path, the test suite), with its exit
  code.
- **Dead-code report** — the stack's detector over the whole repo: `knip` for
  TypeScript, `vulture` for Python (another stack: its usual unused-code
  tool). Use the repo's config when it has one; otherwise run it with defaults
  and say so in the run report. Check the tool's current flags against the
  installed version; a detector that cannot run is noted, not skipped
  silently.

Then invoke the `code-review-full` skill once over the whole run: the plan, the full diff `BASE...HEAD` (BASE from
Step 1, handed over as a file path, as in Step 5.4), the design documents
it cites, the declared security requirements (the SRS's Security NFR rows and
the architecture's security decisions table), this run's report so far
(including grade corrections and the cross-unit watch list from Step 5.4), the
definition of done with its saved output, and the dead-code report. It is the
only place that checks what no single unit's review could — drift between
units, aggregate coverage of invariants and ACs that needed more than one unit,
and the definition of done itself, with its own lenses and verdict rather than
an inline checklist here.

Honor its verdict the same way: `PASS` closes the run, `FIX_THEN_CLOSE` routes
mechanical findings to `mechanical-worker` as their own follow-up unit(s) before
closing, `RETURN_TO_UNIT` re-opens the named unit through its own executor,
`STOP` goes to the user with the findings attached.

Anything but `PASS`: before the first fix, add «Исправления по финальному
ревью» to the progress file — every finding a row with who fixes it and
`⏳ ждёт` (`references/progress-file.md` → Fixes after the final review),
and post the link again before the first fix, pointing at the section:
`Исправления по финальному ревью: [progress.md](documentation/plans/<version>/progress.md) — раздел внизу файла, обновляется по ходу работы.` Each fix then lands like a unit, updating its rows. After
the last fix, run `code-review-full` once more over the fix commits; a second
blocking verdict is a stop for the user.

At the close write the verdict path into the `Финальное ревью:` line
(`RETURN_TO_UNIT → исправлено → PASS`, or plain `PASS`).

Stop there. The last chat line is `План: <сделано> из <всего>`. No PR, no
push, no CI watching. The branch stays local: the pipeline still has
the UI acceptance run (`ui-test-cases`, when there are screens), `deploy-topology` and `ci-pipeline` ahead, and push and PR are the user's
step after the whole pipeline, not after this run.

## Run report

```markdown
## Run report — <plan path>

**Base** — `BASE` recorded at Step 1; the start of every `BASE..HEAD` range.
**Прогресс** — `<сделано> из <всего>`, the same numbers as the chat line.

| U | Status | Executor used | Escalated | Commit |
|---|---|---|---|---|

**Decisions** — per unit, the worker's `DECISIONS` lines; the source for
`FROM DEPENDENCIES` in every dependent unit's packet.
**Verification** — what was run plan-wide and what it returned.
**Evidence** — per unit: the strategy used, and whether the red was witnessed
by the orchestrator (two-phase) or taken from the worker's report. A unit
committed on a reported red is a weaker claim than one committed on a witnessed
one, and the report should not blur them.
**Grade corrections** — units whose real difficulty did not match the plan's
grade, with the signal the cascade missed. This is the feedback that keeps
`complexity.md` calibrated for this project.
**Out of scope** — problems workers reported and nobody fixed.
**Cross-unit watch** — `OPEN` suspicions carried up from per-unit reviews, for
`code-review-full` to resolve at Step 7.
**Open** — units not attempted, and why.
**Lib docs** — which libraries Step 2b fetched (id + pinned version), or why
it wrote `none`.
**Full-plan review** — `code-review-full`'s verdict and findings from Step 7.
```

A filled excerpt, for calibration — match its density, not its domain:

```markdown
**Base** — `a41c9e2`
**Прогресс** — `3 из 12`

| U | Status | Executor used | Escalated | Commit |
|---|---|---|---|---|
| U3 | committed | mechanical-worker | — | `5b0d7f1` |
| U4 | committed | impl-lite | — | `c81e3a9` |
| U6 | committed | impl-critical | from impl-hard: `HARDER_THAN_EXPECTED` — два вебхука на одну оплату гоняются, нужна блокировка строки | `9e22c40` |

**Decisions** — U6: ключ идемпотентности `payment_intent_id`, unique в `payments.idempotency_key`; повтор возвращает сохранённый результат.
**Evidence** — U4: test-first, red из отчёта worker (2 падения в `order.test.ts`). U6: test-first, red witnessed в `PHASE tests-only` (4 падения в `pay-webhook.test.ts`).
**Grade corrections** — U6: каскад не учёл конкурентный внешний ретрай провайдера (signal 6); High верно, но без `impl-critical` не хватило.
**Cross-unit watch** — U4: `OrderStatus` в U4 — строковый union, в U2 — enum; сверить в Step 7.
```

## Before you finish

- Every attempted unit has one commit, mapped to it by its `Plan-Unit:`
  trailer — Step 5.5.
- No production code in the diff was written by the orchestrator — Step 5.
- Every unit ran on the executor the plan named, or a recorded one-tier
  escalation — Steps 2, 6.
- Every unit has an evidence strategy and the evidence it owes, taken from the
  worker's report, never reconstructed from the diff — Steps 4b, 5.3.
- Every listed scenario exists as a test that would fail if the behavior
  broke — Step 5.3.
- Every High and risk-floor unit had its red witnessed in a `tests-only`
  phase — Step 4b.
- The plan document is byte-identical to how the run found it — Step 1.
- The chat showed `План: <сделано> из <всего>` after the committed set was
  known and after every commit — Step 1, Step 5.6.
- The run report names grade corrections — Step 6.
- The progress file next to the plan matches the `Plan-Unit:` trailers, and
  its last commit carries the final review verdict or the stop reason —
  Step 1, Step 5.5.
- `code-review-full` ran once after every unit in scope was committed, and
  at most once more over the fix commits; it checked the definition of done,
  and every verdict is recorded — Step 7.
- When the final review found problems, the progress file listed every fix
  as a task before the first fix, and each row ends `✅ исправлено`,
  `📝 в отчёт` or `⛔ остановлено` — Step 7.

## References

- `executor-catalog` (skill) — name → agent, nesting, escalation, review
  routing, and the dispatch contract.
- `code-review-unit` (skill) — the per-unit review invoked at Step 5.4, and the
  verdict that loop honors.
- `code-review-full` (skill) — the whole-run review at Step 7, plus one re-review over the fix commits.
- `references/progress-file.md` — the progress file: units table, the fixes section after the final review, statuses, commits.
- `executor-catalog/references/worker-prompt.md` — the packet and the report
  format, used verbatim per dispatch.
- `references/context7.md` — the Step 2b library-docs procedure; read before
  the first dispatch when a unit calls a public library API. Context7 is not a
  stage and not a substitute for language skills.
- `references/two-phase-dispatch.md` — the witnessed-red protocol; read before
  dispatching a High or risk-floor unit.
- `pipeline` (skill) — read it after `code-review-full` closes the run.
  The reviews inside this run stay automatic. The handoff to the next
  stage is a question, per `pipeline` → "Asking before a transition".
  Do not list the rest.
