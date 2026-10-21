# Stack skills for a unit

A worker writes better code with the house rules of its language and libraries in the packet — and none of them
reaches it unless `work` puts them there. Pick them from the architecture's §1 «Стек» and the unit's `Файлы`, paste
each `SKILL.md` in full into `STACK SKILLS` (a `references/` file only when the skill's text sends the worker to it
for this unit), and add any skill the user attached.

| The unit's files | Stack skills |
|---|---|
| any `.ts` / `.tsx` | `typescript` |
| React components, hooks or their tests (`.tsx`, `use*.ts`) | `react`; for browser UI code also `frontend` with its one profile and `web-design-guidelines` (SKILL.md → Inputs) |
| Fastify routes, plugins, the server factory | `typescript-fastify` |
| Drizzle tables, repositories, queries, migrations runner | `typescript-drizzle-orm` |
| Zod schemas, the wire boundary, a form schema | `zod-skill` |
| `*.test.ts` / `*.test.tsx`, test helpers, `vitest.config` | `vitest` |
| any `.py` | `python` |
| FastAPI routers, dependencies, the app factory | `fastapi` |
| SQLAlchemy models, repositories, sessions | `fastapi-sqlalchemy` |
| `tests/`, `conftest.py` | `pytest-patterns` |
| Playwright specs and config | `playwright-cli` |

A unit that touches several kinds gets every skill that applies. A stack the table does not name gets no invented
pack: `none — no stack skill for <stack>`.

The reviewer of the unit (`code-review-unit`) receives the «The reviewer checks» section of each of these skills
that has one, so the review looks at what the linter cannot.
