---
name: fastapi
description: >-
  FastAPI rules (routes from openapi.yaml, Depends, problem+json, JWT login, settings); read before FastAPI code. The
  contract: openapi-spec-generator.
---

# FastAPI

The project's conventions for the FastAPI web layer: routes, dependencies, request and response models, the
problem+json error handlers, login and settings, tooling. The database layer (models, repositories, sessions,
Alembic) belongs to `fastapi-sqlalchemy`.

## Which layout governs — decide first

- **An architecture document exists**: the layout is the foundation's §5 tree (`documentation/architecture/architecture.md`); entity and use-case file paths come from the headings of the domain model (`domain.md`) and the scenarios documents (`scenarios/<area>/<group>.md`). Routers are factories in `<area>/adapters/http/` — `build_<area>_router(<use cases>) -> APIRouter` — and `bootstrap/` constructs the use cases, calls the factories and includes the routers (clean-architecture-design, FastAPI row). A handler parses the request, calls one use case or query, and maps the result to the response schema; it holds no rule and builds no use case. `Depends` resolves only request-scoped things: the session (handed to a use-case factory from `bootstrap/` when the use case needs it) and the auth context.
- **The level is Framework-first** (foundation §1 «Уровень»): no ports, use-case classes or mappers — a handler calls the one framework-free `domain/` module for the rules and the ORM directly; the contract, the error handlers and auth below hold unchanged.
- **No architecture document, existing repo**: follow the repo's routers, modules and patterns for the change at hand; do not restructure the project or move code into new layers unasked. A new business rule goes into a function or class that imports neither FastAPI nor SQLAlchemy, not into the handler; say so in one line of the final answer.
- **Contract**: paths, `operationId`, status codes, bodies, the error body, the validation status and its `code` and field list, JSON casing and the page shape come from `documentation/api/openapi.yaml` when it exists (`openapi-spec-generator` is their one source); this skill defines none of them. Change the spec first when the contract changes. Without a spec, keep the shapes the repo already returns.

## Use the `fastapi` CLI

