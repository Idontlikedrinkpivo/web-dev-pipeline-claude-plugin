# Two approaches at the top of the ladder

Read by `work` (Step 6) when a unit at `impl-critical` has failed in a way
that puts its approach in doubt.

One more round at the top tier, with every report so far, usually gets one
more variant of the same approach: the reports steer the executor back to
it. Two executors that start from the same base, each told a different
approach, rarely make the same mistake — and here the tests, not a judge,
pick which one worked. Measured 2026-10-14 on design documents: two
independent Opus writers missed different risks, and a blind judge reading
both did not notice the winner's gaps — so the choice belongs to the tests,
and nothing is merged from the loser.

## When

All of these hold:

- the unit is at `impl-critical`;
- two rounds there have failed the same check, or the unit came back
  `HARDER_THAN_EXPECTED` from `impl-critical`;
- the premise check (`pipeline` → `references/convergence.md` → Attack the
  premise) found the approach itself false — or could not tell — rather
  than a slip inside a sound approach.

A slip inside a sound approach gets the usual next round. A missing design
decision is a stop for the user, never two approaches. A UI unit
(`impl-ui`) and a grade-0 unit never get two.

## How

1. **Name the two approaches** — one sentence each, before any dispatch:
   the one the premise check points to, and a different one — not a
   variant of the failed attempts («держать блокировку строки кошелька» /
   «оптимистичная проверка версии с повтором»). When a second approach
   that differs in kind cannot be named, there is only one: run the normal
   round.
2. **Restore the base.** Save the current attempt's diff as a patch
   (`pipeline` → `references/pause-and-resume.md` → Pausing) and reset the
   tree to the last commit: both attempts start from the same commit.
3. **Dispatch two `impl-critical`** with the unit's packet, every previous
   report, and one more line under `APPROACH`: «Подход A: <sentence>.
   Другой подход пробует второй исполнитель — не переходи на него». In
   parallel with `isolation: "worktree"` when the focused tests share no
   runtime resource (Step 3); otherwise one after the other, the second
   also from the base commit. The progress row reads `🔄 в работе: два
   подхода (A, B)`.
4. **Pick by the checks.** An attempt counts only when its focused tests
   and the unit's `Verification` pass in its own tree. One passes — it
   wins. Both pass — each goes to the unit's reviewer (`code-review-unit`);
   the one with fewer P0 and P1 wins, and on a tie the smaller diff.
   Neither passes — that is the stop in `convergence.md` (a finding
   survived the top tier), with both reports and both approaches named.
5. **Bring the winner home** — merge or cherry-pick its worktree branch
   into the main tree, then the unit's usual review and its one commit
   (`Plan-Unit:`). Nothing is taken from the loser. Remove both worktrees
   and their branches.
6. **Record** one line in the run report and the progress row's Ревью
   cell: «U14: два подхода — A «…» прошёл, B «…» упал на <check>».
