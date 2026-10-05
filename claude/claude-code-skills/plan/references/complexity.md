# Complexity grading

The grade answers one question: **how much judgment does this unit require
from whoever writes it?** Not how long it takes, not how many lines it
produces, not how important the feature is. A 400-line codemod is cheap
judgment; a 12-line state transition may not be.

Grade after the unit's fields are filled, from the fields.

## The six signals

Score each signal, then run the cascade below. Never average them.

| # | Signal | Cheap end | Expensive end |
|---|---|---|---|
| 1 | **Decision left open** | the design fully determines the outcome; the unit transcribes it | the unit must choose a shape, an algorithm, a boundary, or an error model |
| 2 | **Spec completeness** | every artifact is named with its signature, states, and errors | `Docs` cite a section that describes intent, not shape |
| 3 | **Blast radius** | one file, or many files with one mechanical shape | multiple rings, or a contract other units import |
| 4 | **Pattern precedent** | an equivalent already exists in the repo to mirror, lands in an earlier unit reachable via `Depends on`, or is fixed by the architecture's file tree / snippet — the unit's `Pattern` names it | first of its kind here — `Pattern` reads `— first of its kind` |
| 5 | **Failure cost** | wrong code fails loudly in tests | wrong code leaks data, loses money, corrupts stored state, or breaks a published contract |
| 6 | **Testability** | outcome asserted directly | needs fakes, time control, concurrency, or an end-to-end path to prove |

## The cascade

Run in order. The first rule that fires decides. Later rules do not soften an
earlier one.

**Order is load-bearing: every High gate sits above every Mid gate.** A
cascade that asks "is anything expensive? → Mid" before it asks "is this
compound? → High" can never reach High except through the risk floor, which
silently routes every hard-but-harmless unit (concurrency, a first-of-its-kind
abstraction, an open algorithmic choice) to the Mid implementer.

1. **Risk floor.** Signal 5 at the expensive end — auth, authorization, money,
   migration over existing rows, secrets, published contract — is **at least
   Mid**, and **High** when signal 1 or 2 is also expensive. No file count
   argues this down.
2. **Compound gate.** Three or more signals at the expensive end, or signal 1
   expensive together with 3 or 6 → **High**. This is the route for work that
   is hard without being dangerous: nothing here mentions risk.
3. **Mechanical gate.** Signals 1, 2 and 5 all cheap, and the change has one
   repeatable shape (rename, move, config value, regenerate, apply a settled
   pattern to N sites) → **0**, regardless of how many files it touches.
4. **Spec floor.** Signal 2 expensive (the design does not determine the
   outcome) is **at least Mid**. Undecided work is expensive work even when it
   is small, because the executor is finishing the design.
5. **Transcription gate.** Signals 1 and 2 cheap, precedent exists (4 cheap),
   one ring, and the tests assert directly → **Low**.
6. **Judgment gate.** Any of signals 1, 3, 4, or 6 at the expensive end → **Mid**.
7. **Default.** Nothing above fired — every signal is cheap but the change has
   no single repeatable shape → **Low**. Reaching here means the unit is
   ordinary, not that the cascade failed.

## What each grade means at dispatch

| Grade | The work is | What the executor is expected to do |
|---|---|---|
| **0** | fully determined and repeatable | apply the shape exactly, change nothing else |
| **Low** | determined but not repeatable | transcribe the design into working code, match local patterns |
| **Mid** | partly open, or costly if wrong | make the remaining local decisions, prove them with tests |
| **High** | open, cross-cutting, or unforgiving | design the missing part inside the given boundaries, then prove it under edge cases |

## Anti-inflation gates

Grade inflation is the expensive failure: it gives a transcription High
latitude and a second review pass, and hides which units actually need care.

- **Volume is not complexity.** 30 files of one shape is **0**. A unit is not
  Mid because it is long.
- **Domain importance is not complexity.** The core aggregate's *getter* is
  still Low. Grade the unit, not the module's prestige.
- **Unfamiliarity is not complexity.** A framework the planner has not used,
  but whose pattern exists in this repo, is Low — signal 4 is about the repo.
- **A long test list is not complexity.** Ten direct assertions are cheap; one
  concurrency assertion is not.
- **The user's tone is not a signal.** "This is critical" raises review, not
  the implementer tier.

## Anti-deflation gates

