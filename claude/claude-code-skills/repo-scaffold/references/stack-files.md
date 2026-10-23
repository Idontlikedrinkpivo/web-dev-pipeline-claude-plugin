# Stack file map

Open only the section that matches architecture §1 Стек (a backend and a
frontend may both apply). Substitute real names from the file tree: the
`bootstrap/…` paths below are defaults, and a flat tree's names win (SKILL.md §5). Lint
rules come from the foundation's §6 rule table — build the config from
those rows, do not invent a second rule set. Every stack gets the same three
check targets (`lint`, `typecheck`, `test`) plus `lint` running the
dead-code detector, so `work` and `ci-pipeline` call the same commands
everywhere.

## TypeScript (Fastify / Express / Nest / Koa)

Create:

- `package.json` + lockfile
- `tsconfig.json` — `rootDir` / `paths` follow the tree (`src/`); the
  compiler flags of `quality-gates.md` → By stack (`strict`,
  `noUncheckedIndexedAccess` and the rest); the tests inside it or in a
  test `tsconfig`, so `typecheck` covers them
- `.dependency-cruiser.cjs` from the architecture sketch; `$1` for area
  capture, `tsPreCompilationDeps: true`, `tsConfig` pointing at the root
  `tsconfig.json` (so `paths` aliases resolve), the `not-to-unresolvable`
  rule, and `severity: 'error'` on every rule
- `eslint.config.js` — ESLint 10.7 or later (the floor `quality-gates.md`
  explains) with `typescript-eslint`, the rules and thresholds of `quality-gates.md`
- `npm` / `pnpm` scripts `lint-boundaries` → `depcruise src --config .dependency-cruiser.cjs`; `lint` (runs `lint-boundaries` + ESLint + `knip` + `jscpd`), `typecheck` (`tsc --noEmit` over `src` and the tests), `test`
- `bootstrap/server.ts` — the service endpoints only (SKILL.md §5). Fastify: build the instance in a
  `buildServer()` factory with the one type provider, `@fastify/swagger` in
  dynamic mode with that provider's schema transform
  (`typescript-fastify/references/zod-type-provider.md`) so `app.swagger()`
  gives the contract test the app's own OpenAPI, and the one global error
  handler the architecture names (problem+json per `documentation/api/openapi.yaml`), so
  `typescript-fastify` finds them; Express/Koa: the same factory shape; Nest:
  a module under `bootstrap/`
- the logger options, the request id, the `prom-client` registry with the
  histogram hook and the three service routes (`bootstrap/service-routes.ts`),
  and the entry point — the one file that calls `listen` — with the SIGTERM /
  SIGINT handlers and the pool closed in an `onClose` hook: copied from
  `typescript-fastify/references/service-endpoints.md`; `prom-client` in
  dependencies. A `dev` script may pipe through `pino-pretty`; nothing else does
- `tests/contract/openapi.contract.test.ts` from
  `typescript-fastify/references/contract-test-template.ts`, its
  placeholders pointed at the real `buildServer` and the fakes it needs;
  `yaml` in devDependencies. Green on the scaffold: every contract
  operation is listed as not served yet
- the Vitest config with `coverage.thresholds` — the foundation §6 number,
  otherwise 80% of lines — and the coverage provider of the installed
  major (`vitest`)
- `knip` config listing the entry points (the file that calls `listen`, the
  migrate script, test globs),
  so the dead-code report starts clean
- `docker-compose.yml` with the database `schema.md` «Решения по базе»
  names (PostgreSQL or MySQL, at its major) + `.env.example` whenever the
  system stores data (SKILL.md §4)
- the migration runner over `documentation/db/migrations/` (SKILL.md §4):
  a plain runner script (`scripts/migrate.ts` → `npm run migrate`) unless §1
  names a tool that reads plain numbered SQL files as they are. Drizzle's
  `migrate()` expects drizzle-kit's own folder format, so it is not that
  tool (`typescript-drizzle-orm`). No `drizzle/` migrations folder

Do not put `@Injectable()` on anything in `domain/` or `application/`.

## Frontend (React + Vite / Next.js)

Layout, default libraries, and command names: the profile in
`frontend/references/react-vite.md` or `frontend/references/nextjs.md` —
follow it, do not restate it here. Create:

- `package.json` + lockfile with scripts `dev`, `build`, `lint` (ESLint with
  the `quality-gates.md` rules and React hooks rules + `dependency-cruiser`
  over the frontend's layers + `knip` + `jscpd`), `typecheck` (`tsc --noEmit`,
  tests included), `test` (Vitest + Testing Library),
  `test:e2e` (Playwright), and `api:gen` — the OpenAPI client generator over
  `documentation/api/openapi.yaml`, writing to the folder the profile names
- `tsconfig.json` with the compiler flags of `quality-gates.md` → By
  stack, the bundler / framework config, ESLint config (ESLint 10.7 or
  later), the Vitest config with `coverage.thresholds` (as for the
  backend), `playwright.config.ts` with `baseURL` and `webServer` pointing
  at the dev server
- the app shell from the profile (root layout or `main.tsx` + router) with
  one placeholder route; no screens, no API client yet — the first screen
  unit runs `api:gen` and builds the app-wide error handler (`frontend`)
- `.env.example` with the API base URL variable the profile names

## Python (FastAPI)

Create:

