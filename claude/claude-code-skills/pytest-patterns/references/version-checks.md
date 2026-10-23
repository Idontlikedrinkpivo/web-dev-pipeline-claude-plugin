# pytest for FastAPI / SQLAlchemy async — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **Async fixtures used by sync tests** — whether the installed pytest-asyncio, in the configured mode, runs them,
  warns, or fails.
- **Event-loop scope** — which options set the loop scope for fixtures and for tests, and whether the
  session-scoped async `engine` ends up on the same loop as the tests that use it.
- **Other async plugins** — how the configured pytest-asyncio mode behaves when another plugin (anyio ships one
  with httpx/Starlette) is also installed.
- **SQLite SAVEPOINT** — if a project tests on SQLite/aiosqlite instead of its real engine, what the driver needs on
  the running Python version for nested transactions to roll back correctly.
- **Per-test rollback** — which session/transaction options in the installed SQLAlchemy let code under test
  `commit()` without escaping the outer transaction.
- **Coverage of async SQLAlchemy paths** — which coverage.py `concurrency` settings the installed version needs to
  trace lines after async DB awaits; compare the report with and without them.
- **factory_boy with `AsyncSession`** — whether `sqlalchemy_session_persistence` and `.create()` await anything, or
  leave an un-awaited coroutine.
- **httpx against the ASGI app** — how the installed httpx attaches `AsyncClient` to the app and whether the app's
  lifespan runs.
- **Migrations from a test** — whether the project's Alembic `env.py` can run inside the test process's event loop
  (an async `env.py` calls `asyncio.run`, which fails inside a running loop), or must run as its own command.
