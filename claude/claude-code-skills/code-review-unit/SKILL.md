---
name: code-review-unit
description: >-
  Reviews one plan unit's diff against its unit spec before the commit,
  picking lenses from what it touched and a reviewer tier from its grade;
  returns COMMIT / FIX_THEN_COMMIT / RETURN_TO_EXECUTOR / STOP and never
  edits the tree. Use after each unit in `work`, or when asked to review a
  single unit's diff. Not the whole-plan review (`code-review-full`) or a
  security audit; an ad-hoc diff or PR goes to the built-in /code-review.
---

# Unit Review

One unit, one diff, one verdict, before the commit. The reviewed question is
narrow on purpose: **does this diff do what its unit spec said, and nothing
else?**

Per-unit review has an economics problem a PR review does not: it runs dozens
of times per plan. So the roster is sized by the unit's complexity grade, the
lenses are sections of one reviewer prompt rather than a fanned-out roster, and
a grade-0 unit gets no dispatch at all. A review that costs more than the unit
it reviews will get switched off, and then nothing is reviewed.

This is the first of two review layers. This skill cannot see the plan as a
whole — no memory of sibling units, no cross-unit view — by design, so it
cannot catch two units drifting apart or an aggregate invariant that needed
several units together. That is `code-review-full`'s job, once, at the end of
the run: a cross-unit suspicion goes into the report's `OPEN` line, not into a
judgment made from inside one unit's packet.

## Not this skill's job

| Not here | Owner |
|---|---|
| Whole-plan review after the run — cross-unit drift, aggregate coverage, definition of done | `code-review-full` |
| Whole-branch or PR review outside this pipeline | Claude Code's built-in `/code-review` |
| Security beyond this unit's diff — enforcement that spans units, or a hole in code this unit never touched | `code-review-full`'s security lens, which holds the whole run's diff at once |
| Whether the design decision was right | the design documents — and the user |
| Applying the fix | the unit's executor, per `work` |
| Grading the unit, choosing its executor | `plan` · `executor-catalog` |

## Inputs

| Input | Required | Notes |
|---|---|---|
| Unit spec | **yes** | the `### U<n>.` block: Goal, Docs, Files, Approach, Test scenarios, Verification, Complexity |
| The diff | **yes** | `git diff HEAD` after `git add -N <unit Files>` (intent-to-add, so untracked files in scope show up) — the orchestrator commits per unit, so uncommitted work *is* this unit's work. A Low batch is built from commits instead (Low batch, Step 3). Handed to the reviewer as a file path under `$(git rev-parse --git-dir)/pipeline-work/`, not pasted: pasted text stays in the orchestrator's context for the whole run |
| Cited design excerpts | **yes** | the sections named in `Docs`, pasted, not linked — resolved under `documentation/` (`scenarios/orders` is `architecture/scenarios/orders/orders.md`, `api` is `api/openapi.yaml`) |
| Worker report | when there was one | `TESTS`, `RED OBSERVED`, `CONCERNS`, `OUT OF SCOPE` |
| Prior findings this run | when any | so a known issue is not raised twice |

Without the unit spec this is not a unit review — it is a generic diff read,
and it will invent expectations the plan never set. Say so and stop.

## Workflow

### Step 1. Bound the diff

`git add -N <unit Files>` first — `git diff HEAD` omits untracked files
otherwise. Then `git diff HEAD --stat` and the diff itself with context. Compare the changed
paths against the unit's `Files`:

- **inside `Files`** — reviewed normally.
- **outside `Files`** — a scope breach. Report it as its own finding, at P1
  minimum, and review the change on its merits too: it may be necessary work
  the plan mis-scoped, or a sibling unit's work leaking in.
- **in `Files` but untouched** — the unit may be incomplete. Check against the
  goal before assuming it.

Untracked files count as this unit's work when the unit was supposed to create
files. List them; `git status --porcelain` catches any outside `Files` that
`add -N` did not mark.

### Step 2. Select lenses

Always: **spec fidelity**. Then add only what the diff actually touched:

| Lens | Fires when | Asks |
|---|---|---|
| **Spec fidelity** | always | does the diff implement the cited design, all of it, and only it? |
| **Test adequacy** | the unit is behavior-bearing | does each named scenario exist, assert the named outcome, and would it fail if the behavior broke — and did the report's evidence strategy actually happen? |
| **Invariant placement** | the unit enforces a quoted invariant row | is the rule in the owner the design named, refusing the illegal case — not re-derived in a use case, controller, or validator? |
| **Boundary** | the diff adds an import across a ring, or touches a port | do dependencies still point inward; does the adapter's shape stay out of the domain? |
| **Contract** | the diff touches HTTP, schema, or a published type | status and error mapping, nullability, migration reversibility, backward compatibility for existing callers; a migration file already committed in `documentation/db/migrations/` is never edited — a schema change is the next numbered file |
| **UI** | the unit's `Docs` cite a screen spec (an `impl-ui` unit) | do elements, states and response outcomes match the screen spec rows, and texts the frame's «Тексты» table; does the screen follow the frame; does it keep the `ux-patterns` rules for the spec's **Тип продукта** — cite the `UX-<n>` it breaks. The orchestrator pastes the product type and the rules the screen touches into the design block |
| **Risk** | grade High, or the unit hit the risk floor (auth, money, migration over live rows, secrets) | what does a hostile or unlucky caller get: missing authorization, non-idempotent retry, partial write, leaked field, race |

