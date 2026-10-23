# Images: what each container's image holds and how they are handed over

Read this at Step 2 and Step 8. The rules reproduce a reference build the
owner accepted: an SPA frontend on unprivileged nginx and a Node backend,
handed over as one tar. Match it; do not "improve" it with extra labels or
ports. The additions are the ones the owner asked for: the tag carries the
app version and the build date, nginx's upload size and timeouts come from
the SRS NFRs, the backend image carries the SQL migrations from
`documentation/db/migrations/` (the reference copied a code-tree folder,
`src/db/migrations`; migrations no longer live in the code tree), and —
for a Kubernetes platform's preflight — a numeric non-root `USER`, a root
filesystem the process never writes, healthchecks through the image's own
runtime, and a variant without a shell when the project chose one.

## Which images

One image per container of the architecture (foundation §1 «Состав
системы», the containers view). The project's answer to the shell question
(below) picks the column; both run as a numeric non-root UID:

| Container | Image | With a shell | Without a shell | UID |
|---|---|---|---|---|
| Backend API (and its `migrate` one-shot — same image, other command), TypeScript | `<project>-backend` | `node:<pinned>-alpine` | `gcr.io/distroless/nodejs<major>-debian<N>:nonroot`, built on `node:<pinned>-<codename>-slim` of the same Debian branch | 1000 / 65532 |
| Backend API, Python | `<project>-backend` | `python:<pinned>-slim` | `gcr.io/distroless/cc-debian<N>:nonroot` with a uv-managed CPython from a build stage on the same branch | 10001 / 65532 |
| SPA client (React + Vite) | `<project>-frontend` | `nginxinc/nginx-unprivileged:<version>-alpine-slim` | an nginx image with no shell, by digest (e.g. `cgr.dev/chainguard/nginx`) | 101 / 65532 |
| SSR client (Next.js) | `<project>-frontend` | `node:<pinned>-alpine` with `output: "standalone"`, shaped like the backend; no nginx | the backend's distroless Node shape | 1000 / 65532 |

No client in the architecture → only the backend image. `<project>` is the
kebab-case project name. Base references are exact — a version tag, or a
digest where the vendor publishes only moving tags — never `latest` alone
or a bare major (Step 2).

The UID is a number in the Dockerfile's last `USER` line: Kubernetes'
`runAsNonRoot` can verify only a numeric user, so `USER node` or
`USER nonroot` fails the platform's check even though it is not root.

## Shell or no shell — asked once per project

An image without a shell holds the runtime and the app only: no `sh`, no
package manager, no `wget`/`curl`. Scanners find less in it, and some
platforms accept nothing else; the cost is that nobody can `docker exec …
sh` into it. The app behaves the same either way.

Before asking, look for the answer: the «Образ» row of «Карточка сервиса»
in `documentation/deploy/deploy.md`, else the base of existing Dockerfiles,
else the progress file's Step 2 row of an interrupted run. Found — reuse it
without asking. Not found — ask once, the first time this stage writes
Dockerfiles, per `pipeline` → `references/question-format.md`:

```text
**Вопрос 1. Образы с оболочкой или без**

В образе без оболочки нет `sh`, утилит и пакетного менеджера: зайти в
контейнер командой `docker exec … sh` нельзя, зато сканер находит в нём
меньше уязвимостей, а платформы с правилом «образ без оболочки» его
принимают. Приложение работает одинаково (`distroless` — образ только с
рантаймом: Node или Python, без утилит ОС).

  A. Без оболочки — distroless; проверки делает сам рантайм или кластер.
  B. С оболочкой — alpine / slim; тоже без root и с защитой контейнера.

Рекомендую A: <платформа, куда уходит сервис, требует образ без оболочки>.

Ответьте сообщением: буква или свой текст.
```

