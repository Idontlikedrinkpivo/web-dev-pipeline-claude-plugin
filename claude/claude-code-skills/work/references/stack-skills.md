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
