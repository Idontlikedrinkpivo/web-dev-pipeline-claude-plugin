---
name: deploy-topology
description: >-
  Wraps a working app in docker-compose test, dev and prod files, an image
  per container (backend; SPA on unprivileged nginx), fail-fast config,
  compose-contract tests, a deploy document for the operators, and a script
  that builds the images for linux/amd64 into one tar and puts it with that
  document in a release folder for hand-over. Use after `work`
  when the user asks to containerize, write a Dockerfile or compose, set
  up environments, build images, or says «докер», «окружения», «собери
  образ». Not for CI, registries, Kubernetes or deploying.
---

# Deploy Topology

Three environments, three compose files, one image per container. The shape that
makes this safe is always the same: **what talks to what changes per
environment; what the code does never does.** The application does not
know it is in test, dev, or prod beyond reading `APP_ENV` and refusing to
start when an environment's required config is missing or contradictory.

## Scope

**USE when:**
- The app has real routes/handlers and a health check (post-`work`, or
  post-scaffold if the user only wants topology, not business code)
- The user asks to containerize the app, add `docker-compose`, or define
  test/dev/prod running modes
- An existing single dev-only compose (from `repo-scaffold`) needs to grow
  into the three-environment shape

**NOT for:**
- Choosing the stack, the framework, or the database — architecture already
  decided that
- Kubernetes manifests, secrets-manager wiring, pushing to a registry,
  deploying anywhere — images leave as a tar file with `DEPLOY.md` beside
  it (Step 8); what happens to them next is the operator's flow
- The CI workflow that runs these checks on every push/PR — `ci-pipeline`,
  once this skill's test topology and compose-contract tests exist
- Writing business logic, entities, or new endpoints
- A repo with no runnable app yet — run `repo-scaffold` first

## Inputs

| Input | Required | Source |
|---|---|---|
| A working app with a health endpoint | **yes** | `repo-scaffold` + `work` |
| External dependencies this app calls | **yes** | architecture's adapters (a database, an object store, third-party APIs) |
| Which dependencies must be mockable | **yes** | ask if not obvious: anything the app calls over the network in a test run needs a mock/fake, or the test suite becomes an integration suite that needs live credentials |
| Containers: backend, client (SPA or SSR), workers | **yes** | architecture foundation §1 (containers view) and §5 (folders) |
| Upload size and request-time NFRs | for the SPA image | the SRS NFRs through foundation §1 «Решения по NFR» — they set nginx's limits (`references/images.md`) |
| Existing compose/Dockerfile/`.env.example` | when present | read and extend in place — do not fork a parallel set of files |

If the app has no health endpoint yet, that is a `repo-scaffold` gap — say
so and stop rather than inventing one here.

## The three environments

| | **test** | **dev** | **prod** |
|---|---|---|---|
| Database | local, in this compose file | local, in this compose file | **external**, no local service |
| Object storage / queue / cache | local (e.g. SeaweedFS for S3), in this compose file | local, in this compose file | **external**, no local service |
| Third-party APIs (payment, mail, external HR/LLM/etc.) | **mocked** — fixture-backed, no network call | **real** — real credentials, real network calls | **real** |
| Port publishing | loopback or none — dev-only convenience | loopback or none | **loopback only**, behind a reverse-proxy/TLS terminator the user runs separately |
| Concurrency / worker count | matches prod's shape enough to exercise it (do not run test single-worker if prod is multi-worker, or the concurrent-path bugs only show up in prod) | same as test, for the same reason | whatever the architecture sized for real load |
| Secrets | fixture/dummy values, safe to commit as defaults | real values, **never committed** | real values, **never committed** |

The asymmetry is the whole point: **test and dev share infrastructure
shape (local DB/storage) and differ only in whether external APIs are real;
dev and prod share "real APIs" and differ only in whether the
DB/storage is local.** A compose file that collapses this into one file with
profiles usually ends up with a flag nobody remembers to set correctly for
prod. Three files that only need to be read top-to-bottom, never diffed
against each other to know what is active, are worth the duplication.

## Workflow

Before Step 1, create `documentation/plans/<version>/progress-deploy.md` per
`pipeline` → `references/progress-files.md` — Steps 1–8 as rows, `⏳ ждёт` — and post its link in
the chat. Set each row `🔄 в работе` → `✅ готово` (or `⏭ не нужно: …`) as
you go; the image build in Step 8 runs for minutes, and its row says so
while it runs. The line under the table carries the compose-contract tests
and the release folder.

### Step 1. Inventory before writing anything

