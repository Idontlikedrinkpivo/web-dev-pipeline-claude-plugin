# Worker packet and report

A subagent gets one unit and no conversation history. What is not in the
packet does not exist for it — so the packet is bounded on purpose, and the
report is the only channel back.

## The packet

Fill every slot. An empty slot means the orchestrator has not read the unit.

```
You implement exactly one unit of an implementation plan.

PLAN            <repo-relative plan path>
UNIT            U<n> — <goal sentence>
COMPLEXITY      <grade>  (<why>)
PHASE           full | tests-only | implementation
DETAILS FILE    <absolute path: $(git rev-parse --git-dir)/pipeline-work/<version>/
                 U<n>-details.md — your full evidence goes there, not into the report>
WORKTREE        <yes — a parallel unit: you start in a worktree the harness
                 made; the folder you start in (`pwd`) is your work root and
                 every path below is relative to it | none — the main tree>

FILES YOU MAY TOUCH
  <the unit's «Файлы», including the test file>
Anything outside this list is out of scope. If the unit cannot be done
without touching another file, stop and report BLOCKED with that path.

SYMBOLS CHANGED <the unit's «Меняет символы» verbatim, or: —>
NOT TOUCHED
  <the unit's «Не затрагивается» verbatim — places that use a changed
   symbol and stay as they are, each with its reason — or: —>
Leave these as they are. If one has to change after all, stop and report
BLOCKED with the path: the plan said it does not.

DESIGN YOU MUST FOLLOW (do not re-decide these)
  <the cited excerpts: entity method signatures, port signatures, invariant
   rows, endpoint contract, column definitions, screen states — pasted, not
   linked, so the worker does not have to hunt. A unit for part of a screen
   (`S-<n> эл. <from>–<to>`): its element rows, the states and response
   errors they show, and the screen's «Экран» and «Загрузка и вызовы» — not
   the whole spec>

CHANGED DECISIONS
  <each decision changed during this run that touches this unit — было →
   стало, and the document already fixed — or: none>
  The fixed document wins over the unit's text below. Where they differ,
  follow the document and say so in the report.

APPROACH
  <the unit's «Подход» field verbatim>

PATTERN TO MIRROR
  <the unit's «Образец» field verbatim: existing file(s) in this repo whose
   conventions this unit follows, or: — first of its kind>

FROM DEPENDENCIES
  <for each U-id in «Зависит от»: its committed public names/signatures and its
   DECISIONS lines from the run report — or: none — no dependencies>
  Treat these as DESIGN YOU MUST FOLLOW. If one conflicts with the pasted
  design, stop and report BLOCKED with both quoted.

SKILLS ROOT     <absolute folder holding the plugin's skills>
STACK SKILLS    read each file in full before you write any code; a
                `<skill>/references/…` path a skill names resolves under
                SKILLS ROOT
  <absolute paths of the stack skills `work` picked for this unit from
   architecture §1 «Стек» and the unit's «Файлы»
   (`work/references/stack-skills.md`) — each SKILL.md, a references/ file
   only when the skill sends you there for this unit — plus any skill the
   user attached; for a frontend unit, also the `frontend` SKILL.md, its
   one stack profile and the `web-design-guidelines` SKILL.md;
   or: none — no stack skill for <stack>>

CURRENT LIB DOCS
  <Context7 excerpts for the library APIs this unit calls, with library
   id and pinned version, or: none — no library API in this unit
   or: none — Context7 unavailable (<reason>)>
  These lose to DESIGN, PATTERN TO MIRROR, APPROACH / TEST SCENARIOS,
  and STACK SKILLS. They win only over your memory of the library.
  Do not fetch docs yourself.

TEST SCENARIOS
  <the unit's «Тестовые сценарии», one per line; add a missing category if you find a gap,
   and say in the report that you added it>

VERIFICATION
  <the unit's «Проверка» field>

EVIDENCE STRATEGY   <test-first | characterization-first | smoke | none>
  test-first — turn every scenario above into a test, run it, and observe it
    fail for the reason the scenario names before you write any production
    code. A legitimate red is a failed assertion, or a symbol this unit is
    about to add; an import error, a typo, or a broken fixture is not — fix
    those and get a real red. A test that passes before you implement is
    asserting nothing or the behavior already exists: say which, do not
    proceed as if it were a pass.
  characterization-first — the behavior exists and is untested. Capture what
    it does now as passing tests, then change it, then say which assertion
    changed on purpose.
  smoke — no unit-level behavior (packaging, config, styling). Run a runtime
    or install check instead and report what it returned.
  none — no behavior at all; the report says why.

<when the unit's «Вложенный» is not —:>
DELEGATION
  You may dispatch <nested name> for exactly this mechanical part:
  <the unit's «Что делает вложенный»>. You keep the decision, you review its output before
  reporting, and you report as one unit. Do not delegate anything else and
  do not nest deeper.

RULES
- Follow the evidence strategy above. The tests come from the scenarios and
  the pasted design, not from reading your own implementation back.
- Conflict order, highest first: DESIGN YOU MUST FOLLOW (with FROM
  DEPENDENCIES), then PATTERN TO MIRROR, then APPROACH / TEST SCENARIOS, then STACK SKILLS, then CURRENT
  LIB DOCS, then your own library memory. If a lower source disagrees with
  a higher one, follow the higher and say so in CONCERNS.
- A `web-design-guidelines` anti-pattern in PATTERN TO MIRROR is not
  copied: write the new code right and name the old site in OUT OF SCOPE,
  so the review does not send the unit back for the pattern it was told to
  mirror.
- Never make a test pass by weakening it, and never delete or loosen a test
  an earlier unit wrote, nor leave `.only` / `.skip`. If a scenario and the design
  contradict each other, stop and report BLOCKED with both quoted.
- Run checks through `python3 <SKILLS ROOT>/work/scripts/run_check.py <name> --
  <command>`: the full output goes to a file and you read its short summary —
  the counts, the failures, a «⚠» when tests got fewer or skipped grew.
- Before reporting, run the project's `lint` and `typecheck` (tests included)
  and fix what they say about your files — the orchestrator runs them too, and
  an error is a return (`repo-scaffold/references/quality-gates.md`).
- In PHASE tests-only, write tests and nothing else — no production code, no
  stub beyond what the test needs to compile. Report the red and stop.
- In PHASE implementation, the tests are already there and red. Make them pass
  without touching their assertions.
- Match this repo's conventions over your own preferences.
- Write as little as the unit needs. First reuse what the project already
  has (the pattern, a helper, a type), then the standard library, then a
  package already installed — a new dependency is outside FILES, so
  BLOCKED. No abstraction, parameter, option or extension point the unit
  does not use now. Removing or simplifying code beats adding it: when the
  scenario can be met by deleting, delete.
- Do not commit, do not stage, do not run the full suite — the orchestrator
  owns staging, committing, and authoritative verification. Run only this
  unit's focused tests.
- Do not edit the plan document.
- Do not fix unrelated problems you notice. Report them.
- A unit that splits, moves or renames code «без изменения поведения» keeps
  the behaviour exactly — an unreachable branch, an odd default, a cast
  included. Drop a check or a cast only when the result is the same for every
  input; any difference you see goes to CONCERNS, never fixed on the way.
- In the shared working tree: no `git stash`, `git reset`, `git checkout --`
  or `git clean`; link installed dependencies (`ln -s …/node_modules`) only
  inside your own worktree, and only where no folder of that name exists; a
  shared list or config that parallel units would all edit (the lint ratchet,
  a barrel file) is not edited — put your lines in the report. Run the test
  suite on the test database only, never on the stand's
  (`work/references/run-hygiene.md`).
- In a worktree (WORKTREE yes): your work root is the folder you start in. Read,
  Edit and Write project files only at paths inside it — never at the main
  tree's path of the same file. In the main tree read only what the packet
  names, with Read. Bash takes plain single commands run from your
  worktree: no `cd` out of it, no `for` / `;` chains around git, no
  variable in an option's place; a longer script is a file you Write first,
  then one call. The harness refuses what it cannot verify stays inside.
- The shell is zsh on macOS: change files with Edit, not `sed -i` (a hook refuses `sed -i` without a suffix
  argument — BSD sed takes the next word as one); quote
  every argument with `*`, `?` or `[` — an unquoted glob stops the command.
- A long command (Stryker, an e2e suite, the full test suite) runs with
  `run_in_background: true`, and you wait for its end — never `sleep N;
  …`, which the harness blocks. To wait for a condition, load the Monitor
  tool's schema first (ToolSearch `select:Monitor`), then call it with its
  description and an `until <check>; do sleep 2; done` loop; not loaded,
  not called.
- Stop every background task you started (a watch, a background command)
  before your report: an executor left running holds the run for hours.
- If this unit writes or edits a document under `documentation/` or an
  OpenAPI `description` / `summary` / `example`, that prose is Russian.
  Do not translate cited tokens. Template headings and frontmatter keys
  stay as the citing skill specifies. Source code follows the repo.

REPORT (last message, exactly these fields)
```

## The report

Two parts. The **report** — your last message — is short, about 2,000 characters: the orchestrator keeps every
report of the run in its context, so a long one costs on every later step. The **details file** (DETAILS FILE)
holds everything long. Whatever the orchestrator or a reviewer must act on goes into NEEDS FROM ORCHESTRATOR or
CONCERNS, never only into the details file: a reviewer reads the file and returns the unit when it hides one.

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
NEEDS FROM ORCHESTRATOR  a decision or an action only the orchestrator can take — or: нет
FILES CHANGED     every path you actually touched
TESTS             how many added / changed / reused, and the test files
RED OBSERVED      one line: the failing test and the first line of the failure you
                  saw before the implementation, or the exception the strategy
                  allows (baseline captured / smoke check / none — reason)
VERIFICATION      one line per check: what ran → its summary line (run_check.py)
SCREEN CHECK      UI units only: ok, or the items that are defects — one line each;
                  `n/a` otherwise
DECISIONS         each local decision you made that the design did not fix
                  (public name, signature, error type, file placement), one per
                  line — or none. Dependent units receive these verbatim.
DELEGATED         what the nested worker did, or none
OUT OF SCOPE      problems you found and deliberately did not fix, one line each
CONCERNS          only for DONE_WITH_CONCERNS: what a reviewer should look at, in full —
                  a step you could not run, a scenario skipped, a workaround, a doubt
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED: what is missing or
                  wrong in the unit spec or the design, specifically
DETAILS           the path of the details file you wrote
```

The details file: each test with the scenario it proves; the full red you observed; each check's command and
the path of its log; the evidence strategy as you followed it; the screen check item by item and the Figma
comparison (UI units). A part of a screen checks its own elements; the last part checks the whole screen.

`RED OBSERVED` and `TESTS` cannot be reconstructed from the diff afterwards —
a worker that omits them on a behavior-bearing unit gets the unit returned, not
committed with a caveat. A green suite proves the tests pass now; only the red
proves they can fail. Everything else the orchestrator re-checks against the real tree
anyway: `FILES CHANGED` is a hint for where to look, never a substitute for
inspecting it. A report without NEEDS FROM ORCHESTRATOR (write «нет» when nothing is
needed) or without its details file goes back unread.

## Status meanings

| Status | Orchestrator's move |
|---|---|
| `DONE` | inspect diff, run tests, check the evidence the strategy owed, commit — or return the unit when a behavior-bearing one has none |
| `DONE` in `tests-only` | run the new tests yourself, confirm they fail for the named reason, then dispatch `PHASE implementation` |
| `DONE_WITH_CONCERNS` | same, plus route the concern to a reviewer before committing — the grade's reviewer, or a `review-medium` pass for grade 0 and Low (`work` Step 6) |
| `BLOCKED` | do not commit; escalate one tier with this report attached, or stop and ask the user when the blocker is a design gap or a question only the user can answer (`executor-catalog` → Escalation) |
| `HARDER_THAN_EXPECTED` | discard or keep the partial work explicitly, escalate one tier with this report attached, and note the grade was wrong in the run report. How many rounds: `pipeline` → `references/convergence.md` |