«(рекомендую)» goes on A, with that reason, when the user or their
platform's requirements say images go to a platform with such a rule;
otherwise say any answer is fine. Write the answer into the progress
file's Step 2 row at once («Образ: без оболочки»), and into the card in
Step 8 («Образ: без оболочки» | «Образ: с оболочкой»).

## Checking a tag

Every base reference is checked against its registry before it goes into a
Dockerfile — never written from memory or from another project:

```bash
docker buildx imagetools inspect node:<version>-alpine
docker buildx imagetools inspect gcr.io/distroless/nodejs<major>-debian<N>:nonroot
```

- The tag exists, and its manifest list holds the card's architecture
  (`linux/amd64`, or `linux/arm64`).
- A moving tag — distroless publishes no patch tags; some vendors give only
  `latest` for free — is pinned by the `Digest:` line it prints:
  `FROM gcr.io/distroless/nodejs22-debian13:nonroot@sha256:<digest>`. A
  digest is immutable, so two builds of one commit still match.
- **Distroless: the newest Debian branch.** `debian<N>` is the highest `N`
  the registry has for this runtime and the card's architecture (2026-10:
  `debian13`). An older branch keeps fixes later or never: on 2026-10-23
  `nodejs22-debian12` carried a CRITICAL in `libssl3` that Debian had
  fixed, which stops every hand-over at Step 8.5, while `nodejs22-debian13`
  had no HIGH or CRITICAL. The build stage sits on the same branch
  (`node:<pinned>-trixie-slim` for `debian13`, `bookworm` for `debian12`)
  so native modules link against the glibc the runtime has.
- The Node major of a distroless runtime equals the build stage's: native
  modules are compiled for that ABI.
- After the first build: `docker image inspect --format '{{.Config.User}}
  {{json .Config.Entrypoint}} {{json .Config.Cmd}}' <image>:<tag>` — the
  user is the number the card names, and the entrypoint is what `CMD`, the
  healthcheck and the `migrate` command assume.

No access to the registry here: say so and leave the placeholder for the
user rather than a remembered tag.

## A vulnerable base (Step 8.5)

The scan finds a CRITICAL in a package of the base image, and a fixed
version exists. First try what changes nothing in the app: a fresh digest
of the same tag, then the newest Debian branch (distroless) or a newer
patch tag; rebuild and rescan. Still there — the hand-over stops with one
question per `pipeline` → `references/question-format.md`. Its text is the
same whether Step 8 runs in this stage or inside `upgrade-code`, which has
no audit question of its own to share:

```text
**Вопрос 1. Критическая уязвимость в базовом образе**

Сканер нашёл в образе `<project>-backend` критическую уязвимость
`<CVE>` в пакете `<пакет> <версия>`: исправление вышло (`<версия>`), а в
базовом образе `<база>` его ещё нет. Платформа может не принять такой
образ на проверке перед установкой.

  A. Перейти на базу `<чистая база>` и пересобрать — сканер её проверил.
  B. Подождать исправленную базу — комплект не передаём, пока сканер не чист.
  C. Передать как есть — риск записывается в «Принятый риск» с датой.

Рекомендую A: <почему>.

Ответьте сообщением: буква или свой текст.
```

A appears only when the tries above found a clean base. C goes into
«Принятый риск» of `documentation/plans/<version>/security-audit.md`, or
into the closing report when there is no audit.

## Backend image — with a shell (TypeScript)

```dockerfile
FROM node:<pinned>-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build                                  # → /app/dist

FROM node:<pinned>-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
COPY documentation/db/migrations ./documentation/db/migrations   # same repo-relative path the runner reads
USER 1000                                          # the image's `node` user, by number
EXPOSE 3000
CMD ["node", "dist/<entry>.js"]
```

- `dist/<entry>.js` is the build output of the one file that calls
  `listen` — `src/index.ts` → `dist/src/index.js` or `dist/index.js`,
  by the tsconfig's `rootDir`/`outDir`; the manifest's `start` script
  names it. The `migrate` command is the build output of the migrate
  script the same way. Read both from the project, never from this page.
