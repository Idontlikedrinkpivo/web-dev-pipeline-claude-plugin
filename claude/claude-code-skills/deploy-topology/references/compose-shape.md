# Compose shape, file by file

Placeholders in `<angle brackets>`. Substitute real service/image/variable
names from the architecture; do not invent services the architecture never
named (a queue, a cache) just because this shape has room for one.

## `docker-compose.test.yml`

```yaml
name: <project>-test

services:
  <db>:                      # e.g. postgres
    image: <db-image>
    environment:
      <DB_USER>: <fixture-user>
      <DB_PASSWORD>: <fixture-password>
      <DB_NAME>: <project>_test
    ports:
      - "127.0.0.1:<db-port>:<db-port>"   # host access for local test runs; drop if tests run inside compose only
    volumes:
      - db_data:<data-path-from-image-docs>   # Postgres ≤17: /var/lib/postgresql/data; 18+: /var/lib/postgresql
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
      - "127.0.0.1:8333:8333"   # S3 API — host `make test` reaches it here; publish the admin UI too only if wanted
    volumes:
      - store_data:/data
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8333/healthz"]
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
    build: .
    depends_on:
      <db>:
        condition: service_healthy
    env_file:
      - path: .env.test.local
        required: false            # test has safe fixture defaults inline below
    environment:
      APP_ENV: test
      DATABASE_URL: <fixture-connection-string-pointing-at-db-service>
    command: <migration-command>   # the project's migrate command over documentation/db/migrations/, e.g. alembic upgrade head
    restart: "no"

  app:
    build: .
    depends_on:
      migrate:
        condition: service_completed_successfully
      <object-store>-init:
        condition: service_completed_successfully
    ports:
      - "127.0.0.1:<app-port>:<app-port>"  # loopback only — never all interfaces
    volumes:
      - ./<mock-fixtures-dir>:/app/<mock-fixtures-dir>:ro
    env_file:
      - path: .env.test.local
        required: false
    environment:
      APP_ENV: test
      DATABASE_URL: <fixture-connection-string>
      <MOCK_GATE_VAR>: /app/<mock-fixtures-dir>   # the ONLY compose file where this is non-empty
      <SECURITY_FLAG_REQUIRING_TLS>: "false"      # test runs over plain HTTP
      <WORKER_COUNT_VAR>: "<N>"                    # matches dev; exercises concurrency paths
    healthcheck:
      test: ["CMD", "<http-probe>", "http://127.0.0.1:<app-port>/<health-path>"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    restart: unless-stopped

volumes:
  db_data:
    name: <project>_test_dbdata
  store_data:
    name: <project>_test_storedata
```

**Invariants for this file:**
- The mock-gate variable is non-empty *only* here.
- `migrate` has no published port and `restart: "no"`.
- `app` waits for `migrate` via `service_completed_successfully`, not a
  healthcheck-based `depends_on` (a migration is a one-shot job, not a
  service with ongoing health).
- `app` has a `healthcheck` that calls the health endpoint. Without it,
  `up --wait` returns as soon as the container is `running`, before the
  app listens or after it crashed on config validation. `<http-probe>` is
  a binary that exists in the image (`curl`, `wget`, or the app's own
  health CLI); a probe the image lacks makes the service permanently
  unhealthy.
- The object store's S3 API port publishes on `127.0.0.1:<api-port>:<api-port>`
  — `make test` on the host and CI Variant A reach it there. A console/admin
  port is optional.

**Object store:** SeaweedFS is the default above (S3 API on 8333,
`/healthz` served on the same port, `curl` present in the image). Any
S3-compatible image works — verify it actually pulls (`docker pull`)
before writing it in; MinIO's Docker Hub images are gone. SeaweedFS can
also create a bucket itself from `S3_BUCKET`; the `-init` service keeps
bucket creation explicit and store-agnostic.

## `docker-compose.dev.yml`

Identical infrastructure shape to test — same `<db>`, `<object-store>`,
`<object-store>-init`, `migrate` pattern — with exactly these differences:

- `env_file: required: true` for `.env.dev.local` (no safe default secrets
  exist for real third-party credentials).
