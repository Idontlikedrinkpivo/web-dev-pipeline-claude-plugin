# Refreshing current library docs (Step 2b)

Read this once per run, before the first dispatch, when any unit in scope
calls a public library API.

The worker has no chat history and may have no MCP. It cannot "go look up
FastAPI". You fetch once, here, and paste slices into each packet.

1. From the plan digest, the units' `Файлы` / `Подход`, and the repo
   manifests (`package.json`, `pyproject.toml`, lockfiles if present), name at
   most four **public** libraries this run will actually call. Skip the rest.
   Internal services and private packages are not Context7's job.
2. For each, read the version the repo already depends on. When Context7
   returns versioned IDs, pick that major.minor. Do not prefer "latest" over a
   declared pin.
3. **The questions come from the stack skills.** The skill that owns a
   library lists, in its `references/version-checks.md`, the facts that change
   between releases — the places where an answer from memory silently breaks:

   | Library | List |
   |---|---|
   | Fastify, its type provider, `@fastify/swagger` | `typescript-fastify/references/version-checks.md` |
   | Drizzle ORM, drizzle-kit | `typescript-drizzle-orm/references/version-checks.md` |
   | Zod | `zod-skill/references/version-checks.md` |
   | Vitest, MSW | `vitest/references/version-checks.md` |
   | FastAPI, PyJWT, pwdlib | `fastapi/references/version-checks.md` |
   | SQLAlchemy, Alembic, the async PostgreSQL driver | `fastapi-sqlalchemy/references/version-checks.md` |
   | pytest-asyncio, factory_boy, httpx, coverage.py | `pytest-patterns/references/version-checks.md` |
   | the frontend's framework and router, data-fetching, form and schema libraries, the OpenAPI client generator | `frontend/references/version-checks.md` |
   | Playwright Test, playwright-cli | `playwright-cli/references/version-checks.md` |

   Read the list of each library from step 1 and keep the points the units in
   scope touch (a unit that adds no streaming route does not need the streaming
   point). If the Context7 tools are in this session (`resolve-library-id`,
   then `query-docs`), resolve each library and ask **one point per query**,
   worded from the point with the pinned version (`Fastify 5.6: the status and
   error shape of a request body that fails schema validation`). Then add a
   query for any other API those units touch that the list does not name — one
   topic per query, never "all of FastAPI".
4. Keep the answers in the run, each under the point it answers. At Step 4,
   each packet's `CURRENT LIB DOCS` gets only the points and excerpts that unit
   needs. A unit that does not call a library API gets
   `none — no library API in this unit`.
5. If the MCP is missing, auth-fails, or a library is not in the index: write
   `none — Context7 unavailable (<reason>)` or `none — <lib> not in Context7`
   and continue. Do not stop the run. Do not tell the worker to fetch docs —
   it has no session and may have no MCP; the stack skill tells it to probe
   the installed version in the project instead.
6. These excerpts lose to `DESIGN YOU MUST FOLLOW`, to `PATTERN TO MIRROR`,
   to the unit's «Подход» / «Тестовые сценарии», and to `STACK SKILLS`. They win
   only over the worker's memory of the library.

Record which libraries you fetched (id + pinned version) and how many points
each answered, or why you wrote `none`, in the run report's **Lib docs** line.

This is a lookup inside the stage, not a pipeline row. Do not offer Context7
to the user as a next step.
