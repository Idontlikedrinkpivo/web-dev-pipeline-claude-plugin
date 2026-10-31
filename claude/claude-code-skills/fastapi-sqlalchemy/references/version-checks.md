# SQLAlchemy async and Alembic — version-sensitive points

Facts that change between releases. Each point is a question for the installed version (read it from the
lockfile); an answer written beside a point is a dated hint, so confirm it against that version before relying on it.
`work` asks once per run (`work/references/context7.md`); elsewhere, Context7 or a quick probe in the project.

- **Dependency versions** — which releases are current (`pip index versions <pkg>` or PyPI) before adding a pin;
  never copy a version range from memory.
- **The 2.x line** — which minor is installed: 2.1 no longer installs greenlet without the `asyncio` extra and
  autoflushes before every executed statement; code written for 2.0 may flush earlier than it expects.
- **`yield`-dependency timing** — when code after `yield` runs relative to sending the response, and whether
  `Depends` takes a scope that makes it run before; this decides where a committing dependency is safe.
- **Async loading** — which loader strategies and `refresh(...)` options work for relationships under
  `AsyncSession`, and what `awaitable_attrs` needs on the base class.
- **Driver errors** — where the SQLSTATE and the constraint name sit on the `IntegrityError` the installed driver
  raises (`e.orig.sqlstate`; the driver's own exception through `e.orig.__cause__` or `e.driver_exception`), probed
  with a real duplicate insert.
- **Alembic** — the async template name for `alembic init`; whether the driver Alembic runs on accepts a whole SQL
  file in one execute (asyncpg behind SQLAlchemy prepares statements and may reject several in one call — split the
  file or run Alembic on a sync driver); how `autocommit_block()` and `transaction_per_migration` behave on that
  driver; which differences `alembic check` does not detect (server defaults, `CHECK` constraints, enum values).
- **Driver types** — how the async PostgreSQL driver returns `Numeric` (Decimal) and timezone-aware timestamps.
