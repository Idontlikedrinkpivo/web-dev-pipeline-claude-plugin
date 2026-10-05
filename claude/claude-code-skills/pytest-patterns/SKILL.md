---
name: pytest-patterns
description: >-
  House conventions for pytest suites of FastAPI / SQLAlchemy async
  backends: tests by architecture layer (entities per invariant, use cases
  with fakes, adapters and mapper round-trips on a real PostgreSQL, one
  end-to-end path), conftest hierarchy, factories, auth fixtures, error
  paths from documentation/api/openapi.yaml, coverage. Use when writing, fixing or
  reviewing backend tests, conftest files or factories, or auditing
  coverage. Not for TypeScript tests (`vitest`), browser E2E
  (`playwright-cli`), or app code.
license: MIT
compatibility: 'Python, pytest, pytest-asyncio, httpx, factory_boy; versions come from the project lockfile'
metadata:
  author: platform-team
  version: '2.0.0'
  sdlc-phase: testing
allowed-tools: Read Edit Write Bash(pytest:*) Bash(uv run pytest:*) Bash(python:*) Bash(bash:*)
---

# Pytest Patterns

## Which layout governs — decide first

- **An architecture document exists**: tests follow its layers and the foundation's §6 test plan (`documentation/architecture/architecture.md`, one row per test file). Import from the foundation §5 package names and the paths the headings of the domain model (`domain.md`) and the scenarios documents (`scenarios/<area>/<area>.md`) give.
- **No architecture document, existing repo**: follow the repo's existing `tests/` layout, fixtures and naming for the change at hand; do not reorganise the suite unasked. With no tests yet, use the unit / integration split below with the repo's own module names.
- **Expected statuses and bodies** come from `documentation/api/openapi.yaml` when it exists, otherwise from what the endpoint returns today.

## Test layout

```
tests/
├── conftest.py            # engine, transactional db_session, client, auth fixtures — nothing autouse
├── fakes/                 # one in-memory fake per port (dict-backed, implements the Protocol)
├── unit/                  # no DB, no network
│   └── <area>/
│       ├── domain/        # entity and value-object tests: one per invariant-table row
│       ├── application/   # use cases with the fakes
│       └── persistence/   # mapper round-trip tests (pure, no connection)
├── integration/           # real PostgreSQL
│   ├── conftest.py        # factory session wiring (autouse) lives here, not at the root
│   ├── <area>/            # repository and query adapters against the real DB
│   └── test_<resource>_api.py   # HTTP through the app; one test drives the real wiring end to end
└── factories/             # storage-record factories, one module per table group
```

- **Entity tests** — one test per row of the domain model's invariant table (`domain.md` §4), named after the rule, asserting the named error, the resulting state or the derived value in the «Исход» column. No DB, no fakes needed.
- **Use-case tests** — the use case built with in-memory fakes for every port it takes; assert what was saved, what was returned, which named error escaped. Never `MagicMock` / `AsyncMock` in place of a port.
- **Mapper round-trip** — every field set to a non-default value, entity → record → entity equal, so a field added without its mapper line fails.
- **Adapter tests** — the repository and query adapters against the real database: save and reload, filters, ordering, constraint violations mapped to the named error. With several tenants, one test proves tenant A never reads or writes B's rows.
- **One end-to-end path** — at least one API test runs HTTP → use case → real repository for the primary action without overriding anything but the session, proving the `bootstrap/` wiring.
- Name files `test_<module>.py`, classes `Test<Feature>` (no `__init__`), functions `test_<action>_<expected_outcome>`, fixtures as nouns (`db_session`, `authenticated_client`). A failure line should say what broke without opening the file.
- Declare markers `unit`, `integration`, `slow` in `[tool.pytest.ini_options]` and run subsets with `-m`. Use `asyncio_mode = "auto"` so async tests need no per-test marker.
- Put an autouse fixture that requests `db_session` only in `tests/integration/conftest.py`: autouse applies to every test under that directory, and at the root it would make each unit test connect to the database.

## Real database, not mocks

- Run integration tests against the project's real engine (PostgreSQL, e.g. in Docker or testcontainers, URL overridable by `TEST_DATABASE_URL`). A mocked session or `execute()` hides the query bugs these tests exist to catch.
- Isolate tests with one outer transaction per test that is rolled back at the end, with the session joined through a savepoint so the code under test may call `commit()` freely. Override the app's session dependency with that session so HTTP requests share it.
- Mock only what leaves the process: HTTP APIs (`respx`), email/SMS, object storage, queues, time (`freezegun`), random/UUID. Do not mock the database, SQLAlchemy sessions, Pydantic validation, FastAPI dependency injection, or repositories in integration tests.
- Never hand code a `MagicMock` / `AsyncMock` in place of an `AsyncSession`, in any test layer: it accepts every call, so a wrong query or a missing flush passes. Code that takes the session directly (a brownfield `service.py`, an adapter) is tested against the real database.
- If the user explicitly requires SQLite (no Docker in CI), put the driver in the dev dependency group, work through the SQLite item of the checklist below, and say that these tests do not replace a PostgreSQL run.

