# Compose shape, file by file

Placeholders in `<angle brackets>`. Substitute real service/image/variable
names from the architecture; do not invent services the architecture never
named (a queue, a cache) just because this shape has room for one.

The application's services are named like its images, so one name means one
thing everywhere — compose, `BACKEND_SERVICE`, `DEPLOY.md`, the tests:
`backend` (image `<project>-backend`), `frontend` (image
`<project>-frontend`), and `migrate` (the backend image run once with the
migrate command). Not `app` / `web`.

## Hardened app containers

Every app container — `backend`, `migrate`, `frontend` — in the test and
prod files carries the same four keys, so the test stand runs under the
rules a restricted Kubernetes namespace enforces (Pod Security Standards,
`restricted`) and the operators' preflight finds nothing new:

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
override here would hide a Dockerfile that runs as root. Two app images
write somewhere besides `/tmp`, each with one more tmpfs: nginx with a
shell renders its templates into `/etc/nginx/conf.d` at start, and a
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
        required: false            # test has safe fixture defaults inline below
    environment:
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
  exist for real third-party credentials).
- `<MOCK_GATE_VAR>` is empty/unset — dev calls real external APIs.
- Real credentials for external services come from `.env.dev.local`, never
  hardcoded in the compose `environment:` block.
- No hardening keys and one database account for both services: dev is
  where a developer opens a shell in a container, and its volume
  (`repo-scaffold`'s) may predate `roles.sql`, which runs only on an empty
  one. The test stand proves both.
- Everything else (worker count, local DB/storage shape, healthchecks,
  `stop_grace_period`) stays the same as test, so the two environments
  share infrastructure behavior and differ only in the mock gate.

## `docker-compose.prod.yml`

```yaml
services:
  backend:
    image: <project>-backend:${IMAGE_TAG:?set IMAGE_TAG to the tag loaded from the tar}
    build: .
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      # Explicit loopback binding — a TLS terminator (reverse proxy) in front
      # is a prerequisite documented separately, not part of this file.
      - "127.0.0.1:<app-port>:<app-port>"
    env_file:
      - path: .env.prod.local        # DATABASE_URL here is the backend account (rows only)
        required: true
    environment:
      APP_ENV: prod
      LOG_LEVEL: info
      SHUTDOWN_TIMEOUT_SEC: "25"
      <SECURITY_FLAG_REQUIRING_TLS>: "true"
      <MOCK_GATE_VAR>: ""          # always blank; the app also refuses it outside test
      <WORKER_COUNT_VAR>: "1"
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    healthcheck:
      test: <the same runtime healthcheck on /health/ready as test>
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    stop_grace_period: 30s
    restart: unless-stopped

  migrate:
    image: <project>-backend:${IMAGE_TAG:?set IMAGE_TAG to the tag loaded from the tar}
    build: .
    # No depends_on on a local database — there is none. DATABASE_URL points
    # at the externally managed instance, assumed reachable before this
    # stack comes up.
    env_file:
      - path: .env.prod.local
        required: true
      - path: .env.prod.migrate.local   # only DATABASE_URL, the migrate account (schema owner); the later file wins
        required: true
    environment:
      APP_ENV: prod
      LOG_LEVEL: info
    command: <migration-command>
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    restart: "no"
```

**Invariants for this file:**
- No `<db>` service, no `<object-store>` service, no `<object-store>-init`
  service — every stateful dependency is external.
- `backend`'s port mapping always has an explicit host IP (`127.0.0.1` or
  `::1`); a bare `"<port>:<port>"` binds all interfaces and is a regression.
- `migrate` has no `depends_on` (nothing local to wait for) and no
  published port; its `DATABASE_URL` comes from its own file, so the two
  containers run as the two accounts «Для DBA» names.
- `backend` keeps the same `healthcheck` and `stop_grace_period` as in
  test; every app service carries the four hardening keys and no `user:`.
- No secret has a default value anywhere in this file.

## `frontend` — the frontend image, when the architecture has a client

Present in all three files, after `backend`. The image is the SPA image of
`images.md`; its nginx proxies `/api/` to `backend` on the compose network.

```yaml
  frontend:
    build:
      context: ./<client-folder>
    depends_on:
      backend:
        condition: service_healthy
    image: <project>-frontend:${IMAGE_TAG:-test}   # dev: ${IMAGE_TAG:-dev}; prod: the hand-over tag, required
    ports:
      - "127.0.0.1:${FRONTEND_PORT:-<frontend-port>}:8080"    # the entry point; loopback only
    environment:                        # image with a shell; the shell-less image has these fixed at build
      BACKEND_SERVICE: backend:<app-port>
      BACKEND_PROTOCOL: http
      SECURE_MODE: plain                # prod: plain behind the operator's TLS terminator, or secure + certs below
    # prod with SECURE_MODE=secure only:
    # volumes:
    #   - ${TLS_CERT_DIR}:/etc/nginx/ssl:ro    # fullchain.pem, privkey.pem
    read_only: true                     # test and prod
    tmpfs:
      - /tmp
      - /etc/nginx/conf.d               # templates rendered at start; the shell-less image needs only /tmp
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
- `frontend` waits for `backend` to be healthy, not merely started.
- In prod only `frontend` publishes a port (loopback); `backend` publishes none —
  the browser reaches the API through `/api/` on the same origin, and the
  backend's `/health/*` and `/metrics` are not reachable through it. In test
  and dev `backend` may keep its loopback port for direct API checks.
- `frontend`'s healthcheck (image with a shell) uses the 8081 health port,
  not a page of the app.
- prod's `image:` names are the hand-over tags —
  `<project>-backend:${IMAGE_TAG}` on `backend` and `migrate`,
  `<project>-frontend:${IMAGE_TAG}` on `frontend` — so the file runs the images
  loaded from the tar; `IMAGE_TAG` is required, `build:` stays for local
  builds.

## Make/task-runner targets (any task runner, this shape)

```
up-test:   build + start docker-compose.test.yml, --wait, then remove exited one-shot containers (migrate, <object-store>-init)
up-dev:    same, docker-compose.dev.yml
up-prod:   same, docker-compose.prod.yml (removes only migrate; no <object-store>-init in prod)

env-test:  copy .env.example -> .env.test.local if absent, patch known test-safe keys
env-dev:   copy .env.example -> .env.dev.local if absent, patch known dev-shape keys, remind to fill real credentials
env-prod:  copy .env.example -> .env.prod.local if absent, patch known prod-shape keys, create .env.prod.migrate.local
           with an empty DATABASE_URL, remind to fill real secrets and both accounts
```

One-shot containers (`migrate`, `<object-store>-init`) stay declared in the
compose file — they are part of the topology's contract — but the
`up-<env>` target removes their exited containers immediately after a
successful `--wait`, so they do not linger visibly next to the long-running
services.
