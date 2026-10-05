# Refreshing current library docs (Step 2b)

Read this once per run, before the first dispatch, when any unit in scope
calls a public library API.

The worker has no chat history and may have no MCP. It cannot "go look up
FastAPI". You fetch once, here, and paste slices into each packet.

1. From the plan digest, the units' `Files` / `Approach`, and the repo
   manifests (`package.json`, `pyproject.toml`, lockfiles if present), name at
   most four **public** libraries this run will actually call. Skip the rest.
   Internal services and private packages are not Context7's job.
2. For each, read the version the repo already depends on. When Context7
   returns versioned IDs, pick that major.minor. Do not prefer "latest" over a
   declared pin.
3. If the Context7 tools are in this session (`resolve-library-id`, then
   `query-docs`), resolve each library and query **only the API those units
   touch** — one topic per query, not "all of FastAPI".
4. Keep the excerpts in the run. At Step 4, each packet's `CURRENT LIB DOCS`
   gets only the slice that unit needs. A unit that does not call a library
   API gets `none — no library API in this unit`.
5. If the MCP is missing, auth-fails, or a library is not in the index: write
   `none — Context7 unavailable (<reason>)` or `none — <lib> not in Context7`
   and continue. Do not stop the run. Do not tell the worker to fetch docs —
   it has no session and may have no MCP.
6. These excerpts lose to `DESIGN YOU MUST FOLLOW`, to `PATTERN TO MIRROR`,
   to the unit's Approach / Test scenarios, and to `STACK SKILLS`. They win
   only over the worker's memory of the library.

Record which libraries you fetched (id + pinned version), or why you wrote
`none`, in the run report's **Lib docs** line.

This is a lookup inside the stage, not a pipeline row. Do not offer Context7
to the user as a next step.
