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

## A stand that cannot be copied yet

A project whose test topology was written before these rules runs on one
stand until someone fixes it — and a silent fallback means nobody does. So
when the stand cannot be copied, the machine holds more than one stand (How
many stands) and the run has more than one test file, ask once, before the
run, per `grill-me` → "How a question is shown":

```text
Стенд пока нельзя копировать: <что мешает — фиксированные порты, container_name, нет scripts/e2e-stands.sh>.
Машина тянет <N> стенда (<что ограничило>), кейсов <M> в <K> файлах.

  A. Сделать стенд копируемым сейчас и прогнать на <N> стендах (Recommended)
  B. Прогнать на одном стенде
```

A: the change is mechanical — ports, addresses and the database URL from
variables with today's values as defaults, no `container_name`, no fixed
host volume path, the Playwright `baseURL` from a variable, and
`scripts/e2e-stands.sh up N` / `down` — dispatched to `mechanical-worker`
before the run and committed alone (`test(e2e): копируемый стенд`); the
existing single-stand commands keep working. The same question comes in
`work` before a browser suite in the definition of done. The answer holds
for the project: once copyable, later runs split without asking.

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
- **One report, one writer.** The user sees one report and nothing else:
  `test-run.md` for a UI test run, the e2e section of `progress.md` for a
  suite in `work`. Several stands never mean several reports, per-stand
  files in `documentation/`, or no live report at all. A stand's raw
  Playwright output (`--reporter=list`) goes to
  `$(git rev-parse --git-dir)/pipeline-work/e2e/stand-<n>.log` — working
  output nobody opens, removed after the run; the stands never touch the
  report. The runner (the session, for `work`) is its only writer, woken by
  the journals (the Monitor tool on them, or a background `sleep 30`) and
  never replaced by a script that rewrites the report on a timer — the
  user's pane would not redraw (`pipeline` → `references/progress-files.md`
  → How). It folds each result into the report with the Edit tool as it
  arrives — the
  case's row, one bar over all stands, and under the count line one line
  per stand («Стенд 2 · 8180: 120 из 188 · упало 4»).
- **An e2e suite's progress is progress only.** In `work` its section of
  `progress.md` holds the overall bar with its count line and, per stand, a
  bar with its count line and state (`🔄 в работе`, `🔍 проверка: разбор
  падений`, `🔄 в работе: повтор после исправлений`, `✅ готово`) — no list of tests, failed or passed. Which
  tests failed and why belongs to the run report and the fixes, not the
  progress view. A UI test run's `test-run.md` keeps its cases table: there
  the table is the defect report.
- **The bar shows what passed, not what ran.** In every test report — a UI
  run, an e2e suite in `work`, a stand's line — the main bar is the share
  of tests that passed, ⌊passed × 100 / (all − not automated)⌋; what ran,
  failed and was skipped is the count line under it («Выполнено 635 из 672
  · прошло 437 · упало 152 · пропущено 46»). A bar of tests run reads as
  nearly done while a third of them fail.
- **Timeouts under load** are re-run alone before triage: a test that
  passes alone is not a defect, and is noted as «падал под нагрузкой».
- **A run already going on one stand** that turns out long may take more
  stands for its tail: start the stands, hand them the last files, stop the
  first run before the first handed-off file, and merge the results — the
  rows already passed stay.

## Cleanup

A run removes what it started, and nothing else.

- **At the end** — passed, failed or stopped — every stand the run started
  goes: `scripts/e2e-stands.sh down`, or `docker compose -p <project> down
  -v --remove-orphans` per stand, so its containers, volumes and networks
  are gone. Images stay: the next run starts its stands from them in
  seconds.
- **Only its own.** The run keeps the list of compose projects it started
  and removes those. Stands it did not start — the user's `dev`, `demo`, a
  stand another session is using — are never touched, and nothing is
  pruned wholesale (`docker system prune`, `docker volume prune`).
- **Leftovers of an interrupted run** — the same stand projects
  (`<project>-e2e-*`) with no live run behind them — are removed at the
  start of the next run, before it starts its own.
- **Watchers too.** Every Monitor or background wait the run started for
  its stands and queues is stopped with them (`pipeline` →
  `references/progress-files.md` → Every watcher ends with its work).
- **Checked.** `docker ps -a --filter
  label=com.docker.compose.project=<project>` is empty for every project
  removed; the report ends with one line: «Стенды убраны: 3, контейнеров
  15, тома удалены, следилки сняты: 4».

## In CI

`ci-pipeline` splits the e2e job the same way: a matrix of shards
(`npx playwright test --shard=<i>/<N>`, by file), each shard with its own
stand inside its own job, the reports merged in a last job
(`npx playwright merge-reports`). N follows the runner's size, not the
formula above.
