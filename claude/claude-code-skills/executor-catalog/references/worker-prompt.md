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

FILES YOU MAY TOUCH
  <paths from the unit, including the test file>
Anything outside this list is out of scope. If the unit cannot be done
without touching another file, stop and report BLOCKED with that path.

DESIGN YOU MUST FOLLOW (do not re-decide these)
  <the cited excerpts: entity method signatures, port signatures, invariant
   rows, endpoint contract, column definitions, screen states — pasted, not
   linked, so the worker does not have to hunt>

APPROACH
  <the unit's Approach field verbatim>

PATTERN TO MIRROR
  <the unit's Pattern field verbatim: existing file(s) in this repo whose
   conventions this unit follows, or: — first of its kind>

FROM DEPENDENCIES
  <for each U-id in Depends on: its committed public names/signatures and its
   DECISIONS lines from the run report — or: none — no dependencies>
  Treat these as DESIGN YOU MUST FOLLOW. If one conflicts with the pasted
  design, stop and report BLOCKED with both quoted.

STACK SKILLS
  <excerpts from language skills the user attached that this unit needs;
   for a frontend unit, also the `frontend` skill in full and its one stack
   profile; or: none — no language skills attached>

CURRENT LIB DOCS
  <Context7 excerpts for the library APIs this unit calls, with library
   id and pinned version, or: none — no library API in this unit
   or: none — Context7 unavailable (<reason>)>
  These lose to DESIGN, PATTERN TO MIRROR, APPROACH / TEST SCENARIOS,
  and STACK SKILLS. They win only over your memory of the library.
  Do not fetch docs yourself.

TEST SCENARIOS
  <one per line from the unit; add a missing category if you find a gap,
   and say in the report that you added it>

VERIFICATION
  <the unit's Verification field>

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

<when the unit has a Nested row:>
DELEGATION
  You may dispatch <nested name> for exactly this mechanical part:
  <Nested does>. You keep the decision, you review its output before
  reporting, and you report as one unit. Do not delegate anything else and
  do not nest deeper.

RULES
- Follow the evidence strategy above. The tests come from the scenarios and
  the pasted design, not from reading your own implementation back.
- Conflict order, highest first: DESIGN YOU MUST FOLLOW (with FROM
  DEPENDENCIES), then PATTERN TO MIRROR, then APPROACH / TEST SCENARIOS, then STACK SKILLS, then CURRENT
  LIB DOCS, then your own library memory. If a lower source disagrees with
  a higher one, follow the higher and say so in CONCERNS.
- Never make a test pass by weakening it. If a scenario and the design
  contradict each other, stop and report BLOCKED with both quoted.
- In PHASE tests-only, write tests and nothing else — no production code, no
  stub beyond what the test needs to compile. Report the red and stop.
- In PHASE implementation, the tests are already there and red. Make them pass
  without touching their assertions.
- Match this repo's conventions over your own preferences.
- Do not commit, do not stage, do not run the full suite — the orchestrator
  owns staging, committing, and authoritative verification. Run only this
  unit's focused tests.
- Do not edit the plan document.
- Do not fix unrelated problems you notice. Report them.
- If this unit writes or edits a document under `documentation/` or an
  OpenAPI `description` / `summary` / `example`, that prose is Russian.
  Do not translate cited tokens. Template headings and frontmatter keys
  stay as the citing skill specifies. Source code follows the repo.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILES CHANGED     every path you actually touched
TESTS             added / changed / reused — with paths
EVIDENCE          the strategy you followed, and if it differs from the
                  packet's, why
RED OBSERVED      the failing test name and the failure message you saw before
                  writing the implementation, or the exception the strategy
                  allows (baseline captured / smoke check / none — reason)
VERIFICATION      what you ran and what it returned
DECISIONS         each local decision you made that the design did not fix
                  (public name, signature, error type, file placement), one per
                  line — or none. Dependent units receive these verbatim.
DELEGATED         what the nested worker did, or none
OUT OF SCOPE      problems you found and deliberately did not fix
CONCERNS          only for DONE_WITH_CONCERNS: what a reviewer should look at
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED: what is missing or
                  wrong in the unit spec or the design, specifically
```

`RED OBSERVED` and `TESTS` cannot be reconstructed from the diff afterwards —
a worker that omits them on a behavior-bearing unit gets the unit returned, not
committed with a caveat. A green suite proves the tests pass now; only the red
proves they can fail. Everything else the orchestrator re-checks against the real tree
anyway: `FILES CHANGED` is a hint for where to look, never a substitute for
inspecting it.

## Status meanings

| Status | Orchestrator's move |
|---|---|
| `DONE` | inspect diff, run tests, check the evidence the strategy owed, commit — or return the unit when a behavior-bearing one has none |
| `DONE` in `tests-only` | run the new tests yourself, confirm they fail for the named reason, then dispatch `PHASE implementation` |
| `DONE_WITH_CONCERNS` | same, plus route the concern to a reviewer before committing — the grade's reviewer, or a `review-medium` pass for grade 0 and Low (`work` Step 6) |
| `BLOCKED` | do not commit; escalate one tier with this report attached, or stop and ask the user when the blocker is a design gap |
| `HARDER_THAN_EXPECTED` | discard or keep the partial work explicitly, escalate one tier once, and note the grade was wrong in the run report |
