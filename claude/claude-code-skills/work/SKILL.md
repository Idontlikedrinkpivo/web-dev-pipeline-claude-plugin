---
name: work
description: >-
  Executes a finished plan: each unit to its named executor, reviewed, a commit per unit. Use for «выполни план»,
  «запусти работу», «продолжи прогон», or a code change asked in chat outside a run («поправь…», «сделай поле
  необязательным»).
---

# Execute an Implementation Plan

The plan already decided the work, the order, and who does it. This skill's
job is to honor that routing and keep the tree green — not to re-plan, and not
to implement the work itself.

**The orchestrator writes no production code.** Every unit goes to the
executor the plan named, and a review fix goes back to that executor or to
`mechanical-worker` — even a one-liner. The grade picks the packet and the
review roster. An orchestrator that types the fix itself skips that loop.

**Tests come from the documentation, before the code.** The design already
fixed the signatures, the states, the error mapping, and the acceptance
criteria, so a test here is not exploration — it is the transcription of a
settled contract. Every behavior-bearing unit turns its `Тестовые сценарии` into
tests, observes them fail for the right reason, and only then gets an
implementation.

TDD is the **order inside a unit**, never a second unit and never a second
commit. A unit is still one green commit: the failing test and the code that
answers it land together. Splitting them into a `test:` commit and a `feat:`
commit doubles the dispatch and breaks the one invariant the plan is built on.
Tests are not nested either: choosing what to assert from an invariant row is
judgment, and it belongs to the unit's own implementer — `mechanical-worker`
may only replicate an assertion that implementer already wrote. Every line the user sees, between tool calls too, is in their language (`pipeline` → Names).

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
**stop and report**, not an improvisation: the unit's row `⛔ остановлено:
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
| Stack skills | yes | chosen per unit from §1 «Стек» and the unit's files — `typescript`, `react`, `python`, the library skills — plus any the user attached, forwarded as `STACK SKILLS` (`references/stack-skills.md`) |
| `frontend` and `web-design-guidelines` skills | for frontend units | every `impl-ui` unit, and any unit whose `Файлы` are browser UI code, gets them in `STACK SKILLS` without being attached: the `frontend` `SKILL.md` plus the one `references/<profile>.md` that matches architecture §1 «Стек» (or the line `no profile — <stack>`), and the `web-design-guidelines` `SKILL.md`, each by its absolute path. Backend units never get them |

### Readiness gate

Before any dispatch, check the plan carries, on **every** unit: `Сложность`,
`Исполнитель`, `Файлы`, `Образец`, `Зависит от`, `Тестовые сценарии`, `Проверка`. Also
check every `Исполнитель` and `Вложенный` name exists in
`executor-catalog/references/assignable-implementers.md` — not merely
somewhere in the catalog.

A plan missing these is not executable here. Do **not** infer a grade, and do
not pick a model yourself — name the units that are incomplete and hand back
to the `plan` skill. Inferring the routing at execution time is how a plan's
economics quietly become the session model's economics. For the same reason,
never override a named `Исполнитель` because the work "looks easy": the plan
graded it with the fields in front of it; you have less context, not more.

**Also confirm `plan-review` passed the plan as it is now** — the `review`
line of `plan_state.py` (Step 1). `plan-review.md` beside the plan opens with
`Verdict: PASS` and a `checked:` line holding the sha256 of `plan.md`; a plan
appended after its review (fix units, a forgotten unit) has another hash, and
its new units would reach workers unchecked. That gate is where a dependency
cycle, an uncoverable invariant, a dangling citation, or a miscalibrated grade
is caught, and each of those defects is far more expensive once workers are
running against it. Any `review` line but `PASS · checked … = plan.md` — no
file, another verdict, `STALE`, no `checked:` — means the gate did not pass:
run it and its revise rounds now, the way `plan` runs them (`plan` step 6),
without asking. Only a `STOP` there — the documents have a gap — or revise
rounds that stop making progress end the run before its first unit, with the
reason in the chat and the run report.

## Workflow

### Step 1. Set up once

Read the plan's §1 digest, §2 unit map, §4 waves, and §5 критерии готовности.
Read individual `### U<n>.` blocks lazily — one when you dispatch it, not all
at the start.