List every external dependency the architecture's adapters name: the
database, any object storage / cache / queue, every third-party API. For
each one, decide:

- **Local-in-compose for test+dev, external for prod** — stateful
  infrastructure the team's own stack manages (Postgres, Redis, an
  S3-compatible store via SeaweedFS or similar — any S3-compatible image
  works; verify it pulls).
- **Mocked for test, real for dev+prod** — anything outside this team's
  infrastructure that costs money, has side effects, or needs credentials
  this repo should not hold in test (payment gateway, third-party HR/LLM
  API, outbound email).

A dependency that is neither — always real, in every environment, no local
substitute possible — is rare and worth asking about explicitly rather than
guessing.

### Step 2. Images

One image per container, the same image in all three environments.
Read `references/images.md` first: it holds the reference build the owner
accepted — the backend image, the SPA image on `nginx-unprivileged` with
the config copied from `assets/nginx/`, and what each takes from the
environment. Match it; do not add users, labels or ports it does not
have. No dev-only tooling baked in, no `--reload`/hot-reload flag in `CMD` (that belongs to a local
non-Docker dev loop, not the container). The process reads its worker/
concurrency count from the environment rather than a hardcoded flag, so
raising it later is a compose edit, not an image rebuild.

`CMD` / `ENTRYPOINT` in exec form (`["python", "-m", "app"]`), never shell
form — a shell-form process does not receive SIGTERM and is killed after
the stop timeout. The app finishes in-flight requests on SIGTERM and exits,
and it logs to stdout/stderr, never to a file inside the container. Pin the
base image to an exact tag (a digest when the project already pins
digests elsewhere); `latest` or a bare major makes two builds of the same
commit differ. Use a multi-stage build when the toolchain is not needed at
runtime.

Write or extend `.dockerignore` in the same step. It excludes every
`.env.*.local`, `.env`, `.git`, local virtualenv / `node_modules`, test
caches, and the compose files themselves. `.env.prod.local` sits in the
build context; without this file a `COPY . .` bakes real prod secrets
into an image that may later be pushed anywhere. `.env.example` may stay
in the context — it holds no secrets.

### Step 3. The mock/live gate lives in the app, not in compose

Whatever selects mock vs. real behavior for a third-party API must be a
config value the application itself validates — typically "this directory
of fixtures is set" or "this flag is on" — **and the application refuses to
honor it unless `APP_ENV=test`.** Compose merely sets the value per file;
the enforcement that a mock cannot leak into dev or prod belongs to the
same fail-fast config layer as Step 5, not to compose alone. Two ways to
leak a mock into prod: someone copies a compose file and forgets to blank
the mock directory, or someone sets it directly in `.env.prod.local`. Only
an application-level check catches both.

### Step 4. Three compose files

If `repo-scaffold` left a single `docker-compose.yml`, first
`git mv docker-compose.yml docker-compose.dev.yml` and extend it in place
(history follows the file), then update the `compose:` line in
`documentation/project-map/project-map.md` to name all three files. No bare
`docker-compose.yml` remains — `docker compose up` without `-f` should
fail rather than guess an environment.

Read `references/compose-shape.md` for the concrete shape and the
invariants each file must hold. In outline:

- `docker-compose.test.yml` — local DB + local object storage (+ their
  one-shot init/seed containers) + a one-shot `migrate` service + `backend`
  with the mock gate on (+ `frontend`, the frontend image, when the
  architecture has a client). Everything the test suite needs to run inside
  Docker with zero external network access.
- `docker-compose.dev.yml` — same local infrastructure shape as test, mock
  gate off, real third-party credentials expected from `.env.dev.local`.
- `docker-compose.prod.yml` — **no database service, no object-storage
  service**, not even commented out "in case" — that reads as an
  invitation next quarter; prod's database is external, not a toggle.
  `backend`, `migrate` (and `frontend`) only, pointed at externally managed instances
  through `.env.prod.local`. The entry port — `frontend`'s when there is a
  client, else `backend`'s — publishes on loopback only
  (`"8080:8080"` binds all interfaces and ships a plaintext port to the
  network); a reverse-proxy/TLS terminator in front is assumed and
  documented, never built into this compose file.

`migrate` is a one-shot service in every file: it runs the project's
migrate command over the SQL files in `documentation/db/migrations/`
(carried in the backend image at that same path) to completion, `backend` depends on it with
`condition: service_completed_successfully`, and the application process
itself never runs a migration on startup. This is what keeps "which
migration is live" a deployment-time fact instead of a race between however
many app replicas start first, or a schema change under a live
connection's cached type information.