- Two stages: the build stage has the TypeScript toolchain; the runtime
  stage installs production dependencies only (`npm ci --omit=dev`, the
  manifest copied before the code so the dependency layer is cached) and
  copies the compiled `dist`.
- Files stay root-owned and the process runs as 1000: it can read its code
  and cannot change it. It writes nothing but `/tmp`, which compose and
  the cluster mount as a tmpfs / `emptyDir` over a read-only root.
- The SQL migrations travel inside the image: `documentation/db/migrations/`
  is copied to the same relative path under `WORKDIR`, because the
  project's migrate command reads it by that path (`repo-scaffold` §4). The
  build context therefore includes that folder — the repo root, not a
  backend subfolder — and `.dockerignore` does not exclude it. The
  `migrate` service runs this same image with the migrate command; the app
  process never migrates on start (Step 4).
- `EXPOSE` the app port, `CMD` in exec form, so the process is PID 1 and
  gets SIGTERM itself (the entry point handles it — graceful shutdown in
  `SHUTDOWN_TIMEOUT_SEC`). The entrypoint is the base image's.

## Backend image — with a shell (Python)

```dockerfile
FROM python:<pinned>-slim AS build
COPY --from=ghcr.io/astral-sh/uv:<pinned> /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev

FROM python:<pinned>-slim
WORKDIR /app
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /app/.venv ./.venv
COPY --from=build /app/<source-dir> ./<source-dir>          # and the migrate tool's config, e.g. alembic.ini
COPY documentation/db/migrations ./documentation/db/migrations
USER 10001
EXPOSE 8000
CMD ["python", "-m", "<package>.bootstrap.serve"]
```

- The system user is created in the runtime stage, so its UID is fixed
  at 10001 rather than whatever `useradd` picks next.
- `PYTHONDONTWRITEBYTECODE=1`: the root filesystem is read-only, so the
  interpreter must not try to write `__pycache__`; `UV_COMPILE_BYTECODE=1`
  compiles it at build time instead, which also shortens the start.
- `CMD` is the stack's production entry (`fastapi` →
  `references/service-endpoints.md`: JSON logging configured first, then
  uvicorn with `SHUTDOWN_TIMEOUT_SEC` as its graceful timeout) — not
  `fastapi run`, never `--reload`.
- **Workers.** One worker process per container; scale by replicas, not
  workers. An app the architecture runs with several workers needs
  `prometheus_client`'s multiprocess mode, its directory
  (`PROMETHEUS_MULTIPROC_DIR`) on a tmpfs such as `/tmp` — `fastapi` says how.

## Backend image — without a shell

TypeScript:

```dockerfile
FROM node:<pinned>-<codename>-slim AS build       # the runtime's Debian branch (trixie = 13): same glibc for native modules
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev           # → /app/dist and production-only node_modules

FROM gcr.io/distroless/nodejs<major>-debian<N>:nonroot@sha256:<digest>
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY documentation/db/migrations ./documentation/db/migrations
USER 65532
EXPOSE 3000
CMD ["dist/<entry>.js"]                            # the entrypoint is node itself
```

The entrypoint is the node binary (`/nodejs/bin/node` — confirm with
`docker image inspect`), so `CMD` and the `migrate` service's `command:`
are node's arguments (`["dist/<migrate-entry>.js"]`), and the compose
healthcheck calls node by that full path: `node` is not on the image's
`PATH`.

Python:

```dockerfile
FROM debian:<codename>-<pinned>-slim AS build      # the runtime's Debian branch (trixie = 13)
COPY --from=ghcr.io/astral-sh/uv:<pinned> /uv /bin/uv
ENV UV_PYTHON_INSTALL_DIR=/python UV_PYTHON_PREFERENCE=only-managed \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv python install <python-version>            # the project's .python-version / requires-python
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev --no-editable

FROM gcr.io/distroless/cc-debian<N>:nonroot@sha256:<digest>
COPY --from=build /python /python                 # same path: the venv's interpreter link points here
WORKDIR /app
COPY --from=build /app/.venv ./.venv
COPY --from=build /app/<source-dir> ./<source-dir>
COPY documentation/db/migrations ./documentation/db/migrations
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1
USER 65532
EXPOSE 8000
CMD ["/app/.venv/bin/python", "-m", "<package>.bootstrap.serve"]
```

