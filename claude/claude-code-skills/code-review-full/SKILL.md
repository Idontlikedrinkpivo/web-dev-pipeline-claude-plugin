---
name: code-review-full
description: >-
  Reviews a completed plan's whole diff once, after every unit is committed:
  cross-unit drift, invariants spanning units, dead leftovers, declared
  security and the definition of done; a unit-local defect goes back by its
  U-id. Use when `work` closes a run or the user asks to review a finished
  plan as a whole. Not the per-unit gate (`code-review-unit`) or a
  whole-repo audit; an ad-hoc diff or PR goes to the built-in /code-review.
---

# Full-Plan Review

One run, one diff, one verdict, after every unit landed. The question this
answers is different from a per-unit review's: **do the committed units add up
to what the plan promised, with nothing left contradicting, duplicating, or
half-wiring another unit?**

`code-review-unit` runs dozens of times and deliberately has no memory of
sibling units — that is what keeps it cheap. The cost of that narrowness is
paid once, here, at the end: this is the only pass that holds the whole branch
diff and the whole plan in view at the same time. So it runs for every plan,
however small, and even when every unit passed its own review: those passes
are necessary, not sufficient, and the definition-of-done check does not
shrink to zero with the plan.

## Not this skill's job

| Not here | Owner |
|---|---|
| Reviewing one unit's diff before its commit | `code-review-unit` |
| Generic PR/branch review outside this planning pipeline | Claude Code's built-in `/code-review` |
| Auditing code no unit in this plan touched | nobody in this pipeline — that is a standing activity on its own cadence, and no stage here depends on one |
| Deciding *whether* a security requirement should exist | the SRS's Security NFR checklist and the architecture's decisions table, reviewed by `doc-review`'s security lens |
| Whether the design decision was right | the design documents — and the user |
| Applying a fix | the named unit's executor, or `mechanical-worker` for the mechanical part |
| Re-grading a unit, re-picking its executor | `plan` · `executor-catalog` |
| Shipping — PR, push, CI | the user's shipping flow |

## Inputs

| Input | Required | Notes |
|---|---|---|
| Plan document `documentation/plans/<version>/plan.md` | **yes** | all units, §1 digest, §2 unit map, §5 definition of done |
| Full diff | **yes** | `git diff BASE...HEAD` for the whole run, with `BASE` taken from the run report — every unit's diff together, not unit by unit. Handed to the reviewer as a file path under `$(git rev-parse --git-dir)/pipeline-work/`, not pasted |
| Cited design documents | **yes** | every section any unit cited, once each, de-duplicated — under `documentation/`: `requirements/srs/srs.md`, `db/schema.md` and `db/migrations/`, `api/openapi.yaml`, `architecture/` (`architecture.md`, `domain.md`, `scenarios/<area>/<area>.md`), `ui/screen-specs/` |
| Declared NFR and configuration decisions | **yes** when they exist | foundation §1 «Решения по NFR» rows and the §4 configuration table — the baseline the NFR lens checks against |
| Declared security requirements | **yes** when either exists | the SRS's Security NFR sub-checklist rows and the architecture's security decisions table — the baseline the security lens checks against |
| Run report `$(git rev-parse --git-dir)/pipeline-work/<version>-run.md` | **yes** | per-unit statuses, evidence strategies, grade corrections, out-of-scope notes, the **Изменённые решения** of the run, and the **Cross-unit watch** list of `OPEN` suspicions carried up from unit reviews |
| Definition-of-done output | **yes** | the plan's §5 commands as `work` Step 7 ran them, with exit codes, as a file path — the reviewer reads it and does not re-run them |
| Dead-code report | **yes** | the stack's detector output (`knip` / `vulture`) from `work` Step 7, as a file path; "could not run" with the reason is a valid input, a missing one is not |
| Prior full-plan findings | when resuming after a fix | so a closed finding is not re-opened |

Without the plan and the run report this is a generic diff read that will
invent its own idea of what the branch was supposed to do. Say so and stop.

## Workflow

### Step 1. Reconstruct the whole

Read the plan's unit map and the run report's status column side by side.
Confirm every unit marked committed actually has a commit in the diff range
(its `Plan-Unit:` trailer in `BASE..HEAD`), and that no committed diff is
missing from the unit map. A fix commit carrying a unit's trailer, or a
`review-fix-<n>` trailer listed in the run report, counts as mapped (`work` →
A fix after a commit). A mismatch here means
the run report is stale — fix that before reviewing anything else.

### Step 2. Cross-unit lenses