## Fixtures

- Default to `function` scope. Use `session` scope only for expensive stateless resources such as the engine; never for mutable data. Every yield fixture cleans up, so test order never matters.
- Auth: `auth_headers` / `admin_headers` sign a token with `sub=str(user.id)` for a persisted `sample_user` / `admin_user`; `authenticated_client` / `admin_client` are `client` with that header. A test states its role by the fixture it requests; plain `client` is how a 401 test proves an endpoint is protected.
- Factories build storage records for adapter and API tests; entity tests construct entities directly. Leave primary keys to the database (a factory-assigned id does not advance the identity sequence, so the app's next insert collides). Use `.build()` in unit tests so they stay DB-free; in integration tests add or create through the session and `await db_session.flush()` yourself.
- Do not `asyncio.gather` calls that share `db_session`: an `AsyncSession` is one transaction on one connection. A concurrency test needs one session per task, and that data is committed outside the per-test rollback, so clean it up explicitly.
- Use pytest-asyncio as the only async test runner; do not also mark tests for the `anyio` plugin. One runner keeps one set of loop settings to reason about.

## API tests

- Assert the status code first, then the body, so a wrong status fails with the code instead of a `KeyError`.
- Each operation gets its success case plus one test per error response `documentation/api/openapi.yaml` declares for it — named errors with their `code`, 422 `VALIDATION_ERROR` with the failing `errors[].field`, 400 for a malformed body or cursor, 401 / 403 when secured, 404 when the path names an id. Assert the `application/problem+json` content type. A status the endpoint returns but the spec does not declare is a spec gap to report, not a test to write. Without a spec, cover the error statuses the endpoint actually returns. A happy-path-only suite passes while the error contract breaks.
- Test pagination beyond the first page: the second page through `next_cursor`, `next_cursor` null on the last page, a tampered cursor rejected (brownfield: the repo's own page parameters and their bounds). Limit and cursor bugs show only there.
- Never assert exact timestamps or generated ids (`"id" in data`); they change every run.
- Use `@pytest.mark.parametrize` with `pytest.param(..., id="member-forbidden")` for input or role matrices, with the expected result as a parameter, not a branch inside the test.

## Coverage

Thresholds: the foundation §6 numbers when it sets them; otherwise 80% overall, 90% `domain/` and `application/` (business decisions and their orchestration), 70% `adapters/persistence/` (thin, proven by adapter tests), 80% `adapters/http/` (success plus declared error paths). Brownfield: the modules that hold business decisions (often `service.py`) take the 90% line.

- If the project has no `[tool.coverage.*]` section, read `references/coverage-config.md` for the house block (`source`, `omit`, `fail_under = 80`, `exclude_lines`). Keep the threshold in that one place.
- Run `uv run pytest --cov=<package> --cov-report=term-missing`, or `scripts/check-test-coverage.sh` for a saved report (exit 1 tests failed, 2 coverage below threshold, 3 pytest could not run).
- A coverage number that looks too low for async SQLAlchemy code is a configuration question before it is a testing gap; see the checklist below.

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **Async fixtures used by sync tests** — whether the installed pytest-asyncio, in the configured mode, runs them, warns, or fails.
- **Event-loop scope** — which options set the loop scope for fixtures and for tests, and whether the session-scoped async `engine` ends up on the same loop as the tests that use it.
- **Other async plugins** — how the configured pytest-asyncio mode behaves when another plugin (anyio ships one with httpx/Starlette) is also installed.
- **SQLite SAVEPOINT** — if a project tests on SQLite/aiosqlite instead of its real engine, what the driver needs on the running Python version for nested transactions to roll back correctly.
- **Per-test rollback** — which session/transaction options in the installed SQLAlchemy let code under test `commit()` without escaping the outer transaction.
- **Coverage of async SQLAlchemy paths** — which coverage.py `concurrency` settings the installed version needs to trace lines after async DB awaits; compare the report with and without them.
- **factory_boy with `AsyncSession`** — whether `sqlalchemy_session_persistence` and `.create()` await anything, or leave an un-awaited coroutine.
- **httpx against the ASGI app** — how the installed httpx attaches `AsyncClient` to the app and whether the app's lifespan runs.

## References

- `references/conftest-template.py` — read when creating or rewriting `tests/conftest.py`: engine, transactional session, client, auth clients, sample data. Its imports are placeholders; point them at the project's real modules.
- `references/factory-template.py` — read when adding factory_boy factories (traits, `SubFactory` parents, batches, session wiring).
- `references/coverage-config.md` — read when the project has no coverage configuration yet.
- `scripts/check-test-coverage.sh` — run for a coverage check with saved report and distinct exit codes.
