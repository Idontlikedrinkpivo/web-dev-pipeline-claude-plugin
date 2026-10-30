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
| surviving mutants — in the lines of units that enforce an invariant row or are graded High | Stryker incremental / `mutmut` on those lines only — **Mutation runs** below |

Save the table under `$(git rev-parse --git-dir)/pipeline-work/` and into the run report as «Здоровье кода»:
each figure at BASE and at HEAD.

**A tool that is not there.** Use the project's own install of each tool (its dev dependencies, its scripts); a
one-off run through the package runner (`npx jscpd`, `uvx mutmut`) is fine when it needs no setup. A tool that
cannot run — not installed and not fetchable, a mutation runner the project never configured, a stack it does
not support — leaves its row «не измерено: <tool> — <причина>» and the rest of the table goes on. Never add a
dependency or a config file to the project for this step: that is a change no unit planned. The review reads
«не измерено» as no data, not as worse, and the run report names the gap so the next plan can add the tool.

## Mutation runs

Mutation testing changes the code on purpose — a `>` into `>=`, a condition into `true` — and runs the tests
against each change, the **mutant**. A mutant the tests catch is **killed**; one they do not is a **survivor**: an
assertion is missing. An **equivalent** mutant changes nothing anyone can observe (`i < n` and `i != n` in a loop
that only counts up): no test can kill it. It is slow — the whole focused suite per mutant — so it stays narrow.

**Tell the user once, before the first mutation run of the iteration**, in plain words: what the three words
mean, what the run will take (the mutant count, the streams and the time estimate below), and one question
about equivalent mutants — `A. Оставить с причиной в отчёте` (рекомендую), `B. Упростить код в следующей итерации, чтобы мутанта
не было`, `C. Пометить в коде (`// Stryker disable next-line <mutator>: <причина>`)`. The answer holds for the
iteration; the run report records it.

**Scope: lines, not files.** The scope is the lines of the rules and guards the units enforce — an entity's
method, a guard, a mapping — named as ranges: Stryker `--mutate "src/a.ts:40-72,src/b.ts:10-31"` (one argument,
comma-separated: **a repeated `--mutate` keeps only the last one**); mutmut — the paths in `[tool.mutmut]` of
`pyproject.toml` for this run, or the mutant names `mutmut run` accepts (check the installed version's `--help`).
A whole file is mutated only when all of it is rule code. A survivor outside the scope goes to the run report's
«Задачи на потом», never into this run.

**In parallel, each stream with its own data.** A mutation run takes the machine for itself — never beside
another test run, a stand build or an e2e suite from the same sources — and then uses all of it: hours of one
stream are the default to avoid, not the safe choice.

1. **The budget.** Count the cores (`sysctl -n hw.ncpu` / `nproc`) and what Docker has (`docker info`: CPUs,
   memory). The workers of everything running at once — every stream, every part — stay within cores − 2; the
   other two keep the database, Docker and the session itself responsive. A stream that pushes the machine into
   swap costs more than it gives: one fewer.
2. **A part without the database** (the frontend, pure domain rules): one process, `--concurrency` up to the
   budget.
3. **A part whose tests use the database** never shares one between two workers — parallel mutants would rewrite
   each other's rows and every failure would lie. Split its ranges into K roughly equal shares (K ≤ 4: the database
   server shares the same cores), and give each share its own process at concurrency 1 with its own resources on
   the same servers: a test database `<project>_test_mut_<k>` (the name holds «test» and differs from
   `DATABASE_URL`, so the test helper accepts it — `references/run-hygiene.md`), migrated before the start; its own
   bucket, queue or temp folder when the tests touch one. All of it through environment variables and temporary
   configs under `$(git rev-parse --git-dir)/pipeline-work/<version>/mutation/` — never a change in the repository.
   mutmut writes its mutants beside the code, so its shares run each in its own worktree.
4. **Parts side by side** — the frontend's beside the backend's shares — when their workers together fit the
   budget and share nothing.
5. **Watch the timeouts.** When «timed out» passes ~5% of a share's mutants, the machine is overloaded: lower the
   workers and rerun that share; a mutant timed out by load is not killed.
6. **Clean up at the end:** drop the `_test_mut_<k>` databases and the buckets, remove the worktrees and temporary
   configs. The run report names the streams («3 потока на своих базах, фронтенд — 4 потока»).

Each backend share takes a temporary test-runner config holding only the tests of its mutated code.

**Estimate first, ask past the budget.** The run prints the mutant count before it starts («Found N mutants»; a
dry run only, when the version has one). Time ≈ initial test run × mutants ÷ the part's workers (its shares
together). Plan the streams first, then estimate; over 30 minutes for a part even in parallel: ask before
running — narrow the ranges, or run it as it is, or skip with «не измерено: долго». The progress line says the
estimate.

**Never in place, never interrupted.** Stryker's default sandbox copies the project; keep it — `inPlace: true`
rewrites the working tree, and an interrupted run leaves instrumented files in `src`. A project config with
`inPlace` gets it switched off for this run on the command line (`--inPlace false`, check the version). If a run
was interrupted anyway: `git status`, then `git checkout -- <the mutated files only>` — never `git checkout -- src`
over files someone else changed — and say so in the run report.

**Read the result.** The report lists every file of the scope as mutated (a file missing means the scope did not
reach it), the counts killed / survived / timed out / no coverage, and each survivor with its line and mutator.
Survivors go to `code-review-full` as findings on the tests, equivalent ones by the user's answer.

## Simplify

When the run added duplicates or grew a function or file past a threshold, dispatch one `impl-medium` unit
«Упрощение»: remove the copies (take them from the one home the architecture names), split what grew, keep
behaviour — no test assertion changes, the full suite green before and after, `lint` and `typecheck` green. It
passes `code-review-unit` like a Mid unit and lands as its own commit before `code-review-full`, with the trailer
`Plan-Unit: <version>/health-<n>` (`n` counts the run's simplifier commits from 1). The run report lists it under
«Здоровье кода», so `code-review-full` counts it as mapped. Surviving mutants are not fixed here: they go to the review as
findings on the tests.

## Hand over

`code-review-full` receives the health table and checks that HEAD is not worse than BASE on any row; a row that got
worse without a reason in the run report is a finding.
