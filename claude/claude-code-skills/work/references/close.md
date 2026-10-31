# Closing a run — the checks and the final-review fixes

Read by `work` at Step 7: the checks it runs itself before `code-review-full`, and the fix rounds when that
review's verdict is not `PASS`.

## The checks

When every unit in scope is committed, run these yourself and save each output under
`$(git rev-parse --git-dir)/pipeline-work/` — `code-review-full` reads them by path and does not re-run them.

1. **Критерии готовности** — every command in the plan's §5, with its exit code, on HEAD after the last commit.
2. **A browser suite among them** runs in this order:
   1. Open its e2e section in `progress.md` (`references/progress-file.md` → The e2e section) and post the progress
      line.
   2. Run the verify skill's doctor (`.claude/skills/verify/`) and go on when it says READY. With no verify skill,
      write and prove it first (`deploy-topology` → `references/verify-skill.md`); its commit carries
      `Plan-Unit: <version>/verify-skill`.
   3. Run the suite on parallel stands and clean up per `ui-test-cases` → `references/parallel-stands.md`. A stand
      not yet copyable is a question there, not a silent single stand; making it copyable is its own commit with
      `Plan-Unit: <version>/stand`.
3. **Health, mutants and dead code** — `references/health.md` → Measure: duplicates, complexity and sizes against
   BASE, mutants over the run's diff, and the dead-code report. A simplifier pass lands what grew before the
   review, as its own commit with the trailer `Plan-Unit: <version>/health-<n>` (`references/health.md` →
   Simplify).

## Fixes after the final review

Anything but `PASS`: before the first fix, add «Исправления по финальному
ревью» to the progress file — every finding a row with who fixes it and
`⏳ ждёт` (`references/progress-file.md` → Fixes after the final review) —
and post the progress line, saying the fixes are the section at the bottom of
the page. Each fix then lands like a unit — your Step 5.3 checks, its own
commit with its trailer, its rows — and its review is the re-review: after each
round of fixes, run `code-review-full` again over that round's fix commits only,
with its re-review packet — never a second time over the whole diff — until `PASS`,
while each round makes progress (`pipeline` → `references/convergence.md`);
when the rounds stop making progress, stop and take the open findings to the
user.
