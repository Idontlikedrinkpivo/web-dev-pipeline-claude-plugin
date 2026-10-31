---
name: pytest-patterns
description: >-
  Internal: pytest rules for FastAPI backends (layers, real PostgreSQL, fixtures); read by work's executors before
  Python tests.
compatibility: 'Python, pytest, pytest-asyncio, httpx, factory_boy; versions come from the project lockfile'
metadata:
  version: '2.0.0'
  sdlc-phase: testing
---

# Pytest Patterns

## Which layout governs — decide first

- **An architecture document exists**: tests follow its layers and the foundation's §6 test plan (`documentation/architecture/architecture.md`, one row per test file). Import from the foundation §5 package names and the paths the headings of the domain model (`domain.md`) and the scenarios documents (`scenarios/<area>/<group>.md`) give.
- **The level is Framework-first** (foundation §1 «Уровень»): no ports, so no fakes and no mapper tests — the one `domain/` module gets plain unit tests, everything else is tested through HTTP against the real database.
- **No architecture document, existing repo**: follow the repo's existing `tests/` layout, fixtures and naming for the change at hand; do not reorganise the suite unasked. With no tests yet, use the unit / integration split below with the repo's own module names.
- **Expected statuses and bodies** come from `documentation/api/openapi.yaml` when it exists — the statuses, error `code`s, the validation answer, the casing and the page shape are the contract's, never typed from memory; otherwise from what the endpoint returns today.

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
├── contract/              # the app's OpenAPI against documentation/api/openapi.yaml (`fastapi` → The contract test)
└── factories/             # storage-record factories, one module per table group
```

- **Entity tests** — one test per row of the domain model's invariant table (`domain.md` §4), named after the rule, asserting the named error, the resulting state or the derived value in the «Исход» column. No DB, no fakes needed.
- **Use-case tests** — the use case built with in-memory fakes for every port it takes; assert what was saved, what was returned, which named error escaped. Never `MagicMock` / `AsyncMock` in place of a port.
- **Mapper round-trip** — every field set to a non-default value, entity → record → entity equal, so a field added without its mapper line fails.
- **Adapter tests** — the repository and query adapters against the real database: save and reload, filters, ordering, constraint violations mapped to the named error. With several tenants, one test proves tenant A never reads or writes B's rows.
- **One end-to-end path** — at least one API test runs HTTP → use case → real repository for the primary action without overriding anything but the session, proving the `bootstrap/` wiring.
- Name files `test_<module>.py`, classes `Test<Feature>` (no `__init__`), functions `test_<action>_<expected_outcome>`, fixtures as nouns (`db_session`, `authenticated_client`). A failure line should say what broke without opening the file.
- Declare markers `unit`, `integration`, `slow` in `[tool.pytest.ini_options]` and run subsets with `-m`. Use `asyncio_mode = "auto"` so async tests need no per-test marker. With a session-scoped async engine also set `asyncio_default_test_loop_scope = "session"` and `asyncio_default_fixture_loop_scope = "session"` (pytest-asyncio 1.x runs each test in its own loop otherwise, and an unset fixture loop scope follows each fixture's own scope, so the engine breaks across loops); check the installed version. The test database gets its schema from the project's migration command (`alembic upgrade head` over the SQL files), never `create_all`: the CHECK constraints, the project schema and every object the files create take part, and a model that disagrees with the files fails here. `references/conftest-template.py` does it once per session.
- Put an autouse fixture that requests `db_session` only in `tests/integration/conftest.py`: autouse applies to every test under that directory, and at the root it would make each unit test connect to the database.

## Real database, not mocks

- Run integration tests against the project's real engine (PostgreSQL, e.g. in Docker or testcontainers, URL in `TEST_DATABASE_URL` — required, a database whose name contains «test», outside CI never `DATABASE_URL` (locally a database of its own, not the one a running stand serves); the conftest fails the database tests otherwise and has no default address, so a run never drops the schema of a stand). A mocked session or `execute()` hides the query bugs these tests exist to catch.
- Isolate tests with one outer transaction per test that is rolled back at the end, with the session joined through a savepoint so the code under test may call `commit()` freely. Override the app's session dependency with that session so HTTP requests share it.
- Mock only what leaves the process: HTTP APIs (`respx`), email/SMS, object storage, queues, time (`freezegun`), random/UUID. Do not mock the database, SQLAlchemy sessions, Pydantic validation, FastAPI dependency injection, or repositories in integration tests.
- Never hand code a `MagicMock` / `AsyncMock` in place of an `AsyncSession`, in any test layer: it accepts every call, so a wrong query or a missing flush passes. Code that takes the session directly (a brownfield `service.py`, an adapter) is tested against the real database.
- If the user explicitly requires SQLite (no Docker in CI), put the driver in the dev dependency group, check the SQLite item of `references/version-checks.md`, and say that these tests do not replace a PostgreSQL run.
- **No PostgreSQL reachable here** (a sandbox without Docker): write the integration tests as they would run, run the unit tests, and report the integration run as owed — in a `work` packet a line in `CONCERNS` with the command to run. Never swap the database for SQLite or a mocked session to get a green run: that run proves nothing about the queries.

## Fixtures

- Default to `function` scope. Use `session` scope only for expensive stateless resources such as the engine; never for mutable data. Every yield fixture cleans up, so test order never matters.
- Auth: `auth_headers` / `admin_headers` sign a token with `sub=str(user.id)` for a persisted `sample_user` / `admin_user`; `authenticated_client` / `admin_client` are `client` with that header. A test states its role by the fixture it requests; plain `client` is how a 401 test proves an endpoint is protected.
- Factories build storage records for adapter and API tests; entity tests construct entities directly. Leave primary keys to the database (a factory-assigned id does not advance the identity sequence, so the app's next insert collides). Use `.build()` in unit tests so they stay DB-free; in integration tests add or create through the session and `await db_session.flush()` yourself.
- Do not `asyncio.gather` calls that share `db_session`: an `AsyncSession` is one transaction on one connection. A concurrency test needs one session per task, and that data is committed outside the per-test rollback, so clean it up explicitly.
- A guard against a double action (a row lock, a conditional update, a unique key, an idempotency key) gets such a race test: `asyncio.gather` of two calls, each with its own session, then count the effect — exactly one refund, one row — and assert what the second caller got. Without it nothing shows that the lock is taken, or taken before the read it protects.
- Use pytest-asyncio as the only async test runner; do not also mark tests for the `anyio` plugin. One runner keeps one set of loop settings to reason about.

## API tests

- Assert the status code first, then the body, so a wrong status fails with the code instead of a `KeyError`.
- Each operation gets its success case plus one test per error response `documentation/api/openapi.yaml` declares for it — each named error with its `code`, the validation answer with the failing fields as the contract names them, the unparsable-request status for a malformed body or cursor, 401 / 403 when secured, 404 when the path names an id. The 500 and the 503 every write declares are the handler's, not the operation's: one test each for the whole app, through a dependency override that raises the failure. Assert the content type the contract gives errors. A status the endpoint returns but the spec does not declare is a spec gap to report, not a test to write. Without a spec, cover the error statuses the endpoint actually returns. A happy-path-only suite passes while the error contract breaks.
- Test pagination beyond the first page: the second page through the contract's next-page cursor, the cursor's last-page value, a tampered cursor rejected (brownfield: the repo's own page parameters and their bounds). Limit and cursor bugs show only there.
- Never assert exact timestamps or generated ids (`"id" in data`); they change every run.
- Use `@pytest.mark.parametrize` with `pytest.param(..., id="member-forbidden")` for input or role matrices, with the expected result as a parameter, not a branch inside the test.

## Coverage

One threshold in one place: `fail_under` in `[tool.coverage.report]` — the foundation §6 number when it sets one,
otherwise 80. The full suite runs with coverage in CI, so a total below it fails the build
(`repo-scaffold/references/quality-gates.md`, the Coverage gate); a unit's focused run during `work` does not measure. No
per-layer numbers: coverage.py checks one total, and a threshold nothing checks is not a rule. The modules that hold
business decisions (`domain/`, `application/`, a brownfield `service.py`) are covered by the entity, use-case and
error-path tests above, not by a percentage.

- If the project has no `[tool.coverage.*]` section, read `references/coverage-config.md` for the house block.
- Run `uv run pytest --cov=<package> --cov-report=term-missing`, or `scripts/check-test-coverage.sh` for a saved
  report (exit 1 tests failed, 2 coverage below threshold, 3 pytest could not run).
- A coverage number that looks too low for async SQLAlchemy code is a configuration question before it is a testing
  gap (`references/version-checks.md` → coverage of async paths).

## References

- `references/version-checks.md` — the version-sensitive points. In a `work` packet their answers come in
  `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead of fetching docs.
  Outside `work`, read the file and check each point you rely on against the installed version.
