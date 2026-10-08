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
| Branches beyond the iteration's, the merge into `main`, CI | the user's shipping flow |
| Docker/compose topology for test, dev, prod | `deploy-topology`, once the plan's units are committed |

**`work` runs on its own from the first dispatch to the run report**:
reviews, fixes and re-reviews go round by round without asking. It stops and
asks the user only when a unit cannot pass — a decision the documents do not
make (`BLOCKED` on a missing design decision, a `STOP` from a review) or fix
rounds that stop making progress (`pipeline` → `references/convergence.md`). That is a
**stop and report**, not an improvisation: the unit's row `⛔ остановлен:
<причина>`, and in the chat what blocks it, what was tried, and what the user
can decide — that question ends the turn. Every other turn ends with the
next dispatch running, called before the chat line; never «продолжать?»
(`pipeline` → `references/progress-files.md` → Keeping the run moving).

**A decision that changes during the run goes into its documents at
once**, committed before the next dispatch, without the user asking —
Step 6, **A decision changed during the run**.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Plan path | **yes** | or `plan.md` of the open version folder (`documentation/plans/<version>/` without `summary.md`) when the user gives none — say which file you picked |
| `executor-catalog` skill | **yes** | read before the first dispatch; it is the only source of name → agent routing (each agent's file holds its model) |
| The design documents the plan cites | on demand | read the cited section when building a worker packet, not up front |
| Context7 MCP (`resolve-library-id`, `query-docs`) | no | live library docs for the packet's `CURRENT LIB DOCS` (Step 2b). Missing MCP is a skip, not a stop |
| Language skill files the user attached | no | forwarded as `STACK SKILLS`. Do not invent a stack pack |
| `frontend` and `web-design-guidelines` skills | for frontend units | every `impl-ui` unit, and any unit whose `Files` are browser UI code, gets them in `STACK SKILLS` without being attached: the `frontend` `SKILL.md` in full plus the one `references/<profile>.md` that matches architecture §1 «Стек» (or the line `no profile — <stack>`), and the `web-design-guidelines` `SKILL.md` in full. Backend units never get them |

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
line other than `Verdict: PASS`, means the gate did not pass: run it and its
revise rounds now, the way `plan` runs them (`plan` step 6), without asking.
Only a `STOP` there — the documents have a gap — or revise rounds that stop
making progress end the run before its first unit, with the reason in the
chat and the run report.

## Workflow

### Step 1. Set up once

Read the plan's §1 digest, §2 unit map, §4 waves, and §5 definition of done.
Read individual `### U<n>.` blocks lazily — one when you dispatch it, not all
at the start.

Branch: the iteration's `iteration/<version>` (`pipeline` → Service
version), never `main`. On another branch, switch to it first; on an
auto-generated one (`worktree-happy-otter`), say so and switch.

Build a task list from the unit map: one task per unit, named from the unit's
goal with the U-id appended (`Add order aggregate (U3)`). Do not edit the plan
document — progress lives in commits, the task list, and the progress file
next to the plan (below).

