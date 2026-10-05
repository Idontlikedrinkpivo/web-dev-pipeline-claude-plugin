---
name: fastapi-sqlalchemy
description: >-
  Persistence for FastAPI on SQLAlchemy async and Alembic: models as storage
  records mapped to domain entities, repository adapters behind ports,
  AsyncSession and unit-of-work commits, migrations, the problem+json error
  handler, and auth wiring. Use when adding or changing models,
  repositories, sessions, commits or migrations, wiring errors or login, or
  debugging MissingGreenlet and lost commits. Not for the skeleton
  (`repo-scaffold`), schema design, route style (`fastapi`), or tests
  (`pytest-patterns`).
---

# FastAPI + SQLAlchemy async

## Which layout governs — decide first

- **An architecture document exists** (`documentation/architecture/architecture.md`, the foundation): its §5 tree is the layout, foundation §4 holds the ports, the wiring and the named-error → HTTP table, the domain model (`documentation/architecture/domain.md`) §4 the invariant table, foundation §1 the security decisions. Use those names; do not add folders §5 does not list.
- **No architecture document, existing repo**: follow the repo's layout and patterns for the change at hand (a `src/<domain>/service.py` stays where it is). Do not restructure the project or move code into new layers unasked. A new business rule still goes into a function or class that imports neither FastAPI nor SQLAlchemy, not into a route; say so in one line of the final answer.
- **HTTP contract**: `documentation/api/openapi.yaml` when it exists, otherwise the shapes and statuses the repo already returns. Never introduce a second error format.

## Layout with an architecture document

| What | Where | Rule |
|---|---|---|
| Entity, value object, named errors | `<area>/domain/` | Owns every invariant-table rule. No `fastapi`, `sqlalchemy`, `pydantic` import |
| Use case | `<area>/application/` | Only orchestrates: load through a port, call the entity method, save through a port. Holds no rule and never touches the session or a record |
| Port | `application/ports.py` (Modest) or `application/ports/` (Full) | `typing.Protocol` with the foundation §4 signatures |
| SQLAlchemy model | `<area>/adapters/persistence/` (file name from foundation §5) | A storage record. Never imported by `domain/` or `application/`, never returned as the entity or as the HTTP response |
| Repository adapter + mapper | `<area>/adapters/persistence/` | Implements the port; `to_entity(record)` / `to_record(entity)` written by hand; returns entities |
| Read query | `adapters/persistence/` | Returns the read model the area's scenarios document (`documentation/architecture/scenarios/<area>/<area>.md`) names, not the entity |
| Router factory, request / response schemas | `<area>/adapters/http/` | See `fastapi` |
| Engine, sessionmaker, use-case construction, exception handlers | `bootstrap/` | May import everything; nothing imports it |

- No `service.py` that holds business logic beside an anemic entity: the rule belongs to the entity method its invariant-table row names.
- Each mapper gets a round-trip test (every field non-default, entity → record → entity equal); see `pytest-patterns`. A field added without its mapper line must fail the build.
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
- The commit happens **before the response is sent**. Code after `yield` in a dependency may run after the response, so a failing commit there still answers 2xx. If a dependency owns commit / rollback, make it finish before the response (see checklist), roll back and re-raise on an exception, and let the code inside call `flush()` (database ids exist before serialization) instead of `commit()`.
- One alias per dependency, a noun without suffix, shared with `fastapi`: `DbSession = Annotated[AsyncSession, Depends(get_db)]`, `CurrentUser`, `CurrentAdmin`. Reuse the names the repo already has.

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
- Never `metadata.create_all` in application code (test fixtures only). Migrations run before the app starts, not from the lifespan. `version_table_schema` is the project schema (`db-schema-design` §0).
- After `alembic upgrade head`, `alembic check` (or autogenerate into a scratch file) must find no difference between the models and the database: a difference is a model that does not match `schema.md`.
- No database up: render the SQL offline (`alembic upgrade head --sql`) and read it.

## Errors as problem+json

- Exception handlers, registered once in `bootstrap/` (brownfield: next to the app object), implement `documentation/api/openapi.yaml`:
  - named domain / use-case error → its status and `code` from the spec (foundation §4 error → HTTP table), body `Problem {type, title, status, detail, instance, code}`;
  - request validation failure → 422 `code: VALIDATION_ERROR` with `errors: [{field, message}]`, `field` in wire (snake_case) names — replace FastAPI's default `{"detail": [...]}` body;
  - unparsable request (malformed JSON, undecodable cursor) → 400; anything unnamed → logged, 500 with a generic `detail`.
- All with media type `application/problem+json`. Routes and use cases raise named errors; they do not build bodies or `raise HTTPException(detail=...)`.
- Brownfield without `openapi.yaml`: keep the error format the repo already returns.

## Auth and configuration

- Token kind, lifetime, hashing and roles come from architecture §1 «Решения по безопасности»; brownfield: from the existing code or the user. Implementing password login with JWT: read [references/jwt-auth.md](references/jwt-auth.md).
- Settings via `pydantic-settings`. A secret (a signing key, an API token, a password) has no default, so a missing one stops the start; `.env.example` lists every variable. Touch only the settings the task needs: in an existing repo, keep the defaults of settings the task is not about (removing `DATABASE_URL`'s default breaks every command run without `.env`). CORS lists exact origins, never `*` with credentials.
- No blocking call inside `async def`: use an async driver, `asyncio.to_thread`, or a plain `def` path operation.

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **Dependency versions** — which releases are current (`pip index versions <pkg>` or PyPI) before adding a pin; never copy a version range from memory.
- **`yield`-dependency timing** — when code after `yield` runs relative to sending the response, and whether `Depends` takes a scope that makes it run before; this decides where a committing dependency is safe.
- **Validation errors** — where per-field locations live in the request-validation exception, and how a malformed JSON body is reported, so it maps to 400 and field failures to 422.
- **Async loading** — which loader strategies and `refresh(...)` options work for relationships under `AsyncSession`, and what `awaitable_attrs` needs on the base class.
- **Alembic** — the async template name for `alembic init`; whether the driver Alembic runs on accepts a whole SQL file in one execute (asyncpg behind SQLAlchemy prepares statements and may reject several in one call — split the file or run Alembic on a sync driver); which differences `alembic check` does not detect (server defaults, `CHECK` constraints, enum values) in the installed version.
- **Driver types** — how the async PostgreSQL driver returns `Numeric` (Decimal) and timezone-aware timestamps.
- **Form and validator quirks** — `model_fields_set` with `Form()` models, optional `Literal` form fields, `Json` inside a form, union-typed path parameters, and whether a `ValueError` in a validator becomes 422 or 500. Probe before relying on any of them.
- **Background work** — whether tasks added to an injected `BackgroundTasks` survive returning a `Response` that carries its own `background`.
- **Postponed annotations** — whether `from __future__ import annotations` with a forward-referenced dependency type still produces the right OpenAPI schema.
