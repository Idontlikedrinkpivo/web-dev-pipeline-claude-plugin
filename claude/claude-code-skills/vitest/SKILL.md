---
name: vitest
description: >-
  Internal: Vitest rules (tests per layer, fakes over vi.mock, MSW); read by work's executors before *.test.ts(x) and
  vitest.config.
---

# Vitest

**Which layering applies.** The cases (architecture document, Framework-first, existing repo) are in
`typescript/references/which-layout-governs.md`, and the rules every test suite shares (mapper round-trip, race
test, property test, grouping, mutants, no database reachable) in `typescript/references/shared-test-rules.md` —
read both first. Vitest's placement in the cases:

- **An architecture document exists** — the foundation §6 test plan:
  - one entity test per row of the domain model's invariant table (`domain.md` §4), no I/O;
  - use-case tests with in-memory fakes of the ports;
  - repository adapter tests against a real Postgres;
  - one round-trip test per mapper;
  - HTTP tests through the server's in-process injector (Fastify `app.inject`), one of them an end-to-end path.
- **Framework-first** — no ports to fake: the one `domain/` module gets plain unit tests, the rest is tested
  through the in-process injector against the real database.
- **Existing repo** — mirror its placement, naming, setup files and fakes (colocated `*.test.ts` when there is no
  precedent).

## The machine checks — keep them green

`@vitest/eslint-plugin` (`repo-scaffold/references/quality-gates.md`); the prose below keeps only what lint cannot
see.

| Rule | Lint |
|---|---|
| every `.resolves` / `.rejects` is awaited or returned | `vitest/valid-expect` |
| no committed `.only` | `vitest/no-focused-tests` |
| a skipped test is flagged (its reason is the reviewer's) | `vitest/no-disabled-tests` |
| every test asserts something | `vitest/expect-expect` |
| component tests query by role and label, act with `userEvent` | `testing-library/*` (`react` → The machine checks) |

## House rules

1. Read neighbouring tests and the config first; one style per suite.
2. Fake only what crosses the process boundary (network, clock, randomness, file system). Pass a fake where the code accepts one instead of `vi.mock` of a module; a test of a mocked internal proves the mock. A fake port is an in-memory store that behaves like the real adapter, and the test asserts what was stored and returned — not which method was called how often, unless the call order is itself a stated rule.
3. One behaviour per test, named after behaviour and condition; edge cases and the error path beside the happy path, including exact boundary values. `describe` blocks and shared setup: shared rule 4.
4. `vi.mock` / `vi.hoisted` only at module top level.
5. Undo what a test changed in `afterEach`: real timers back, spies restored, mock state reset. Fake time instead of sleeping. No mutable state shared between tests; the file must pass in shuffled order.
6. Run the file, then break the code under test once and watch the test fail.
7. A `.skip` carries why and when it returns. Read every snapshot diff before accepting it.
8. Property tests with `fast-check` (shared rule 3).
9. A guard against a double action gets the race test of shared rule 2: `Promise.all` of two calls, each with its
   own connection from the pool.
10. A surviving mutant gets the assertion that kills it (shared rule 5).
11. **The test database is named, never defaulted**: the database helper reads `TEST_DATABASE_URL` and throws
   when it is unset, when its database name has no «test», or, outside CI (`CI` unset), when it equals `DATABASE_URL`
   — locally it is a database of its own, not the one a running stand serves; a fallback address
   once sent these tests to a running stand and wiped its data. **No database reachable here**: shared rule 6.
12. Coverage has one threshold, in `coverage.thresholds` of the Vitest config (the foundation §6 number, otherwise 80% of lines); the full suite measures it in CI (`repo-scaffold/references/quality-gates.md`, the Coverage gate), a unit's focused run does not.

A whole-application browser flow (log in, open a page, type, click, see the result) is Playwright, not Vitest:
route it to `playwright-cli`. A component test is Vitest with Testing Library (jsdom, or Browser Mode where the
project uses it): render through the shared `renderWithProviders`, mock the network with MSW, query by role and
label, act with `userEvent`, wait with `findBy*` — the rules are `react` → The reviewer checks, item 15.

**Version-sensitive points** — [references/version-checks.md](./references/version-checks.md). In a `work` packet
their answers come in `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead
of fetching docs. Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **A fake of a port, never `vi.mock` of the project's own module or a mocked database client**; the test asserts
   what was stored and returned, not call counts.
2. **What a test changed is undone in `afterEach`**; no state shared between tests.
3. **A guard against a double action has a race test against the real database** — two calls, each on its own
   connection, the effect counted.
4. **The error path and the exact boundary values sit beside the happy path**, one behaviour per test, `describe`
   by behaviour, never by plan unit.
5. **A `.skip` says why and when it returns.**
