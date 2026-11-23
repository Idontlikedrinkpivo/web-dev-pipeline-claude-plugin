# Env vars and the fail-fast config contract

The home of the env rule: every variable is described once, in the application's config schema; the project's own
generator renders from it every file a person reads; two stands, test and dev, hold their non-secret values in
compose and read only secrets and per-machine values from `.local` files; prod leaves as the kit. The templates of
the schema entry, the generator and its tests are `env-doc-typescript.md` (zod) and `env-doc-python.md`
(pydantic-settings), beside this file.

Before this (up to plugin 1.2.305) a hand-written `.env.example` with `{test: …, dev: …, prod: …}` marks fed a plugin
script that built every environment's file, beside a prod compose file and `.env.prod.local`. Four files written in
four places drifted apart in names, order and stale variables (ai-initiatives). A project still on it moves over by
`upgrade-code` → the `env-schema` row; nothing on this page asks for the old files.

## One description per variable — the config schema

Each variable is one entry of the schema the app parses its environment with: zod for TypeScript, pydantic-settings
for Python. There is no separate template with descriptions. An entry holds:

| Field | Means |
|---|---|
| the parser | the type and its check (`z.enum([...])`, `Field(ge=5, le=1440)`) |
| `block` | the group in the kit file and in DEPLOY.md: «backend и migrate», «языковая модель», «frontend» |
| `required` | prod refuses to start without it |
| `requiredNote` | optional: the «Обязательна» cell when the answer is conditional («да, при AUTH_MODE=external») |
| `secret` | a credential or key: never a real value in git |
| `purpose` | «для чего» — one Russian line, the comment above the variable in both files |
| `default` | optional: the value an unset variable gets; it must pass the parser |
| `prod` | the value of the kit file: a real one, or empty / `<заглушка>` for a secret and a per-site value |
| `example`, `details` | the «Пример / формат» and «Что задаёт» cells of DEPLOY.md's table (no `|` in them) |

- **«Обязательная»** is `required` with no `default`. The list of required names is derived from the schema
  (`REQUIRED_ENV_KEYS`, `required_env_keys()`), and the start check uses that same list — never a second list typed
  by hand.
- **An empty value is unset**, in the app and in compose alike: the app puts the default in before parsing
  (`withDefaults`), compose writes `${VAR:-default}`. `LOG_LEVEL=` in a `.local` file runs with `info`, not a crash.
- **Variables only compose reads** — the stand's bind interface (`DEV_BIND`), the stand's own infrastructure passwords
  (`DEV_MINIO_PASSWORD`) — are a short list beside the schema (`STAND_ENV_VARIABLES`: name, `secret`, purpose). The
  frontend image's variables (nginx's `BACKEND_SERVICE`, `SECURE_MODE`) are a list beside it too
  (`FRONTEND_ENV_VARIABLES`, full entries without the parser): the backend does not read them, the kit file holds them.
- **The schema is its own module** beside config (`shared/providers/env-schema.ts`, `bootstrap/env_schema.py`), and
  config re-exports it: config stays under `max-lines`, and the generator imports the schema without the app.

## Where each value lives