- `pyproject.toml` + lock (`uv.lock` or `poetry.lock`); in it the type
  checker of `quality-gates.md` → By stack (`mypy --strict` with
  `enable_error_code = ["exhaustive-match"]`, or pyright `strict`) over
  `src` and `tests/`, `[tool.coverage.report]` `fail_under` — the
  foundation §6 number, otherwise 80 — and PyYAML and `pytest-cov` among the
  dev dependencies
- package named after the project, not `app` or `platform`
- `[tool.importlinter]` contracts from the architecture sketch, one
  `layers` contract per area; `bootstrap` only in the forbidden contract;
  an `independence` contract once there are two or more areas
- `Makefile` targets `lint-boundaries` → `lint-imports`; `lint` (runs `lint-boundaries` + the stack linter + `vulture` with a whitelist file for framework entry points), `typecheck` (the type checker §1 Стек named), `test`
- `bootstrap/main.py` + `bootstrap/wiring.py` — the app factory with the
  service endpoints only (SKILL.md §5); no use-case construction
- `bootstrap/observability.py` (the JSON formatter, the request-id and
  duration middleware, the three service routes), the lifespan that disposes
  the engine, and `bootstrap/serve.py` — the production entry
  (`python -m <package>.bootstrap.serve`: logging first, then `uvicorn.run`
  with `log_config=None` and the graceful-shutdown timeout): copied from
  `fastapi/references/service-endpoints.md`; `prometheus-client` in the
  dependencies. The service routes stay in `bootstrap/` — they reach the
  engine `bootstrap/` owns — never in an area's adapters
- Alembic (or the named tool) with one revision per file in
  `documentation/db/migrations/`, each executing its file; revision 1 runs
  `0001_init.sql` (SKILL.md §4, `fastapi-sqlalchemy`); `env.py` sets
  `transaction_per_migration=True`; `make migrate` → `alembic upgrade head`
- `tests/contract/test_openapi_contract.py` from
  `fastapi/references/contract-test-template.py`, its placeholders pointed
  at the real app factory. Green on the scaffold: every contract operation
  is listed as not served yet
- `tests/conftest.py` from `pytest-patterns/references/conftest-template.py`
  when the system stores data: the test database gets its schema from the
  migration command, never `create_all`

Django: `models.py` is a one-line re-export; `migrations/` stay at the
app root, one migration per file in `documentation/db/migrations/`, each a
`migrations.RunSQL` of that file; `urls.py` is the composition root. No `ModelAdmin` that writes.

Forbidden in `domain/` / `application/`: fastapi, starlette, sqlalchemy,
django, pydantic, httpx (match the architecture's forbidden list).

## Go (chi / pgx)

Create:

- `go.mod`
- stack-shaped root `internal/` as in the tree
- HTTP adapter package `httpserver`, never `http`
- `.go-arch-lint.yml` version 3 from the architecture sketch (`workdir`
  relative to the module, `deps` sibling of `components`)
- `.golangci.yml` with depguard vendor bans from the sketch
- `cmd/<service>/main.go` constructs only the chi router + the service
  endpoints, JSON logs (`log/slog` with a JSON handler) and the shutdown of
  SKILL.md §5 (`signal.NotifyContext`, `http.Server.Shutdown` with the
  timeout)
- a plain runner (`cmd/migrate`) over `documentation/db/migrations/`
  (SKILL.md §4) — `golang-migrate` and `goose` expect their own file names
  or markers, so they wrap nothing here unless §1 names one

`bootstrap` / `cmd` may import everything. `domain` `mayDependOn: []`.

## C# / ASP.NET Core

Create:

- solution + projects matching the tree (HTTP, Application, Domain,
  Persistence, Host)
- Host references everything; HTTP references Application, **not**
  Persistence
- NetArchTest project with one `[Fact]` per import direction from
  section 8; Host exempt
- `Program.cs` + `bootstrap/` extensions — the service endpoints, JSON logs
  and shutdown of SKILL.md §5 only (health checks mapped to `/health/live`
  and `/health/ready` with tag filters, a Prometheus exporter at `/metrics`,
  `HostOptions.ShutdownTimeout` from `SHUTDOWN_TIMEOUT_SEC`)
- EF (or named tool): one migration per file in
  `documentation/db/migrations/`, whose `Up` runs that file through
  `migrationBuilder.Sql(...)` (SKILL.md §4). Fluent API
  / `[Table]` stay in Persistence

No `[ApiController]` on a use-case class — there are no use-case classes
yet. Do not add MediatR "for later".

## Java / Kotlin (Spring)

Create:

- Maven or Gradle module graph matching the tree
- ArchUnit test from the architecture sketch
- `@Configuration` only in the outermost / bootstrap package
- the service endpoints of SKILL.md §5 via Spring Actuator (health groups
  `live` and `ready` at `/health/live` and `/health/ready`, the Prometheus
  endpoint at `/metrics`), JSON console logs, and
  `server.shutdown=graceful` with
  `spring.lifecycle.timeout-per-shutdown-phase` from `SHUTDOWN_TIMEOUT_SEC`
- Liquibase: one `sqlFile` changeset per file in
  `documentation/db/migrations/`; Flyway only when its naming settings read
  those file names as they are — otherwise a plain runner (SKILL.md §4)

No Spring annotations under `domain/` or `application/`.