### Step 5. Fail-fast config validation

The application's own config/settings layer — not compose, not a shell
script — enforces the rules that must never depend on someone remembering
to set a flag correctly. Read "The fail-fast rules" in
`references/env-and-config-contract.md` while writing this validation; it
gives each rule's failure message and why it crashes rather than defaults.

- An unset `APP_ENV` (or equivalent) refuses to start.
- The mock gate (Step 3) refuses to activate outside `APP_ENV=test`.
- A prod-only guarantee that depends on network topology (secure cookies,
  HSTS, TLS-only) refuses to start if the paired flag is not also set — one
  flag alone is not proof the terminator is actually there, but a
  contradiction (secure cookies on, TLS flag off) is proof something is
  wrong.
- Every secret and external credential prod needs has **no default** in
  code or in `docker-compose.prod.yml` — a missing one is a startup crash
  with the variable's name, not a silent fallback.
- If the architecture named a resource budget that scales with worker count
  (a connection pool, a rate limit), validate the arithmetic at startup
  against the configured limit instead of discovering the overrun at
  runtime under load.

### Step 6. Env files, not secrets in compose

Before writing any env file, sort every variable into one of the four
categories in `references/env-and-config-contract.md` — the category
decides whether it sits inline in compose or in an env file, and the same
file fixes the `DATABASE_URL` schema option for every environment.

- `.env.example` is **documentation**, never read by compose directly —
  say so in a comment at its top. It lists every variable with a one-line
  comment on what test/dev/prod each expect.
