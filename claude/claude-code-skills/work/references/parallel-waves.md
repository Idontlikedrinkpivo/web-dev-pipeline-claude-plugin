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
- **Bring the wave home before Step 5.1.** Merge or cherry-pick each
  worker's worktree branch into the main tree, then integrate unit by unit.
  If that is not possible, run the wave serially instead.

Re-verify the plan's parallel claim against the tree before dispatching, then
decline parallelism under any remaining doubt. Speed is optional; a clean
history is not.
