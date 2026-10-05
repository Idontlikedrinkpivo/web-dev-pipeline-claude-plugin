# Two-phase dispatch (Step 4b)

Read this before dispatching any High unit or any unit on the risk floor:
auth, authorization, money, migrations over live rows, secrets.

For these units, do not accept the red as a claim — witness it. Dispatch the
unit's own implementer twice:

1. `PHASE tests-only` — it writes the tests for the listed scenarios and
   touches no production code. You then run those tests yourself and confirm
   they fail for the reason the scenario names. A test that passes here is a
   finding, not a pass: it asserts nothing, or the behavior already exists.
2. `PHASE implementation` — the same implementer makes them pass without
   editing their assertions. An assertion it believes is wrong comes back as
   `BLOCKED`, not as a quietly relaxed expectation.

Both phases go to the same named implementer: the one that wrote the tests is
the one that has to satisfy them, and a cheaper agent picking up the second
phase would be free to misread assertions it never chose. Both phases are one
unit, one commit, and **one attempt** of the unit's budget (`work` Step 6) —
not a second unit and not an escalation.

A retry of a two-phase unit (a `RETURN_TO_EXECUTOR`, or an escalation to the
next tier including `impl-critical`) keeps the tests you already saw fail: it
is a single `PHASE implementation` dispatch carrying the findings or the
previous report. Only when the finding is about the tests themselves does the
retry go back to `PHASE tests-only`.

For every other grade a single `PHASE full` dispatch is enough — the cost of a
second round trip is not worth it below the risk floor.

In the run report's **Evidence** line, mark these units' red as witnessed by
the orchestrator, not taken from the worker's report.