A lens that does not fire is not mentioned in the report. Silence is the
correct output for an absent surface.

### Step 3. Dispatch by grade

Resolve reviewers through `executor-catalog` and dispatch each under that
file's Dispatch contract (read the section with the row): the grade's row,
no question to the user. The lenses go into
**one** reviewer packet, built from
`references/reviewer-prompt.md`. The grade decides the roster — never review a
Low unit at High cost, or skip a Mid unit because the diff "looks fine":

| Grade | Review |
|---|---|
| **0** | no dispatch — the orchestrator's own diff-vs-`Files` check is the review. A mechanical diff has no judgment to second-guess. |
| **Low** | no per-unit dispatch. Accumulate the units and run one `review-medium` pass over the batch at the next wave boundary (see Low batch below). |
| **Mid** | one `review-medium` carrying the fired lenses. |
| **High** | one `review-hard` carrying the fired lenses, plus a second `review-hard` dispatch with LENSES TO APPLY = Risk only — a single reviewer that just designed an opinion about the diff is a poor adversary to it. |

Keep the catalog's split: a High unit reviewed on the implementer's
alias tends to ratify its blind spots. `impl-ui` is the named
exception: its review stays on the grade's review row.

Give a grade-0 or Low unit its own `review-medium` pass when the worker
returned `DONE_WITH_CONCERNS`, or when Step 1 found a scope breach. Cheap grades earn
the batch; an anomaly forfeits it.

**Low batch.** By the wave boundary each Low unit is already committed, so
`git diff HEAD` is empty. Build the batch diff from the commits instead: for
each Low unit, the commit whose `Plan-Unit: <version>/U<n>` trailer
matches, `git show <sha>` per unit into one file under `pipeline-work/`, each
section headed by its U-id. The packet is the Low-batch variant in
`references/reviewer-prompt.md`: one UNIT/FILES/SCENARIOS block per unit,
THE DIFF = that file, one VERDICT line per U-id. The
verdict applies to a follow-up commit, never a rewrite of history:
`FIX_THEN_COMMIT` sends the fix to `mechanical-worker` as a new commit with the
same `Plan-Unit:` trailer; `RETURN_TO_EXECUTOR` re-dispatches that unit's
implementer on top of its commit; `COMMIT` means nothing to add.

### Step 4. Judge the findings

Severity, and what it does to the commit:

| Level | Meaning | Effect |
|---|---|---|
| **P0** | breaks a cited contract or invariant, loses or exposes data, or the unit does not do its goal | blocks the commit |
| **P1** | deviates from the cited design, a named scenario is missing or vacuous, scope breach | blocks the commit |
| **P2** | local quality: duplication, unclear naming, a missed edge the design never named | recorded, does **not** block |
| **P3** | nit | recorded, does **not** block |

The test-evidence findings sit at P1 by definition, because the whole point of
a per-unit gate is that a green suite is not proof:

- a named scenario has no test, or has one that asserts nothing the scenario
  names;
- a test asserts what the implementation happens to do rather than what the
  cited design says — the tell is an expected value that only makes sense if
  you read the code first;
- the report claims a red that the diff contradicts (the test file is not
  there, or the assertion could not have failed against the previous tree);
- an existing assertion was relaxed or deleted to make the unit pass, and the
  report does not say the design changed.

Check the evidence strategy the packet named first: a `characterization-first`
or `smoke` unit owes a baseline or a runtime check, not a failing assertion,
so demanding a red there is a false finding.

The reviewer reads the test as if the implementation did not exist: given the
scenario and the design excerpt, is this what should be asserted? A test that
can only be understood by reading the implementation is a P1 no matter how
green it is. Judge tests by whether they would catch the scenario failing, not
by style — naming, structure, and fixtures are P2 at most.

**P2 and P3 never block a unit commit.** The cadence — one unit, one green
commit — is worth more than a perfect diff, and quality passes have their own
place at wave boundaries. A reviewer that blocks on naming stops the pipeline.

**Every P0/P1 quotes its line.** A blocking finding carries the line the diff
adds or changes that it is about (for a missing scenario test, the scenario
line instead). A problem in a context line the diff neither adds nor newly
calls into is pre-existing — `OPEN`, never blocking. A false P1 sends the unit
back to its implementer and moves it one step
closer to the second-failure stop.

Three dismissal rules, because they are where per-unit review generates its
false positives:

1. **The design already decided it.** A finding arguing against a decision the
   `Docs` cite is out of order here. Dismiss it, and if it is genuinely
   worrying, route it to the run report as an open question for the user — not
   as a fix for the executor.
