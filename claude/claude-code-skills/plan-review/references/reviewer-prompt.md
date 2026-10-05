# Plan reviewer packets and report

Two packets from one template. The **structural** packet goes to
`plan-review-medium`, the **judgment** packet to `plan-review-hard`. Both are
bounded: everything a reviewer may look at is pasted in, and neither explores
the repo beyond the file tree it is given.

Fill `LENSES` with only that packet's lenses. A reviewer given all eleven skims
the three that matter.

## The packet

```
You review a finished implementation plan before any code exists. You do not
edit the plan, the design documents, or the repo. Findings and one verdict only.

PLAN                documentation/plans/<version>/plan.md — pasted in full: §1
                    digest with its version line, the unit table, every unit's
                    fields, §5 definition of done, open-questions.md, pins

SERVICE VERSION     (structural packet only) the folder's version, the
                    manifest's current `version`, the iteration's typed
                    changes (changelog rows of this version, OpenAPI
                    info.x-changelog included, plus changes not stamped yet,
                    typed from the diff since the last tag), and whether the
                    API has external consumers (partner-versioned, `/vN` path)

DESIGN DOCUMENTS CITED BY THE PLAN (de-duplicated)
  <every section, id, operationId, table, and screen any unit's Docs names,
   pasted once each — this is what citations are resolved against>

COVERAGE LEDGER
  Covered by a test:
  <every invariant row and AC id from the design documents, one per line>
  Covered by a unit:
  <every use case, operationId, and screen, one per line; every foundation
   §1 «Решения по NFR» row and every §4 configuration variable, one per line>

LEGAL EXECUTOR NAMES
  <executor-catalog/references/assignable-implementers.md, verbatim —
   Implementer: mechanical-worker | impl-lite | impl-medium | impl-hard | impl-ui;
   Nested: — | mechanical-worker. A unit whose Docs cite a screen spec and a
   Figma nodeId is impl-ui with Nested —. Any other unit on impl-ui is a finding.
   Not the catalog's full Name column: a
   review, plan-review, plan-writer, design, or impl-critical name in a plan is a finding.>

GRADING STANDARD
  <plan/references/complexity.md, pasted in full>

REPO FILE TREE
  <the tree, so Files paths and scaffold overlap can be checked>

PRIOR FINDINGS  (if this is a re-review after a fix)
  <one line per already-closed finding, or "none">

LENSES
  <only this packet's lenses, from the list below>

DO NOT REPORT
- A better slicing you would have chosen. Report a unit that cannot land green
  alone; do not redesign the plan.
- A design decision you disagree with — that is OPEN, not a finding.
- A grade the cascade genuinely permits, where the unit's `Why` names the signal
  it followed and no floor or gate contradicts it.
- A row in `open-questions.md` the plan already raised against a named unit.
- Anything about code or files no unit in this plan touches.

SEVERITY
  P0  the plan cannot execute as written: dependency cycle, a unit that cannot
      land green alone, a floor violation, a Docs citation that does not resolve
      in the pasted documents, an invariant or AC covered by no unit, an
      Implementer name absent from LEGAL EXECUTOR NAMES
  P1  executable but buys avoidable rework: a false Parallel-safe, a grade off by
      one tier without a floor breach, a scenario whose expected outcome is not
      decided yet, a unit recreating scaffold output, a PATCH over
      «добавляет» / «ломает» changes, a partner API broken inside its
      major, or no bump unit
  P2  ordering or naming a maintainer would improve — recorded, never blocks
  P3  nit — recorded, never blocks

Every calibration finding cites the cascade rule or the floor it rests on.
Every citation finding names the document and the id that did not resolve.
```

## Structural lenses — `plan-review-medium`

