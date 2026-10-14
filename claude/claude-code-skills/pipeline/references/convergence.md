# Repeat until it passes

Read this whenever a check sends work back: a review verdict that blocks, a
lint error, a missing frame or file, a failing test. The pipeline repeats
the fix-and-check cycle until the check passes — there is no fixed number of
rounds. What ends a cycle early is lack of progress, not a count, so a run
that converges is never cut off, and a run that circles is stopped at once.

## How a round stays cheap

- **Scope shrinks.** A re-check reads what the last fix changed and the
  findings still open, not the whole work again: the fix commits' diff for
  code, the changed units for a plan, the missing items for frames. A new
  finding in a later round must sit in what the last fix changed; anything
  else was already checked. (A document review is the exception — see
  below.)
- **History travels.** The fixer gets every open finding with what was
  already tried for it, so no approach is repeated blind.
- **Strength rises only when needed.** A finding that survives a fix goes to
  the next tier of its ladder (`executor-catalog` → Escalation) — after the
  premise check below when two fixes have already failed it, so the stronger
  tier gets the right target, not a better version of the same miss; a first
  fix stays on the cheapest tier that can make it. A mechanical finding
  stays with `mechanical-worker`, and the session's own check confirms it —
  no reviewer dispatch.
- **Only what blocks circles.** P0 and P1 findings loop; P2 and P3 go to the
  report and never start a round.

## Progress

After every round compare the open findings with the round before.
Progress is either:

- the open set shrank, or
- the only new findings sit in what the last fix changed and none of them
  was closed before.

## Attack the premise

Each failed fix built on one assumption is evidence against the assumption,
not a reason to tune the fix. So when **two fixes that share one premise
have failed the same check**, the third is not written yet:

1. **Write the premise** in one sentence — what both fixes took for granted
   («the element appears, only slowly»; «this database belongs to this
   code»; «the file pane redraws on a subagent's Edit»).
2. **Run a check that would come out differently if the premise were
   false** — not another fix: log where the request really goes, list the
   migrations the database recorded against the files, screenshot the page
   at the moment of the timeout, open the file and watch it. A script when
   it can be rerun.
3. **Act on what it shows.** The premise holds — the next fix (or the next
   tier) goes on, with the check as evidence. It is false — the next fix
   targets what the check found, and the two failed fixes are reverted when
   they only served the false premise.
   On the code branch at `impl-critical`, a false approach gets two
   approaches from one base, chosen by the tests (`work` →
   `references/two-approaches.md`).

This comes before escalation and before the stop rules below: a round that
merely changes the error text looks like progress while the premise is
wrong. The round's line says it: «Круг 3: допущение «запрос доходит до
стенда» — ложно: уходит на :8080 чужого стенда».

## When to stop and ask the user

Stop the cycle and ask — what is open, what was tried, the options «ещё
круг», «беру на себя», «остановиться» — when:

1. **A closed finding came back** — two fixes undo each other;
2. **a round closed nothing** — the same open set as before;
3. **a finding survived a fix at the top tier** of its ladder
   (`impl-critical`, `design-hard`, `plan-hard`, the Figma builder);
4. **the verdict is `STOP`**, or the fix needs a decision only the user can
   make (a design gap, a missing requirement) — at once, in any round.

Each round is one line in the stage's progress file or report («Круг 3:
закрыто 2, осталось 1, новых 0»), so the user sees convergence without
asking.

## A document review

`doc-review` re-reads the whole document every round, because a fix in one
section can contradict another; the decision primer keeps it cheap — a
rejected finding is never raised again and an applied one is only checked
for having landed. After a round whose fixes were applied the user is asked
whether to run the next one — no limit on how many; a round that brings no new finding ends the review,
and the progress rules above stop it early.
