# Design-document complexity

The grade answers one question: **how much judgment does writing this
document require?** Not how long the file will be. A 600-line CRUD
architecture is still Low; a 120-line public-API increment can be High.

Used by `clean-architecture-design`, `db-schema-design`, and
`openapi-spec-generator`. They do not type a model. The name they
dispatch is in the catalog's **design** branch, and that name is the agent.
`clean-architecture-design` grades each of its documents separately and
dispatches one writer at the highest grade — see "Architecture: grade
per mode" below.

## The cascade

Run in order. The first rule that fires decides. The risk floor (rule 2)
is the one exception: it sets a minimum and the cascade runs on, so a
later rule may raise the grade but none lowers it.

1. **Mechanical increment.** One table, one operation, or one entity with
   no new invariant and a local pattern already in the document → **Low**.
   Only when the increment adds no new auth rule, no new money rule, and
   no migration over existing rows; otherwise skip to rule 2. It runs
   first so a settled increment is not re-graded by the surface it
   touches. A new column on a populated table fails the guard and stays
   Mid (rule 5).
2. **Risk floor.** An auth, object-level access, money, PII-audience,
   secrets, or versioned public / partner API decision that is left open
   for this document to make → **at least Mid**, and **High** when the
   increment rewrites more than one existing section. Being in scope is
   not a decision. No table-count argues this down.
   - Escalates: which role may call which operation when the SRS names
     the roles but not the matrix; how an amount is rounded, converted,
     or kept idempotent on retry; which fields each audience sees when
     the SRS names the audiences but not the fields.
   - Does **not** escalate: auth, roles, or secrets already fixed by an
     SRS NFR row (or by a pre-dispatch answer in INPUTS) and only
     transcribed; an amount column with no rounding or currency rule to
     decide; the SRS's standard security checklist itself.
3. **Level gate** (architecture only, and only when Step 2 has already
   picked a level). Framework-first → **Low**. Modest whose rules are only
   field validation (plain CRUD, no state transition, no rule across two
   entities) → **Low**; other Modest → **Mid**. Full → **High**.
   An increment that only appends one entity / one table / one
   operation, with no rule change, is graded by its own size (rule 1 or
   5), not the old document's level.
4. **Compound gate.** Any two of: more than five state-changing use cases,
   more than five entity/aggregate tables, more than seven HTTP operations,
   an increment that rewrites three or more existing sections → **High**.
   Count only use cases and operations that carry an invariant or a state
   transition; CRUD endpoints over one aggregate do not count. The gate
   measures complexity, not length.
5. **Default.** Ordinary one-slice Modest work → **Mid**.

Missing inputs are a **stop**, not a grade. `db-schema-design` and
`openapi-spec-generator` stop without the SRS (and, for OpenAPI, without
the schema when the system stores data). `clean-architecture-design`
stops without the SRS or without a schema or OpenAPI spec the pipeline
already produced; `domain` also stops without the foundation, and
`scenarios` without the foundation and the domain model. Do not
dispatch a writer to invent a table the SRS did not imply, an operation
with no use case, or an auth scheme.

## Architecture: grade per mode

Run the cascade once per document, counting only what that document
decides. The risk floor (rule 2) still applies to each. One writer
settles all documents of the sitting, so the dispatch takes the
**highest** of their grades.

| Mode | What sets the grade |
|---|---|
| `foundation` | as above: rules 1–5, with the level gate (rule 3). Full → High. An increment that only adds names (a port method, an HTTP row, a config variable, a file line) is rule 1 → Low |
| `domain` | the rules and entities it settles. Only field validation, no state transition, no rule across two entities → Low. Up to about five entities with state transitions or rules across entities → Mid. More than that, or money / time-boundary / at-most-once rules left to decide, or a Full level with audiences → High. An increment adding one entity or a few rows with no changed rule → Low |
| `scenarios:<area>` | the area's use cases. Load-ask-save and read-and-return only → Low. Any key scenario (≥ 3 ports or externals, parallel calls, a transaction spanning an external call, retries / idempotency, a long-running operation) → Mid. Two or more key scenarios, or an outbox / idempotency decision this document makes → High. An increment adding one plain use case → Low |

## What each grade dispatches

| Grade | Executor | The writer is expected to |
|---|---|---|
| **Low** | `design-lite` | confirm a fully bounded slice fits the template. `doc-typist` prints it |
| **Mid** | `design-medium` | close the remaining local design decisions inside the skill's rules. `doc-typist` prints it |
| **High** | `design-hard` | hold Full-trigger / security / cross-section judgment. `doc-typist` prints it |

There is no grade 0. `design-hard` is terminal on this branch. A
writer that returns `BLOCKED` or `HARDER_THAN_EXPECTED` escalates one
tier per failure (lite → medium → hard); at `design-hard` it repeats
while each round makes progress (`pipeline` → `references/convergence.md`).