- `references/conftest-template.py` — read when creating or rewriting `tests/conftest.py`: the migrated test database, transactional session, client, auth clients, sample data. Its imports and constants are placeholders; point them at the project's real modules.
- `references/factory-template.py` — read when adding factory_boy factories (traits, `SubFactory` parents, batches, session wiring).
- `references/coverage-config.md` — read when the project has no coverage configuration yet.
- `scripts/check-test-coverage.sh` — run for a coverage check with saved report and distinct exit codes.

## Properties and mutants

- An invariant over many values (a format, a range, a round trip, «whoever edits can see») gets a property test
  with `hypothesis` beside its examples.
- Group tests by behaviour, never by plan unit; shared fixtures live in `conftest.py`, never copied.
- A surviving mutant named in a review finding points to the missing assertion: add one that fails on that mutant;
  never change the mutated code or weaken a test to kill it. Mutation runs are `work`'s, at the run's close
  (`work/references/health.md` → Mutation runs), never a unit's.

## The reviewer checks

1. **No `MagicMock` / `AsyncMock` in place of an `AsyncSession` or a port** — an in-memory fake per port, the real
   database for anything that holds a session.
2. **Every error response the contract declares for a touched operation has its test**, asserting the status first,
   then the `code` and the error content type.
3. **A guard against a double action has a race test**: two calls through `asyncio.gather`, each with its own
   session, counting the effect.
4. **The test schema comes from the migrations**, on PostgreSQL; no `create_all`, no SQLite stand-in unless the
   user required it.
5. **No autouse fixture at the root `conftest.py` that touches the database**; mutable data is never
   session-scoped.
6. **A paged operation is tested past the first page**, the last page and a tampered cursor included.
