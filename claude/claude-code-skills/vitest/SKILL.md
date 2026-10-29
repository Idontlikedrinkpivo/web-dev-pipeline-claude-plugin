---
name: vitest
description: >-
  Vitest rules (tests per layer, fakes over vi.mock, MSW); read before writing *.test.ts files.
---

# Vitest

**Which layering applies.** With an architecture document (`clean-architecture-design`; foundation `documentation/architecture/architecture.md` §6): one entity test per row of the domain model's invariant table (`domain.md` §4), no I/O; use-case tests with in-memory fakes of the ports; repository adapter tests against a real Postgres; one round-trip test per mapper; HTTP tests through `app.inject`; one end-to-end path. At the Framework-first level (foundation §1 «Уровень») there are no ports to fake: the one `domain/` module gets plain unit tests, the rest is tested through `app.inject` against the real database. Without an architecture document, in an existing repo: mirror its placement, naming, setup files, and fakes (colocated `*.test.ts` when there is no precedent); do not restructure the suite unasked.

## House rules

1. Read neighbouring tests and the config first; one style per suite.
2. Fake only what crosses the process boundary (network, clock, randomness, file system). Pass a fake where the code accepts one instead of `vi.mock` of a module; a test of a mocked internal proves the mock. A fake port is an in-memory store that behaves like the real adapter, and the test asserts what was stored and returned — not which method was called how often, unless the call order is itself a stated rule.
3. One behaviour per test, named after behaviour and condition; edge cases and the error path beside the happy path, including exact boundary values. Group `describe` blocks by behaviour, never by plan unit (`U17:`); setup a second file needs goes to the shared test helpers, never copied.
4. `await` (or `return`) every `.resolves` / `.rejects`. `vi.mock` / `vi.hoisted` only at module top level.
5. Undo what a test changed in `afterEach`: real timers back, spies restored, mock state reset. Fake time instead of sleeping. No mutable state shared between tests; the file must pass in shuffled order.
6. Run the file, then break the code under test once and watch the test fail.
7. Never commit `.only`; a `.skip` carries why and when it returns. Read every snapshot diff before accepting it.
8. An invariant over many values (a format, a range, a round trip, «whoever edits can see») gets a property test with `fast-check` beside its examples.
9. A guard against a double action (a row lock, a conditional update, a unique key, an idempotency key) gets a
   race test against the real database: `Promise.all` of two calls, each with its own connection from the pool
   (never one transaction shared), then count the effect — exactly one — and assert what the second caller got.
10. A surviving mutant named in a review finding points to the missing assertion: add one that fails on that mutant; never change the mutated code or weaken a test to kill it. Mutation runs are `work`'s, at the run's close (`work/references/health.md` → Mutation runs), never a unit's.
11. **The test database is named, never defaulted**: the database helper reads `TEST_DATABASE_URL` and throws
   when it is unset, when its database name has no «test», or, outside CI (`CI` unset), when it equals `DATABASE_URL`
   — locally it is a database of its own, not the one a running stand serves; a fallback address
   once sent these tests to a running stand and wiped its data. **No database reachable here** (a sandbox without Docker): write the repository, race and HTTP tests as they would run, run the rest, and report the database run as owed — in a `work` packet a line in `CONCERNS` with the command. Never replace the database with a mocked client to get a green run.
12. Coverage has one threshold, in `coverage.thresholds` of the Vitest config (the foundation §6 number, otherwise 80% of lines); the full suite measures it in CI (`repo-scaffold/references/quality-gates.md`, the Coverage gate), a unit's focused run does not.

A whole-application browser flow (log in, open a page, type, click, see the result) is Playwright, not Vitest:
route it to `playwright-cli`. A component test is Vitest with Testing Library (jsdom, or Browser Mode where the
project uses it): render through the shared `renderWithProviders`, mock the network with MSW, query by role and
label, act with `userEvent`, wait with `findBy*` — the rules are `react` → «Tests».

**Version-sensitive points** — [references/version-checks.md](./references/version-checks.md). In a `work` packet
their answers come in `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead
of fetching docs. Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **A fake of a port, never `vi.mock` of the project's own module or a mocked database client**; the test asserts
   what was stored and returned, not call counts.
2. **Every `.resolves` / `.rejects` is awaited; what a test changed is undone in `afterEach`**; no state shared
   between tests.
3. **A guard against a double action has a race test against the real database** — two calls, each on its own
   connection, the effect counted.
4. **The error path and the exact boundary values sit beside the happy path**, one behaviour per test, `describe`
   by behaviour, never by plan unit.
5. **No committed `.only`; a `.skip` says why and when it returns.**
