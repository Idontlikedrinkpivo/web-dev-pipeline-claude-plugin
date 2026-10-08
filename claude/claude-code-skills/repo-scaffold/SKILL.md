---
name: repo-scaffold
description: >-
  Materializes an architecture document's file tree and stack into an empty
  runnable repo: folders, manifest, boundary linter, .env.example, a
  migration runner over documentation/db/migrations/, a health-only entry
  point, and the project map. Use after `clean-architecture-design` when the user asks to scaffold
  or init the repo — «каркас репозитория», «разверни структуру», «карта
  проекта» — or when an architecture change adds folders. Not for choosing
  the stack, business code (`work`), compose files (`deploy-topology`), or
  CI.
---

# Repository Scaffold

Turn the architecture foundation's **tree + stack** into files on disk
and write `documentation/project-map/project-map.md` — one page that points at the
docs and how to run. Stop when an empty app starts, `/health` answers,
the boundary linter is green, and the map exists. Do not write domain or
application logic.

## Not for

- Choosing or re-opening the stack — that was decided in architecture
- Entities, use cases, controllers that implement OpenAPI, UI
- Production CI/CD, Kubernetes, a secrets manager
- The full test/dev/prod compose topology with mocked externals and an
  externally managed prod database — this skill's compose, if any, is a
  single dev-shaped convenience file; `deploy-topology` builds the three-
  environment shape once there is real application code to wrap
- Rewriting a repo that already has application code — see the
  Already-a-repo gate below

## Input

Resolve `<repo-root>` via `git rev-parse --show-toplevel` (cwd if not a
git repo). Write application files there. The one documentation file
this skill writes is `documentation/project-map/project-map.md` (section 6).

The architecture is three documents in `documentation/architecture/`.
This skill reads the foundation, `architecture.md`; the domain model
(`domain.md`) and the scenarios documents (`scenarios/<area>/<area>.md`)
hold no folders or lint rules it needs.

| Required | Source |
|---|---|
| Stack | Foundation §1 Стек — language, HTTP framework, database. Local run — §5. Boundary linter — §6 |
| File tree | Foundation §5 — real area and file names, not `<area>` |
| Import-direction table + lint rule table | Foundation §6 |
| Composition-root pattern | Foundation §4 Сборка, matching the chosen framework |

| Optional | Source |
|---|---|
| Migration files | `documentation/db/migrations/*.sql` from `db-schema-design` (`0001_init.sql` first) |
| Variable names | Foundation §4 «Конфигурация» — names only, never values |
| Entity file names | Domain model `documentation/architecture/domain.md` — the path in each entity heading; read it only when a stub or a lint path needs an entity file name |

If §1 Стек or the tree is missing, stop and say what is missing. Do
not invent a stack or a different folder layout (no Nx or generic
starter): the next stages build on exactly the tree architecture drew.

