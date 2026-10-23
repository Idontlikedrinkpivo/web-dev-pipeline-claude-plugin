# Vitest — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- Which of clear / reset / restore mocks is on by default, and what each undoes for `vi.spyOn` vs `vi.fn()` — calls
  recorded in `beforeAll` or at module level may be wiped before the test reads them.
- What `vi.mock` / `vi.hoisted` do when not at top level, and which outer variables a factory may use.
- Whether a mock implementation called with `new` must be a `function` / `class`, not an arrow.
- Config keys from older snippets (pool options, per-glob environments, workspace files, worker limits): renamed or
  removed keys may be ignored silently — compare collected test counts before and after.
- `projects`: whether inline projects inherit root plugins, setup files, and environment, and how to opt out.
- Sharding: which reporter shards need, where each shard writes its blob report, where the merge reads from, and how
  coverage merges.
- Coverage: the provider package for the installed major, the `coverage.thresholds` keys, and whether thresholds
  apply to a run of a few files.
- Concurrent tests: whether the global `expect` misattributes snapshots and assertion counts (use the test-context
  `expect`).
- Upgrades: read every crossed major's migration guide, walk this list against the config and suite (Vitest 5:
  `clearMocks` on by default, an un-awaited `resolves` / `rejects` fails the test; Vitest 4: `workspace` became
  `projects`, `poolOptions` removed; MSW 3: `onUnhandledRequest` became `onUnhandledFrame`).