`cc` carries glibc and libgcc, which the uv-managed standalone CPython
needs; the interpreter is copied to the same path it was installed at, so
the venv's links resolve. When the stack skill documents another minimal
Python image, use that instead.

## Healthchecks through the runtime

The compose healthcheck of `backend` asks `/health/ready` with the
image's own runtime — never `wget` or `curl`, which a minimal image does
not have (and an image without them would stay unhealthy forever):

| Image | `healthcheck.test` |
|---|---|
| Node (alpine) | `["CMD", "node", "-e", "fetch('http://127.0.0.1:<port>/health/ready').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]` |
| Node (distroless) | the same with `/nodejs/bin/node` in place of `node` |
| Python (slim or distroless, venv on `PATH`) | `["CMD", "python", "-c", "import sys,urllib.request as u; sys.exit(0 if u.urlopen('http://127.0.0.1:<port>/health/ready', timeout=2).status==200 else 1)"]` |
| Frontend nginx (alpine) | `["CMD", "wget", "-qO-", "http://127.0.0.1:8081/_healthz"]` — nginx has no HTTP client of its own; busybox's `wget` is part of this image |
| Frontend nginx (no shell) | none — the kubelet probes over HTTP and needs no binary; compose treats the running container as up |

`/health/ready` touches the database, so `up --wait` means "the app can
serve", not "the process started".

## Frontend image — the reference (SPA)

