# Code health at a run's close

An agent's code drifts the same way every time: blocks get copied, functions and files grow, tests turn into
records of calls. Step 7 measures that drift against the run's base before the whole-run review, removes what grew
in one behaviour-neutral commit, and hands the numbers to `code-review-full`.

## Measure

Over the run's diff `BASE...HEAD`, with the tools of `repo-scaffold/references/quality-gates.md`:

| Measure | Source |
|---|---|
| duplicates — the share and the blocks the run added | `jscpd` on the changed files against the base |
| functions over the complexity and length thresholds, files over the size thresholds — added or grown | the linter's rules over the changed files |
| surviving mutants — in the files of units that enforce an invariant row or are graded High | Stryker incremental / `mutmut` on those files only |

Save the table under `$(git rev-parse --git-dir)/pipeline-work/` and into the run report as «Здоровье кода»:
each figure at BASE and at HEAD.

## Simplify

When the run added duplicates or grew a function or file past a threshold, dispatch one `impl-medium` unit
«Упрощение»: remove the copies (take them from the one home the architecture names), split what grew, keep
behaviour — no test assertion changes, the full suite green before and after, `lint` and `typecheck` green. It
lands as its own commit before `code-review-full`. Surviving mutants are not fixed here: they go to the review as
findings on the tests.

## Hand over

`code-review-full` receives the health table and checks that HEAD is not worse than BASE on any row; a row that got
worse without a reason in the run report is a finding.
