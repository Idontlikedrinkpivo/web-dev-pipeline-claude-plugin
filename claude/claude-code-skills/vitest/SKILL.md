---
name: vitest
description: >-
  Vitest house rules: tests by architecture layer, what to fake, async
  assertions, mock and timer cleanup, and what to verify against the
  installed version before relying on config, sharding, projects or vi.*
  behaviour. Use when writing, debugging, reviewing or speeding up Vitest
  tests, configuring vitest.config, upgrading Vitest, or migrating from
  Jest. Not for browser E2E (`playwright-cli`) or Jest-specific APIs.
---

# Vitest

**Which layering applies.** With an architecture document (`clean-architecture-design`; foundation `documentation/architecture/architecture.md` §6): one entity test per row of the domain model's invariant table (`domain.md` §4), no I/O; use-case tests with in-memory fakes of the ports; repository adapter tests against a real Postgres; one round-trip test per mapper; HTTP tests through `app.inject`; one end-to-end path. Without one, in an existing repo: mirror its placement, naming, setup files, and fakes (colocated `*.test.ts` when there is no precedent); do not restructure the suite unasked.

## House rules

1. Read neighbouring tests and the config first; one style per suite.
2. Fake only what crosses the process boundary (network, clock, randomness, file system). Pass a fake where the code accepts one instead of `vi.mock` of a module; a test of a mocked internal proves the mock.
3. One behaviour per test, named after behaviour and condition; edge cases and the error path beside the happy path, including exact boundary values.
4. `await` (or `return`) every `.resolves` / `.rejects`. `vi.mock` / `vi.hoisted` only at module top level.
5. Undo what a test changed in `afterEach`: real timers back, spies restored, mock state reset. Fake time instead of sleeping. No mutable state shared between tests; the file must pass in shuffled order.
6. Run the file, then break the code under test once and watch the test fail.
7. Never commit `.only`; a `.skip` carries why and when it returns. Read every snapshot diff before accepting it.
8. Review findings: `file:line` — what is wrong — rule number — fix. Report only; do not edit in a review.

A browser flow (open a page, type, click, see text) is Playwright, not Vitest: route it to `playwright-cli` and add no DOM environment for it.

## Version-sensitive behaviour — verify

Read the installed version from the lockfile, then check docs via context7 (`resolve-library-id`, `query-docs`) or a quick probe. The answers change between majors:

- Which of clear / reset / restore mocks is on by default, and what each undoes for `vi.spyOn` vs `vi.fn()` — calls recorded in `beforeAll` or at module level may be wiped before the test reads them.
- What `vi.mock` / `vi.hoisted` do when not at top level, and which outer variables a factory may use.
- Whether a mock implementation called with `new` must be a `function` / `class`, not an arrow.
- Config keys from older snippets (pool options, per-glob environments, workspace files, worker limits): renamed or removed keys may be ignored silently — compare collected test counts before and after.
- `projects`: whether inline projects inherit root plugins, setup files, and environment, and how to opt out.
- Sharding: which reporter shards need, where each shard writes its blob report, where the merge reads from, and how coverage merges.
- Concurrent tests: whether the global `expect` misattributes snapshots and assertion counts (use the test-context `expect`).
- Upgrades: read every crossed major's migration guide, walk this list against the config and suite.