- **Small is not cheap** when the design left the shape open (rule 4).
- **"Just wiring"** that decides transaction boundaries, error mapping, or
  ordering is Mid — wiring is where consequences get decided.
- **A migration is never Low** once rows exist, even a one-column one.
- **First of its kind** is at least Mid even when the docs are precise, because
  there is no local pattern to check against. A unit has precedent when an
  earlier unit in this plan, reachable via `Depends on`, establishes the
  pattern, or when the architecture's file tree / snippet fixes the shape —
  `Pattern` then cites that unit's path or that section.

## When the grade splits the unit

If half the unit is expensive and half is mechanical, that is a signal about
the *slicing*, not the grading. Two responses, in order of preference:

1. **Split** into two units when both halves land green alone — the decision
   unit and the mechanical unit, ordered.
2. **Nest** when they cannot land separately: grade the unit by its expensive
   half, keep that tier as `Implementer`, and put the mechanics in
   `Nested does`. The implementer keeps the decision and hands out the typing.

Nesting is never a way to reach a stronger model. That is what the tier is for.

## Calibration

Schematic on purpose — match the shape, not the domain.

| Unit shape | Grade | Deciding signal |
|---|---|---|
| Rename a symbol across the repo; add a config key; regenerate a client from an unchanged spec | **0** | rule 3 — one repeatable shape, nothing open |
| Value object whose one invariant is quoted in the design, with a sibling value object already in the repo to mirror | **Low** | rule 5 — determined, precedented, one ring |
| A read model / query for an audience whose fields the design lists | **Low** | rule 5 — transcription |
| Aggregate root owning three quoted invariants and a two-state transition | **Mid** | rule 6 — signal 6, and the transition is the first of its kind |
| Use case whose steps are listed but whose error-to-status mapping the design leaves to the adapter | **Mid** | rule 4 — spec incomplete on the boundary |
| Repository adapter with an explicit storage model and mapper in the design | **Low** | rule 5 — unless it introduces the unit-of-work shape, then Mid |
| Migration adding a nullable column plus its backfill over existing rows | **Mid** | rule 1 — stored-state cost, shape given |
| Authorization check across two aggregates, or the token issue/refresh path | **High** | rule 1 — risk plus an open decision |
| Outbox / must-deliver side effect: transaction boundary, retry, idempotency key | **High** | rule 2 — three expensive signals |
| Job scheduler's lease/heartbeat/reaper shape: no money, no secrets, but the design names the goal and leaves the mechanism open, and proving it needs time control and a second worker | **High** | rule 2 — signal 1 with 6, no risk surface at all |
| First cross-ring abstraction in the repo (a unit-of-work, an event bus) whose shape the design sketches but does not fix | **High** | rule 2 — signals 1, 3, 4 expensive together |
| Screen with all its states where the screen spec names each state and response outcome and a sibling screen exists | **Low** | rule 5 — states enumerated |
| Screen whose screen spec lists open «Разрывы» or leaves a state undecided | **Mid** | rule 4 |

Those two rows set the grade only. When the unit's `Docs` cite a screen
spec and a Figma `nodeId`, `Implementer` is `impl-ui` and `Nested` is `—`.
The grade does not assign `impl-lite`, `impl-medium`, or `impl-hard`. The
assignment rule is in `executor-catalog/references/assignable-implementers.md`.

## Sanity-check the distribution before writing the plan

The cascade is per-unit, but its output has a shape worth checking as a whole:

- **No High anywhere in a plan that has a hard part.** Almost always means
  rule 2 was skipped and risk was treated as the only route to High. Re-run
  the cascade on the units whose `Approach` still contains a decision.
- **Everything Mid.** The cascade was not run — Mid is what a grade looks like
  when nobody counted signals. Real plans have 0 and Low units.
- **High on more than a third of the units.** Either the design is genuinely
  unfinished (say so in `open-questions.md` instead of routing around it), or
  importance is being read as complexity.

## Recording the grade

`Why` names the one deciding signal, in the cascade's vocabulary, under twelve
words:

- `rule 3 — one repeatable rename shape, nothing open`
- `rule 4 — error mapping undecided in api spec`
- `rule 1 — authorization decision across two aggregates`
- `rule 2 — mechanism open, needs time control and a peer worker`

A `Why` that restates the goal ("implements the order entity") is not a grade;
it is a label. Re-run the cascade.
