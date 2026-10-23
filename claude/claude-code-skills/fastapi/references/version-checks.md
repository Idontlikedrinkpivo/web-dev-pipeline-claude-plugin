# FastAPI — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **CLI entrypoint config** — which `pyproject.toml` table and key the installed `fastapi-cli` reads for the app,
  and what it does when both the config and a path argument are given.
- **Streaming** — whether the installed FastAPI streams JSON Lines or Server-Sent Events directly from a
  `yield`ing path operation, which module the SSE classes live in, how yielded objects are serialized, and whether
  bytes should be streamed via a `response_class=` or a returned response instance.
- **Serving a built frontend** — whether a built-in helper for SPA assets exists in this version or `StaticFiles`
  must be mounted, and how its routes are ordered against API routes and the client-side-routing fallback.
- **`yield` dependencies** — when the code after `yield` runs relative to sending the response (matters for
  sessions used by streaming responses), whether that timing is configurable, and what happens to an exception
  raised after `yield`.
- **Response serialization** — which response classes are deprecated or redundant once a return type is
  declared, and which one wins when both a return annotation and `response_model=` are present.
- **Plain-type bodies** — whether a single `Body()` parameter with a plain annotation is read from the top-level
  JSON or embedded under its name, and how that shows in OpenAPI.
- **Validation errors** — where per-field locations live in `RequestValidationError`, and how a malformed JSON
  body is reported, so it maps to the contract's unparsable-request status and field failures to its validation
  status.
- **Form and validator quirks** — `model_fields_set` with `Form()` models, optional `Literal` form fields, `Json`
  inside a form, union-typed path parameters, and whether a `ValueError` in a validator becomes 422 or 500.
- **Background work** — whether tasks added to an injected `BackgroundTasks` survive returning a `Response` that
  carries its own `background`.
- **Postponed annotations** — whether `from __future__ import annotations` with a forward-referenced dependency
  type still produces the right OpenAPI schema.
- **The app's OpenAPI** — which OpenAPI version `app.openapi()` emits (3.0 or 3.1, so how a nullable field looks),
  whether a custom `app.openapi` replaces it, and how `responses=` with a model and a non-JSON media type shows.
- **Ruff FastAPI rules** — the rule prefix and which checks exist in the installed Ruff version before enabling or
  suppressing them.
- **Auth libraries** — the current PyJWT and pwdlib releases (`pip index versions <pkg>`), the signatures of
  `jwt.encode` / `jwt.decode` and `PasswordHash.recommended()` / `hash` / `verify`, and which extra installs the
  Argon2 backend.
- **uvicorn and the production entry** (`references/service-endpoints.md`) — `uvicorn.run`'s `log_config`,
  `access_log`, `timeout_graceful_shutdown` and `workers`; whether it still re-raises the captured signal after a
  graceful shutdown (it does from 0.29: under the default SIGTERM handler the process then ends with 143, hence the
  no-op handlers); whether the installed `fastapi run` has gained a shutdown-timeout option and leaves logging to the
  app (fastapi-cli 0.0.32 has neither) — only then may the container start through it.
- **The route template** — that the matched route sits on the ASGI scope after the call (`scope["route"]`, an
  `APIRoute` whose `path` is the template with the router's prefix), so a middleware can label by it.
- **prometheus-client** — the current release; `Histogram`'s signature, `generate_latest` and
  `CONTENT_TYPE_LATEST` (its `version=` follows the text format); the multiprocess mode (`PROMETHEUS_MULTIPROC_DIR`,
  `MultiProcessCollector`, `mark_process_dead`).
