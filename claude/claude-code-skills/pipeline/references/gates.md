# Where each gate comes from, and why it is there

Read before asking a gate question: why each gate sits on its stage and what
the question says about its cost.

**`grill-me` is an exit gate, and only on stages 1 and 2.** The document is
written first. A written use case with flows and acceptance criteria is far
easier to falsify than a brief that is still prose. Whatever the grill
reverses is applied to that same document in place, before its `doc-review`
is asked about.

The question is asked on both of those stages every time. Mockups are not
grilled: the user reviews them in Figma, and the screen specs written from
them go through `doc-review`. The gate runs only when the user picks yes.
`grill-me` is frontier-driven, so a stage that settled nothing new has an
empty frontier and the session ends immediately — say that in the question,
as the reason the gate is cheap when nothing new was decided.

**`doc-review` is asked on stages 2, 3, 4, 5, and 8** — the SRS, the schema,
the API, each architecture document (foundation, domain model, scenarios of
an area), and the screen specs. It does not start because the previous gate
finished. Its personas check a written document against itself and against
its premise.

Its cost is real and was accepted deliberately: two always-on personas per
document, plus the conditional ones — a full greenfield run dispatches on
the order of 20–35 document-review subagents, and the `doc-review-hard`
third runs on `opus`. Say that cost in the question. Trim it by narrowing
which personas activate (that lives in `doc-review`), or by recommending the
skip when the change is small — never by not asking.

**`docs-consistency` is stage 10, where the branches meet.** Each
`doc-review` reads one document; nothing else reads the SRS, schema, API,
architecture documents and screen specs together, and a contradiction
between two of them otherwise surfaces in `work` as a unit that cannot
satisfy both. It is one `sonnet` dispatch over the whole set — say that in
the question. On an increment it is offered again whenever a document
changed after the last check ("Where am I" step 3); for a one-field change
recommend the skip.

**`plan-review`, not `doc-review`, is the gate on stage 11 — and it is not asked.** By the plan every product decision is settled in the documents, so `plan` runs the review itself and fixes what it finds round by round until it passes; only a `STOP` (the documents have a gap) or a cycle that stops making progress comes back to the user. A plan is a work order, not a contract: the questions that matter are
whether a unit lands as one green commit, whether `Depends on` forms a DAG,
whether a grade is calibrated, whether every invariant and acceptance
criterion is covered by some unit. `doc-review` has no persona for any of
that, and its classifier has no type for a plan.

