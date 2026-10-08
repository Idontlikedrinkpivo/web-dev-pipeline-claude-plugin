# Parallel stands

Read before a UI test run (mode run), before an e2e suite runs in `work`'s
definition of done, and when `repo-scaffold`, `deploy-topology` or
`ci-pipeline` write the test topology. A browser suite is slow because its
tests share one stand: one database, one storage, one set of users and
rights. Two workers on one stand break each other — one empties a list
while the other counts it — and the false failures cost more than the wait.
So the unit of parallelism is the **stand**, not the worker: N identical
stands, each with its own database and storage, each running its own share
of the test files.

## A stand that can be copied

The test topology is written ready for copies from the start, so a parallel
run needs no code change later:

- Ports, the frontend and backend addresses, the database URL and the
  storage endpoint come from variables with today's values as defaults
  (`E2E_BASE_URL`, `E2E_API_URL`, `HTTP_PORT`, …); the Playwright config
  reads `baseURL` from the variable.
- The compose file has no `container_name` and no fixed host volume path;
  a copy starts under another project name (`docker compose -p
  <project>-e2e-2 …`) with its own ports, so copies never collide.
- `scripts/e2e-stands.sh up N` / `down` starts N stands from the images
  already built (no rebuild), each with its own ports (a fixed offset per
  stand), database and storage, migrated and seeded, and prints each
  stand's addresses; `down` removes them and their volumes.

## Tests that can be split

- **Each test file stands alone**: it prepares the data it needs and does
  not rely on what another file left. Shared steps (empty a list, change
  rights, count journal rows) are fine inside a file, never across files.
- Inside one file the tests may depend on each other's order; the file is
  the unit a stand receives.
- A file that fails only after another file ran is a test defect — fixed,
  not a reason to go back to one stand.

## How many stands

Measure, do not estimate time:

```text
stands = min(
  test files,                                     — a stand needs at least one file
  performance cores − 1,                          — one core for the OS, the editor and the session
  ⌊ free Docker memory / (one stand × 2) ⌋,       — one stand measured with docker stats after start
  ⌊ free host memory / 0.6 GB ⌋,                  — a browser per stand runs on the host
  4                                               — above this the extra stand stops paying
)
```

`sysctl hw.perflevel0.physicalcpu` gives the performance cores on macOS
(all cores elsewhere); `docker info` the Docker memory; `docker stats
--no-stream` the stand. Stands already running count against free memory
as they are. The report names the number and what limited it («3 стенда:
ядра»). One stand is a normal result, not a failure.

## The run

- **Split by files**, into groups of about equal test count; each stand
  runs one group, in its own checkout or worktree, so test artifacts and
  reports do not mix.
- **One worker per stand** while the tests share data; more only when
  every test works in its own data namespace.
- **One report.** Results from all stands land in the same `test-run.md`
  as they arrive, under one bar; a row names its stand.
- **Timeouts under load** are re-run alone before triage: a test that
  passes alone is not a defect, and is noted as «падал под нагрузкой».
- **A run already going on one stand** that turns out long may take more
  stands for its tail: start the stands, hand them the last files, stop the
  first run before the first handed-off file, and merge the results — the
  rows already passed stay.
- When done, `scripts/e2e-stands.sh down` removes the extra stands.

## In CI

`ci-pipeline` splits the e2e job the same way: a matrix of shards
(`npx playwright test --shard=<i>/<N>`, by file), each shard with its own
stand inside its own job, the reports merged in a last job
(`npx playwright merge-reports`). N follows the runner's size, not the
formula above.
