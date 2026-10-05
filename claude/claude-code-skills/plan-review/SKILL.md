---
name: plan-review
description: >-
  Independently reviews a finished implementation plan before any code is
  written — one commit per unit, dependencies and parallel safety, grades
  against the complexity cascade, citations, invariant and AC coverage — and
  returns one verdict. Use after `plan` writes or revises a plan, or when
  the user asks to check a task breakdown, work order or unit list. Not for
  design documents (`doc-review`), re-planning (`plan` edits), or code
  review.
---

# Plan Review

A plan is the cheapest place in the pipeline to be wrong and the most expensive
place to stay wrong. Every defect here is multiplied by execution: a
mis-graded unit gives a rename design latitude or hands a state machine the
apply-the-shape packet, a false `Parallel-safe: yes` turns into a merge fight, an
uncovered invariant ships untested, a citation that does not resolve makes an
executor invent the design it was supposed to follow.

`plan` runs its own quality gate before closing. This skill is the independent
pass over the result — the same relationship `code-review-unit` has to `work`.
Write findings in Russian. Do not translate U-ids, executor names, file paths,
verdict tokens, or the report's `Verdict:` line and headings (`doc-versioning`
→ Document language).
Self-checks catch what the author remembered to look for; this catches what the
author's own framing hid.

## Not this skill's job

| Not here | Owner |
|---|---|
| Re-slicing units or re-grading them | `plan` — this skill proposes, that skill edits |
| Whether the design decision behind a unit is right | the design documents, then `doc-review` and the user |
| Reviewing a written document's coherence, feasibility, or premise | `doc-review` |
| Reviewing code or a diff | `code-review-unit` · `code-review-full` |
| Deciding which model a tier maps to | `executor-catalog` and its agent files |
| Executing anything | `work` |

## Inputs