**Where the run stands comes from git, never from memory.** At the start,
after any context compaction, and whenever you are unsure, run:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/plan_state.py" documentation/plans/<version>/plan.md
```

A unit is done when its `Plan-Unit: <version>/U<n>` trailer is anywhere on the
iteration branch (`git log main..iteration/<version>`), so a second run in the
same iteration — units appended to the plan, a fix plan — sees the first run's
units as done. The run's scope is the `todo` line unless the user narrows it;
`ready` is what may be dispatched; `count` gives both numbers of the progress
line. A unit with a trailer is never dispatched again: re-dispatching finished
units after losing your place is the single most expensive way a run fails.
A follow-up that is not in the plan changes neither number.

- **The `where` line.** A linked worktree with no `documentation/plans/` (out
  of git): stop and tell the user to open the session in the main folder the
  line names. One with the plans folder linked in is an older iteration being
  finished (`references/run-hygiene.md`). On another branch, switch to
  `iteration/<version>` (`pipeline` → Service version); never run on `main`.
- **Hygiene and the run base.** Read `references/run-hygiene.md` now — the test
  database, commits, the orchestrator's own commits, executors in the shared
  tree. `BASE` is the HEAD the last whole review covered (this run's start on a
  first run); record it in the run report before the first dispatch. It bounds
  Step 7's diff and nothing else.

**The run report** (`references/run-report.md`) is a file at
`$(git rev-parse --git-dir)/pipeline-work/<version>-run.md` — outside the
tree, so the plan stays byte-identical and no unit's `Файлы` grows; a second
run in the iteration adds its own section under its own BASE. Append to it
after every commit and read it back after a compaction. Its «В работе» line
lists each dispatch still out — `U7 → impl-medium (задача <id>)` — written
before the `Agent` call and cleared when it returns. After a compaction a
unit listed there is still running: wait for its result, or confirm its task
ended, and never send it to a second executor.

**The resume note.** On start read `documentation/plans/<version>/resume.md`
when a run left one (`pipeline` → `references/pause-and-resume.md` → Picking
up). Refresh it after every commit and every stop, and delete it when the run
closes (Step 7): a note left behind sends the next session after a run that
is over.

**The task list** has one task per unit in scope, named from the unit's goal
with the U-id appended (`Add order aggregate (U3)`). Do not edit the plan
document — progress lives in commits, the task list, and the progress file.

**The progress file and its line.** Create — on a resumed run, rebuild from
git — `documentation/plans/<version>/progress.md` per
`references/progress-file.md`; it is never committed (`pipeline` →
`references/service-version.md` → Plans stay out of git). The chat gets it only as **the progress line**: with the file's
count set from `plan_state.py`, run

```bash
python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/progress_link.py" documentation/plans/<version>/progress.md
```

(add `--desktop` when this session has the built-in browser) and paste the
one line it prints, as printed — never a link written by hand. Post it before
the first dispatch, and again after a resume or a compaction before the next
one: a run started without it is invisible until its first commit. Post it
after every Step 5 commit, every stop and every fix of the final review, and
as the run's last message, so a user who closed the page or stepped away
reopens it from the last message.

### Step 2. Resolve the routing table

Read `executor-catalog` and build a small in-run table: for each distinct
`Исполнитель` and `Вложенный` name in the plan, `Name | subagent_type` — the
`subagent_type` is `dev-pipeline:<name>`, since every row is its own agent; you
may append the model and effort read from that agent's file. Resolve once,
reuse for the run. Print that table in this turn before the first `Agent`
call. Every dispatch in this run — workers, reviewers, follow-ups — goes out
under the catalog's Dispatch contract: no `model` (only a model the user names
for one call, on their own), no permission-mode override, no question about
models. Read that section with the rows.

An agent the `Agent` call does not know is not installed: stop and tell the
user to install or update the `dev-pipeline` plugin and restart the session,
per the Dispatch contract. An alias the harness rejects inside an agent file
is handled by the catalog's Slug hygiene: stop on that tier and report it with
the tier name and the file. Neither is fixed by adding agents or executor
setup to the project.

### Step 2b. Refresh current library docs once

The worker has no chat history and may have no MCP, so you fetch library docs
once, here, and paste slices into each packet — never tell a worker to look
them up itself. When any unit calls a public library API, read
`references/context7.md` now and follow it; a missing MCP is a skip, not a
stop.

### Step 3. Pick the next unit or wave

A unit is ready when every id in `Зависит от` is done — the `ready` line of
`plan_state.py`. Among ready units:

- **Serial** by default — one unit, one dispatch, one commit.
- **Parallel** only when all four hold (cap a wave at three or four):
  - the plan marks the peers `Параллельно: yes`;
  - their `Файлы` are genuinely disjoint in the current tree;
  - the harness gives each worker an isolated workspace — in Claude Code,
    pass `isolation: "worktree"` on each parallel `Agent` call, its packet's
    `WORKTREE yes` and every path in it, and in files it reads, relative;
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

**The Low batch at a wave boundary.** When the last unit of a §4 wave is
committed — and before Step 7 in any case — run `code-review-unit`'s Low
batch over the Low units committed since the previous batch, before the next
wave's first dispatch. Low units get no review of their own, so a run that
skips this step commits them unreviewed. Its verdicts land as fix commits on
top (Step 6, **A fix after a commit**).

Do not re-scope the run into sessions ("phase 1 of 3 for today"). Context
pressure is handled by dispatching units and resuming from git (Step 1), not
by splitting the run.

### Step 4. Dispatch

Build the packet from `executor-catalog/references/worker-prompt.md`. Fill
every slot: paste the cited design excerpts rather than telling the worker to
go read the architecture, list the exact files, carry the unit's `Подход`,
`Тестовые сценарии` and `Проверка` verbatim — «Меняет символы» and «Не
затрагивается» too, into `SYMBOLS CHANGED` and `NOT TOUCHED` — list in `STACK SKILLS` the absolute
paths chosen by `references/stack-skills.md` (the `frontend` skill, its one
profile and `web-design-guidelines` for a frontend unit too — see Inputs),
paste `CURRENT LIB DOCS` from Step 2b, fill `FROM DEPENDENCIES` from the run
report's `Decisions` of every `Зависит от` unit, and include the `DELEGATION`
block only when the unit has a `Вложенный` row — nesting hands typing to
`mechanical-worker` under the decision-maker, never extra horsepower; more
reasoning is a recorded escalation (Step 6). `PATTERN TO MIRROR` is the unit's
`Образец` field verbatim; do not pick a pattern yourself — a pattern chosen at
execution time is a design decision nobody reviewed.

Dispatch with the Step 2 row, after the unit is written into the run report's
«В работе» line (Step 1) and its progress row reads `🔄 в работе`.

Grade-specific expectations to state in the packet:

| Grade | What the worker is told |
|---|---|
| **0** | apply the shape exactly, touch nothing else, no design latitude |
| **Low** | mirror the named pattern; if the pattern does not fit, report rather than invent |
| **Mid** | the remaining local decisions are yours; list each one under `DECISIONS` in the report |
| **High** | design the missing part inside the cited boundaries, and prove the edge cases the scenarios name |

### Step 4b. Name the unit's evidence strategy in the packet

Write one into the packet's `EVIDENCE STRATEGY` slot; what each owes is in
the packet itself (`worker-prompt.md`). The unit's `Тестовые сценарии` and the
state of the code it touches decide it — not the grade alone:

- `test-first` — the unit adds or changes behavior on a new surface; the
  default for any unit with real scenarios.
- `characterization-first` — it changes behavior that exists and is
  untested. Legacy code is the one honest exception to test-first: demanding
  a red first test where none exists rewards guessing at current behavior
  instead of pinning it.
- `smoke` — packaging, config, styling, wiring with no unit-level behavior.
- `none` — the plan's scenarios say `none — <reason>` (grade 0 and similar).

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
   unit's `Файлы` is a scope breach: revert it. If the unit truly needed it,
   the plan mis-listed the footprint — record why in the run report and
   re-dispatch with the corrected `Файлы` (Step 6), so the review sees the file
   inside the unit's scope instead of flagging it as a breach. A deleted or loosened earlier test, or a left `.only` / `.skip`, is a return.
2. **Check the diff against the unit spec.** Does it implement the cited
   design, or something adjacent? Does it re-decide something the design
   already fixed?
3. **Run the checks** (through `scripts/run_check.py`) — `lint`, `typecheck` (tests too) and the unit's tests plus what the plan names for
   this ring (`repo-scaffold/references/quality-gates.md`). This run is authoritative; the worker's
   self-check is not. Then check the proof, not just the green: every scenario
   the plan listed exists as a test in the diff and asserts what the scenario
   names (a test named after a scenario that asserts nothing reports coverage
   that does not exist), and the details file's evidence matches what the diff
   shows. **A behavior-bearing unit returning `DONE` with
   no observed red and no recorded exception is not done** — send it back for
   the evidence rather than committing on the claim. `RED OBSERVED` cannot be
   reconstructed after the fact, which is exactly why an empty one is a return
   and not a note in the report.
4. **Review by grade** — first set the unit's row to `🔍 ревью` (the page shows the user where the run
   is); then `code-review-unit` does the review, and your part is its inputs and its verdict:
   1. Write the diff to a file under `$(git rev-parse --git-dir)/pipeline-work/`.
      Never paste it: pasted text stays in your context for the rest of the
      run and brings on the compaction Step 1 exists to survive.
   2. Invoke `code-review-unit` with the unit spec, that diff path, the cited
      design excerpts, the stack skills' review sections, the worker report, and the findings already recorded
      this run. It sizes its own roster from the grade (0 needs no dispatch,
      Low waits for the batch of Step 3, an `impl-ui` unit gets its own pass
      at any grade) and returns findings plus one verdict.
   3. Before acting on `RETURN_TO_EXECUTOR`, confirm each blocking finding's
      quoted line exists in the diff (for a missing scenario test, in the
      unit's `Тестовые сценарии`). Drop one that does not to the run report
      instead of sending it back: a false P1 costs a re-dispatch and a round that
      closes nothing real.
   4. Honor the verdict. `COMMIT` continues to 5. `FIX_THEN_COMMIT` goes to
      `mechanical-worker`. `RETURN_TO_EXECUTOR` re-dispatches the unit's own
      implementer with the findings. `STOP` (a design gap) stops the run and goes to
      the user — Step 6.
      P2/P3 never hold up the commit; they land in the run report.
   5. Copy every `OPEN` cross-unit suspicion into the run report's
      **Cross-unit watch** for Step 7.
5. **Коммит** — its own call, after 5.3's output was read green; the unit's
   `Коммит` message with `Plan-Unit: <version>/U<n>` in the last paragraph
   beside `Co-Authored-By:` (`references/run-hygiene.md` → Commits), staging only that unit's files —
   never `git add .`, which drags a sibling unit's half-work into this commit —
   then set the unit's row in the progress file to `✅ готово` with its
   review verdict. Never batch several units into one commit because it was
   faster. Do not stage a contract document (SRS, OpenAPI, DB schema,
   architecture, UI spec) with a unit: a document changes only in its own
   commit for a changed decision (**A decision changed during the run**).
6. **Update the task list, the run report** (the unit's row, the worker's
   `DECISIONS`, «В работе» cleared) **and the resume note**, post the progress
   line (Step 1), check the context (`references/run-hygiene.md` → Context), then move on. When the run stops on a unit instead (a
   design gap, rounds that stopped making progress), set that row to
   `⛔ остановлено: <причина>`.

### Step 6. Handle a bad return

| Return | Move |
|---|---|
| `DONE_WITH_CONCERNS` | route the concern to a reviewer before committing — the grade's reviewer, or a single `review-medium` pass on that unit for grade 0 and Low; commit only after the concern is closed or explicitly accepted |
| `BLOCKED` on a missing file or contract | if the plan simply mis-listed `Файлы`, re-dispatch with the corrected list; if a design decision is missing, **stop and ask the user** — the answer is a changed decision (below) before the re-dispatch |
| `BLOCKED` / `HARDER_THAN_EXPECTED` on difficulty | escalate exactly one tier per `executor-catalog`, carrying the previous report. An `impl-ui` unit is not on that ladder: re-dispatch `impl-ui` with the report, round after round while it makes progress |
| Scope breach | revert the out-of-scope part, re-dispatch the unit narrowed |
| A red test made green by editing its assertion | treat as `BLOCKED`, not a pass — it hides a real conflict between the scenario and the design |

**Repeat until it passes.** How many rounds a unit gets, what each round
carries and when the rounds stop is `pipeline` → `references/convergence.md`,
the one rule for every retry here — there is no separate attempt budget. What
is particular to code: a `FIX_THEN_COMMIT` fix by `mechanical-worker` is
confirmed by the orchestrator's own check; at `impl-critical`, when the
premise check finds the approach itself false (or cannot tell), the next round
is two approaches from one base, picked by the tests
(`references/two-approaches.md`); the Ревью cell shows the rounds
(`RETURN_TO_EXECUTOR ×2 → COMMIT`).

**A fix after a commit** — from a Low batch review or from the final review —
is a new commit on top, never a rewrite of history. It goes to the executor
the verdict names (`mechanical-worker` for a mechanical finding, the unit's
own implementer for `RETURN_TO_EXECUTOR` / `RETURN_TO_UNIT`), passes your
Step 5.3 checks, and has one review per round — a Low-batch fix
`code-review-unit` over its own diff (a mechanical one your own check), a
final-review fix `code-review-full`'s re-review, never both. It carries the trailer of the unit it fixes
(`Plan-Unit: <version>/U<n>`); a fix that spans units carries
`Plan-Unit: <version>/review-fix-<n>`. List every such commit in the
run report, so `code-review-full` counts it as mapped.

**A decision changed during the run** — the user answers a stop, changes
their mind («давай по-другому»), or a fact overrules a document. Before
the next dispatch, follow `pipeline` → `references/decision-changes.md`:
a line under «Изменённые решения», every document that states the old
decision fixed through its writer, one commit with no version change and the
trailer `Plan-Unit: <version>/decision-<n>`, so `code-review-full` maps it.
Later packets carry it as `CHANGED DECISIONS`; a committed unit built on
the old decision gets a follow-up commit, as in **A fix after a commit**;
a change that needs a new unit is a plan change — stop and ask. A run
that leaves a changed decision only in code has failed this step.

Escalations and grade corrections are recorded in the run report only. Never
write them back into the plan: the next run must re-derive the tier from the
unit, and a plan carrying scars stops being a decision artifact.

### Step 7. Close the run

When every unit in scope is committed, first run these checks yourself and save
each output under `$(git rev-parse --git-dir)/pipeline-work/`:

- **Критерии готовности** — every command in the plan's §5, with its exit code, on HEAD after the last commit. A browser suite first opens
  its e2e section in `progress.md` and posts the progress line, then runs after the verify skill's doctor
  (`.claude/skills/verify/`) says READY — with none, write and prove it first (`deploy-topology` →
  `references/verify-skill.md`; its commit carries `Plan-Unit: <version>/verify-skill`) — on parallel stands,
  and cleans up per `ui-test-cases` → `references/parallel-stands.md` (a stand not yet copyable is a question
  there, not a silent single stand; making it copyable is its own commit with `Plan-Unit: <version>/stand`).
- **Health and mutants** — `references/health.md`: duplicates, complexity and sizes against BASE, mutants over the
  run's diff; a simplifier pass lands what grew before the review, as its own commit with the trailer
  `Plan-Unit: <version>/health-<n>`. **Dead-code report** — `knip` for TypeScript, `vulture` for Python (another
  stack: its usual unused-code tool). Use the repo's config when it has one; otherwise run it with defaults and say
  so in the run report. Check the tool's current flags against the installed version; a detector that cannot run
  is noted, not skipped silently.

Then invoke the `code-review-full` skill once over the whole run: the plan, the full diff `BASE...HEAD` (BASE from
Step 1, handed over as a file path, as in Step 5.4), the design documents
it cites, the declared security requirements (the SRS's Security NFR rows and
the architecture's security decisions table), this run's report so far
(including grade corrections and the cross-unit watch list from Step 5.4), the
критерии готовности with its saved output, the «Здоровье кода» table, and the dead-code report. It is the
only place that checks what no single unit's review could — drift between
units, aggregate coverage of invariants and ACs that needed more than one unit,
and the критерии готовности itself, with its own lenses and verdict rather than
an inline checklist here.

Honor its verdict the same way: `PASS` closes the run, `FIX_THEN_CLOSE` routes
mechanical findings to `mechanical-worker` as their own follow-up unit(s) before
closing, `RETURN_TO_UNIT` re-opens the named unit through its own executor,
`STOP` goes to the user with the findings attached — and the user's answer
is a changed decision, landed in the documents before the fix.

Anything but `PASS`: before the first fix, add «Исправления по финальному
ревью» to the progress file — every finding a row with who fixes it and
`⏳ ждёт` (`references/progress-file.md` → Fixes after the final review) —
and post the progress line, saying the fixes are the section at the bottom of
the page. Each fix then lands like a unit — your Step 5.3 checks, its own
commit with its trailer, its rows — and its review is the re-review: after each
round of fixes, run `code-review-full` again over that round's fix commits only,
with its re-review packet — never a second time over the whole diff — until `PASS`,
while each round makes progress (`pipeline` → `references/convergence.md`);
when the rounds stop making progress, stop and take the open findings to the
user.

**Close.** Write the verdict path into the `Финальное ревью:` line
(`RETURN_TO_UNIT → исправлено → PASS`, or plain `PASS`), write the run
report (`references/run-report.md` — read it now), stop every watcher the run
started, and delete `resume.md`. The run's last message is the progress line,
then the question about the next stage: read `pipeline` → "Asking before a
transition" now and ask it as that section says — stage 12's row offers
`ui-test-cases` mode run when the product has screens, else
`security-audit`. The reviews inside the run stayed automatic; this handoff
is a question. No PR, no push, no CI watching: the branch stays local, and
push and PR are the user's step after the whole pipeline.

## A change asked in chat outside a run

When no run is in progress and the user asks in the chat for a change to the
built code — «сделай поле необязательным», «убери предупреждение» — it is not
committed on the executor's word. The executor writes it, `code-review-unit`
reviews it, the tests it can break run on the branch, and only then is it
committed; the report line names both checks
(«Ревью: … · тесты: …»). How to size it, the steps and the line:
`references/chat-change.md` — read it before the first dispatch of such a
change.

## Before you finish

- Every unit in scope has its own commit with its `Plan-Unit:` trailer, plus
  only the fix commits Step 6 allows, each with its trailer — Steps 5.5, 6.
- No unit with a trailer was dispatched again; the «В работе» line was
  checked after every compaction — Step 1.
- No production code in the diff was written by the orchestrator; every unit
  ran on the executor the plan named, or on recorded escalations — Steps 2, 5, 6.
- Every unit has an evidence strategy and the evidence it owes, taken from the
  worker's report, never reconstructed from the diff; every High and
  risk-floor unit had its red witnessed — Steps 4b, 5.3.
- Every Low unit went through a batch review, every `impl-ui` unit through
  its own — Steps 3, 5.4.
- The plan document is byte-identical to how the run found it — Step 1.
- The progress line came from `progress_link.py`: before the first dispatch,
  after every commit and stop, and last — Step 1.
- Every changed decision is under «Изменённые решения» and committed in
  its documents before the next dispatch — Step 6.
- `code-review-full` ran once over the whole diff, then over each round's fix
  commits only, and every verdict is recorded; when it found problems, the
  progress file listed every fix before the first one — Step 7.
- `resume.md` is gone, the watchers are stopped, and the next stage was
  offered as a question — Step 7.

## References

Each is named where it is read: `scripts/plan_state.py` (Step 1), `references/progress-file.md` (Steps 1, 7),
`references/context7.md` (2b), `references/two-phase-dispatch.md` (4b), `references/two-approaches.md` (6),
`references/health.md` and `references/run-report.md` (7), `references/chat-change.md`; the skills
`executor-catalog`, `code-review-unit`, `code-review-full`, and `pipeline` → `references/decision-changes.md`,
`references/convergence.md`, `references/pause-and-resume.md`.
