# Compose shape, file by file

Contents:

- Hardened app containers — the four keys every app container carries.
- `docker-compose.test.yml` — the copyable test stand and its invariants.
- Two database accounts — `docker/db-init/roles.sql` for the test stand.
- `docker-compose.dev.yml` — the developer's stand, `.env.dev.local` required.
- What compose sets and what `.local` holds — two stands, no prod file.
- `frontend` — the frontend image, when the architecture has a client.
- Make/task-runner targets — the two `.local` files and `up-<stand>`.
- The compose-contract tests (Step 7) — each invariant a test checks, key by key.

Placeholders in `<angle brackets>`. Substitute real service/image/variable
names from the architecture; do not invent services the architecture never
named (a queue, a cache) just because this shape has room for one.

The application's services are named like its images, so one name means one
thing everywhere — compose, `BACKEND_SERVICE`, `DEPLOY.md`, the tests:
`backend` (image `<project>-backend`), `frontend` (image
`<project>-frontend`), and `migrate` (the backend image run once with the
migrate command). Not `app` / `web`.

## Hardened app containers

Every app container — `backend`, `migrate`, `frontend` — in the test file
carries the same four keys, so the test stand runs the kit's images under the
rules a restricted Kubernetes namespace enforces for the prod pod (Pod
Security Standards, `restricted`) and the operators' preflight finds nothing
new. There is no prod compose file: prod's facts live in DEPLOY.md
(`deploy-doc.md`), and the test stand is where they are proven.

```yaml
    read_only: true                  # the root filesystem; the process writes only the tmpfs below
    tmpfs:
      - /tmp
    cap_drop:
      - ALL                          # no Linux capability; the app ports are above 1024
    security_opt:
      - "no-new-privileges:true"     # no setuid escalation inside the container
```

No `user:` key: the image's numeric `USER` holds (`images.md`), and an
override here would hide a Dockerfile that runs as root; `image_preflight.py stand` runs the same file under a
foreign UID. One app image writes somewhere besides `/tmp`, with one more tmpfs: a
Next.js SSR frontend writes `/app/.next/cache`. Third-party store services
(the database, the S3 emulator, their init containers) stay as their images
ship — their vendors' images are not built for a read-only root.

## `docker-compose.test.yml`

Written to be copied from the start: a long browser run starts several
identical stands side by side (`ui-test-cases` → `references/parallel-stands.md`),
each as its own compose project — `docker compose -p <project>-e2e-2 -f
docker-compose.test.yml up` with other ports. Three things in the file decide
whether a copy is a separate stand or a second door into the first one:

- **Host ports come from variables with today's value as the default**
  (`${DB_PORT:-5432}`): a copy sets other values; a fixed port makes the copy
  fail to start, or — worse — its tests reach the first stand.
- **Volumes have no `name:`.** Compose then prefixes them with the project
  name, so every stand gets its own data. A fixed `name:` makes every copy
  share one database, and `docker compose -p <copy> down -v` deletes the main
  stand's data with the copy's.
- **The application images are named** — `image: <project>-backend:${IMAGE_TAG:-test}`
  next to `build:` — so the copies run the image built once instead of each
  building its own, and `scripts/e2e-stands.sh` starts them without a rebuild.