2. **A later unit owns it.** Missing wiring, a missing adapter, an absent
   endpoint that another U-id creates is not a defect. Check `Depends on` and
   the unit map before reporting an absence.
3. **Already known.** A finding matching one recorded earlier in this run is
   not raised again.

### Step 5. Verdict

Exactly one, with no hedge attached ("COMMIT, but reconsider the whole
approach" is not a verdict — put the doubt in the run report):

| Verdict | When | Orchestrator's move |
|---|---|---|
| `COMMIT` | no P0/P1 | commit the unit; P2/P3 to the run report |
| `FIX_THEN_COMMIT` | P0/P1 that is mechanical and fully specified | dispatch `mechanical-worker` with the finding, re-verify, commit |
| `RETURN_TO_EXECUTOR` | P0/P1 needing the unit's judgment back | re-dispatch the unit's own implementer with the findings attached |
| `STOP` | the finding is a design gap, or the unit's attempt budget is spent (`work` Step 6) | do not commit; take it to the user |

Follow-up `Agent` calls (`mechanical-worker`, the unit's implementer) resolve their
own catalog row under the same Dispatch contract as Step 3.

The reviewer proposes fixes in words; it never edits, stages, or commits. A
reviewer that patches the tree destroys the one signal the next step needs —
whether the executor could do the unit as specified.

## Report

Compact, inline, no artifact files — this runs dozens of times.
Write findings in Russian. Keep the heading, column names, and verdict tokens
exactly as below (`doc-versioning` → Document language).

```markdown
### Review U<n> — <verdict>

| # | Sev | File:line | Lens | Finding | Fix | Quoted line |
|---|---|---|---|---|---|---|

**Dismissed** — findings ruled out by design citation, later-unit ownership,
or prior record, one line each with which rule applied.
**Not blocking** — P2/P3 for the run report.
**OPEN** — cross-unit suspicions this unit cannot close (`work` copies
them into Cross-unit watch; `code-review-full` resolves them). Omit the
line when there are none.
**Lenses** — which fired, and the one-line reason for each conditional one.
```

When nothing fired: `### Review U<n> — COMMIT. No findings.` and nothing else.
An empty review needs no ceremony.

A filled review, for calibration — match its density, not its domain:

```markdown
### Review U6 — RETURN_TO_EXECUTOR

| # | Sev | File:line | Lens | Finding | Fix | Quoted line |
|---|---|---|---|---|---|---|
| 1 | P1 | `src/app/pay-order.ts:31` | Invariant placement | запрет повторной оплаты проверяется в use case, а domain §4 отдаёт его `Order.pay()` | убрать проверку статуса, пробрасывать `IllegalTransition` из `Order.pay()` | `if (order.status === 'Paid') throw new ConflictError()` |
| 2 | P1 | `src/app/pay-order.test.ts` | Test adequacy | сценарий повторной оплаты без теста | написать тест по сценарию | `заказ Paid → PayOrder → IllegalTransition, 409 ORDER_ALREADY_PAID (covers BR-3)` |

**Dismissed** — «нет ретрая при сбое шлюза»: scenarios/orders `PayOrder` решает не ретраить (правило 1).
**Not blocking** — P2 `src/app/pay-order.ts:12`: `ord` → `order`.
**OPEN** — `PaymentGateway.charge` принимает `amountCents: number`, а U2 моделирует деньги как `Money`; сверить в `code-review-full`.
**Lenses** — Spec fidelity: clean. Test adequacy: #2 (use case несёт поведение). Invariant placement: #1 (unit исполняет BR-3). Contract: clean (маппинг ошибки в 409).
```

Finding #1 quotes the line the diff adds; #2, a missing test, quotes the
scenario instead. `RETURN_TO_EXECUTOR`, not `FIX_THEN_COMMIT`, because writing
the missing test means choosing what it asserts — the implementer's judgment.

## Before you finish

- Every changed path was classified inside or outside `Files` — Step 1.
- Every fired lens produced a finding or an explicit clean line — Step 2.
- Every named scenario was checked for existence *and* for asserting its
  outcome, judged against the design excerpt, not the implementation — Step 4.
- The evidence strategy was reconciled with the diff; a missing or
  contradicted red on a `test-first` unit is a P1 — Step 4.
- Every P0/P1 quotes a line this diff adds or changes, or the untested
  scenario; anything else moved to `OPEN` — Step 4.
- Every dismissal cites which of the three rules applied — Step 4.
- Exactly one verdict, no P0/P1 left unclassified under it — Step 5.
- Nothing in the tree was changed by this review — Step 5.

## References

- `references/reviewer-prompt.md` — the packet the reviewer subagent receives
  and the report it returns.
- `executor-catalog` (skill) — the review tier per grade and its agent.
- `plan/references/complexity.md` — what each grade claims about the unit,
  which is what the review is calibrated against.
- `code-review-full` (skill) — the second layer, run once after the whole plan
  lands, that this skill's narrow scope hands off to.
