---
name: fastapi
description: >-
  FastAPI web-layer conventions: path operations that implement
  documentation/api/openapi.yaml, router factories with use cases injected from bootstrap,
  Annotated parameters and Depends, Pydantic request and response models,
  sync vs async, streaming and SSE, the fastapi CLI with uv, Ruff and ty.
  Use whenever code adds or changes FastAPI endpoints, dependencies, schemas
  or tooling. Not for the database layer, the error handler or auth
  (`fastapi-sqlalchemy`), or tests (`pytest-patterns`).
---

# FastAPI

The project's conventions for the FastAPI web layer: routes, dependencies, request and response models, tooling. The database layer, the error handler and auth belong to `fastapi-sqlalchemy`.

## Which layout governs — decide first

- **An architecture document exists**: the layout is the foundation's §5 tree (`documentation/architecture/architecture.md`); entity and use-case file paths come from the headings of the domain model (`domain.md`) and the scenarios documents (`scenarios/<area>/<area>.md`). Routers are factories in `<area>/adapters/http/` — `build_<area>_router(<use cases>) -> APIRouter` — and `bootstrap/` constructs the use cases, calls the factories and includes the routers (clean-architecture-design, FastAPI row). A handler parses the request, calls one use case or query, and maps the result to the response schema; it holds no rule and builds no use case. `Depends` resolves only request-scoped things: the session (handed to a use-case factory from `bootstrap/` when the use case needs it) and the auth context.
- **No architecture document, existing repo**: follow the repo's routers, modules and patterns for the change at hand; do not restructure the project or move code into new layers unasked. A new business rule goes into a function or class that imports neither FastAPI nor SQLAlchemy, not into the handler; say so in one line of the final answer.
- **Contract**: paths, `operationId`, status codes, bodies, snake_case property names and the page shape come from `documentation/api/openapi.yaml` when it exists; change the spec first when the contract changes. Every 4xx / 5xx is `application/problem+json`, and field validation failures are 422 `VALIDATION_ERROR` with `errors` — FastAPI's default 422 body does not match, so the handler from `fastapi-sqlalchemy` replaces it. Without a spec, keep the shapes the repo already returns.

## Use the `fastapi` CLI

Start the app with `fastapi dev` locally and `fastapi run` in production (through `uv run`), not by calling uvicorn directly, so every environment starts the app the same way. Prefer declaring the entrypoint (the app object §7 places in `bootstrap/`, or the repo's existing one such as `src.main:app`) in `pyproject.toml` over passing a file path on every call; pass the path only when the config cannot be added or the user asks not to.

## Conventions

### Parameters and dependencies

- **`Annotated` everywhere.** Declare `Path`, `Query`, `Header`, `Body` and `Depends` inside `Annotated[...]`, not as default values: signatures stay callable outside FastAPI and the types stay honest.
- **Dependency aliases.** Give each reusable dependency a type alias named as a noun without suffix — `DbSession = Annotated[AsyncSession, Depends(get_db)]`, `CurrentUser = Annotated[User, Depends(get_current_user)]`, `CurrentAdmin` — and use the alias in every signature, unless asked not to. Reuse the names the repo already has; the same names appear in `fastapi-sqlalchemy`.
- **No class dependencies.** Do not pass a class to `Depends()`. Write a function dependency that takes the parameters and returns the instance (a dataclass is fine), so the request parameters are explicit.

### Models and responses

- **No Ellipsis defaults.** Never write `name: str = ...`, `Field(..., gt=0)` or `Query(...)`. A field or parameter without a default is already required; `...` is noise.
- **No `RootModel`.** Annotate the plain type instead, e.g. `items: Annotated[list[int], Field(min_length=1), Body()]`. The wrapper class only adds `.root` indirection.
- **Declare the return type** (`async def get_item() -> ItemRead:`) so the response is validated, filtered and documented. Use `response_model=` on the decorator only when the returned object is not the public schema, e.g. an internal model carrying a secret field.
- **Response schemas are built, not borrowed.** With an architecture document the handler maps the entity or read model to the response schema explicitly; an ORM record is never the response. Brownfield: keep the repo's existing pattern.

### Routing

- **Self-contained routers.** Put `prefix`, `tags` and shared `dependencies=[Depends(...)]` on the `APIRouter` itself, not in `include_router()`, so every place that includes it gets the same prefix and auth. Exceptions are allowed; this is the default.
- **One function per HTTP operation.** Do not branch on `request.method` inside `@app.api_route(methods=[...])`; separate functions get their own parameters, response model and OpenAPI entry.

### Sync vs async

- **`def` unless sure.** Use `async def` only when everything awaited inside is async and nothing blocks; otherwise use plain `def`. The same rule applies to dependencies. Never call blocking code inside `async def`: it works but stalls the event loop.

## Tooling and libraries

- uv for dependencies, Ruff for lint and format (enable its FastAPI rules), ty for type checking, when available.
- Asyncer (`asyncify` / `syncify`) when mixing blocking and async code; prefer it over raw AnyIO or asyncio.
- HTTPX for outbound HTTP; prefer it over Requests.
- SQLModel only if the user asks for it, and never beside an existing SQLAlchemy layer: that gives two model systems for one table.

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **CLI entrypoint config** - which `pyproject.toml` table and key the installed `fastapi-cli` reads for the app, and what it does when both the config and a path argument are given.
- **Streaming** - whether the installed FastAPI streams JSON Lines or Server-Sent Events directly from a `yield`ing path operation, which module the SSE classes live in, how yielded objects are serialized, and whether bytes should be streamed via a `response_class=` or a returned response instance.
- **Serving a built frontend** - whether a built-in helper for SPA assets exists in this version or `StaticFiles` must be mounted, and how its routes are ordered against API routes and the client-side-routing fallback.
- **`yield` dependencies** - when the code after `yield` runs relative to sending the response (matters for sessions used by streaming responses), whether that timing is configurable, and what happens to an exception raised after `yield`.
- **Response serialization** - which response classes are deprecated or redundant once a return type is declared, and which one wins when both a return annotation and `response_model=` are present.
- **Plain-type bodies** - whether a single `Body()` parameter with a plain annotation is read from the top-level JSON or embedded under its name, and how that shows in OpenAPI.
- **Ruff FastAPI rules** - the rule prefix and which checks exist in the installed Ruff version before enabling or suppressing them.