```yaml
name: <project>-test

services:
  <db>:                      # e.g. postgres
    image: <db-image>
    environment:
      <DB_USER>: <fixture-superuser>       # the image's superuser: runs roles.sql, no app container uses it
      <DB_PASSWORD>: <fixture-password>
      <DB_NAME>: <project>_test
    ports:
      - "127.0.0.1:${DB_PORT:-<db-port>}:<db-port>"   # host access for local test runs; drop if tests run inside compose only
    volumes:
      - db_data:<data-path-from-image-docs>   # Postgres ≤17: /var/lib/postgresql/data; 18+: /var/lib/postgresql
      - ./docker/db-init/roles.sql:/docker-entrypoint-initdb.d/10-roles.sql:ro   # the migrate and backend accounts
    healthcheck:
      test: ["CMD-SHELL", "<db-readiness-check>"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

  <object-store>:             # e.g. seaweedfs, for an S3-compatible store
    image: chrislusf/seaweedfs:<pinned-tag>   # default CMD `mini -dir=/data`: master+volume+filer+S3 in one process
    environment:
      AWS_ACCESS_KEY_ID: <fixture-access-key>       # SeaweedFS reads these as the S3 identity
      AWS_SECRET_ACCESS_KEY: <fixture-secret-key>
    ports:
      - "127.0.0.1:${S3_PORT:-8333}:8333"   # S3 API — host `make test` reaches it here; publish the admin UI too only if wanted
    volumes:
      - store_data:/data
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8333/healthz"]   # the image has wget, not curl
      interval: 5s
      timeout: 3s
      retries: 10
    restart: unless-stopped

  <object-store>-init:        # one-shot: create the bucket/queue/etc. this app expects
    image: amazon/aws-cli:<pinned-tag>
    depends_on:
      <object-store>:
        condition: service_healthy
    environment:
      AWS_ACCESS_KEY_ID: <fixture-access-key>
      AWS_SECRET_ACCESS_KEY: <fixture-secret-key>
      AWS_DEFAULT_REGION: us-east-1
    entrypoint: ["/bin/sh", "-c"]
    command:
      - >-
        aws --endpoint-url http://<object-store>:8333 s3api head-bucket --bucket <bucket>
        || aws --endpoint-url http://<object-store>:8333 s3 mb s3://<bucket>
    restart: "no"

  migrate:
    image: <project>-backend:${IMAGE_TAG:-test}   # the backend image, built once, shared by the copies
    build: .
    depends_on:
      <db>:
        condition: service_healthy
    env_file:
      - path: .env.test.local
        required: false            # optional: only secrets and machine values; an empty one runs on stubs
    environment:                   # every non-secret value of the stand; wins over env_file
      APP_ENV: test
      LOG_LEVEL: info
      DATABASE_URL: <fixture-url-as-<schema>_migrate>   # the owner: creates and changes tables
    command: <migration-command>   # the project's migrate command over documentation/db/migrations/, e.g. alembic upgrade head
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    restart: "no"

  backend:
    image: <project>-backend:${IMAGE_TAG:-test}
    build: .
    depends_on:
      migrate:
        condition: service_completed_successfully
      <object-store>-init:
        condition: service_completed_successfully
    ports:
      - "127.0.0.1:${APP_PORT:-<app-port>}:<app-port>"  # loopback only — never all interfaces
    volumes:
      - ./<mock-fixtures-dir>:/app/<mock-fixtures-dir>:ro
    env_file:
      - path: .env.test.local
        required: false
    environment:
      APP_ENV: test
      DATABASE_URL: <fixture-url-as-<schema>_backend>   # rows only — the account prod's backend gets
      LOG_LEVEL: info
      SHUTDOWN_TIMEOUT_SEC: "25"
      <MOCK_GATE_VAR>: /app/<mock-fixtures-dir>   # the ONLY compose file where this is non-empty
      <SECURITY_FLAG_REQUIRING_TLS>: "false"      # test runs over plain HTTP
      <WORKER_COUNT_VAR>: "1"                      # stacks that have one: one process per container, scale by replicas
      <THIRD_PARTY>_API_URL: ${<THIRD_PARTY>_API_URL:-http://<third-party>-stub:<port>/…}   # a machine may point it elsewhere in .env.test.local
      # <THIRD_PARTY>_API_TOKEN is never written here: a secret, from .env.test.local only
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    healthcheck:
      test: <the runtime healthcheck on /health/ready — images.md → Healthchecks through the runtime>
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    stop_grace_period: 30s         # ≥ SHUTDOWN_TIMEOUT_SEC + 5; Docker's default 10 s cuts the drain short
    restart: unless-stopped

volumes:
  db_data:        # no `name:` — compose prefixes it with the project, one per stand
  store_data:
```

**Invariants for this file:**
- Copyable: no `container_name`, no volume `name:`, no fixed host path for
  data, every published host port a `${VAR:-default}`, the application
  services carry `image:` with `${IMAGE_TAG:-test}`.
