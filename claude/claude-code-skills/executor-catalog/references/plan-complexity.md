# Plan-document complexity

The grade answers one question: **how much judgment does slicing this
plan require?** Not how many units it will contain and not how long the
file will be. A long CRUD plan is still Low; a short plan that cuts
across auth and money can be High.

Used by `plan` before it dispatches. The session does not type a model.
The name it dispatches is in the catalog's **plan-writer** branch, and that
name is the agent.
Unit grades inside the plan are a different cascade
(`plan/references/complexity.md`) and run after the slice, on the writer.

## The cascade

Run in order. The first rule that fires decides. The risk floor (rule 2)
is the one exception: it sets a minimum and the cascade runs on, so a
later rule may raise the grade but none lowers it. Count from the
architecture, the SRS, and the other design documents — not from a unit
table that does not exist yet.

1. **Mechanical increment.** One use case, one screen, or one operation,
   a local pattern already in the tree, and docs that fully specify the
   outcome → **Low**. Only when the increment adds no new auth rule, no
   new money rule, and no migration over existing rows; otherwise skip
   to rule 2. It runs first so a settled increment is not re-graded by
   the surface it touches.
2. **Risk floor.** An auth, authorization, money, secrets, or external
   contract decision that is left open for this plan to make — how the
   change is cut into units and ordered when the design does not already
   place it — or a migration on existing data, whose staging is always
   the plan's call → **at least Mid**, and **High** when the increment
   rewrites more than one existing section. Being in scope is not a
   decision. No file-count argues this down.
   - Does **not** escalate: auth, roles, or secrets already fixed by an
     SRS NFR row or the architecture's security decisions and only
     transcribed into units; an amount column with no rounding or
     currency rule to decide; the SRS's standard security checklist
     itself.
3. **Level gate.** Framework-first → **Low**. Modest whose rules are
   only field validation (plain CRUD, no state transition, no rule across
   two entities) → **Low**; other Modest → **Mid**. Full → **High**.
   An increment that only appends one use case, one screen, or
   one operation, with no rule change, is graded by its own size (rule 1
   or 5), not the old document's level.
4. **Compound gate.** Any two of: more than five state-changing use
   cases, more than five entity tables, more than seven HTTP operations,
   brownfield with no architecture document → **High**. Count only use
   cases and operations that carry an invariant or a state transition;
   CRUD endpoints over one aggregate do not count. The gate measures
   complexity, not length.
5. **Default.** Ordinary one-slice Modest work → **Mid**.

A greenfield plan with no architecture document is a **stop**, not a
grade. Brownfield with no docs is a grade: rule 4 counts it as one
signal, and rule 2 still applies.

## Grading a revise

A revise after `plan-review` is graded on its own, not by the plan it
edits: four spelled-out text fixes on a High plan do not need the High
writer. Read the `Fix kind` column of `plan-review.md` over the blocking
(P0/P1) rows and take the highest:

| Blocking rows | Revise grade | Executor |
|---|---|---|
| every one `mechanical` — the Fix is the finished edit to the plan text: a citation, a `Parallel-safe` value, an executor name, a grade a floor dictates, a missing scenario line spelled out | **Low** | `plan-lite` |
| any `local`, none `reslice` — a local decision: change a grade and its implementer, move units between waves, add `Files` after checking the code, write scenarios for a changed document | **Mid** | `plan-medium` |
| any `reslice` — split or merge units, add a unit, change `Depends on` across several units, change a security, money, or migration decision | the plan's own grade (the cascade above) | that grade's row |

A report without the column (an older review) grades the revise as the
plan. `BLOCKED` or `HARDER_THAN_EXPECTED` escalates one tier per failure,
lite → medium → hard, as on a first write. The cascade above is unchanged for writing a
plan.

## What each grade dispatches

| Grade | Executor | The writer is expected to |
|---|---|---|
| **Low** | `plan-lite` | slice a fully bounded increment along seams the design already drew. `doc-typist` prints it |
| **Mid** | `plan-medium` | close the remaining slice and grade decisions inside the skill's rules. `doc-typist` prints it |
| **High** | `plan-hard` | hold Full-trigger, security, or cross-section slicing. `doc-typist` prints it |

There is no grade 0 on this branch. `plan-hard` is terminal. A writer
that returns `BLOCKED` or `HARDER_THAN_EXPECTED` escalates one tier per
failure (lite → medium → hard), and that dispatch asks again; at
`plan-hard` it repeats while each round makes progress
(`pipeline` → `references/convergence.md`).
