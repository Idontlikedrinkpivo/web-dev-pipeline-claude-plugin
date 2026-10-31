---
name: fastapi-sqlalchemy
description: >-
  Internal: SQLAlchemy async and Alembic under FastAPI (repositories, sessions, migrations); read by work's executors
  before such code.
---

# FastAPI + SQLAlchemy async

## Which layout governs — decide first

The cases (architecture document, Framework-first, existing repo) are in
`typescript/references/which-layout-governs.md`, shared by the backend and test skills of both stacks — read it
first. SQLAlchemy's placement in them:

- **An architecture document exists**: the table below.
- **Framework-first**: the models are the storage, and the route or a small service queries them directly.
- **Existing repo**: a `src/<domain>/service.py` stays where it is; a new rule imports neither FastAPI nor SQLAlchemy.
- **HTTP**: routes, the problem+json error handlers, auth and settings are `fastapi`; this skill ends where a repository returns an entity or raises a named error.

## Layout with an architecture document

| What | Where | Rule |
|---|---|---|
| Entity, value object, named errors | `<area>/domain/` | Owns every invariant-table rule. No `fastapi`, `sqlalchemy`, `pydantic` import |
| Use case | `<area>/application/` | Only orchestrates: load through a port, call the entity method, save through a port. Holds no rule and never touches the session or a record |
| Port | `application/ports.py` (Modest) or `application/ports/` (Full) | `typing.Protocol` with the foundation §4 signatures |
| SQLAlchemy model | `<area>/adapters/persistence/` (file name from foundation §5) | A storage record. Never imported by `domain/` or `application/`, never returned as the entity or as the HTTP response |
| Repository adapter + mapper | `<area>/adapters/persistence/` | Implements the port; `to_entity(record)` / `to_record(entity)` written by hand; returns entities |
| Read query | `adapters/persistence/` | Returns the read model its group's scenarios document (`documentation/architecture/scenarios/<area>/<group>.md`) names, not the entity |
| Router factory, request / response schemas | `<area>/adapters/http/` | See `fastapi` |
| Engine, sessionmaker, use-case construction, exception handlers | `bootstrap/` | May import everything; nothing imports it |

- No `service.py` that holds business logic beside an anemic entity: the rule belongs to the entity method its invariant-table row names.
- Each mapper gets a round-trip test (`typescript/references/shared-test-rules.md` → 1, written by `pytest-patterns`).
- Run the import-linter contracts from foundation §6 after the change (`uv run lint-imports`, or the command the repo already uses).

```python
# <area>/adapters/persistence/order_repository.py — shape only, names from foundation §4/§5
class SqlOrderRepository:                      # implements application.ports.OrderRepository
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, order_id: OrderId) -> Order | None:
        record = await self._session.scalar(
            select(OrderRecord).options(selectinload(OrderRecord.lines)).where(OrderRecord.id == order_id)
        )
        return None if record is None else to_entity(record)
```

`save` adds `to_record(entity)` for a new entity, or copies the entity's fields onto the record it loaded with the same options, then flushes or commits per the unit-of-work rule below.

## Session and unit of work

- One `AsyncSession` per request (or per use-case run in a job). Never module-global, never shared between concurrent tasks.
- Create the sessionmaker with `expire_on_commit=False`, so returned objects stay readable after commit without implicit IO.
- Commit explicitly at the unit-of-work boundary the design names: inside `repository.save` for a single-entity save, a `UnitOfWork` adapter when a scenario saves several. Brownfield: where the repo already commits.
- The commit happens **before the response is sent**. Code after `yield` in a dependency may run after the response, so a failing commit there still answers 2xx. If a dependency owns commit / rollback, make it finish before the response (`references/version-checks.md` → `yield`-dependency timing), roll back and re-raise on an exception, and let the code inside call `flush()` (database ids exist before serialization) instead of `commit()`.
- The session reaches a route through the `DbSession` alias (`fastapi` → Dependency aliases).

## Models and column types

- Typed declarative (`Mapped[...]`, `mapped_column`). Column types, lengths, nullability, `CHECK` / `UNIQUE` / `FK` and indexes copy the schema document (`documentation/db/schema.md`, from `db-schema-design`) or, brownfield, the existing migrations.
- Money is never `float` / `Float`: `Numeric(p, s)` with `Decimal`, or integer minor units, whichever the schema says. Timestamps are timezone-aware.
- The database is PostgreSQL as the schema document states; `DATABASE_URL` has no SQLite default. Tests run on PostgreSQL too (`pytest-patterns`).

## Relationships under AsyncSession

