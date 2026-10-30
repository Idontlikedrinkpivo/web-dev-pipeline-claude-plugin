# Plan reviewer packets and report

Two packets from one template. The **structural** packet goes to
`plan-review-medium`, the **judgment** packet to `plan-review-hard`. Both are
bounded: everything a reviewer may look at is named by path, read from disk,
and neither explores the repo beyond `git ls-files` — except the structural
reviewer's search for the symbols a unit removes or changes (Files
completeness). Only the coverage ledger is pasted: the session built it
and it exists nowhere on disk (`executor-catalog` → Dispatch contract →
Paths, not pasted documents).

Fill `LENSES` with only that packet's lenses. A reviewer given all twelve skims
the three that matter.

## The packet

```
You review a finished implementation plan before any code exists. You do not
edit the plan, the design documents, or the repo. Findings and one verdict only.

SKILLS ROOT         <absolute folder holding the plugin's skills
                    (executor-catalog → Dispatch contract)>
PLAN                documentation/plans/<version>/plan.md and open-questions.md
                    beside it — read both in full
MODE                greenfield | increment | fix | brownfield
UNITS               <the U-ids to review: all, or on a fix plan the appended
                    units, on a re-review the changed ones>

SERVICE VERSION     (structural packet only) the folder's version, the
                    manifest's current `version`, the iteration's typed
                    changes (changelog rows of this version, OpenAPI
                    info.x-changelog included, plus changes not stamped yet,
                    typed from the diff since the last tag), and whether the
                    API has external consumers (partner-versioned, `/vN` path)

READ FROM DISK
  <repo-relative paths of every document the units' «Документы» cite, every
   part of a split one (srs.md and areas/*.md; openapi.yaml, paths/,
   components/); on a fix plan the report (test-run.md or security-audit.md
   beside the plan); on a brownfield plan the code:<path> files — this is
   what citations are resolved against>

COVERAGE LEDGER   (structural packet only)
  <only the ids in scope (plan-review → Step 1): on an increment, those this
   version added or changed; on greenfield, all; on a fix plan, the report
   rows; on brownfield, the request's items.>
  Covered by a test:
  <invariant row and AC ids, one per line>
  Covered by a unit:
  <use cases, operationIds, screens, foundation §1 «Решения по NFR» rows,
   §4 configuration variables; report rows — one per line>

LEGAL EXECUTOR NAMES
  <executor-catalog/references/assignable-implementers.md, verbatim —
   «Исполнитель»: mechanical-worker | impl-lite | impl-medium | impl-hard | impl-ui;
   «Вложенный»: — | mechanical-worker. A unit whose «Документы» cite a screen
   spec and a Figma nodeId is impl-ui with «Вложенный» —. Any other unit on impl-ui is a finding.
   Not the catalog's full Name column: a
   review, plan-review, plan-writer, design, or impl-critical name in a plan is a finding.>

GRADING STANDARD  (judgment packet only)
  <SKILLS ROOT>/plan/references/complexity.md — read it before the units

REPO FILE TREE
  run `git ls-files` yourself, so «Файлы» paths and scaffold overlap can be
  checked

PRIOR FINDINGS  (if this is a re-review after a fix)
  <one line per already-closed finding, or "none">

LENSES
  <only this packet's lenses, from the list below>

DO NOT REPORT
- A better slicing you would have chosen. Report a unit that cannot land green
  alone; do not redesign the plan.
- A design decision you disagree with — that is OPEN, not a finding.
- A grade the cascade genuinely permits, where the unit's `Почему` names the signal
  it followed and no floor or gate contradicts it.
- A row in `open-questions.md` the plan already raised against a named unit.
- Anything about code or files no unit in this plan touches.

SEVERITY
  P0  the plan cannot execute as written: dependency cycle, a unit that cannot
      land green alone, a floor violation, a «Документы» citation that does
      not resolve in the documents read, an in-scope invariant, AC or report
      row covered by no unit, an «Исполнитель» name absent from LEGAL
      EXECUTOR NAMES
  P1  executable but buys avoidable rework: a false «Параллельно: yes», a grade off by
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
  Dependency graph — «Зависит от» forms a DAG, every named dependency exists,
    every unit is reachable in the wave ordering.
  Parallel safety — for each Параллельно: yes pair: disjoint «Файлы» AND no
    shared type, migration, registry, config, generated client, lockfile, or
    runtime resource (test database, port, dev server).
    File disjointness alone is not sufficient; an unmarked shared contract is
    a finding.
  Files completeness — for each unit with «Меняет символы», and each unit
    that visibly removes or changes a field, a constant, an environment
    variable, a response shape or a public symbol without listing it there:
    search the repository (grep) for the symbol — code, tests, e2e, CI,
    documents — and check that every hit is in the unit's «Файлы» or named
    under «Не затрагивается» with a reason. A missing caller or test, or a
    changed symbol missing from «Меняет символы», is P1. Then, from the plan
    alone: a later unit naming a path an earlier unit splits, moves or
    renames, without the new path or «по итогам U<K>»; a new test file the
    unit's evidence strategy needs; the configs of a tool or a dependency a
    unit changes (vite, vitest, dependency-cruiser, knip, eslint, tsconfig);
    sites a unit defers «до U<N>» missing from U<N>'s «Файлы» — each P1
    (plan/references/files-field.md). This is the one lens that reads the
    repository, and only the hits — plus the config file names of the tool
    a unit changes.
  Citation integrity — every «Документы» entry resolves to a real section, id,
    operationId, table, or screen in the documents read; a report row
    (test-run.md TC-n, security-audit.md F<n>) to that row of the report;
    code:<path> (brownfield) to a file in the repository; plugin change <id>
    to that id in <SKILLS ROOT>/upgrade-docs/changes.json.
  Coverage — every "covered by a test" line appears in some unit's
    «Тестовые сценарии»; every "covered by a unit" line belongs to some
    unit's «Документы» or «Файлы» (it needs no test line of its own). Name anything with no unit, and
    anything two units both claim. The ledger is already scoped: an id
    outside it — built by an earlier version — is not a finding.
    A screen split into part units (`S-<n> эл. <from>–<to>`): the ranges
    cover every element of its spec exactly once, the first part sets the
    screen up and the last one checks it whole — a gap or an overlap is P1.
  Executor validity — every «Исполнитель» and «Вложенный» name is one of
    LEGAL EXECUTOR NAMES; no model slug anywhere in the plan; «Вложенный»
    filled only where «Что делает вложенный» describes separable mechanics.
    A unit whose «Документы» cite a screen spec and a Figma nodeId is impl-ui
    with «Вложенный» —; impl-ui anywhere else is a finding.
  Existing work — a unit that recreates what the REPO FILE TREE shows already
    exists, and every «Образец» path exists in the REPO FILE TREE — or is
    written `path (U<n>)` and created by that earlier unit reachable via
    «Зависит от», or names an architecture section whose file tree / snippet
    fixes the shape. Do not judge
    whether a grade is too low; the judgment half owns calibration.
  Service version — §1 states a version, its level and reason, matching the
    folder name; the level matches SERVICE VERSION: any «добавляет» or
    «ломает» → MINOR or above, PATCH only with none. MAJOR is the owner's
    call — check only that §1 states it. With a partner-versioned API, a
    «ломает» in OpenAPI inside the same API major (no new path prefix) is
    P1. A level below the changes is a finding. When the manifest's version
    differs from the folder's, the last unit is the grade-0
    mechanical-worker bump to that number, depending on every other unit;
    when they are equal, no bump unit is needed, and a fix plan adds none.
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
    filled fields («Файлы» count and ring spread, whether «Подход» still
    contains an open decision, whether «Тестовые сценарии» has error and
    integration rows, whether «Документы» fully determine the outcome) and compare to the stated grade.
    Check both floors. Check the anti-deflation gate: a unit whose «Образец» is
    `— first of its kind` is at least Mid unless the mechanical gate graded
    it 0, so Low, or 0 outside that gate, is a finding.
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
FINDINGS          one per line: <sev> | <unit ids> | <lens> | <what> | <fix> | <вид правки>
                  вид правки on P0/P1: mechanical (the fix is the finished text
                  edit) | local (a local decision left) | reslice (split, merge,
                  new unit, cross-unit «Зависит от», security/money/migration
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
  to the plan text — a wrong `Параллельно`, a mistyped executor name, a
  citation whose target is unambiguous, a grade a floor decides. Otherwise
  `RETURN_TO_PLAN`.
- `RETURN_TO_PLAN` names which units the planner must re-open.
- `STOP` when the fix belongs in a design document rather than the plan.
- Exactly one verdict, no hedging clause attached to it.

A `GRADE TABLE` row is not automatically a finding: state it, and raise it as
P1 only when a floor, a gate, or the unit's own fields contradict the stated
grade.