These only exist at this scope; a single unit's review cannot run them.
Re-checking one unit's fidelity to its own spec is not a lens here — that
already happened, and redoing it adds cost without the cross-unit view. The
full wording of each lens, the security baseline table, the evidence-based
severity for undeclared holes, and the P0–P3 definitions live in the packet in
`references/reviewer-prompt.md`; read it when you build the dispatch (Step 3)
and again when you judge the findings (Step 4).

- **Drift** — one concept modeled two ways across units.
- **Aggregate coverage** — every quoted invariant row and AC has a real
  assertion somewhere in the combined diff, including a scenario split across
  units.
- **Wiring** — every port implemented, adapter registered, route mounted, use
  case reachable where the design calls it.
- **Superseded code** — code this run made dead or duplicate without removing
  it, whoever wrote the original: an earlier unit's approach a later unit
  replaced (a duplicate validator, an old code path), or a scaffold stub a
  unit's real implementation now shadows.
- **Stale docs** — an existing README, `.env.example`, or doc this diff made
  wrong; a changed decision from the run report's «Изменённые решения» that
  did not land in its documents; code that departs from a contract document
  with no such line behind it.
- **Definition of done** — the plan's §5 checked against the tree, not assumed
  from the per-unit sums.
- **Declared NFR and configuration** — each «Решения по NFR» row and each
  configuration variable the plan's units cite or this diff touches: where
  the shipped code applies it (`file:line`), or that it does not. A variable
  the config layer reads but nothing uses (a pool size the pool ignores, a
  worker count that starts no worker), or a limit the document states and
  the server never sets (a body limit left at the framework default), is
  not applied. Rows outside this run's scope are `OPEN`, not findings.
- **Security** — two modes, both bounded by this run's diff. *Declared
  baseline*: each SRS Security NFR row and architecture security decision,
  verified as cross-unit — the check lives in one unit, the route that
  bypasses it in another. *Undeclared surface*: a hole this diff introduced
  that no document named, graded by whether its exploit path traces through
  shipped lines; without this mode a verification pass would have to stay
  silent about a live vulnerability nobody wrote down. Anything not traceable
  to this diff is `OPEN` — inventing it makes the verdict unfalsifiable.
  Arguing with a security decision is `STOP` for the user.
- **Cross-unit watch** — every suspicion carried up from per-unit reviews is
  confirmed (promoted to a finding) or dismissed with a reason; none left open.

Skip a lens only when the plan has no surface for it (e.g. a one-unit plan has
nothing to drift against) and say so.

### Step 3. Dispatch

Resolve `review-full-plan` through `executor-catalog` and dispatch it under
that file's Dispatch contract (read the section with the row), with no
question to the user. One dispatch,
built from
`references/reviewer-prompt.md`, carrying the whole diff as a file path, the de-duplicated
design excerpts, the run report, and the cross-unit lenses. Do not fan this out
per lens or per unit — the value of this pass is one reviewer holding
everything at once; splitting it recreates the per-unit blind spot this skill
exists to close.

One pass, on every plan — High-heavy ones included. A second whole-run pass
on another model was tried and removed: in the 2026-10-01 benchmark the first
pass alone found the planted cross-unit defect in 9 of 9 runs across four
levels of subtlety, and the second pass never found anything the first had
missed, while costing 1.5–2 times as much. Do not add one back by
re-dispatching `review-full-plan` or another reviewer.

### Step 4. Judge the findings

What each level means is the packet's SEVERITY block — one text, so the
reviewer and you grade by the same definitions. Its effect here: **P0 and P1
block close; P2 and P3 are recorded and do not block.**

Two dismissal rules specific to this scope:

1. **A later run's scope, not this run's.** A gap the plan itself marked out of
   scope, or a follow-up the run report already opened as its own item, is not
   a finding here — confirm it is tracked, do not re-raise it.
2. **The design already decided the inconsistency is intentional** — two units
   deliberately use different shapes because the design does. Dismiss with the
   citation, same rule as the per-unit review. A design decision that looks
   wrong is `STOP` material for the user, not a finding.

### Step 5. Verdict

Exactly one:

| Verdict | When | Orchestrator's move |
|---|---|---|
| `PASS` | no P0/P1 | close the run; P2/P3 to the run report |
| `FIX_THEN_CLOSE` | P0/P1 that is mechanical and fully specified (delete dead code, rename to converge, wire a missing registration) | dispatch `mechanical-worker` as a follow-up, re-verify, then close |
| `RETURN_TO_UNIT` | P0/P1 that needs the judgment of the unit that caused it | re-open that unit through its own named executor with the finding attached; re-run this review after |
| `STOP` | the finding shows the plan itself under-specified an interaction between units, or the design has a genuine gap | do not close; take it to the user |

