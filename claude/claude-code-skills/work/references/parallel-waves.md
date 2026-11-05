# Parallel waves

Read by `work` at Step 3 when a ready unit is `Параллельно: yes`. Serial is the default — one unit, one dispatch,
one commit — and most plans never need this file.

- **Parallel** only when all four hold (cap a wave at three or four):
  - the plan marks the peers `Параллельно: yes`;
  - their `Файлы` are genuinely disjoint in the current tree;
  - the harness gives each worker an isolated workspace — in Claude Code,
    pass `isolation: "worktree"` on each parallel `Agent` call, its packet's
    `WORKTREE yes` and every path in it, and in files it reads, relative;
  - their focused tests share no runtime resource (one compose database, a
    fixed port, a dev server) — isolation of files is not isolation of the
    database.
- **Never parallel** in a shared working directory: concurrent writes and
  concurrent test runs corrupt each other regardless of what the plan claims.
- **UI units are never parallel** — not with each other and not with any
  other unit: one screen at a time, in plan order, each its own dispatch,
  review, and commit. Screens share the generated API client, the app-wide
  error handler, and shared components; the first UI unit of a run sets them
  up and the next ones reuse them, so a later screen sees what the earlier
  one built.
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
  pick up the other's half. A worktree is removed only after its unit is committed: until then its executor may be
  resumed for a review fix, which comes home the same way — the unit's files in the main tree back to HEAD (by
  name; a new file deleted), then the worktree's new patch applied. A patch that does not apply means the files
  were not disjoint: run the rest of the wave serially.
- **The context measure of Step 5.6 runs once per wave**, after its last unit is committed, not between its units.
  The other units' patches are not in the tree yet, so each unit's boundary is clean, but a hand-over mid-wave
  would leave the wave half-integrated. The next item for that measure is the next wave's first unit, or the sum
  of the next wave's units when it is parallel too (`references/run-hygiene.md` → Context).

Re-verify the plan's parallel claim against the tree before dispatching, then
decline parallelism under any remaining doubt. Speed is optional; a clean
history is not.