**Say the count in the chat.** `<всего>` is the number of units in this
run's scope, taken from the unit map. The default scope is every unit in
the map. `<сделано>` is how many of those have a `Plan-Unit:` trailer in
`BASE..HEAD`. A follow-up that is not in the plan does not change either
number. After the committed set is known, and again after every Step 5
commit, every stop and every fix of the final review, write one line with
the progress file's link: `План: <сделано> из <всего> ·
[progress.md](documentation/plans/<version>/progress.md)`, so the user who
closed the file or stepped away reopens it from the last message. Take both
numbers from the map and from git, not from the previous message. A resumed
or compacted session writes the line before the next dispatch.

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
План: 0 из 6 · [progress.md](documentation/plans/1.1.0/progress.md)
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
language skills the user attached, plus the `frontend` skill, its one
profile and `web-design-guidelines` for a frontend unit (see Inputs), or `none — no language skills attached`,
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
      instead of sending it back: a false P1 costs a re-dispatch and a round that
      closes nothing real.
   4. Honor the verdict. `COMMIT` continues to 5. `FIX_THEN_COMMIT` goes to
      `mechanical-worker`. `RETURN_TO_EXECUTOR` re-dispatches the unit's own
      implementer with the findings. `STOP` (a design gap) stops the run and goes to
      the user — Step 6.
      P2/P3 never hold up the commit; they land in the run report.
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
   spec) with a unit: a document changes only in its own commit for a
   changed decision (**A decision changed during the run**), and its
   version and changelog belong to `doc-versioning`, which the user
   invokes. `plan` does not call it.
6. **Update the task list and the run report file** (the unit's row and the
   worker's `DECISIONS`), write the `План:` line with the link in the chat
   (Step 1), then move on. When the run stops on a unit instead (a
   design gap, rounds that stopped making progress), set that row to
   `⛔ остановлен: <причина>`.

Fixing a worker's output yourself is the one thing this loop forbids, even a
one-liner. A failing test, a missed scenario, or a review finding goes back —
to the same executor with the finding, or to `mechanical-worker` when the fix
is purely mechanical.

### Step 6. Handle a bad return

| Return | Move |
|---|---|
| `DONE_WITH_CONCERNS` | route the concern to a reviewer before committing — the grade's reviewer, or a single `review-medium` pass on that unit for grade 0 and Low; commit only after the concern is closed or explicitly accepted |
| `BLOCKED` on a missing file or contract | if the plan simply mis-listed `Files`, re-dispatch with the corrected list; if a design decision is missing, **stop and ask the user** — the answer is a changed decision (below) before the re-dispatch |
| `BLOCKED` / `HARDER_THAN_EXPECTED` on difficulty | escalate exactly one tier per `executor-catalog`, carrying the previous report. An `impl-ui` unit is not on that ladder: re-dispatch `impl-ui` with the report, round after round while it makes progress |
| Scope breach | revert the out-of-scope part, re-dispatch the unit narrowed |
| A red test made green by editing its assertion | treat as `BLOCKED`, not a pass — it hides a real conflict between the scenario and the design |

**Repeat until it passes.** A unit is re-dispatched — `RETURN_TO_EXECUTOR`,
an escalation, a corrected `Files` — round after round until its review
says `COMMIT`, as long as each round makes progress (`pipeline` → `references/convergence.md`):
the re-review reads only what the round changed, every re-dispatch carries
the open findings and the previous reports, and a finding that survives a
fix moves the unit one tier up. A `FIX_THEN_COMMIT` fix by
`mechanical-worker` is confirmed by the orchestrator's own check. When
progress stops — a closed finding came back, a round closed nothing, a
finding survived a fix at `impl-critical` — the unit or the design is
wrong: stop and say so. The progress file's Ревью cell shows the rounds
(`RETURN_TO_EXECUTOR ×2 → COMMIT`).

**A fix after a commit** — from a Low batch review or from the final review —
is a new commit on top, never a rewrite of history. It goes to the executor
the verdict names (`mechanical-worker` for a mechanical finding, the unit's
own implementer for `RETURN_TO_EXECUTOR` / `RETURN_TO_UNIT`), passes
`code-review-unit` like any unit, and carries the trailer of the unit it fixes
(`Plan-Unit: <version>/U<n>`); a fix that spans units carries
`Plan-Unit: <version>/review-fix-<n>`. List every such commit in the
run report, so `code-review-full` counts it as mapped.

**A decision changed during the run** — the user answers a stop, changes
their mind («давай по-другому»), or a fact overrules a document. Before
the next dispatch, follow `pipeline` → `references/decision-changes.md`:
a line under «Изменённые решения», every document that states the old
decision fixed through its writer, one commit with no version change.
Later packets carry it as `CHANGED DECISIONS`; a committed unit built on
the old decision gets a follow-up commit, as in **A fix after a commit**;
a change that needs a new unit is a plan change — stop and ask. A run
that leaves a changed decision only in code has failed this step.

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
`STOP` goes to the user with the findings attached — and the user's answer
is a changed decision, landed in the documents before the fix.

Anything but `PASS`: before the first fix, add «Исправления по финальному
ревью» to the progress file — every finding a row with who fixes it and
`⏳ ждёт` (`references/progress-file.md` → Fixes after the final review),
and post the link again before the first fix, pointing at the section:
`Исправления по финальному ревью: [progress.md](documentation/plans/<version>/progress.md) — раздел внизу файла, обновляется по ходу работы.` Each fix then lands like a unit, updating its rows. After
each round of fixes, run `code-review-full` again over that round's fix
commits, until `PASS` (`pipeline` → `references/convergence.md`); when the rounds stop making
progress, stop and take the open findings to the user.

At the close write the verdict path into the `Финальное ревью:` line
(`RETURN_TO_UNIT → исправлено → PASS`, or plain `PASS`).

Stop there. The last chat line is the `План:` line with the link. No PR, no
push, no CI watching. The branch stays local: the pipeline still has
the UI acceptance run (`ui-test-cases`, when there are screens), `security-audit`, `deploy-topology` and `ci-pipeline` ahead, and push and PR are the user's
step after the whole pipeline, not after this run.

## Run report

The report's shape, filled for one run: `references/run-report.md` — read it
at Step 7, before writing the report.

## Before you finish

- Every attempted unit has one commit, mapped to it by its `Plan-Unit:`
  trailer — Step 5.5.
- No production code in the diff was written by the orchestrator — Step 5.
- Every unit ran on the executor the plan named, or on recorded
  escalations — Steps 2, 6.
- Every unit has an evidence strategy and the evidence it owes, taken from the
  worker's report, never reconstructed from the diff — Steps 4b, 5.3.
- Every listed scenario exists as a test that would fail if the behavior
  broke — Step 5.3.
- Every High and risk-floor unit had its red witnessed in a `tests-only`
  phase — Step 4b.
- The plan document is byte-identical to how the run found it — Step 1.
- The chat showed the `План:` line with the progress file's link after the
  committed set was known, after every commit and every stop — Step 1,
  Step 5.6.
- The run report names grade corrections — Step 6.
- Every changed decision is under «Изменённые решения» and committed in
  its documents before the next dispatch — Step 6.
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
- `code-review-full` (skill) — the whole-run review at Step 7, plus its re-reviews over the fix commits until `PASS`.
- `references/progress-file.md` — the progress file: units table, the fixes section after the final review, statuses, commits.
- `pipeline` → `references/decision-changes.md` — a decision that changes
  during the run: the owner document, the cascade, the commit.
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