- Compose reads `.env.<environment>.local` via `env_file`, `required: true`
  for dev and prod (the stack must not silently start with defaults),
  `required: false` for test (safe fixture defaults may live inline in the
  compose file's own `environment:` block instead).
- Only test fixture values (a dummy API key, a well-known local password)
  may sit inline in compose YAML. Anything that would matter if leaked
  lives only in a gitignored `.env.<environment>.local`.
- Non-secret, environment-fixed values (log level, worker count, the mock
  gate, security flags) belong in each compose file's own `environment:`
  block, not the env file — that way the value that decides "am I in a
  safe-to-mock environment" is not something a stray `.env.*.local` edit
  can quietly override.
- Provide bootstrap targets (Makefile, `package.json` scripts, or the
  stack's task runner) that copy `.env.example` → `.env.<environment>.local`
  on first use and patch the handful of keys that differ from the template
  by convention, plus `up-<environment>` targets that bring the stack up and
  remove the exited one-shot containers so they do not linger.

### Step 7. Compose-contract tests

Encode the invariants that must never silently regress as tests in the
project's own test suite, not just as prose here:

- The prod port mapping has an explicit loopback host IP; a mapping with no
  host IP (binds all interfaces) fails the test.
- `docker-compose.prod.yml` has no local database/storage service.
- `migrate` in every file has no published port, and `backend` depends on it
  with `service_completed_successfully`.
- Every Dockerfile's `CMD` has no hot-reload flag, `CMD`/`ENTRYPOINT` is
  exec form, and every `FROM` has an explicit tag other than `latest`.
- With a client: `frontend`'s healthcheck reaches `:8081/_healthz`, its
  environment sets `BACKEND_SERVICE`, `BACKEND_PROTOCOL` and
  `SECURE_MODE`, and no `<<…>>` placeholder is left in `nginx/`.
- `scripts/build-images.sh` passes `--platform linux/amd64`, saves to
  `release/<APP_VERSION>/<project>-<APP_VERSION>.tar` and copies
  `documentation/deploy/deploy.md` beside it as `DEPLOY.md`.
- `documentation/deploy/deploy.md` agrees with `docker-compose.prod.yml`
  and `.env.example`: containers, every variable per container with its
  required and secret marks, ports, health checks, volumes — "The sync test"
  in `references/deploy-doc.md`.
- `.dockerignore` exists and matches `.env.*.local` (a build context
  that can see `.env.prod.local` fails the test).
- `backend` in every compose file has a `healthcheck` whose command reaches the
  health endpoint — it is what makes `up --wait` mean "the app answers",
  not "the container started".
- `.env.example` contains every variable the config layer requires, and no
  variable the config layer does not recognize — the two drift silently
  otherwise, in either direction. Test pattern: "The `.env.example` sync
  test" in `references/env-and-config-contract.md`.
- Setting the mock gate with `APP_ENV` other than `test` makes config
  loading fail (a config-layer test, not a compose check).

These are cheap, fast, and exist specifically so a future edit that
reopens a closed hole (an all-interfaces port publish, a mock flag with a
default) fails CI instead of shipping. Infra regressions are exactly the
class of bug nobody notices locally and everybody notices in prod, so
"it's just infra" is not a reason to skip them.

### Step 8. The release for hand-over

The operators get one folder per release and nothing else: the image
archive and `DEPLOY.md`. They do not get `docker-compose.prod.yml` — they
run the images their own way, so they need the facts it holds, written
down.

1. **Write `documentation/deploy/deploy.md`** per `references/deploy-doc.md`:
   containers with image and command, start order (migrations first, once),
   ports and health checks, variables per container (required, secret,
   format), external dependencies, volumes (or «томов нет»), the first start
   (the first admin or seed data — ask when the architecture and SRS do not
   say), and how to update to a new version. Facts come from the prod
   compose file, the Dockerfiles and `.env.example`; Step 7's sync test holds
   them together.
2. **Write `scripts/build-images.sh`** and a `build-images` target per
   `references/images.md` → Hand-over: one tag `<version>-<YYYYMMDD-HHMM>`
   for every image, `docker buildx build --platform linux/amd64 --load` per
   image, one `docker save` of all of them into
   `release/<version>/<project>-<version>.tar` (e.g.
   `release/1.4.0/room-booking-1.4.0.tar`), and a copy of
   `documentation/deploy/deploy.md` as `release/<version>/DEPLOY.md`.
   `release/` is in `.gitignore` and `.dockerignore`.
3. **Run it once** and report the folder, the tar size and the image tags;
   if Docker or buildx is not available here, say so instead of claiming the
   build. Add the «Сборка образов» section to the README.

`release/`, not `dist/`: `dist/` is the compiler's output folder, which
`clean` scripts and bundlers empty before a build — a hand-over archive kept
there can disappear with it. A folder per version keeps the previous release
beside the new one for a rollback; a rebuild of the same version replaces
its folder's contents.

## Guardrails

- **A value that departs from the architecture.** A port, a variable, a
  service name, an image or a command that turns out different from what
  `architecture.md` says (the port is taken, the user picks another name)
  is settled first — by the user, or here when the choice is this stage's
  own — and then the architecture is fixed and committed at once, with no
  version change (`pipeline` → `references/decision-changes.md`). A config
  that silently departs from the document sends the next plan building
  against the old one.
- **A one-time risky step left out of `deploy.md`.** If a cutover (new
  external DB, new external storage, a secret rotation) has an
  order-sensitive sequence where doing it wrong is destructive or leaks
  data, write that sequence into `deploy.md` as its own section rather than
  trusting it to be improvised correctly once, live.

## Before you finish

- Three compose files, each readable on its own — "The three environments".
- One Dockerfile per container, matching `references/images.md`, plus
  `.dockerignore` — Step 2.
- `documentation/deploy/deploy.md` covers every section of
  `references/deploy-doc.md` — Step 8.
- `scripts/build-images.sh` ran: `release/<version>/` holds the tar with
  every image under the `<version>-<date>` tag and `DEPLOY.md` — Step 8.
- Mock gate enforced in application config — Steps 3 and 5.
- Prod file has no local stateful service; `up-test` runs the suite with
  zero outbound network calls — Step 4.
- Bootstrap and `up-<environment>` targets for all three — Step 6.
- A passing compose-contract test for every Step 7 invariant — Step 7.

## References

- `references/images.md` — the reference images (backend, SPA on nginx),
  tag format and the tar hand-over (Steps 2 and 8).
- `references/deploy-doc.md` — what `deploy.md` holds, where each fact comes
  from, and its sync test (Steps 7 and 8).
- `assets/nginx/` — the SPA image's nginx config and templates, copied as
  they are with the `<<…>>` values filled (Step 2).
- `references/compose-shape.md` — the concrete file-by-file compose
  skeleton and the exact invariants each service must hold (Step 4).
- `references/env-and-config-contract.md` — the env-var categories, the
  fail-fast validation shape, and the `.env.example`-sync test pattern
  (Steps 5–7).
- `repo-scaffold` (skill) — the empty-skeleton stage this one follows;
  read its single dev-only compose (if any) before writing three.
- `ci-pipeline` (skill) — the consumer of `docker-compose.test.yml`: it
  wires that exact fixture shape into a workflow that runs on every push/PR.
- `pipeline` (skill) — where this stage sits. At the close, ask about the
  stage its table names after this one, per "Asking before a transition".
  Read it at the end instead of naming a next step from memory.