Start the app with `fastapi dev` locally (through `uv run`). Prefer declaring the entrypoint (the app object the §5 tree places in `bootstrap/`, or the repo's existing one such as `src.main:app`) in `pyproject.toml` over passing a file path on every call; pass the path only when the config cannot be added or the user asks not to.

The container, and any run the platform stops, starts through the production entry in `bootstrap/` (`python -m <package>.bootstrap.serve`), not `fastapi run`: the entry configures the JSON logs before uvicorn starts and passes it `log_config=None` and the graceful-shutdown timeout, which `fastapi run` does not (`references/service-endpoints.md`).

## Conventions

### Parameters and dependencies

- **`Annotated` everywhere.** Declare `Path`, `Query`, `Header`, `Body` and `Depends` inside `Annotated[...]`, not as default values: signatures stay callable outside FastAPI and the types stay honest.
- **Dependency aliases.** Give each reusable dependency a type alias named as a noun without suffix — `DbSession = Annotated[AsyncSession, Depends(get_db)]`, `CurrentUser = Annotated[User, Depends(get_current_user)]`, `CurrentAdmin` — and use the alias in every signature, unless asked not to. Reuse the names the repo already has; the same names appear in `fastapi-sqlalchemy`.
- **No class dependencies.** Do not pass a class to `Depends()`. Write a function dependency that takes the parameters and returns the instance (a dataclass is fine), so the request parameters are explicit. The one exception is FastAPI's own `OAuth2PasswordRequestForm` in the login route (`Annotated[OAuth2PasswordRequestForm, Depends()]`, `references/jwt-auth.md`): it is the framework's parser of the login form, and its fields are fixed by the OAuth2 spec.

### Models and responses

- **No Ellipsis defaults.** Never write `name: str = ...`, `Field(..., gt=0)` or `Query(...)`. A field or parameter without a default is already required; `...` is noise.
- **No `RootModel`.** Annotate the plain type instead, e.g. `items: Annotated[list[int], Field(min_length=1), Body()]`. The wrapper class only adds `.root` indirection.
- **Declare the return type** (`async def get_item() -> ItemRead:`) so the response is validated, filtered and documented. Use `response_model=` on the decorator only when the returned object is not the public schema, e.g. an internal model carrying a secret field.
- **Response schemas are built, not borrowed.** With an architecture document the handler maps the entity or read model to the response schema explicitly; an ORM record is never the response. Brownfield: keep the repo's existing pattern.
- **Declare the contract's error statuses on the operation** (`responses=` from one shared helper that points at the Problem model), so the app's own OpenAPI lists what the contract lists — the contract test compares them.

### Routing

- **Self-contained routers.** Put `prefix`, `tags` and shared `dependencies=[Depends(...)]` on the `APIRouter` itself, not in `include_router()`, so every place that includes it gets the same prefix and auth. Exceptions are allowed; this is the default.
- **One function per HTTP operation.** Do not branch on `request.method` inside `@app.api_route(methods=[...])`; separate functions get their own parameters, response model and OpenAPI entry.

### Sync vs async

- **`def` unless sure.** Use `async def` only when everything awaited inside is async and nothing blocks; otherwise use plain `def`. The same rule applies to dependencies. Never call blocking code inside `async def` — use an async driver, `asyncio.to_thread`, or a plain `def` path operation: it works but stalls the event loop.

## Errors as problem+json

- Exception handlers, registered once in `bootstrap/` (brownfield: next to the app object), implement the contract's error answers, all as `application/problem+json`:
  - a named domain or use-case error → the status and `code` the contract gives it (foundation §4 named-error → HTTP table), in the contract's Problem body;
  - a request that fails its schema → the contract's validation status, `code` and per-field list, field names in the wire casing. FastAPI's default `{"detail": [...]}` body is not that answer, so the handler for `RequestValidationError` replaces it;
  - a request that cannot be parsed (malformed JSON, an undecodable cursor) → the contract's status for it;
  - a serialization failure (`40001`) or deadlock (`40P01`) that is left after the bounded reruns (`fastapi-sqlalchemy` → Driver errors and install) → the contract's 503 with `Retry-After`;
  - anything unnamed → logged with its cause, the contract's 500 with a generic `detail` — never the message, stack or SQL. An unexpected constraint violation is this case: the repository classifies the conflicts it expects into named errors, and a duplicate is never answered as a bare 409 (`openapi-spec-generator` → Step 6).
- Routes and use cases raise named errors; they do not build bodies or `raise HTTPException(detail=...)`.
- Brownfield without `openapi.yaml`: keep the error format the repo already returns. Never introduce a second one.

## Auth and configuration

- Token kind, lifetime, hashing and roles come from architecture §1 «Решения по безопасности»; brownfield: from the existing code or the user. Implementing registration, password login with JWT or the current-user dependencies: read [references/jwt-auth.md](references/jwt-auth.md) — libraries, the timing-safe check, `algorithms=[...]`, 401 with `WWW-Authenticate`, roles read from the database.
- Settings via `pydantic-settings`, built in `bootstrap/`. A secret (a signing key, an API token, a password) has no default, so a missing one stops the start; `.env.example` lists every variable. Touch only the settings the task needs: in an existing repo, keep the defaults of settings the task is not about (removing `DATABASE_URL`'s default breaks every command run without `.env`). CORS lists exact origins, never `*` with credentials.

## Service endpoints, logs and shutdown

The platform the service is handed to probes it, scrapes it, collects its stdout and stops it with SIGTERM. The code for all four is written once, in `bootstrap/`, from [references/service-endpoints.md](references/service-endpoints.md) — read it before touching them.

- `GET /health/live` touches nothing; `GET /health/ready` checks the database (2 s) and each store the app cannot serve without, never a partner's API; `GET /metrics` serves `prometheus-client`'s registry with `http_request_duration_seconds`, which one pure ASGI middleware fills, labelled by the route template. The three sit outside the contract (`NOT_IN_CONTRACT`, `include_in_schema=False`) and outside auth.
- Logs are stdlib `logging` with the JSON formatter from `bootstrap/`, configured before the server starts; uvicorn's loggers go through the same handler. One object per line with `time`, `level`, `msg`, `logger`, `request_id` (a contextvar the middleware sets from `X-Request-Id`) and `err`. Code logs through `logging.getLogger(__name__)`, never `print`. No secret, token or personal data in a line.
- Shutdown: uvicorn's `timeout_graceful_shutdown` from `SHUTDOWN_TIMEOUT_SEC`, the lifespan's shutdown disposes the engine, exit 0. One worker process per container; several workers need `prometheus_client`'s multiprocess mode.

## The contract test

`tests/contract/test_openapi_contract.py` compares the OpenAPI the app builds from its routes (`get_openapi`) with
`documentation/api/openapi.yaml`: every operation the app serves exists there with the same method, path and
`operationId`, the same error statuses, and the same request and success-response schemas. It is written once
from [references/contract-test-template.py](references/contract-test-template.py) (`repo-scaffold`); a unit that
adds or changes a route keeps it green — a red contract test is a route that differs from the contract, never a
reason to loosen the comparison.

## Tooling and libraries

- uv for dependencies, Ruff for lint and format (enable its FastAPI rules), the type checker the quality gates name
  (`repo-scaffold/references/quality-gates.md`). Language rules: `python`.
- Asyncer (`asyncify` / `syncify`) when mixing blocking and async code; prefer it over raw AnyIO or asyncio.
- HTTPX for outbound HTTP; prefer it over Requests.
- SQLModel only if the user asks for it, and never beside an existing SQLAlchemy layer: that gives two model systems for one table.

**Version-sensitive points** — `references/version-checks.md`. In a `work` packet their answers come in
`CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead of fetching docs.
Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **A handler parses, calls one use case or query, and maps the result** — no rule, no use-case construction, no
   ORM record as the response.
2. **Errors reach the client only through the handlers in `bootstrap/`**: no `HTTPException(detail=...)`, no body
   built in a route, a validation failure answers the contract's validation status, not FastAPI's default 422 body.
3. **Login is timing-safe and strict**: tokens through PyJWT and passwords through `pwdlib` (Argon2) — not
   `python-jose`, `passlib` or a bare `hashlib`; an unknown email still verifies against a dummy hash; decoding passes
   `algorithms=[...]`; a bad token is 401 with `WWW-Authenticate: Bearer`; a role is read from the database on each
   request, never from a token claim; login and registration are rate-limited by address and by account where
   architecture §1 puts it, answering the contract's 429 with `Retry-After`.
4. **Secrets have no default and no literal anywhere**; CORS names exact origins.
5. **No blocking call inside `async def`** (a sync driver, `requests`, file IO, a password hash) — `def`, a thread,
   or an async library.
6. **A new or changed operation matches the contract** — the contract test covers it and passes.
7. **`/health/live` touches nothing; `/health/ready` checks only stores the app cannot serve without**, each bounded,
   never a partner's API — a partner outage must not take every pod out of rotation.
8. **No metric label or log field comes from raw input**: `route` is the template (`scope["route"].path`), never
   the request path; no user id, email, token or body in a label or a log line. A label takes a small fixed set of values (the route template, the method, the status class): an id from the path or a user's value in a label makes a new series per value.
9. **A write takes the request model's fields by name**: no `**body.model_dump()` into a record or an update, and
   a field the client may not set — the owner, a role, a status, a price — is not in the request model; request
   models forbid extra fields (`extra="forbid"`), so a sent one is refused, not stored.