- `<MOCK_GATE_VAR>` is empty/unset — dev calls real external APIs.
- Real credentials for external services come from `.env.dev.local`, never
  hardcoded in the compose `environment:` block.
- Everything else (worker count, local DB/storage shape, healthchecks) stays
  the same as test, so the two environments genuinely share infrastructure
  behavior and differ only in the mock gate.

## `docker-compose.prod.yml`

```yaml
services:
  app:
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
      - path: .env.prod.local
        required: true
    environment:
      APP_ENV: prod
      <SECURITY_FLAG_REQUIRING_TLS>: "true"
      <MOCK_GATE_VAR>: ""          # always blank; the app also refuses it outside test
      <WORKER_COUNT_VAR>: "<sized-by-architecture>"
    healthcheck:
      test: ["CMD", "<http-probe>", "http://127.0.0.1:<app-port>/<health-path>"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    restart: unless-stopped

  migrate:
    image: <project>-backend:${IMAGE_TAG:?set IMAGE_TAG to the tag loaded from the tar}
    build: .
    # No depends_on on a local database — there is none. DATABASE_URL in
    # .env.prod.local points at the externally managed instance, assumed
    # reachable before this stack comes up.
    env_file:
      - path: .env.prod.local
        required: true
    environment:
      APP_ENV: prod
    command: <migration-command>
    restart: "no"
```

**Invariants for this file:**
- No `<db>` service, no `<object-store>` service, no `<object-store>-init`
  service — every stateful dependency is external.
- `app`'s port mapping always has an explicit host IP (`127.0.0.1` or
  `::1`); a bare `"<port>:<port>"` binds all interfaces and is a regression.
- `migrate` has no `depends_on` (nothing local to wait for) and no
  published port.
- `app` keeps the same `healthcheck` as in test and dev.
- No secret has a default value anywhere in this file.

## `web` — the frontend image, when the architecture has a client

Present in all three files, after `app`. The image is the SPA image of
`images.md`; its nginx proxies `/api/` to `app` on the compose network.

```yaml
  web:
    build:
      context: ./<client-folder>
    depends_on:
      app:
        condition: service_healthy
    ports:
      - "127.0.0.1:<web-port>:8080"    # the entry point; loopback only
    environment:
      BACKEND_SERVICE: app:<app-port>
      BACKEND_PROTOCOL: http
      SECURE_MODE: plain                # prod: plain behind the operator's TLS terminator, or secure + certs below
    # prod with SECURE_MODE=secure only:
    # volumes:
    #   - ${TLS_CERT_DIR}:/etc/nginx/ssl:ro    # fullchain.pem, privkey.pem
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8081/_healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
```

**Invariants with a client:**
- `web` waits for `app` to be healthy, not merely started.
- In prod only `web` publishes a port (loopback); `app` publishes none —
  the browser reaches the API through `/api/` on the same origin. In test
  and dev `app` may keep its loopback port for direct API checks.
- `web`'s healthcheck uses the 8081 health port, not a page of the app.
- prod's `image:` names are the hand-over tags —
  `<project>-backend:${IMAGE_TAG}` on `app` and `migrate`,
  `<project>-frontend:${IMAGE_TAG}` on `web` — so the file runs the images
  loaded from the tar; `IMAGE_TAG` is required, `build:` stays for local
  builds.

## Make/task-runner targets (any task runner, this shape)

```
up-test:   build + start docker-compose.test.yml, --wait, then remove exited one-shot containers (migrate, <object-store>-init)
up-dev:    same, docker-compose.dev.yml
up-prod:   same, docker-compose.prod.yml (removes only migrate; no <object-store>-init in prod)

env-test:  copy .env.example -> .env.test.local if absent, patch known test-safe keys
env-dev:   copy .env.example -> .env.dev.local if absent, patch known dev-shape keys, remind to fill real credentials
env-prod:  copy .env.example -> .env.prod.local if absent, patch known prod-shape keys, remind to fill real secrets
```

One-shot containers (`migrate`, `<object-store>-init`) stay declared in the
compose file — they are part of the topology's contract — but the
`up-<env>` target removes their exited containers immediately after a
successful `--wait`, so they do not linger visibly next to the long-running
services.