- A lazy load performs IO on attribute access and raises `MissingGreenlet`. Declare every relationship `lazy="raise"` so a missing load fails in tests, not in production.
- Load explicitly (`selectinload` / `joinedload`) in every query whose result is mapped or serialized, including the object a create returns: re-select with options, or refresh the named attributes. A path that "works" because the related row is already in the session's identity map is the same bug waiting for another caller.
- With an architecture document the repository loads everything its mapper reads, so no lazy attribute leaves the adapter.

## Migrations

- The migrations are the SQL files in `documentation/db/migrations/` (`0001_init.sql`, `0002_…`), written by `db-schema-design`. Alembic only orders and records them: one revision per file, revision id = the file's number, `down_revision` = the previous one, and `upgrade()` executes that file's text read from `documentation/db/migrations/` (path from the repo root, the same relative path inside the image). Never autogenerate DDL and never retype a file into `op.*` calls — two copies of a migration drift. A committed SQL file is never edited; a change is the next file and the next revision.
- `downgrade()` undoes what the schema changelog row calls reversible; otherwise it raises with the file name.
- A file with `CONCURRENTLY` (its own file, `db-schema-design/references/migration-safety.md`) runs inside `with op.get_context().autocommit_block():` — a revision runs in a transaction, and PostgreSQL refuses `CREATE INDEX CONCURRENTLY` inside one. The block commits what ran before it, so `env.py` sets `transaction_per_migration=True`: each revision is then its own transaction, and a failed one leaves the earlier ones recorded.
- Never `metadata.create_all` — not in application code and not in test fixtures: the tests build their schema with the same migrations (`pytest-patterns`), so a model that disagrees with the files fails there. The one exception is a brownfield repo with no migration files at all: its test fixture keeps `create_all` until the first migration file exists, and the report says so. Migrations run before the app starts, not from the lifespan. `version_table_schema` is the project schema (`db-schema-design` §0).
- After `alembic upgrade head`, `alembic check` (or autogenerate into a scratch file) must find no difference between the models and the database: a difference is a model that does not match `schema.md`.
- No database up: render the SQL offline (`alembic upgrade head --sql`) and read it.

## Driver errors and install

- A constraint violation the repository can expect (a duplicate email, a dangling reference, an overlap the
  database refuses) is classified by its SQLSTATE and constraint name read from the driver's error (`e.orig.sqlstate`;
  where the constraint name sits is a version check), never from its message — and raised as a domain exception with fields
  (`raise BookingOverlap(room_id=…) from e`); its HTTP status is the contract's for that named error (`fastapi`).
  Never a bare re-raise of the driver's error as an answer, never `except Exception: pass` (`python`).
- A serialization failure (`40001`) or a deadlock (`40P01`) propagates unchanged from the repository. A use case
  whose transaction can lose to a concurrent one is wrapped in `bootstrap/` by one shared helper that reruns its
  whole run — load → decide → save, with a fresh session — a bounded number of times (three, with a short random
  wait); never one statement, never a loop in the repository, and the use case knows no driver codes. What is left
  after the attempts the handler answers with the contract's 503 and `Retry-After`. Anything else the
  repository does not classify propagates unchanged and ends as the contract's 500 (`fastapi` → «Errors as
  problem+json»).
- Async SQLAlchemy needs `sqlalchemy[asyncio]`: from 2.1 greenlet is no longer installed by default, and without it
  the first async call fails with an error that names the missing greenlet library — install the extra.
  `MissingGreenlet` is a different failure: IO started outside an `await`, nearly always a lazy load — fix the
  loading (above), not the install.

**Version-sensitive points** — `references/version-checks.md`. In a `work` packet their answers come in
`CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead of fetching docs.
Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **The commit happens before the response is sent** — not in code after a dependency's `yield` that runs after
   it; a failing commit must not answer 2xx.
2. **Every relationship is `lazy="raise"` and every query that is mapped or serialized loads what it reads**
   (`selectinload` / `joinedload`), the object a create returns included.
3. **Migrations are the SQL files**: one revision per file executing its text, no autogenerated or retyped DDL, no
   edited committed file, `CONCURRENTLY` inside `autocommit_block()`, no `create_all` anywhere — except the test
   fixture of a brownfield repo with no migration files at all.
4. **`domain/` and `application/` import no SQLAlchemy**; the repository returns entities through a mapper that has
   a round-trip test.
5. **An expected constraint violation becomes a named exception with fields, `from e`**, classified by SQLSTATE
   and constraint name; nothing else is swallowed or turned into a client answer here.
6. **One `AsyncSession` per request or job**, never module-global, never shared by concurrent tasks.
