# Stack file map

Open only the section that matches architecture §1 Стек (a backend and a
frontend may both apply). Substitute real names from the file tree. Lint
rules come from the foundation's §6 rule table — build the config from
those rows, do not invent a second rule set. Every stack gets the same three
check targets (`lint`, `typecheck`, `test`) plus `lint` running the
dead-code detector, so `work` and `ci-pipeline` call the same commands
everywhere.

## TypeScript (Fastify / Express / Nest / Koa)

Create:

- `package.json` + lockfile
- `tsconfig.json` — `rootDir` / `paths` follow the tree (`src/`)
- `.dependency-cruiser.cjs` from the architecture sketch; `$1` for area
  capture, `tsPreCompilationDeps: true`, `tsConfig` pointing at the root
  `tsconfig.json` (so `paths` aliases resolve), the `not-to-unresolvable`
  rule, and `severity: 'error'` on every rule
- `npm` / `pnpm` scripts `lint-boundaries` → `depcruise src --config .dependency-cruiser.cjs`; `lint` (runs `lint-boundaries` + the stack linter + `knip`), `typecheck` (`tsc --noEmit`), `test`
- `bootstrap/server.ts` — health route only. Fastify: build the instance in a
  `buildServer()` factory with the one type provider and the one global error
  handler the architecture names (problem+json per `documentation/api/openapi.yaml`), so
  `typescript-fastify` finds them; Express/Koa: the same factory shape; Nest:
  a module under `bootstrap/`
- `knip` config listing the entry points (`bootstrap/server.ts`, the migrate
  script, test globs),
  so the dead-code report starts clean
- `docker-compose.yml` with Postgres + `.env.example` whenever the system
  stores data (SKILL.md §4)
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

- `package.json` + lockfile with scripts `dev`, `build`, `lint` (ESLint +
  `knip`), `typecheck` (`tsc --noEmit`), `test` (Vitest + Testing Library),
  `test:e2e` (Playwright), and `api:gen` — the OpenAPI client generator over
  `documentation/api/openapi.yaml`, writing to the folder the profile names
- `tsconfig.json`, the bundler / framework config, ESLint config,
  `playwright.config.ts` with `baseURL` and `webServer` pointing at the dev
  server
- the app shell from the profile (root layout or `main.tsx` + router) with
  one placeholder route; no screens, no API client yet — the first screen
  unit runs `api:gen` and builds the app-wide error handler (`frontend`)
- `.env.example` with the API base URL variable the profile names

## Python (FastAPI)

Create:

- `pyproject.toml` + lock (`uv.lock` or `poetry.lock`)
- package named after the project, not `app` or `platform`
- `[tool.importlinter]` contracts from the architecture sketch, one
  `layers` contract per area; `bootstrap` only in the forbidden contract;
  an `independence` contract once there are two or more areas
- `Makefile` targets `lint-boundaries` → `lint-imports`; `lint` (runs `lint-boundaries` + the stack linter + `vulture` with a whitelist file for framework entry points), `typecheck` (the type checker §1 Стек named), `test`
- `bootstrap/main.py` + `bootstrap/wiring.py` — include a health router
  factory; no use-case construction
- `adapters/<area>/http/` may contain `health.py` as a router factory
- Alembic (or the named tool) with one revision per file in
  `documentation/db/migrations/`, each executing its file; revision 1 runs
  `0001_init.sql` (SKILL.md §4, `fastapi-sqlalchemy`); `make migrate` →
  `alembic upgrade head`

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
- `cmd/<service>/main.go` constructs only the chi router + health
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
- `Program.cs` + `bootstrap/` extensions — health endpoint only
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
- health via Spring Actuator or a one-method controller in the HTTP
  adapter
- Liquibase: one `sqlFile` changeset per file in
  `documentation/db/migrations/`; Flyway only when its naming settings read
  those file names as they are — otherwise a plain runner (SKILL.md §4)

No Spring annotations under `domain/` or `application/`.
