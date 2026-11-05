# Stack skills for a unit

A worker writes better code with the house rules of its language and libraries — and none of them reaches it
unless `work` names them in the packet. Pick them from the architecture's §1 «Стек» and the unit's `Файлы` (and
its «Цель» where the table says so), and list in `STACK SKILLS` the absolute path of each `SKILL.md` under
`SKILLS ROOT` (a `references/` file only where the table names it or the skill's text sends the worker to it for
this unit), plus any skill the user attached. The worker reads them from disk before it writes code. They are not
pasted: three or four skills are tens of kilobytes the session would type into every dispatch, two per unit for a
two-phase one (`executor-catalog` → Dispatch contract → Paths, not pasted documents). A skill's
`references/version-checks.md` is never listed: Step 2b turns it into the answers in `CURRENT LIB DOCS`
(`context7.md`).

| The unit's files | Stack skills |
|---|---|
| any `.ts` / `.tsx` | `typescript` |
| React components and hooks (`.tsx`, `use*.ts`; test files are the test row) | `react`; for a screen or component source file also `frontend` with its one profile and `web-design-guidelines` (SKILL.md → Inputs) |
| Fastify routes, plugins, the server factory, the error handler | `typescript-fastify` |
| the contract test (`tests/contract/openapi.contract.test.ts`) | `typescript-fastify` and its `references/contract-test-template.ts` |
| TypeScript login, registration, password hashing, tokens, the current-user and role guards | `typescript-fastify` and its `references/auth.md` |
| Drizzle tables, repositories, queries, migrations runner | `typescript-drizzle-orm` |
| Zod schemas, the wire boundary, a form schema, env parsing | `zod-skill` |
| `*.test.ts` / `*.test.tsx`, test helpers, `vitest.config` | `vitest`; a React test file or test helper also `react` — never `frontend` or `web-design-guidelines` |
| any `.py` | `python` |
| FastAPI routers, dependencies, the app factory, exception handlers, settings | `fastapi` |
| login, registration, password hashing, tokens, the current-user and role dependencies — by its files or its «Цель» | `fastapi` and its `references/jwt-auth.md` |
| the contract test (`tests/contract/test_openapi_contract.py`) | `fastapi` and its `references/contract-test-template.py` |
| SQLAlchemy models, repositories, sessions, the unit of work; Alembic revisions and `env.py` | `fastapi-sqlalchemy` |
| `tests/`, `conftest.py` | `pytest-patterns`; a new or rewritten `tests/conftest.py` also its `references/conftest-template.py` |
| Playwright specs and config | `playwright-cli`, but not its `SKILL.md` (the browser-driving loop): list `references/test-config.md` and `references/playwright-tests.md`; add `references/test-generation.md` when the unit records specs from the running app or heals failing ones — of it only its «Inside dev-pipeline» block, §0 and §3.1–3.3 apply, and the packet says so |

A unit that touches several kinds gets every skill that applies. A stack the table does not name gets no invented
pack: `none — no stack skill for <stack>`.

The reviewer of the unit (`code-review-unit`) receives the «The reviewer checks» section of each of these skills
that has one — every language and library skill above does — so the review looks at what the linter cannot.

## Sections by subject

Every stack skill opens with `## Essentials`: the rules a unit breaks most or that cost most, each with a pointer to
its section. «Always» is read by every unit that gets the skill; a «by subject» section only when the unit's facts
match.

| Skill | Always | By subject: section — the unit facts that call for it |
|---|---|---|
| `typescript` | Essentials | «The machine checks» — lint or `tsconfig` config, a disable comment; «The reviewer checks» — source code, not only config |
| `react` | Essentials | «The machine checks» — lint config, a disable comment; «The reviewer checks» — a component, a hook, state or an effect (for the reviewer always) |
| `zod-skill` | Essentials | «Boundary rules» — a wire schema, env parsing; «Failure response» — a route or handler that answers a parse failure; «Schema evolution and tests» — a changed schema or its test; «On the frontend» — a form schema, a client parsing a response; «The reviewer checks» — any schema |
| `vitest` | Essentials | «The machine checks» — `vitest.config`, lint config; «House rules» — any test file or helper; «The reviewer checks» — any test file |
| `typescript-fastify` | Essentials, «Which contract and layout apply» | «Rules» — a route, a plugin, the server factory; «Errors» — the error handler, a new named error; «Collections and cursors» — a paged read; «Idempotency keys» — a create with the header; «Versions side by side» — an API with external consumers; «Service endpoints, logs and shutdown» — `bootstrap/`, health, metrics, logging; «The contract test» — a route added or changed; «The reviewer checks» — a route or `bootstrap/` code |
| `typescript-drizzle-orm` | Essentials, «Which layout applies» | «Rules» — a table, a query, a transaction, a migration; «Shape of a repository adapter» — a repository or its mapper; «The reviewer checks» — any Drizzle code |
| `python` | Essentials | «The machine checks» — Ruff or type-checker config, a `noqa` / `type: ignore`; «The reviewer checks» — source code, not only tests or config |
| `pytest-patterns` | Essentials, «Which layout governs», «Test layout» | «Real database, not mocks» — an integration or adapter test, a mock; «Fixtures» — conftest or factories, a race test; «API tests» — an HTTP test; «Coverage» — coverage config or its threshold; «References» — a new conftest or factory; «Properties and mutants» — a property test, a surviving mutant; «The reviewer checks» — any test |
| `fastapi` | Essentials, «Which layout governs» | «Use the `fastapi` CLI» — the entrypoint, `pyproject.toml`, the serve entry; «Conventions» — a route, a dependency, a request or response model; «Errors as problem+json» — the exception handlers, a new named error; «Auth and configuration» — login, tokens, a cookie, settings, CORS; «Service endpoints, logs and shutdown» — `bootstrap/`, health, metrics, logging; «The contract test» — a route added or changed; «Tooling and libraries» — a new dependency, an outbound call; «The reviewer checks» — a route or `bootstrap/` code |
| `fastapi-sqlalchemy` | Essentials, «Which layout governs», «Layout with an architecture document» | «Session and unit of work» — a session, a commit, a unit of work; «Models and column types» — a model or a column; «Relationships under AsyncSession» — a query or a model with relations; «Migrations» — a migration or `env.py`; «Driver errors and install» — a write that can conflict, a constraint violation, the install; «Raw SQL» — `text()`, `exec_driver_sql`; «The reviewer checks» — any SQLAlchemy code |

`work` writes after each `SKILL.md` path in `STACK SKILLS` the sections to read:
`<path> — sections: <the «always» ones>, <the by-subject ones>`. Essentials and the «always» sections are always
named; a by-subject section is named when the unit's `Файлы`, «Цель» or «Тестовые сценарии» match its facts; under
doubt, the whole file — a path with no sections named is read whole. A `references/…` path is read whole. The
reason: the full set is about 500 lines of dense rules per unit for a hundred lines of code, and the rules in the
middle were the ones the worker lost; Essentials keeps the costly ones in front, the named sections keep the rest
that this unit needs. The reviewer's input (`code-review-unit`) is unchanged: the whole «The reviewer checks» of
each picked skill.