```dockerfile
FROM node:<pinned>-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build                                  # → /app/dist

FROM nginxinc/nginx-unprivileged:<version>-alpine-slim
COPY nginx/ /etc/nginx/
COPY --from=build /app/dist /usr/share/nginx/html
USER 101                                           # the base image's user, written out for the contract test
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

The base image already runs as UID 101 and listens on 8080. `nginx/` in
the client folder is copied from this skill's `assets/nginx/` —
`nginx.conf` and `templates/*.template` — as they are, with only these
write-time values filled:

| Placeholder | File | Value |
|---|---|---|
| `<<SERVICE>>` | `nginx.conf`, three log formats | `<project>-frontend` |
| `<<MAX_BODY_SIZE>>` | `default.conf.template` | the SRS NFR for the largest upload (`4G`), through foundation §1 «Решения по NFR» |
| `<<CLIENT_TIMEOUT>>` | `default.conf.template` | the NFR for the longest client request or upload (`600s`) |
| `<<BACKEND_TIMEOUT>>` | `default.conf.template` | the NFR for the longest backend response (`600s`) |

When the SRS names no such NFR, write nginx's defaults (`1m`, `60s`,
`60s`) and say so in the report — never another project's values. The
body limit covers the request as sent: a file sent as base64 inside JSON
is a third larger than the file, so size the limit to the encoded body and
say so. A Content-Security-Policy is added only when foundation §1
security decisions set one; otherwise the commented note stays.

At container start the base image renders every template into
`/etc/nginx/conf.d/` from the environment, so one image serves every
environment:

| Variable | Meaning | test / dev | prod |
|---|---|---|---|
| `BACKEND_SERVICE` | `host:port` of the backend | `backend:<app-port>` | `backend:<app-port>` |
| `BACKEND_PROTOCOL` | `http` or `https` to the backend | `http` | `http` (same network) |
| `SECURE_MODE` | `plain` — HTTP on 8080; `secure` — TLS 1.2/1.3 and HTTP/2 on 8080 with `/etc/nginx/ssl/fullchain.pem` and `privkey.pem` mounted read-only | `plain` | `plain` behind the operator's TLS terminator; `secure` when this nginx terminates TLS itself |

- `/api/` is proxied to the backend on the same origin, with the
  forwarding, `X-Request-ID` and `X-Correlation-ID` headers. The SPA calls
  relative `/api/...` URLs; no CORS, no build-time API host.
- **Only `/api/` reaches the backend.** Its service endpoints —
  `/health/live`, `/health/ready`, `/metrics` — sit outside `/api/`, so
  the entry point never exposes them: a request for `/metrics` there gets
  the SPA's `index.html`. The cluster reaches them on the backend's own
  port. Do not add a `location` that proxies them.
- `X-Request-ID` carries nginx's own `$request_id`, which its access log
  records too; the backend logs it as `request_id`, so one id follows a
  request through both logs.
- SPA routing (`try_files … /index.html`), HTML never cached, hashed assets
  cached for a year, dotfiles denied except `.well-known`, the security
  headers, gzip — all in the template.
- Health: `/_healthz` on port 8081, outside the access log; the frontend's
  own check, not the backend's.
- Read-only root: nginx writes its pid and temp files under `/tmp`
  (`nginx.conf`), and the start renders the templates into
  `/etc/nginx/conf.d/` — so this image needs both writable: a tmpfs on
  each in compose, an `emptyDir` on each in the cluster.
- Access log: one JSON line per request on stdout (`json_combined`); the
  `json_detailed` and `json_debug` formats stay defined for switching.

## Frontend image — without a shell

A shell-less nginx has no entrypoint script to render templates at start,
so the templates are rendered at build time, in a stage that only lends its
`envsubst`:

```dockerfile
FROM node:<pinned>-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build                                  # → /app/dist

FROM nginxinc/nginx-unprivileged:<version>-alpine-slim AS config   # only for envsubst; nothing of it ships
ARG BACKEND_SERVICE=backend:<app-port>
ARG BACKEND_PROTOCOL=http
ARG SECURE_MODE=plain
COPY nginx/templates/ /tmp/templates/
RUN mkdir -p /tmp/conf.d && for t in /tmp/templates/*.template; do \
      envsubst '${BACKEND_SERVICE} ${BACKEND_PROTOCOL} ${SECURE_MODE}' < "$t" > "/tmp/conf.d/$(basename "$t" .template)"; \
    done

FROM cgr.dev/chainguard/nginx@sha256:<digest>      # no shell; its free tier publishes `latest` only — the digest pins it
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=config /tmp/conf.d/ /etc/nginx/conf.d/
COPY --from=build /app/dist /usr/share/nginx/html
USER 65532
EXPOSE 8080
```

- `envsubst` gets the list of the three variables, so nginx's own `$uri`,
  `$host` and the rest stay as they are.
- The base's `ENTRYPOINT`/`CMD` stay when `docker image inspect` shows
  nginx in the foreground reading `/etc/nginx/nginx.conf`; otherwise set
  `CMD` to that. Prove the built image once:
  `docker run --rm --read-only --tmpfs /tmp <project>-frontend:<tag> -t`
  (nginx's config test, through its entrypoint) — it fails on a missing
  `mime.types` or include.
- The three variables are fixed in the image: the frontend reaches
  `backend:<app-port>` over HTTP. DEPLOY.md says so — the operators name
  the backend's service `backend`, or mount their own
  `/etc/nginx/conf.d/upstream.conf`; TLS inside the container
  (`SECURE_MODE=secure`) needs a rebuild with that build argument.
- Only `/tmp` needs to be writable (the config is already in the image).
  No compose healthcheck (table above); `frontend`'s compose
  `environment:` holds no `BACKEND_*` / `SECURE_MODE`.

## Version, date, tag

- `APP_VERSION` — the `version` of the project manifest (`package.json`,
  `pyproject.toml`); both images carry the same one. It is the plan
  folder's version (`documentation/plans/<version>/`) that the last plan
  unit set in the manifest, so the tag starts with that folder's name.
- Build date in UTC, `YYYYMMDD-HHMM`, taken once per build so both images
  share it.
- Tag: `<APP_VERSION>-<YYYYMMDD-HHMM>`, e.g. `1.4.0-20261004-0936`.
  Never `latest`.

## Architecture

`linux/amd64` unless the user says the cluster is ARM — then
`linux/arm64`. One platform per build: both at once needs a registry that
stores a manifest list, which is the operators' side, so it is not offered.
The value is the card's «Архитектура» row and the `PLATFORM=` line at the
top of `scripts/build-images.sh`; the sync test holds the two together.
The flag is explicit because a build on Apple silicon otherwise produces
`arm64` images that do not start on `amd64` servers, and the reverse.

## Hand-over: one tar and the release folder

Images are handed over as one file, never pushed to a registry. Write
`scripts/build-images.sh` (and a `build-images` task-runner target) that:

1. reads the version from the manifest, takes the date once, and sets
   `PLATFORM` from the card;
2. builds each image with
   `docker buildx build --platform "$PLATFORM" --load -t <project>-<backend|frontend>:<tag> -f <Dockerfile> <context>`;
3. saves both into one archive named after the project and the service
   version, in that version's release folder:
   `docker save <project>-frontend:<tag> <project>-backend:<tag> -o release/<APP_VERSION>/<project>-<APP_VERSION>.tar`
   (e.g. `release/1.4.0/room-booking-1.4.0.tar`);
4. puts every other file the operators get beside it:
   - `documentation/deploy/deploy.md` → `DEPLOY.md`, replacing `<версия>`
     with the version and `<тег>` with the image tag;
   - `documentation/deploy/prod.env.example` → `<project>.env.example`
     (`deploy-doc.md` → The variables file);
   - `documentation/api/openapi.yaml` → `openapi.yaml`, one file: a split
     contract (a `$ref` that points at another file) is bundled, a single
     file is copied —

     ```bash
     api=documentation/api/openapi.yaml
     if grep -Eq '\$ref:[[:space:]]*["'\'']?[^#"'\''[:space:]]' "$api"; then
       npx --yes @redocly/cli bundle "$api" -o "release/$APP_VERSION/openapi.yaml"
     else
       cp "$api" "release/$APP_VERSION/openapi.yaml"
     fi
     ```
   - `documentation/operations/operations.md`, when it exists →
     `OPERATIONS.md` (`operations-doc`);
5. checks the folder against `DEPLOY.md`, so an operator never gets an
   instruction for a file they do not have. A file name is a backtick span
   with no space or `/` that ends in a known extension — a logger name
   (`<project>.migrate`), a field (`res.statusCode`) or `schema.table` is
   not one; a line with «создайте» names a file the operator makes, so it is skipped:

   ```bash
   missing=0
   for f in $(grep -vE '[Сс]оздайте' "release/$APP_VERSION/DEPLOY.md" \
       | grep -oE '`[^` /]+\.(tar|md|yaml|yml|example|pem|crt|key|sql|json|txt|env|local)`' | tr -d '`' | sort -u); do
     [ -e "release/$APP_VERSION/$f" ] || { echo "DEPLOY.md называет $f, а в release/$APP_VERSION/ его нет" >&2; missing=1; }
   done
   [ "$missing" -eq 0 ] || exit 1
   ```
6. prints the folder, the tar size, both image names with tags and the
   platform.

The file name carries the version so the releases sit side by side and an
older one is still there for a rollback; a rebuild of the same version
replaces its folder's contents (the build date is in the image tags inside).
`release/` is in `.gitignore` and `.dockerignore`.

The receiver runs `docker load -i <project>-<APP_VERSION>.tar`; both images
appear with their tags, and they load them into their own registry
themselves. Put that line, the tag format, the platform, the release folder
and the variable table above in the README's «Сборка образов» section.
