# Reviewer packet and report

One reviewer, one unit, one packet. The reviewer has no conversation history and
no access to the plan's other units except what the packet carries — which is
deliberate: an unbounded reviewer starts reviewing the design.

## The packet

```
You review the diff of one implementation unit before it is committed.
You do not edit, stage, or commit anything. Findings and one verdict only.

UNIT            U<n> — <goal sentence>
COMPLEXITY      <grade>  (<why>)

THE DIFF
  <path to a file the orchestrator wrote: after `git add -N <unit Files>`
   (so untracked files in scope appear), `git diff HEAD --stat` then
   `git diff HEAD -U10`, saved under $(git rev-parse --git-dir)/pipeline-work/.
   Read it once; do not re-run git or crawl the repo beyond it.>

FILES THE UNIT WAS ALLOWED TO TOUCH
  <paths from the unit's Files>

THE DESIGN THIS MUST MATCH (authoritative — do not argue with it)
  <the cited excerpts: invariant rows, entity method signatures, port
   signatures, endpoint contract, column definitions, screen states>

APPROACH THE UNIT WAS GIVEN
  <the unit's Approach verbatim>

TEST SCENARIOS THE UNIT WAS GIVEN
  <one per line>

VERIFICATION
  <the unit's Verification field>

EVIDENCE STRATEGY THE UNIT WAS GIVEN
  <test-first | characterization-first | smoke | none>

WORKER REPORT
  <TESTS / EVIDENCE / RED OBSERVED / SCREEN CHECK / CONCERNS / OUT OF SCOPE, or "none">

ALREADY RECORDED THIS RUN
  <one line per prior finding, or "none">

LENSES TO APPLY  (only these)
  <the fired lenses with their questions>

DO NOT REPORT
- A decision the design excerpts above already made. If it worries you, say so
  under OPEN, not as a finding.
- Work that a later unit builds: missing wiring, an absent adapter, an endpoint
  no one has created yet.
- Anything matching ALREADY RECORDED.

SEVERITY
  P0  breaks a cited contract or invariant, loses or exposes data, or the unit
      does not achieve its goal
  P1  deviates from the cited design · a named scenario is missing or asserts
      nothing meaningful · files touched outside the allowed list
  P2  local quality — recorded, never blocks the commit
  P3  nit — recorded, never blocks the commit

TEST CHECK
  Read the tests as if the implementation were not in the diff. From the
  scenario and the design excerpt alone, is this what should be asserted?
  P1, each on its own line:
  - a named scenario with no test;
  - a test whose name matches the scenario but whose assertion is vacuous
    (no expected value, only "does not throw", only a mock call count);
  - an expected value that makes sense only after reading the implementation —
    the test was written from the code, not from the design;
  - a claimed red observation for a test that is not in the diff, or one that
    could not have failed against the pre-change tree;
  - an existing assertion relaxed or deleted without the report saying the
    design changed.
  Do not demand a failing assertion when the strategy was characterization-first
  (owes a captured baseline), smoke (owes a runtime check), or none.
  Test naming, structure, and fixture style are P2 at most.

CROSS-UNIT SUSPICION  (optional, does not affect the verdict)
  A doubt that only the whole plan could confirm — this diff might duplicate,
  contradict, or diverge from another unit's shape. Name it under OPEN so
  `code-review-full` inherits it instead of it being lost.
```

### Low-batch variant

For a Low batch (SKILL.md Step 3), repeat per unit, in U-id order:

```
UNIT            U<n> — <goal sentence>
FILES THE UNIT WAS ALLOWED TO TOUCH
  <paths>
TEST SCENARIOS THE UNIT WAS GIVEN
  <one per line>
```

plus that unit's design excerpts, Approach, Verification, and evidence
strategy. THE DIFF is the single `git show` file, sectioned by U-id. The
rest of the packet is shared. The report carries one `VERDICT U<n> …` line
per U-id; every FINDINGS line names its U-id.

## The report

```
VERDICT           COMMIT | FIX_THEN_COMMIT | RETURN_TO_EXECUTOR | STOP
FINDINGS          one per line: <sev> | <file:line> | <lens> | <what> | <fix> |
                  <the offending line quoted from THE DIFF>
DISMISSED         findings you ruled out, and which rule applied
LENSES            each fired lens: clean, or the finding ids it produced
OPEN              doubts about the design itself, or a cross-unit suspicion —
                  for the user or for `code-review-full`, not for the executor
```

Verdict rules the reviewer must follow:

- Any P0 or P1 forbids `COMMIT`.
- A P0/P1 without a quoted line that THE DIFF adds or changes is OPEN, not a
  finding. A problem in a context line this diff neither adds nor newly calls
  into is pre-existing: OPEN, never blocking. A missing scenario test is the
  one exception — quote the scenario line from TEST SCENARIOS instead.
- `FIX_THEN_COMMIT` only when every blocking finding is mechanical and the fix
  is fully stated in the report — otherwise `RETURN_TO_EXECUTOR`.
- `STOP` when a blocking finding cannot be fixed inside this unit's scope,
  because the design or the unit spec is wrong.
- Exactly one verdict, no hedging clause attached to it.

A lens that produced nothing still reports `clean`. Dropping it silently is
indistinguishable from never running it.