| Input | Required | Read for |
|---|---|---|
| Plan document `documentation/plans/<version>/plan.md` | **yes** | §1 digest and its version line, the unit table, every unit's fields, §5 definition of done, `open-questions.md` beside the plan, version pins |
| Cited design documents | **yes** | resolving every `Docs` citation to a real section or id — a citation nobody checked is the plan's most common silent defect |
| `executor-catalog/references/assignable-implementers.md` | **yes** | the only legal `Implementer` / `Nested` names |
| `plan/references/complexity.md` | **yes** | the cascade, the six signals, both floors, the anti-inflation and anti-deflation gates — the standard grades are checked against |
| The iteration's changes | **yes** | the manifest's current `version`; the iteration's typed changes — changelog rows whose `Версия` is the folder's version (OpenAPI: `info.x-changelog`), plus changes not stamped yet, from the diff of the versioned documents since the last tag `v<version>`; whether the API has external consumers (the foundation's Full trigger "versioned partner API", a `/vN` path) — what the level is checked against |
| Repo file tree | **yes** | whether a unit's `Files` paths are plausible and whether a unit recreates something the scaffold already produced |
| Prior plan-review findings | when re-reviewing after a fix | so a closed finding is not re-opened |

Without the cited documents this degrades into proofreading: every coverage and
citation lens needs the source it cites. Say so and stop rather than reviewing
the plan against itself.

The tree and the cited documents are the whole context. Do not go reading the
repo: a reviewer that explores produces findings about code no unit in this
plan touches.

## Workflow

### Step 0. Classify the artifact

Filename and body decide what the file **is**. The user's "review this as
a plan" does not change the type.

| This is | Then |
|---|---|
| Architecture, domain model, scenarios, SRS, screen spec, OpenAPI, or DB schema | **Stop.** Name `doc-review` as the skill that reviews it **now**. Do not apply the lenses below. Do not issue `PASS` / `RETURN_TO_PLAN` / `FIX_THEN_PROCEED` on it. |
| A finished plan (unit map, `Depends on`, grades, `Docs`) | Continue with Step 1 |
| Missing, or neither a plan nor a design document | Say so and stop |

"Not `doc-review`" means those personas do not review a **work order**.
It does not mean "never send the user to `doc-review`." An architecture
file submitted as a plan still goes to `doc-review`.

### Step 1. Establish the standard before reading the units

Read `complexity.md` and `executor-catalog/references/assignable-implementers.md` first. A reviewer that forms
an opinion about a grade before reading the cascade is applying taste, and taste
is exactly what the cascade exists to replace. So every calibration finding
cites the cascade rule or floor it rests on; "feels like Mid" is not a finding.

Extract from the design documents, once, a coverage ledger in two parts:
**covered by a test** — every invariant row and every acceptance criterion id;
**covered by a unit** — every use case, every operation, every screen, every
foundation §1 «Решения по NFR» row, and every §4 configuration variable. The
units are checked against both. Build it even when the plan
says it covered everything — that claim is what is being checked.

### Step 2. The lenses

| Lens | Asks |
|---|---|
| **Commit atomicity** | does each unit land green **alone**? A unit that imports from a sibling that ships later, a unit whose test cannot pass until a second unit arrives, a unit that leaves a route registered against a missing handler — each is a split, not a preference. |
| **Dependency graph** | does `Depends on` form a DAG with no cycle, and does every unit's declared dependency actually exist? Is every unit reachable from the wave ordering? |
| **Parallel safety** | for each `Parallel-safe: yes` pair: disjoint `Files` **and** no shared type, migration, registry, config, generated client, lockfile, or runtime resource (test database, port, dev server). Declared file disjointness is necessary, never sufficient — the unmarked shared contract is what a merge fight is made of. |
| **Grade calibration** | run the cascade on the unit's own filled fields and compare to the stated grade. Check both floors — auth, authorization, money, migrations on existing data, secrets, external contracts never below Mid; a unit whose `Docs` do not determine the outcome never below Mid. Check the anti-deflation gate: a `— first of its kind` unit graded 0 or Low is miscalibrated. Check the compound gate was reachable: a plan whose only High units are risky ones usually skipped it. |
| **Citation integrity** | does every `Docs` entry resolve to a real section, id, `operationId`, table, or screen in the named document? A dangling citation is P0: the executor cannot see this session and will fill the gap by inventing. |
| **Coverage** | does every invariant row and every AC appear in some unit's `Test scenarios`, and does every use case, operation, screen, NFR decision and configuration variable belong to some unit (its `Docs` or `Files`)? An operation or screen needs a unit, not its own test line. Nothing silently dropped, nothing covered twice by two units that will both claim ownership. |
| **Test-first writability** | can each scenario's expected outcome be written before the implementation exists? A scenario whose expected value can only be filled in after reading the code has not been specified — the design already fixed the invariant, the status mapping, the constraint. |
| **Executor validity** | does every `Implementer` sit on the assignable list (`mechanical-worker`, `impl-lite`, `impl-medium`, `impl-hard`, `impl-ui`), is `Nested` either `—` or `mechanical-worker`, and is no review / plan-review / doc-review / `code-explorer` / `impl-critical` name or model slug written into the plan? A unit whose `Docs` cite a screen spec and a Figma `nodeId` is `impl-ui` with `Nested: —`. Any other unit on `impl-ui` is a finding. |
| **Existing work** | does a unit recreate what the scaffold or an earlier increment already produced? Does every `Pattern` path exist in the tree, or is it written `path (U<n>)` and created by that earlier unit reachable via `Depends on`, or does it name an architecture section whose file tree / snippet fixes the shape? Whether a `— first of its kind` grade is too low is Grade calibration's call, not this lens's — it needs the cascade. |
| **Service version** | does §1 state a version, its level and reason, matching the folder name, and does the level match the iteration's typed changes (`pipeline` → Service version)? Any «добавляет» or «ломает» needs MINOR or above; PATCH only with none. MAJOR is the owner's call: check only that §1 states it, never whether the change is big enough. With a partner-versioned API, a «ломает» in OpenAPI inside the same API major (no new path prefix) is P1. Is the last unit the grade-0 `mechanical-worker` bump of the manifest's `version` to that number, depending on every other unit? |
| **Plan hygiene** | U-ids unique and unrenumbered, no progress state (`status:`, checkboxes, "done"), repo-relative paths, version pins present, rows in `open-questions.md` blocking named units instead of absorbed as guesses. The plan body has no open-questions section. |

### Step 3. Dispatch

Resolve each half's row through `executor-catalog` and dispatch that pair
under that file's Dispatch contract (read the section with the rows), without
asking which model. Two dispatches, in
parallel, because the two halves fail differently:

| Executor | Carries |
|---|---|
| `plan-review-medium` | the structural lenses — dependency graph, parallel safety, citation integrity, coverage, executor validity, existing work, service version, plan hygiene. These are checkable against the text and the tree, and they are where volume lives. |
| `plan-review-hard` | the judgment lenses — commit atomicity, grade calibration, test-first writability. Deciding that a unit *cannot* land alone, or that a Low unit is really Mid, is the same kind of reasoning that graded it, so it needs a tier that can hold the cascade and argue with it. |

Build both from `references/reviewer-prompt.md`. Do not merge them into one
dispatch to save a call: the structural half is mechanical and the judgment half
is adversarial, and one packet holding both reliably produces a reviewer that
skims the calibration it was supposed to challenge.

Both halves run on every plan, small ones included: the structural half on
`plan-review-medium` is the cheap row, and running it on the session model
would be the "do the row's work on the session" the catalog forbids.

### Step 4. Judge the findings

| Level | Meaning | Effect |
|---|---|---|
| **P0** | the plan cannot execute as written: a dependency cycle, a unit that cannot land green alone, a floor violation, a `Docs` citation that does not resolve, an invariant or AC covered by no unit, an `Implementer` or `Nested` name absent from the assignable list | blocks the handoff to `work` |
| **P1** | the plan will execute but buy avoidable rework: a false `Parallel-safe: yes`, a grade off by one tier without a floor breach, a scenario whose expected outcome is not yet decided, a unit duplicating scaffold output, a PATCH over «добавляет» / «ломает» changes, a partner API broken inside its major, or no bump unit | blocks the handoff |
| **P2** | ordering or naming that a maintainer would improve — a wave that could be wider, a `Why` that names a weak signal | recorded, does not block |
| **P3** | nit | recorded, does not block |

Three dismissal rules:

1. **The design decided it.** A unit that looks odd because the architecture is
   odd is not a finding here — cite the section and dismiss. Arguing with the
   design is `STOP`.
2. **The plan already flagged it.** A row in `open-questions.md` that blocks a
   named unit is the plan working correctly, not a defect.
3. **A grade the cascade genuinely permits.** When two signals point at
   different tiers and the plan's `Why` names the one it followed, that is a
   judgment inside the cascade, not a miscalibration. A grade is only wrong when
   a floor, a gate, or the unit's own filled fields contradict it.

### Step 5. Verdict

Exactly one:

| Verdict | When | Next move |
|---|---|---|
| `PASS` | no P0/P1 | the plan may proceed to the next stage per `pipeline`; P2/P3 recorded in the review report |
| `FIX_THEN_PROCEED` | P0/P1 fully specified and mechanical in the plan text — a wrong `Parallel-safe`, a mistyped executor name, a missing citation whose target is obvious, a grade the floor decides | `plan` applies them in place, then this review re-runs over the changed units only |
| `RETURN_TO_PLAN` | P0/P1 needing the planner's judgment — a dependency cycle, a unit that has to be split, a re-grade with knock-on executor changes, coverage that has no obvious home | `plan` re-opens with the findings attached; re-review after |
| `STOP` | the finding is upstream: the design has a gap, a document contradicts another, or the plan cannot be fixed without a product decision | do not proceed to `work`; take it to the user, and the fix lands in the document, not the plan |

Every P0/P1 row carries a **Fix kind**, so `plan` can pick the revise
writer without re-reading the findings (`plan-complexity.md` → Grading a
revise):

| Fix kind | When |
|---|---|
| `mechanical` | the Fix cell is the finished edit — a citation, a `Parallel-safe` value, an executor name, a grade a floor dictates, a scenario line spelled out |
| `local` | a local decision is left: change a grade and its implementer, move units between waves, add `Files` after checking the code, write scenarios for a changed document, a service version the session re-asks the user |
| `reslice` | split or merge units, add a unit, change `Depends on` across several units, change a security, money, or migration decision |

`FIX_THEN_PROCEED` means every blocking row is `mechanical`. P2/P3 rows
leave the cell `—`.

This skill never edits the plan. It reviews a decision artifact, and an artifact
a reviewer silently rewrote is no longer a decision anyone made. Proposing a
better slicing in a finding's `Fix` is fine; rewriting the unit table is not.

## Report

Write the report to `documentation/plans/<version>/plan-review.md`, beside
the plan, overwriting any earlier one. Its first line is the verdict
alone, e.g. `Verdict: PASS`; `work` and `pipeline` read that line as the
gate. This file is the only thing this skill writes — the plan itself is
never edited.

```markdown
Verdict: <verdict>

## Plan review — <plan path> — <verdict>

| # | Sev | Unit(s) | Lens | Finding | Fix | Fix kind |
|---|---|---|---|---|---|---|

**Coverage ledger** — invariant rows and ACs with no unit, or the explicit clean
line.
**Grade table** — every unit whose cascade result differs from its stated grade,
with the signal that decides it; plus the tier distribution as written.
**Dismissed** — findings ruled out, and which rule applied.
**Not blocking** — P2/P3, for the record.
**Open** — doubts about the design itself, for the user.
```

A filled report, for calibration — match its density, not its domain:

```markdown
Verdict: FIX_THEN_PROCEED

## Plan review — documentation/plans/1.3.0/plan.md — FIX_THEN_PROCEED

| # | Sev | Unit(s) | Lens | Finding | Fix | Fix kind |
|---|---|---|---|---|---|---|
| 1 | P0 | U6 | Citation integrity | `Docs` ссылается на `api POST /orders/{order_id}/refund`, в OpenAPI такой операции нет; возврат описан как `operationId refundPayment` | заменить цитату на `api refundPayment` | mechanical |
| 2 | P1 | U4, U5 | Parallel safety | обе правят `src/domain/order/order.ts`, но U5 помечен `Parallel-safe: yes` и стоит в волне 2 вместе с U4 | U5: `Parallel-safe: no — U4`, перенести в волну 3 | mechanical |
| 3 | P2 | U9 | Plan hygiene | `Why` пересказывает цель, а не сигнал | «rule 5 — прецедент `src/adapters/invoice-repo.ts`» | — |

**Coverage ledger** — все инварианты и AC покрыты.
**Grade table** — U8: заявлено Mid; если считать signal 6 дешёвым, каскад даёт Low (rule 5), но `Why` называет rule 6 — сценарий ретрая требует управления временем. Каскад это допускает, не находка. Распределение: 0:1 Low:4 Mid:3 High:1.
**Dismissed** — U3 правит 6 файлов, но foundation §5 кладёт репозиторий и маппер в один модуль (правило 1: решил дизайн).
**Not blocking** — #3.
**Open** — нет.
```

The grade table is the part a run cannot reconstruct later: once `work` starts,
a wrong grade shows up only as cost.

## Before you finish

- Every lens produced a finding, an explicit clean line, or a stated reason it
  has no surface in this plan — Step 2.
- Every invariant row and AC from the ledger has a named unit or a P0 — Step 1.
- Every `Docs` citation was resolved against the actual document — Step 2.
- `Implementer` / `Nested` names were checked against the assignable list, not
  the full catalog Name column — Step 2.
- The version's level was checked against the iteration's typed changes,
  and the bump unit is last — Step 2.
- Exactly one verdict, no P0/P1 left unclassified; a design defect is `STOP`,
  not a finding — Steps 4–5.
- The plan file is byte-identical to how the review found it — Step 5.
- `plan-review.md` exists beside the plan with `Verdict: <verdict>` on its
  first line — Report.

## References

- `references/reviewer-prompt.md` — the packet each reviewer receives and the
  report it returns.
- `plan` (skill) — its writer settles the plan this reviews, owns every fix, and runs its own quality gate first. The session re-dispatches that writer and does not edit the file.
- `plan/references/complexity.md` — the cascade and floors every calibration
  finding must cite.
- `executor-catalog/references/assignable-implementers.md` — the legal
  implementer names; the parent catalog only for the two
  `plan-review-*` rows this skill dispatches.
- `pipeline` (skill) — where this gate sits. When `plan` invoked this
  review, report and return; `plan` asks the next stage. When the user
  opened this review directly, ask the next transition per `pipeline`
  → "Asking before a transition".
