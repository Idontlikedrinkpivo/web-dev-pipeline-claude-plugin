# Stack skills for a unit

A worker writes better code with the house rules of its language and libraries in the packet — and none of them
reaches it unless `work` puts them there. Pick them from the architecture's §1 «Стек» and the unit's `Файлы`, paste
each `SKILL.md` in full into `STACK SKILLS` (a `references/` file only when the skill's text sends the worker to it
for this unit, or in its place where the table names the files), and add any skill the user attached.

| The unit's files | Stack skills |
|---|---|
| any `.ts` / `.tsx` | `typescript` |
| React components and hooks (`.tsx`, `use*.ts`; test files are the test row) | `react`; for a screen or component source file also `frontend` with its one profile and `web-design-guidelines` (SKILL.md → Inputs) |
| Fastify routes, plugins, the server factory | `typescript-fastify` |
| Drizzle tables, repositories, queries, migrations runner | `typescript-drizzle-orm` |
| Zod schemas, the wire boundary, a form schema | `zod-skill` |
| `*.test.ts` / `*.test.tsx`, test helpers, `vitest.config` | `vitest`; a React test file or test helper also `react` — never `frontend` or `web-design-guidelines` |
| any `.py` | `python` |
| FastAPI routers, dependencies, the app factory | `fastapi` |
| SQLAlchemy models, repositories, sessions | `fastapi-sqlalchemy` |
| `tests/`, `conftest.py` | `pytest-patterns` |
| Playwright specs and config | `playwright-cli`, but not its `SKILL.md` (the browser-driving loop): paste `references/test-config.md` and `references/playwright-tests.md`; add `references/test-generation.md` when the unit records specs from the running app or heals failing ones |

A unit that touches several kinds gets every skill that applies. A stack the table does not name gets no invented
pack: `none — no stack skill for <stack>`.

The reviewer of the unit (`code-review-unit`) receives the «The reviewer checks» section of each of these skills
that has one, so the review looks at what the linter cannot.