**Already-a-repo gate.** If `src/`, `internal/`, or a lockfile already
contains application modules (not just this skill's empty stubs), do
**not** rewrite the tree. If the user asked for a project map, go to
section 6 and stop. If a foundation changelog row's «Кого затрагивает»
cell names `repo-scaffold`, go to "Increment mode". Otherwise stop:
"This repo already has application code. Scaffold would overwrite it.
Say which new service path to use, or stop." When the user names a path
(`services/billing/`), scaffold there as if it were an empty repo: that
directory is the root for this run, and nothing outside it is touched.

## Increment mode

Trigger: a foundation changelog row names this skill in «Кого
затрагивает» and the repo already has application code. The pipeline
sends an architecture change here when the tree or the stack moved; without this mode a new area
would get neither folders nor a lint contract.

- Diff the new §5 against the disk. Create only the folders and stubs §5
  names and the disk lacks.
- Add each new area or layer to the boundary lint (a new `layers`
  contract, a new go-arch-lint component, a new ArchUnit / NetArchTest
  rule). Do not rewrite existing rules.
- Touch nothing else except the manifest (a dependency the new §1 Стек
  names), `.env.example` (new names only), and
  `documentation/project-map/project-map.md`.
- A §5 change that renames, moves, or deletes an existing folder is not
  scaffold work — it moves live code. Stop and name `plan`.
- Run the Quality gate (lint with the canary, health), then Closing.

## Progress file

Before section 1, create `documentation/plans/<version>/progress-scaffold.md`
per `pipeline` → `references/progress-files.md` — sections 1–6 below as rows, `⏳ ждёт` — and
post its link in the chat. Set each row `🔄 в работе` → `✅ готово` as you
go, and after each section write the count with the link in the chat
(«Каркас: 3 из 6 · [progress-scaffold.md](…)»); the line under the table
carries the quality gate. Installing the
tooling and running the first lint and tests take minutes.

## 1. Folders

Create every directory in foundation §5 with its real name. Do not add
`utils/`, `helpers/`, `common/`, or extra `shared/` when the tree
omitted it.

One stub per package so the tree is real on disk (the stack's
`__init__.py`, `.gitkeep`, or empty `.csproj`). Do not create
placeholder entity or use-case files "for later" — those names appear
when business code is written, not now.

## 2. Manifest and tooling

Read `references/stack-files.md` for the chosen stack only. Install the
minimum: language toolchain, HTTP framework, DB driver, test runner,
boundary linter named in §6, and the dead-code detector (`knip` /
`vulture`) that `work` runs before the final review.

Pin versions in the lockfile. Install the majors §1 Стек names; a
lockfile that resolves a different major is a stop, not a silent
upgrade, because the lint rules target those majors. Do not add
ORMs, queues, or admin UIs §1 Стек did not name. A major, a tool, a port or
a variable that ends up different from the architecture — the user picks
the other major, a version assumption checks out differently — is a
changed decision: §1 Стек or §4 is fixed and committed at once, with no
version change, before the next section (`pipeline` →
`references/decision-changes.md`).

The manifest's own `version` is the service version: on a new repo the
open iteration's, the name of `documentation/plans/<version>/` (`0.1.0`
on greenfield). Increment mode leaves it alone; the plan's last unit
moves it (`pipeline` → Service version).

## 3. Boundary lint

Build the config from the foundation's lint rule table (§6:
one row per rule, from → must not import) in the shape the stack's
reference shows (`clean-architecture-design/references/machine-checkable-boundaries.md`).
An older architecture that pasted a config instead is a starting point,
not a file to copy blind. Use the real area names and the real root
package — no leftover `<area>` / `<root>`. Keep Host / `bootstrap/` exempt from inward-only rules.

Every production folder from §5 must appear in the config. A
folder the linter does not know is an unguarded door.

Wire a single command (`lint-boundaries` or the stack equivalent) and
run it. If it fails on the empty tree, fix the config (usually a
leftover placeholder), not the tree.