- The mock-gate variable is non-empty *only* here.
- `migrate` has no published port and `restart: "no"`.
- `backend` waits for `migrate` via `service_completed_successfully`, not a
  healthcheck-based `depends_on` (a migration is a one-shot job, not a
  service with ongoing health).
- `backend` has a `healthcheck` that asks `/health/ready` through the
  image's runtime (`node -e` / `python -c`, never `wget`/`curl`). Without
  it, `up --wait` returns as soon as the container is `running`, before the
  app listens or after it crashed on config validation; with a binary the
  image lacks, the service stays unhealthy forever.
- `backend`, `migrate` (and `frontend`) carry the four hardening keys and no
  `user:`; `backend`'s `stop_grace_period` is at least
  `SHUTDOWN_TIMEOUT_SEC` + 5 s.
- `migrate` and `backend` connect as two accounts (below).
- Every non-secret value is in `environment:`; `.env.test.local` is optional
  (`required: false`) and holds only secrets and per-machine values
  (`env-and-config-contract.md` → Where each value lives).
- The object store's S3 API port publishes on `127.0.0.1:${S3_PORT:-<api-port>}:<api-port>`
  — `make test` on the host and CI Variant A reach it there. A console/admin
  port is optional.

**Object store:** SeaweedFS is the default above (S3 API on 8333,
`/healthz` served on the same port; the image has `wget` and no `curl` —
a probe through a missing binary keeps the service unhealthy and
`up --wait` fails). Any
S3-compatible image works — verify it actually pulls (`docker pull`)
before writing it in; MinIO's Docker Hub images are gone. SeaweedFS can
also create a bucket itself from `S3_BUCKET`; the `-init` service keeps
bucket creation explicit and store-agnostic.

## Two database accounts

The operators' DBA gives `migrate` and `backend` different accounts
(`deploy-doc.md` → «Для DBA»): `migrate` owns the schema and changes it,
`backend` only reads and writes rows. Neither is a superuser there, so
neither is one on the stand: the image's superuser (`<DB_USER>`) only runs
this file, and a migration that needs a right the DBA's SQL does not give
fails here rather than at its first prod start — as does a backend that
quietly needs DDL or `TRUNCATE`. `docker/db-init/roles.sql`, which the
PostgreSQL image runs once, on an empty volume, as `<DB_USER>`:

```sql
CREATE ROLE <schema>_migrate LOGIN PASSWORD '<fixture-password>';
CREATE ROLE <schema>_backend LOGIN PASSWORD '<fixture-password>';
DO $$ BEGIN   -- CREATE on the database: 0001_init.sql's CREATE SCHEMA IF NOT EXISTS checks it first
  EXECUTE format('GRANT CREATE ON DATABASE %I TO <schema>_migrate', current_database());
END $$;
CREATE SCHEMA IF NOT EXISTS <schema> AUTHORIZATION <schema>_migrate;
GRANT USAGE ON SCHEMA <schema> TO <schema>_backend;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA <schema> TO <schema>_backend;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA <schema> TO <schema>_backend;
ALTER DEFAULT PRIVILEGES FOR ROLE <schema>_migrate IN SCHEMA <schema>
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO <schema>_backend;
ALTER DEFAULT PRIVILEGES FOR ROLE <schema>_migrate IN SCHEMA <schema>
  GRANT USAGE ON SEQUENCES TO <schema>_backend;
```

- `<schema>` is `db-schema-design` §0's. PostgreSQL checks `CREATE` on the
  database before it looks whether the schema exists, so without that grant
  `0001_init.sql`'s `CREATE SCHEMA IF NOT EXISTS` stops `migrate` with
  42501 «permission denied for database», even though the schema is there.
  `%I` quotes the database name, which may hold a hyphen.
- The `GRANT` and `ALTER DEFAULT PRIVILEGES` lines are the ones DEPLOY.md
  hands the DBA, word for word (the database grant names the database
  there); the sync test compares them.
- With `CREATE` on the database `migrate` creates trusted extensions itself
  (`citext`, `pgcrypto`). An untrusted one a migration needs (`postgis`) is
  created in this file first, by the superuser — as the DBA does in prod
  («Для DBA» lists both kinds).
- Tests run from the host (`make test`, CI) use the migrate account's URL —
  they create and truncate data; only the `backend` container uses the
  rows-only one.