```
  Dependency graph — Depends on forms a DAG, every named dependency exists,
    every unit is reachable in the wave ordering.
  Parallel safety — for each Parallel-safe: yes pair: disjoint Files AND no
    shared type, migration, registry, config, generated client, lockfile, or
    runtime resource (test database, port, dev server).
    File disjointness alone is not sufficient; an unmarked shared contract is
    a finding.
  Citation integrity — every Docs entry resolves to a real section, id,
    operationId, table, or screen in the pasted documents.
  Coverage — every "covered by a test" line appears in some unit's Test
    scenarios; every "covered by a unit" line belongs to some unit's Docs or
    Files (it needs no test line of its own). Name anything with no unit, and
    anything two units both claim.
  Executor validity — every Implementer and Nested name appears verbatim in
    LEGAL EXECUTOR NAMES; no model slug anywhere in the plan; Nested filled
    only where the unit describes separable mechanics. A unit whose Docs cite
    a screen spec and a Figma nodeId is impl-ui with Nested —; impl-ui
    anywhere else is a finding.
  Existing work — a unit that recreates what the REPO FILE TREE shows already
    exists, and every Pattern path exists in the REPO FILE TREE — or is
    written `path (U<n>)` and created by that earlier unit reachable via
    Depends on, or names an architecture section whose file tree / snippet
    fixes the shape. Do not judge
    whether a grade is too low; the judgment half owns calibration.
  Service version — §1 states a version, its level and reason, matching the
    folder name; the level matches SERVICE VERSION: any «добавляет» or
    «ломает» → MINOR or above, PATCH only with none. MAJOR is the owner's
    call — check only that §1 states it. With a partner-versioned API, a
    «ломает» in OpenAPI inside the same API major (no new path prefix) is
    P1. A level below the changes is a finding. The last unit is the grade-0
    mechanical-worker bump of the manifest's version to that number,
    depending on every other unit.
  Plan hygiene — U-ids unique and unrenumbered, no progress state (status:,
    checkboxes, "done"), repo-relative paths, version pins present, Open
    Questions blocking named units rather than absorbed as guesses.
```

## Judgment lenses — `plan-review-hard`

```
  Commit atomicity — does each unit land green ALONE? Look for: importing from
    a sibling that ships later, a test that cannot pass until a second unit
    arrives, a route registered against a handler another unit adds, a
    migration whose adapter is elsewhere. Each is a split, not a preference.
  Grade calibration — run the GRADING STANDARD's cascade on each unit's own
    filled fields (Files count and ring spread, whether Approach still contains
    an open decision, whether Test scenarios has error and integration rows,
    whether Docs fully determine the outcome) and compare to the stated grade.
    Check both floors. Check the anti-deflation gate: a unit whose Pattern is
    `— first of its kind` is at least Mid, so 0 or Low there is a finding.
    Check the compound gate was reachable: when every High
    unit in the plan is a risky one, that gate was probably skipped and the
    plan's hardest unit went to the Mid implementer.
  Test-first writability — can each scenario's expected outcome be written
    before the implementation exists? The design already fixed the invariant,
    the error-to-status mapping, the constraint, the AC. "Rejects an invalid
    transition" is not specified; "Paid→Draft raises IllegalTransition, per
    BR-3" is.
```

## The report

```
VERDICT           PASS | FIX_THEN_PROCEED | RETURN_TO_PLAN | STOP
FINDINGS          one per line: <sev> | <unit ids> | <lens> | <what> | <fix> | <fix kind>
                  fix kind on P0/P1: mechanical (the fix is the finished text
                  edit) | local (a local decision left) | reslice (split, merge,
                  new unit, cross-unit Depends on, security/money/migration
                  decision); `—` on P2/P3
COVERAGE LEDGER   ledger lines with no unit, or "all covered"
GRADE TABLE       <unit> | stated <grade> | cascade says <grade> | <rule or floor>
                  — only units where the two differ; plus the tier distribution
DISMISSED         findings ruled out, and which rule applied
OPEN              doubts about the design itself, for the user
```

Verdict rules:

- Any P0 or P1 forbids `PASS`.
- `FIX_THEN_PROCEED` only when every blocking finding is a fully specified edit
  to the plan text — a wrong `Parallel-safe`, a mistyped executor name, a
  citation whose target is unambiguous, a grade a floor decides. Otherwise
  `RETURN_TO_PLAN`.
- `RETURN_TO_PLAN` names which units the planner must re-open.
- `STOP` when the fix belongs in a design document rather than the plan.
- Exactly one verdict, no hedging clause attached to it.

A `GRADE TABLE` row is not automatically a finding: state it, and raise it as
P1 only when a floor, a gate, or the unit's own fields contradict the stated
grade.