Also wire the three check targets `ci-pipeline` later calls verbatim:
`make lint` (runs `lint-boundaries` plus the stack's linter),
`make typecheck`, and `make test` — or `npm run lint` / `npm run
typecheck` / `npm test` for a Node-only repo. Use hyphens, not colons,
in Make target names: `lint:boundaries` breaks Make.

## 4. Local run and schema

`.env.example` lists every variable of foundation §4 «Конфигурация»
(names and a comment, never values). No `.env` committed, no values
invented.

`.gitignore` carries `documentation/plans/` from the first commit: plans,
reviews, progress files, reports and summaries are working files of this
machine, not project history (`pipeline` → Plans stay out of git).

`docker-compose.yml` whenever the system stores data (a schema exists): a
Postgres service (and nothing else unless §1 Стек / §5 named it),
documented port, variable names in `.env.example`; values in a gitignored
`.env.dev.local`, read via `env_file` (the file `deploy-topology` keeps when
it renames this compose to `docker-compose.dev.yml`). `work` runs the
integration tests against this database, so it exists before the first
unit, not after `deploy-topology`. The `test` target documents how to start
it (`docker compose up -d`) when a test needs it. Write it ready for
copies (`ui-test-cases` → `references/parallel-stands.md` → A stand that can
be copied): ports and addresses from variables with defaults, no
`container_name`, no fixed host volume path, and a Playwright `baseURL`
read from a variable when the project has browser tests.

**Migrations run from the documentation folder.** The SQL files in
`documentation/db/migrations/` (`db-schema-design`) are the migrations —
reviewed, numbered `NNNN_<slug>.sql`, never edited once committed. Do not
copy them into the code tree: a copy drifts from the reviewed file. Point
the project's migration tool at that folder (runner config or a small
script) and wire one command (`make migrate` or `npm run migrate`). A plain
runner applies the files in name order, each once, records it in a version
table in the project schema, and applies a file that contains
`CONCURRENTLY` outside a transaction. A tool with its own format (Alembic,
EF, Liquibase) gets one entry per file that executes that file's text —
`references/stack-files.md`. The runner reads the folder by its
repo-relative path, so the backend image carries it at that same path
(`deploy-topology`). If no migration file exists, wire the runner
over the empty folder — do not invent `CREATE TABLE`, because tables nobody
designed become a schema the next stages must honour.

Check that `0001_init.sql` opens with `CREATE SCHEMA IF NOT EXISTS <schema>;`
and `SET search_path TO <schema>;`, and every later file with the `SET` line
(`db-schema-design` §0). If a line is missing, do not edit the file — it
belongs to `db-schema-design`, and a committed one is frozen — do not apply
it either: name the gap for `db-schema-design` in the report. Point
`DATABASE_URL`'s `search_path` (and the migration tool's own version-table
config) at that same schema.

## 5. Health-only composition root

Follow the wiring pattern the architecture already named for this
framework (router factory, `Program.cs`, `cmd/` + bootstrap). The
process:

- reads config from the environment
- connects to the database only if a URL is present (health may report
  `db: down` only when no database URL is configured)
- exposes `GET /health` → `200` with a small JSON body
- does not construct a use case or a repository

## 6. Project map

Write (or update in place) `documentation/project-map/project-map.md`. Create
`documentation/project-map/` if missing. One file per repo — never a dated sibling.

This is an index, not a second architecture. Do not copy the
foundation's §5 tree or §2 modules table. Do not invent product behavior, screens,
or tables. One sentence from the SRS Summary (or architecture digest);
everything else is a path, a command, or «нет».

If the file already exists, refresh paths and «Как запустить» / «Где
код» to match the disk. Leave the one-sentence product line unless the
SRS Summary changed.

No `version`. No changelog. `updated:` today. `sources:` is the
architecture path with no `@<version>` pin. See `doc-versioning`.

```markdown
---
title: <Name> — карта проекта
updated: YYYY-MM-DD
sources:
  - documentation/architecture/architecture.md
---

# Карта проекта: <Name>

<одно предложение из Summary SRS>

## Документы

| Что | Путь |
|---|---|
| Бизнес-требования | `documentation/requirements/business-requirements/business-requirements.md` или «нет» |
| SRS | `documentation/requirements/srs/srs.md` — оглавление; группы требований — `documentation/requirements/srs/areas/` |
| Архитектура — основа | `documentation/architecture/architecture.md` — §5 дерево, §2 модули; схемы встроены в разделы |
| Доменная модель | `documentation/architecture/domain.md` |
| Сценарии по областям | `documentation/architecture/scenarios/<area>/<area>.md`, по строке на область из §2 |
| Экраны | `documentation/ui/` — `frames-register.md`, `screen-specs/` (файл на экран), `test-cases/` (`README.md` и файл на раздел), или «нет UI» |
| Схема БД | `documentation/db/schema.md` или «нет» |
| Миграции БД | `documentation/db/migrations/` или «нет» |
| OpenAPI | `documentation/api/openapi.yaml` — корень; операции — `paths/`, схемы — `components/`; или «нет» |
| Открытые вопросы | `open-questions.md` в папке каждого документа |

## Как устроено

Стек: <одна строка из arch §1 Стек>.
Дерево и владельцы состояния — в основе архитектуры (§5, §2), не здесь.

## Как запустить

- процесс: <команда из §5 / манифеста>
- `GET /health` → 200
- compose: <файл или «нет»>
- секреты: `.env.example` (имена, не значения)

## Где код

- composition root: <path>
- `make lint` → `lint-boundaries` (или эквивалент); `make typecheck`, `make test`
- миграции: `documentation/db/migrations/`, команда <`make migrate` / `npm run migrate`> (или «пусто»)
```