- MySQL: the same two accounts — `GRANT ALL ON <db>.*` for the migrate one,
  `GRANT SELECT, INSERT, UPDATE, DELETE ON <db>.*` for the backend one.

## `docker-compose.dev.yml`

Identical infrastructure shape to test — same `<db>`, `<object-store>`,
`<object-store>-init`, `migrate` pattern, ports from variables,
`image: <project>-backend:${IMAGE_TAG:-dev}` — with exactly these
differences:

- **An existing dev file keeps its volumes as they are**: their names, any
  `name:`, and the file's top-level `name:` (absent stays absent) — compose
  prefixes volume names with the project name, so changing either moves the
  developer onto empty volumes and their data looks lost. Only a new file
  writes volumes without `name:`.

- `env_file: required: true` for `.env.dev.local` (no safe default secrets
  exist for real third-party credentials); `make up-dev` without it stops
  before Docker and names the file.
- `<MOCK_GATE_VAR>` is empty/unset — dev calls real external APIs.
- Real credentials and the addresses that differ per machine come from
  `.env.dev.local`, never hardcoded in the compose `environment:` block; the
  stand's own infrastructure passwords are substitutions with a fixture
  default — `POSTGRES_PASSWORD: ${DEV_DB_PASSWORD:-<fixture-password>}` — so a
  shared server sets its own in `.env.dev.local`.
- Ports on loopback like test; only the site's mapping takes the bind
  interface from the machine: `"${DEV_BIND:-127.0.0.1}:<frontend-port>:8080"`
  (`DEV_BIND=0.0.0.0` in `.env.dev.local` opens the dev site to the network on
  a shared server; the database, the API and the store stay on loopback).
- No hardening keys and one database account for both services: dev is
  where a developer opens a shell in a container, and its volume
  (`repo-scaffold`'s) may predate `roles.sql`, which runs only on an empty
  one. The test stand proves both.
- Everything else (worker count, local DB/storage shape, healthchecks,
  `stop_grace_period`) stays the same as test, so the two environments
  share infrastructure behavior and differ only in the mock gate.

## What compose sets and what `.local` holds

Two stands, two files: `docker-compose.test.yml` and `docker-compose.dev.yml`.
There is no `docker-compose.prod.yml` — not even «to run the prod shape
locally»: prod runs in the operators' cluster from the kit (the images,
`<project>.env.example`, DEPLOY.md), and a prod file in the repository drifted
from the kit it was meant to mirror. No `.env.prod.local`, no
`.env.prod.migrate.local`.

- **Every non-secret value of a stand is in its compose file's
  `environment:`.** `environment:` wins over `env_file`, so a value set there
  is never repeated in a `.local` file.
- **`.env.<stand>.local` holds only secrets and per-machine values**: a
  model's or API's token, the bind interface, the stand's own infrastructure
  passwords, an external service's address that differs per machine. A value
  a machine may change is a substitution with its default in compose —
  `${VAR:-default}` — and is listed for that `.local` file only.
- **An empty value is unset**: `${VAR:-default}` gives the default for an
  empty one too, and the app applies its schema's default before parsing.
- **The root `.env.example` lists what each `.local` file may hold**; the
  project's env:doc renders it from the schema, and compose never reads it
  (`env-and-config-contract.md` → The generator).
- **Every host port is on loopback** (`127.0.0.1:`), in both files; the only
  exception is the dev site's `${DEV_BIND:-127.0.0.1}`.

## `frontend` — the frontend image, when the architecture has a client

Present in both files, after `backend`. The image is the SPA image of
`images.md`; its nginx proxies `/api/` to `backend` on the compose network.