A re-review after every `FIX_THEN_CLOSE` or `RETURN_TO_UNIT` fix, until
`PASS`. Each reads only that round's fix commits with the open findings
attached and answers per finding — resolved or not — plus anything the fixes
broke; it never re-reviews the whole run. The rounds go on while each makes
progress, and stop for the user when it does not (`pipeline` → `references/convergence.md`).

Follow-up `Agent` calls (`mechanical-worker`, a unit's implementer) resolve their
own catalog row under the same Dispatch contract as Step 3.

Same discipline as the per-unit reviewer: the finding is proposed in words,
never applied by this skill — no staging, no committing, no "cleaned it up
while I was in there".

## Report

Write findings in Russian. Keep the heading, column names, bold labels, and
verdict tokens exactly as below (`doc-versioning` → Document language).

```markdown
## Full-plan review — <plan path> — <verdict>

| # | Sev | Units involved | Lens | Finding | Fix |
|---|---|---|---|---|---|

**Cross-unit watch resolved** — each carried-up suspicion, confirmed or
dismissed, with the reason.
**Security baseline** — each declared requirement: enforced (where), or not —
or the one line saying no security requirements were declared upstream.
**Undeclared surface** — holes this diff introduced that no document named:
each with its traced path and severity, plus the SRS or architecture row that
should have forbidden it. `none` when there are none.
**Definition of done** — each §5 item, met or not, with what was actually run
to check it.
**Dismissed** — findings ruled out, and which rule applied.
**Not blocking** — P2/P3, for the record.
```

A filled report, for calibration — match its density, not its domain:

```markdown
## Full-plan review — documentation/plans/1.3.0/plan.md — RETURN_TO_UNIT

| # | Sev | Units involved | Lens | Finding | Fix |
|---|---|---|---|---|---|
| 1 | P0 | U5, U8 | Security | `GET /invoices/{invoice_id}` (U8) передаёт `invoice_id` из пути в `GetInvoice` (U5), который не сверяет владельца; arch «Безопасность» D-4 требует проверку владельца | U5: принимать `requesterId`, отказывать `NotAuthorized`, тест на чужой счёт |
| 2 | P1 | U6 (+ scaffold) | Superseded code | scaffold-заглушка `src/app/health-stub.ts` осталась смонтированной рядом с `GET /health` из U6 | удалить заглушку и её регистрацию в `src/http/routes.ts` |

**Cross-unit watch resolved** — U4 «`OrderStatus` union vs enum»: dismissed, U4 выводит union из enum U2 (`keyof typeof OrderStatus`), модель одна.
**Security baseline** — D-4 владелец ресурса: не enforced (#1). NFR-Sec-2 хэш токенов: enforced в `src/adapters/token-repo.ts:hashToken`.
**Undeclared surface** — none.
**Definition of done** — по выводу команд из `work` Step 7: lint-контракты met (`npm run lint:deps`, код 0). E2E UC-2 met (`npm run test:e2e -- pay-order`, код 0). Покрытие BR-1…BR-5: met.
**Dead code** — отчёт knip: `src/app/health-stub.ts` не используется (#2); остальное — до этого прогона.
**Dismissed** — «даты в двух форматах в U4 и U7»: foundation §1 задаёт ISO для API и epoch для событий (правило 2).
**Not blocking** — none.
```

`RETURN_TO_UNIT` names U5: #1 needs its judgment, so the run cannot close on a
mechanical follow-up even though #2 alone would be `FIX_THEN_CLOSE`.

## Before you finish

- Every unit the run report marks committed has a matching commit in the diff
  range, and vice versa — Step 1.
- Every lens produced a finding, an explicit clean line, or a stated reason it
  has no surface in this plan — Step 2.
- Every declared security requirement names where it is enforced, or is a P0;
  `Undeclared surface` says `none` only after actually looking — Step 2.
- Every Cross-unit watch item was confirmed or dismissed — Step 2.
- Every §5 definition-of-done item was checked against the tree — Step 2.
- Exactly one verdict, no P0/P1 left unclassified under it — Steps 4–5.
- Nothing in the tree was changed by this review — Step 5.

## References

- `references/reviewer-prompt.md` — the packet the `review-full-plan` subagent
  receives (the only full wording of every lens, the security baseline table,
  undeclared-surface severity, and the P0–P3 definitions) and the report it
  returns.
- `executor-catalog` (skill) — the `review-full-plan` row and its agent.
- `code-review-unit` (skill) — the per-unit layer this skill complements; its
  `OPEN` cross-unit suspicions are an input here.
- `work` (skill) — invokes this once, at Step 7, after every unit lands.
