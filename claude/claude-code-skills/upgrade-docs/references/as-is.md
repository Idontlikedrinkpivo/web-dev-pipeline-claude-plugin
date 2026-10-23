# A document written from the code as it is («как есть»)

Read by a stage `upgrade-docs` runs for a missing document of the set (`project_format.py set`), and by its
writer through the packet's `MODE as-is`. The project's code exists and the document does not — a project
started without the plugin, or a stage that was skipped. The stage writes its own document, by its own template,
with its own gates; only the source changes: instead of the document above it in the chain, the writer reads the
code, and the project's own earlier documents. Nothing in the document's shape changes.

## Sources, by path

The packet names them by path, as every packet does (`executor-catalog` → Dispatch contract): the code that
shows what this document describes — entry points and routes, models and migrations, validators and types,
configuration, the tests (a test is the best evidence of intended behaviour the code has) — and the project's own
documents that cover it (`project_format.py set . --foreign` lists them). A document of the set that already
exists comes first, as in the normal chain; a missing one above it is read from the code instead.

## Rules

1. **Describe, do not design.** The document says what the code does now — including what looks wrong. A rule
   the code enforces is a rule; a rule the code nowhere enforces is not invented; dead code is named as dead, not
   described as a feature. A decision that breaks the plugin's design rules (logic in handlers, no ports, internal
   ids in the API) is described as it is: changing it is `upgrade-code`'s audit, not this document's.
2. **A guess is an open question.** Intent the code cannot tell — «так задумано или ошибка?», a magic number, a
   field nobody reads, two code paths that disagree — goes to the document's `open-questions.md` with the file and
   line, never into the body as a decision. The stage's gate shows them to the user.
3. **Requirements** (business requirements, SRS) speak the user's language, never the code's: a use case per
   action a user can take (a route, a screen action, a scheduled job that changes data), its acceptance criteria
   from the tests that cover it, else from the code paths — the success path and each error the code returns.
   The grill and the review are not optional here: the user confirms that what the code does is what they want,
   and each «нет, должно быть иначе» is a changed decision (`pipeline` → `references/decision-changes.md`).
4. **The database schema** is the state the project's migrations produce, cross-checked with the models. The
   migrations stay where the project keeps them: `schema.md`'s frontmatter `migrations: <folder>` names that folder
   (the table pages read its constraint comments there) and `migration:` the newest file in it; nothing is copied
   into `documentation/db/migrations/` and no migration is written — the packet's OUTPUT PATH is `schema.md` alone.
   The DBML, the ER diagram and the table pages are made as usual.
5. **The API** has an operation for every route the application serves except its service paths (`/health`,
   `/health/*`, `/ready`, `/live`, `/metrics`), with the request and response shapes from its validators and
   types, and each status and error as the code returns it — in the code's format, even when it is not
   problem+json: the stage's own problem+json rule, status list and base schemas do not apply. The path and the
   version are the code's, for a partner API too: a missing major path (`/v1`) or no authentication is described
   as it is and written as an open question, never designed. Of the questions the stage asks before its writer,
   as-is asks none — the code answers them. When the project has the contract test
   (`tests/contract/`), it must pass against the new `openapi.yaml`; when not, say that `upgrade-code`'s
   `contract-test` change adds it.
6. **The architecture** shows the real modules, layers, dependencies and transactions. A section the template
   requires that the code has nothing for — no ports, no entities with behaviour, no invariant table — says «в коде
   нет» in one line instead of inventing structure. The file tree is the real one.
7. **Screen specs** come from the frontend: a screen `S-n` per route, in route order; its elements, the states the
   code renders, the operations it calls by `operationId`. There are no frames: where a spec cites a `nodeId` it
   cites the component's file, and the spec says «кадров нет — по коду». The frames register is not written; a
   later `ui-design` run can draw the screens and add it.
8. **The deploy document** is `deploy-topology` Step 8 alone, from the project's own Dockerfiles and compose files
   as they are. Rebuilding them to the plugin's shape is `upgrade-code`'s `devops-ready` change.
9. **Version.** No iteration is opened for an as-is document: it describes a release that already runs. A
   versioned document is born at the service's current version — the manifest's `version`; with none, ask the
   user once for the number the running system has — and that number is the packet's `VERSION`, the writer's and
   the typist's alike. Its single journal row: «описан выпуск <version> как есть», typed «—». Its `sources:` pin
   the documents it read at their versions; when it read only code, they list the code folders, unpinned (code
   has no document version).
10. **Commit as written — that commit is its stamp.** The document is born complete at its version, so its first
    commit is `docs: <документ> <version> — как есть`, on the branch `upgrade-docs` picked; the gates follow it,
    and a fix a gate makes is a later commit under the same version on that branch — no iteration, no new
    journal row, no separate stamp.

## After the set

The project's own earlier documents (`set . --foreign`) are asked about one file per message, once the documents
that replace them exist: keep it, or remove it (`git rm` — it stays in the history). Never removed unasked, never
edited.