```yaml
  frontend:
    build:
      context: ./<client-folder>
    depends_on:
      backend:
        condition: service_healthy
    image: <project>-frontend:${IMAGE_TAG:-test}   # dev: ${IMAGE_TAG:-dev}
    ports:
      - "127.0.0.1:${FRONTEND_PORT:-<frontend-port>}:8080"    # the entry point; loopback only (dev: "${DEV_BIND:-127.0.0.1}:<frontend-port>:8080")
    environment:                        # image with a shell; the shell-less image has these fixed at build
      BACKEND_SERVICE: backend:<app-port>
      BACKEND_PROTOCOL: http
      SECURE_MODE: plain                # the prod pod: plain behind the operator's TLS terminator, or secure (DEPLOY.md)
      LOG_LEVEL: notice
      TRUSTED_PROXY_CIDR: 127.0.0.1/32  # the prod pod: the network of the proxy in front (DEPLOY.md)
      # MAX_BODY_SIZE, CLIENT_TIMEOUT, BACKEND_TIMEOUT: the image's defaults from the NFRs; the kit file names them
    read_only: true                     # test; dev has no hardening
    tmpfs:
      - /tmp                            # the only path it writes: the rendered config lives here too
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    healthcheck:                        # image with a shell; the shell-less image has none
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8081/_healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
```

**Invariants with a client:**
- `frontend` waits for `backend` to be healthy, so `up --wait` means the whole stand works; the frontend itself
  starts without a backend (`images.md`), and a cluster needs no such order.
- The browser reaches the API through `frontend`'s `/api/` on the same
  origin, and the backend's `/health/*` and `/metrics` are not reachable
  through it — DEPLOY.md gives the prod pod only `frontend`'s entry. On the
  stands `backend` may keep its loopback port for direct API checks.
- `frontend`'s healthcheck (image with a shell) uses the 8081 health port,
  not a page of the app.

## Make/task-runner targets (any task runner, this shape)

```make
# The stands read only secrets and per-machine values from the .local files; every other value is in the compose
# file. .env.test.local is optional (an empty one is created for --env-file); .env.dev.local must exist.
# What each may hold: .env.example.
.env.test.local:
	@(umask 077 && : > .env.test.local)
	@echo "test: created an empty .env.test.local; secrets go there (what it may hold: .env.example)"

.env.dev.local:
	@echo "dev: create .env.dev.local first (what it may hold: .env.example)" >&2
	@exit 1

up-test: .env.test.local
	docker compose --env-file .env.test.local -f docker-compose.test.yml up --build --wait --remove-orphans
	docker compose --env-file .env.test.local -f docker-compose.test.yml rm -f migrate <object-store>-init

up-dev: .env.dev.local
	docker compose --env-file .env.dev.local -f docker-compose.dev.yml up --build --wait --remove-orphans
	docker compose --env-file .env.dev.local -f docker-compose.dev.yml rm -f migrate <object-store>-init

build-images:
	scripts/build-images.sh
```

- Every `docker compose` call carries `--env-file .env.<stand>.local -f
  docker-compose.<stand>.yml`: the `${VAR:-default}` substitutions read the
  same file the containers' `env_file` does.
- No `env`, `env-test`, `env-dev`, `env-prod` or `up-prod` target, and no
  target that writes a `.local` file's contents: a person fills
  `.env.dev.local` by `.env.example`, and env:doc writes only files in git.
- A stand server updates by `git pull --ff-only` and
  `docker compose --env-file .env.<stand>.local -f docker-compose.<stand>.yml up -d --build`;
  never by running the env generator there.

One-shot containers (`migrate`, `<object-store>-init`) stay declared in the
compose file — they are part of the topology's contract — but the
`up-<stand>` target removes their exited containers immediately after a
successful `--wait`, so they do not linger visibly next to the long-running
services.

## The compose-contract tests (Step 7)

One test in the project's own suite per invariant below, so a future edit that reopens a closed hole fails
CI instead of shipping:

- Every port mapping in both files has an explicit loopback host IP; the
  only exception is the dev site's `"${DEV_BIND:-127.0.0.1}:<frontend-port>:8080"`.
  A mapping with no host IP (binds all interfaces) fails the test.
- Two stands and no prod: no `docker-compose.prod.yml`, no `up-prod`, `env`
  or `env-*` target, and no `.env.prod.local`, `.env.prod.migrate.local`,
  `docker-compose.prod` or `env_files.py` named in the Makefile, the compose
  files, `.env.example` or the scripts.
- Every `docker compose` call in the Makefile carries `--env-file
  .env.<stand>.local -f docker-compose.<stand>.yml`; no compose file reads
  `.env.example`.
