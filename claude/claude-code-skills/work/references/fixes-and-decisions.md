# A fix after a commit, a decision changed during the run

Read by `work` when either happens, before the next dispatch: a Low-batch or final-review verdict asks for a fix
on a committed unit, or the user answers a stop, changes their mind, or a fact overrules a document.

## A fix after a commit

**A fix after a commit** — from a Low batch review or from the final review —
is a new commit on top, never a rewrite of history. It goes to the executor
the verdict names (`mechanical-worker` for a mechanical finding, the unit's
own implementer for `RETURN_TO_EXECUTOR` / `RETURN_TO_UNIT`), passes your
Step 5.3 checks, and has one review per round — a Low-batch fix
`code-review-unit` over its own diff (a mechanical one your own check), a
final-review fix `code-review-full`'s re-review, never both. It carries the trailer of the unit it fixes
(`Plan-Unit: <version>/U<n>`); a fix that spans units carries
`Plan-Unit: <version>/review-fix-<n>`. List every such commit in the
run report, so `code-review-full` counts it as mapped.

## A decision changed during the run

**A decision changed during the run** — the user answers a stop, changes
their mind («давай по-другому»), or a fact overrules a document. Before
the next dispatch, follow `pipeline` → `references/decision-changes.md`:
a line under «Изменённые решения», every document that states the old
decision fixed through its writer, one commit with no version change and the
trailer `Plan-Unit: <version>/decision-<n>`, so `code-review-full` maps it.
Later packets carry it as `CHANGED DECISIONS`; a committed unit built on
the old decision gets a follow-up commit, as in **A fix after a commit**;
a change that needs a new unit is a plan change — stop and ask. A run
that leaves a changed decision only in code has failed this step.