| Kind | test stand | dev stand | prod |
|---|---|---|---|
| Env selector (`APP_ENV`) and behavior flags (the mock gate, `BEHIND_TLS`, `LOG_LEVEL`, worker count) | compose `environment:` | compose `environment:` | a container variable from the kit file |
| Local-infra connection (`DATABASE_URL`, the object store) | compose `environment:`, pointed at the stand's service | compose `environment:` | a secret per container (the operators' store) |
| A secret the stand needs from outside (a model's token) | `.env.test.local`, optional | `.env.dev.local` | a secret per container |
| A per-machine value (bind interface, the stand's own infra passwords, an external service's address that differs per machine, the sign-in mode) | `.env.test.local` | `.env.dev.local` | a container variable |

- **Compose `environment:` wins over `env_file`.** A value compose sets is never repeated in a `.local` file: the
  second copy does nothing and misleads the next reader. A value a machine may change is a substitution with its
  default — `LLM_API_URL: ${LLM_API_URL:-http://llm-stub:8082/…}` — and then belongs to `.local` alone.
- **`.env.test.local` is optional**: `make up-test` creates it empty with mode 0600 when it is missing, and an empty
  one runs the stand on its stubs. **`.env.dev.local` is required** for `docker-compose.dev.yml` (`required: true`);
  `make up-dev` without it stops before Docker and names the file.
- **No prod in the repository**: no `docker-compose.prod.yml`, no `.env.prod.local`, no `.env.prod.migrate.local`, no
  `make up-prod` or `make env-*`. Prod is the kit — the images, `<project>.env.example`, DEPLOY.md — and the operators
  run it their own way (`deploy-doc.md`).

Every `DATABASE_URL` in every environment carries the same `search_path`/schema option, pointed at the dedicated
schema from `db-schema-design` §0 — never `public`. The schema name is a project constant, not a variable: the
environments differ in which server hosts the schema, never in its name. A different name on the operators' instance
is a fact for DEPLOY.md's «Для DBA», not something search_path absorbs quietly (a misnamed schema fails migrate loudly).

`migrate` and `backend` read the same `DATABASE_URL` name with different values: the schema owner for `migrate`, a
rows-only account for `backend` (`compose-shape.md` → Two database accounts). The test stand sets both inline; in prod
each container gets its own value from the operators' store, and the variable's `details` cell says so.

CI that runs `make test` on the runner (see `ci-pipeline`) rewrites compose hostnames to `127.0.0.1` and still copies
`APP_ENV`, the mock-gate variable and the same `search_path`; it takes the `migrate` service's URL (the owner),
because the runner applies migrations and the tests create and truncate data.

## Variables every backend has

Besides its own, the backend's schema has these entries, so the kit file and DEPLOY.md's tables list them:

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `LOG_LEVEL` | no | `info` | the logger's level; the set is the stack logger's (`typescript-fastify`, `fastapi`) |
| `SHUTDOWN_TIMEOUT_SEC` | no | `25` | seconds the server drains in-flight requests after SIGTERM — below Kubernetes' default 30 s grace period |
| `TRUSTED_PROXIES` | no | empty: nobody | networks of the proxies whose `X-Forwarded-*` the backend believes: the frontend's pods and the ingress |
| `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME` | only when the project chose tracing | — | where spans go and under which name; absent otherwise |

`APP_VERSION` and `CI_COMMIT_SHORT_SHA` come from the image (`images.md`): the config layer reads them, with `dev`
and `unknown` when run outside an image, and they are not schema entries. A Node backend's `NODE_OPTIONS`
(`--max-old-space-size`, `images.md`) is set in each compose file and named in «Ресурсы».

The first two are behavior flags: each compose file sets them in `environment:` — `backend` both, `migrate`
`LOG_LEVEL` — even at the default value. `backend`'s `stop_grace_period` is at least `SHUTDOWN_TIMEOUT_SEC` + 5 s:
Docker's own default of 10 s would kill the drain halfway.

## The generator — the project's own script

It lives in the project, beside the backend's manifest: `backend/scripts/env-doc.ts` (TypeScript) or
`backend/scripts/env_doc.py` (Python); `scripts/` at the root when the backend is the root. The plugin ships no env
script. From the schema it renders three files:

1. `deploy/prod.env.example` — every variable prod reads, for the operator (the kit's `<project>.env.example`);
2. the variables tables of `documentation/deploy/deploy.md`, between `<!-- env-doc:<table> — сгенерировано из <schema
   path> (<command>), руками не править -->` and `<!-- /env-doc:<table> -->`; a missing marker pair is an error, the
   text around the pair stays as it is;
3. the root `.env.example` — only the keys the `.local` files may hold.

| | TypeScript | Python |
|---|---|---|
| env:doc — write the three files | `npm run env:doc` in `backend/` (`tsx scripts/env-doc.ts`) | `uv run python scripts/env_doc.py` in `backend/` |
| env:check — compare, write nothing | `npm run env:check` (`… --check`) | `uv run python scripts/env_doc.py --check` |

env:check exits 1 and names each stale file on stderr: `env-doc: deploy/prod.env.example differs from env-schema.ts;
run npm run env:doc in backend/`. The three files are never edited by hand — a hand edit is what env:check catches.

- `scripts/build-images.sh` runs env:check first, so a stale render stops the build before any `docker` call, and only
  then copies `deploy/prod.env.example` into `release/<version>/` (`images.md` → Hand-over).
- `deploy_check.py` (this skill) runs the project's env:check and prints its output as findings.
- CI runs env:check with the tests (`ci-pipeline`).
- The project's linters and type check cover the script: `scripts/**/*.ts` in eslint's files, knip's entries and the
  test tsconfig; `scripts/` in ruff and mypy's paths.
- Never run the generator on a server. A stand server updates by `git pull --ff-only` and
  `docker compose --env-file .env.<stand>.local -f docker-compose.<stand>.yml up -d --build`, nothing else.

## The layout of both files

The kit file and the root `.env.example` share one layout; they differ in what they hold.

```bash
# ===== backend и migrate =====

# [required] среда приложения: test, dev или prod
APP_ENV=prod

# [required] [secret] подключение к PostgreSQL, схема room_booking
DATABASE_URL=postgresql://<пользователь>:<пароль>@<хост>:5432/<база>

# подробность логов: trace, debug, info, warn, error, fatal
LOG_LEVEL=info
```

- A block opens with `# ===== <блок> =====` and a blank line. In the kit file the block is the schema's; in the root
  `.env.example` it is only the file name — `# ===== .env.test.local =====`, `# ===== .env.dev.local =====` — with no
  explanation: README and the architecture explain the stands.
- The marker line sits directly above `NAME=value`: `[required]` and `[secret]` where they apply, then the purpose.
  Pairs are split by one blank line; no double blank line; the file ends with one newline.
- The kit file: every variable prod reads, in the schema's order, `NAME=<prod>`; a secret is empty or `<заглушка>`.
- The root `.env.example`: per `.local` file, the keys it may hold — secrets and per-machine values — all empty
  except safe machine defaults (`DEV_BIND=127.0.0.1`, `AUTH_MODE=external`). No `<заглушка>`, and no name a compose
  file sets. Compose never reads it.

| Marker | Means |
|---|---|
| `[required]` | `required` and no default: prod refuses to start without it — «Обязательна: да» in DEPLOY.md |
| `[secret]` | a credential or key: never a real value in git — «Секрет: да» in DEPLOY.md |

## The fail-fast rules, as a checklist for the app's own config/settings code

Write these as validation in the same place the app parses its config — not as a compose-time check, not as a
comment asking someone to remember:

1. **Env selector is required.** No default. An unset selector crashes at startup, not silently picks one
   environment's behavior.
2. **The mock gate refuses outside test.** If the mock-fixtures variable is set and the env selector is not `test`,
   crash with a message naming both values — the rule that turns «someone copied a compose file wrong» into «prod
   served fixture data» if it is missing.
3. **Security flags that assume a network topology contradict, not just default.** «Cookies require HTTPS» being true
   is not proof a TLS terminator exists — but that flag true while a paired «we are behind TLS» flag is false (or vice
   versa) is a contradiction worth crashing on, where the app can express one.
4. **No default for a prod/dev secret.** A missing required secret is a startup crash naming the variable — an empty
   string that silently «works» until the first real call fails is worse. So is one too short for its use (a signing
   or encryption key under 32 characters) or a known placeholder (`change-me`, `secret`, `admin`, `<заглушка>`).
5. **Resource-budget arithmetic, if the architecture named one.** Worker count × per-worker connection/resource usage
   ≤ the configured limit, checked at startup.
6. **An optional variable still has a type.** Unset or empty means the default; set to something outside its set —
   `LOG_LEVEL=verbose`, `SHUTDOWN_TIMEOUT_SEC=30s` — is a startup crash naming it.
7. **An unknown name is ignored, not fatal.** The parser reads only the schema's names, so an old `.env.dev.local`
   with keys a newer version dropped still starts (an upgrade never has to touch a running stand's file).

## What the application's code holds to

These reach `work`'s executors through the stack skills (`fastapi`, `typescript-fastify`), each in that stack's
terms; this list is their home. A platform that accepts the service checks each of them.

- **The first administrator** comes from variables out of a Secret, or a documented command. No default account in
  code, a migration or a config file.
- **Each integration is configured**: its URL, connect and read timeouts, its connection pool's size where it has
  one, and `<INTEGRATION>_ENABLE`. No address, IP or personal email in code or in a default.
- **TLS verification is always on.** `verify=False`, `rejectUnauthorized: false` and their kin never appear. A
  corporate CA comes as a file path: `NODE_EXTRA_CA_CERTS`, `SSL_CERT_FILE`, `<INTEGRATION>_SSL_FILE`.
- **The app sits behind a TLS-terminating proxy.** Trusted proxies come from `TRUSTED_PROXIES`, so the client's
  address and the scheme in `X-Forwarded-*` are believed only from them: the rate limit by address and the Secure
  cookie depend on it. A link the app builds for the outside uses a configured `PUBLIC_BASE_URL`.
- **Service interfaces stay off in production**: an API's generated docs and admin screens are switched off by
  config or closed by authorization. The human-readable API documentation lives in the docs site.
- **Nothing that must be shared lives in the process.** Sessions, rate-limit counters, locks, caches and queues go
  to an external store; with only one replica possible, DEPLOY.md's «Масштабирование» says so and why. A scheduled
  job takes a distributed lock (`pg_advisory_lock`, a Redis lock).

## The tests the project gets with the generator

In the project's own suite (`tests/deploy/env-doc.test.ts` or `tests/deploy/test_env_doc.py`); the templates hold
each one:

- **Drift**: the three files equal the render, and a hand edit of any one is named alone.
- **Layout**, for both files: the blocks in order, the marker line directly above each `NAME=value`, pairs split by
  one blank line, no double blank line; the root file's headers are only the file names.
- **Schema entries**: unique names; a one-line purpose; `example` and `details` filled and free of `|`; each default
  passes its own parser; every name in the root `.env.example` is in the schema or the compose-only list; the
  frontend's names are not read by the backend.
- **Compose contract** (`compose-shape.md` → The compose-contract tests): the root `.env.example` lists exactly the
  keys the `.local` files may hold; no name a compose file sets in `environment:` with a fixed value is in a `.local`
  list; each secret in the kit file is empty or `<заглушка>`; no `docker-compose.prod.yml`, prod local file or
  `env_files` anywhere.
- **The build**: `make build-images` with a failing env:check stops before Docker and writes no `release/`.
- **The test stand's file**: `make .env.test.local` creates an empty file with mode 0600 and keeps an existing one;
  `make up-dev` without `.env.dev.local` stops before Docker naming it.

## One wording in every document

Every document that speaks of variables says the same: «каждая переменная описана один раз — в схеме; env:doc
собирает из неё файл комплекта, таблицы DEPLOY.md и корневой `.env.example`; стендов два, в `.local` только секреты и
значения машины». Where:

- README (`repo-scaffold`, the «Сборка образов» and stands sections);
- architecture.md: the config section, and the file tree — `scripts/env-doc.ts` (or `env_doc.py`), `.env.example`
  «собирает env:doc; compose его не читает», `deploy/prod.env.example` «собирает env:doc, руками не править»;
- project-map.md: the `compose:` line and the variables line;
- the operations document (`operations-doc`);
- deploy.md (`deploy-doc.md`);
- the project's verify skill: it brings up the test stand only (`verify-skill.md`).