- `migrate` in every file has no published port, and `backend` depends on it
  with `service_completed_successfully`.
- `docker-compose.test.yml` is copyable: no `container_name`, no volume
  `name:`, every published host port a `${VAR:-default}`, `image:` on the
  application services.
- Every Dockerfile's `CMD` has no hot-reload flag, `CMD`/`ENTRYPOINT` is
  exec form, every `FROM` has an explicit tag other than `latest` or a
  digest, and the final stage's `USER` is a number other than 0.
- Every app service in the test file has `read_only: true`,
  `/tmp` in `tmpfs`, `ALL` in `cap_drop`, `no-new-privileges:true` in
  `security_opt`, and no `user:`; `migrate` and `backend` have
  different `DATABASE_URL`s, neither with the database image's superuser.
- With a client: no `<<…>>` placeholder is left in `nginx/`, and its only
  uncommented `proxy_pass` is under `location /api/` (the backend's
  `/health/*` and `/metrics` stay off the entry point), that `proxy_pass` names a variable, and no `upstream {`
  block is left: a name resolved once at the start kills the container when the backend is not up. With a shell,
  `frontend`'s healthcheck reaches `:8081/_healthz` and its environment
  sets `BACKEND_SERVICE`, `BACKEND_PROTOCOL`, `SECURE_MODE`, `LOG_LEVEL` and `TRUSTED_PROXY_CIDR`, its Dockerfile
  sets `NGINX_ENVSUBST_OUTPUT_DIR=/tmp` and the defaults of `MAX_BODY_SIZE`, `CLIENT_TIMEOUT` and `BACKEND_TIMEOUT`,
  and `/etc/nginx/conf.d` is in no `tmpfs`; without
  one, it has neither and its Dockerfile renders the templates at build.
- `scripts/build-images.sh` runs the project's env:check before its first
  `docker` call and before it copies `deploy/prod.env.example`, passes `--platform "$PLATFORM"` and both `--build-arg`s, saves to
  `release/<APP_VERSION>/<project>-<APP_VERSION>.tar`, and puts
  `DEPLOY.md`, `<project>.env.example`, `openapi.yaml` (bundled when
  the contract is split) and `build/` beside it.
- Every Dockerfile's final stage sets `APP_VERSION` and `CI_COMMIT_SHORT_SHA` from build arguments.
- `documentation/deploy/deploy.md` agrees with the schema (its variables
  tables are env:doc's render), the kit file `deploy/prod.env.example` and
  the test stand's kit containers — the services with a `build:` target:
  containers, ports, probes, volumes, the allowed values of a variable that
  has a fixed set (`SECURE_MODE`: `plain` or `secure`), and every file it
  names is one the release folder holds; its card, «Для DBA», «Остановка» and
  «Безопасность пода» agree with the build script, the Dockerfiles, the
  migrations, `roles.sql` and the config layer — "The sync test" in
  `references/deploy-doc.md`.
- `.dockerignore` exists and holds `images.md` → `.dockerignore`: `.env`, `.env.*`, `docker-compose*.yml`,
  `Dockerfile*`, `.git`, tests and keys (a build context that can see `.env.dev.local` or a `.pem` fails the
  test), with no exception for `.env.example`.
- `backend` in every compose file has a `healthcheck` that asks
  `/health/ready` through the runtime (`node`/`python`, not `wget`/`curl`) —
  it is what makes `up --wait` mean "the app can serve", not "the container
  started" — and a `stop_grace_period` of at least `SHUTDOWN_TIMEOUT_SEC` + 5 s.
- The env tests of `env-and-config-contract.md` → The tests the project gets
  with the generator — drift of the three rendered files, their layout, the
  schema entries, the root `.env.example` listing exactly the `.local` keys,
  no `environment:` value repeated in a `.local` list, each kit secret empty
  or `<заглушка>`, `make build-images` stopping before Docker on a failed
  env:check, `make .env.test.local` creating an empty 0600 file. The code is
  `env-doc-typescript.md` or `env-doc-python.md`.
- Setting the mock gate with `APP_ENV` other than `test` makes config
  loading fail (a config-layer test, not a compose check).