### Point every session to the map

Claude Code reads the repo's `CLAUDE.md` at the start of every session, so a
pointer there tells any model — and any person — where the documents are
before it starts searching. Add this section to `CLAUDE.md` at the repo root
(create the file when there is none; in an existing one, add or refresh only
this section and leave the rest as the owner wrote it):

```markdown
## Где что лежит

Карта документов и кода — `documentation/project-map/project-map.md`.
Большие документы разложены по файлам, у каждого есть оглавление:
SRS — `documentation/requirements/srs/srs.md`, OpenAPI —
`documentation/api/openapi.yaml`, тест-кейсы —
`documentation/ui/test-cases/README.md`. Ищите id и operationId по папке
документа, а не только в оглавлении.
```

## Quality gate

The one final check. Items 1–3 skip on a map-only run.

1. Tree on disk equals foundation §5 — real names, a stub per empty
   package, no extra top-level app folders (Step 1). Manifest and
   lockfile hold only the minimum at the §1 majors (Step 2).
2. `lint-boundaries` (or equivalent) exits 0 — and it can fail. On an
   empty tree every rule is green, so green alone proves nothing. Write
   one throwaway file in the first area's `domain/` that imports that
   area's `adapters/` in the import style the tree uses (alias or
   relative). Run the lint, expect a non-zero exit naming the domain
   rule, delete the file, run again, expect 0. A lint that stays green
   on the canary guards nothing: fix the config (unresolved alias, wrong
   root package, a layer missing from the config, a rule left at
   warning severity).
3. Local run (Steps 4–5):
   1. The process starts and `GET /health` returns 200.
   2. `.env.example`, compose, and the migration runner match Step 4;
      the runner reads `documentation/db/migrations/` and nothing in the
      code tree holds a copy of a migration file.
   3. When §5 said Compose and a migration file exists, start only the
      database service and apply the files with the wired migrate command.
   4. Expect `GET /health` to report `db: up`, and the tables to sit in
      the project schema, not `public`.
   5. With no Docker, skip 3–4 and say «миграция не применялась» in
      Closing.
4. No entity, use-case, repository, or OpenAPI handler files were added
   (Step 5).
5. No stack was chosen or changed here.
6. `documentation/project-map/project-map.md` exists. Every path in it is a real
   file or the explicit «нет» / «нет UI» / «пусто». The body does not
   paste foundation §5 or §2 (Step 6).

If health cannot be started in this environment (no Docker, no runtime),
say what was created and what was not verified. Do not skip the lint run
when the toolchain is present.

## Closing

List the paths created (manifest, lint config, compose, composition root,
migration runner config or script, `documentation/project-map/project-map.md`). A map-only run names the map
path and stops — it does not ask the next stage again if a plan already
exists.

Read `pipeline` and ask about the stage its table names after this one,
per "Asking before a transition". This skill often runs inside an
isolated subagent that cannot open `pipeline`; only then ask about
`plan` with the same two options. Do not list the rest of the pipeline,
and do not start the next stage on a no.
