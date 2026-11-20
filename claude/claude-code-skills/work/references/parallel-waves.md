# Parallel waves

Read by `work` at Step 3 when a ready unit is `Параллельно: yes`. Serial is the default — one unit, one dispatch,
one commit — and most plans never need this file.

- **Parallel** only when all four hold (cap a wave at three or four):
  - the plan marks the peers `Параллельно: yes`;
  - their `Файлы` are genuinely disjoint in the current tree;
  - the harness gives each worker an isolated workspace — in Claude Code,
    pass `isolation: "worktree"` on each parallel `Agent` call, its packet's
    `WORKTREE yes` and every path in it, and in files it reads, relative;
  - their focused tests share no runtime resource — or each gets its own. Files isolated in worktrees are not
    a database isolated: two streams on one compose database corrupt each other. A plan's `yes (своя БД)` /
    `yes (свой стенд)` means that is the only contention, so give it away — Streams below.
- **Never parallel** in a shared working directory: concurrent writes and
  concurrent test runs corrupt each other regardless of what the plan claims.
- **UI units after the foundation.** The first UI unit in plan order is the foundation: the generated API client,
  the app-wide error handler, shared components, styles and the dictionary of labels. It runs alone. After its
  commit, screen units the plan marks `yes (свой стенд)` run in parallel when their `Файлы`, e2e specs included,
  are disjoint — each on its own stand (ports, database). A screen executor never edits a shared component, a
  style or the dictionary: a lack of one goes into its NEEDS FROM ORCHESTRATOR, and the change is a separate unit
  in the main tree before the screen goes on.
- **Streams.** A plan's §4 may group independent chains of units into streams: a stream runs its units in order
  in one worktree, beside the others. Each stream gets, without a question to the user:
  - its own postgres container, started from the project's postgres image with the data in memory —
    `docker run -d --name <project>-s<k>-pg --tmpfs /var/lib/postgresql/data -e POSTGRES_HOST_AUTH_METHOD=trust
    -e POSTGRES_DB=<project>_test -p <free port>:5432 <image> -c fsync=off -c synchronous_commit=off -c full_page_writes=off`, the migrations
    applied, its `TEST_DATABASE_URL` in the packet;
  - its own bucket and env when the tests need object storage, its own ports when they need a stand;
  - a line in `resume.md` → «Запущено» (container, port, bucket, worktree), so the stage's close removes
    them (`pipeline` → `references/handover-check.md` → The stage's leftovers).

  Inside a stream the executor runs only the unit's own tests, with `--maxWorkers=2` (pytest `-n 2`); the full
  suite runs once the unit's patch lands in the main tree (Step 5). Streams at once: about one per four cores,
  at most three — a full run takes every core, and two more beside it turn into timeouts. After a unit of a stream
  is committed, the stream's worktree moves onto that commit (`git -C <worktree> reset -q --hard <sha>`): its
  changes are in it, and the next unit starts from the main line with every stream's work so far.
- **Bring the wave home, one unit at a time.** A worker never commits or stages (`executor-catalog` →
  `references/worker-prompt.md` → RULES), so its worktree branch carries nothing: what comes home is the
  worktree's changes, as a patch. When the wave's workers have returned, for each unit in plan order:
  1. in its worktree, save the changes, new files included — the recipe of `pipeline` →
     `references/pause-and-resume.md` → Pausing, step 2:

     ```bash
     git ls-files --others --exclude-standard -z | xargs -0 git add --intent-to-add --
     git diff --binary > "$(git rev-parse --path-format=absolute --git-common-dir)/pipeline-work/<version>/U<n>.patch"
     git reset -q                       # undo the intent-to-add; the files stay
     ```

  2. in the main tree, `git apply` that patch and run Step 5 — 5.1 to 5.6 — for this unit alone, to its commit;
  3. only then apply the next unit's patch.

  The wave's `Файлы` are disjoint by its conditions, so each patch applies cleanly on the commits before it; one
  unit at a time keeps «one unit, one commit» — two patches in the tree at once let one unit's checks and staging
  pick up the other's half. A stream does not wait for the others: its unit comes home as soon as it returns, in
  the queue of returned units. A worktree is removed only after its unit — a stream's last unit — is committed: until then its executor may be
  resumed for a review fix, which comes home the same way — the unit's files in the main tree back to HEAD (by
  name; a new file deleted), then the worktree's new patch applied. A patch that does not apply means the files
  were not disjoint: run the rest of the wave serially.
- **A compaction waits for the wave.** While any unit of the wave is «🔄» or «🔍» in the progress file, the plugin's
  hook holds the host's compaction (`references/run-hygiene.md` → Context), so it lands after the wave's last
  commit and never leaves the wave half-integrated; past the hook's cap it goes through, and the units' lines in
  `resume.md` and their patches carry the wave on.

Re-verify the plan's parallel claim against the tree before dispatching, then
decline parallelism under any remaining doubt. Speed is optional; a clean
history is not.
