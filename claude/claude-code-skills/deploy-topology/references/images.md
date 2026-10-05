# Images: what each container's image holds and how they are handed over

Read this at Step 2 and Step 8. The rules reproduce a reference build the
owner accepted: an SPA frontend on unprivileged nginx and a Node backend,
both `linux/amd64`, handed over as one tar. Match it; do not "improve" it
with extra users, labels or ports. The only additions are the ones the
owner asked for: the tag carries the app version and the build date,
nginx's upload size and timeouts come from the SRS NFRs, and the backend
image carries the SQL migrations from `documentation/db/migrations/`
(the reference copied a code-tree folder, `src/db/migrations`; migrations
no longer live in the code tree).

## Which images

One image per container of the architecture (foundation §1 «Состав
системы», the containers view):

| Container | Image | Runtime base |
|---|---|---|
| Backend API (and its `migrate` one-shot — same image, other command) | `<project>-backend` | `node:<pinned>-alpine` (TypeScript) / `python:<pinned>-slim` (Python) |
| SPA client (React + Vite) | `<project>-frontend` | `nginxinc/nginx-unprivileged:<version>-alpine-slim` |
| SSR client (Next.js) | `<project>-frontend` | `node:<pinned>-alpine` with Next.js `output: "standalone"`, shaped like the backend; no nginx |

No client in the architecture → only the backend image. `<project>` is the
kebab-case project name. Base tags are exact versions, never `latest` or a
bare major (Step 2).

## Backend image — the reference (TypeScript)

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
EXPOSE 3000
CMD ["node", "dist/src/index.js"]
```

- Two stages: the build stage has the TypeScript toolchain; the runtime
  stage installs production dependencies only (`npm ci --omit=dev`, the
  manifest copied before the code so the dependency layer is cached) and
  copies the compiled `dist`.
- No `USER` line — the reference runs as the base image's default user.
- The SQL migrations travel inside the image: `documentation/db/migrations/`
  is copied to the same relative path under `WORKDIR`, because the
  project's migrate command reads it by that path (`repo-scaffold` §4). The
  build context therefore includes that folder — the repo root, not a
  backend subfolder — and `.dockerignore` does not exclude it. The
  `migrate` service runs this same image with the migrate command; the app
  process never migrates on start (Step 4).
- `EXPOSE` the app port, `CMD` in exec form. The entrypoint is the base
  image's.

Python, the same shape: build stage `uv sync --frozen --no-dev` into
`/app/.venv`; runtime `python:<pinned>-slim`, `WORKDIR /app`, copy `.venv`
and the source, `PATH=/app/.venv/bin:$PATH`, `documentation/db/migrations`
copied to the same relative path (the Alembic revisions read it), `EXPOSE`
the port, exec-form `CMD` for the server (workers from the environment).

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
| `BACKEND_SERVICE` | `host:port` of the backend | `app:<app-port>` | `app:<app-port>` |
| `BACKEND_PROTOCOL` | `http` or `https` to the backend | `http` | `http` (same network) |
| `SECURE_MODE` | `plain` — HTTP on 8080; `secure` — TLS 1.2/1.3 and HTTP/2 on 8080 with `/etc/nginx/ssl/fullchain.pem` and `privkey.pem` mounted read-only | `plain` | `plain` behind the operator's TLS terminator; `secure` when this nginx terminates TLS itself |

- `/api/` is proxied to the backend on the same origin, with the
  forwarding, `X-Request-ID` and `X-Correlation-ID` headers. The SPA calls
  relative `/api/...` URLs; no CORS, no build-time API host.
- SPA routing (`try_files … /index.html`), HTML never cached, hashed assets
  cached for a year, dotfiles denied except `.well-known`, the security
  headers, gzip — all in the template.
- Health: `/_healthz` on port 8081, outside the access log. The compose
  `healthcheck` for this service is
  `["CMD", "wget", "-qO-", "http://127.0.0.1:8081/_healthz"]`.
- Access log: one JSON line per request on stdout (`json_combined`); the
  `json_detailed` and `json_debug` formats stay defined for switching.

## Version, date, tag

- `APP_VERSION` — the `version` of the project manifest (`package.json`,
  `pyproject.toml`); both images carry the same one. It is the plan
  folder's version (`documentation/plans/<version>/`) that the last plan
  unit set in the manifest, so the tag starts with that folder's name.
- Build date in UTC, `YYYYMMDD-HHMM`, taken once per build so both images
  share it.
- Tag: `<APP_VERSION>-<YYYYMMDD-HHMM>`, e.g. `1.4.0-20261004-0936`.
  Never `latest`.

## Hand-over: one tar

Images are handed over as one file, never pushed to a registry. Write
`scripts/build-images.sh` (and a `build-images` task-runner target) that:

1. reads the version from the manifest and takes the date once;
2. builds each image with
   `docker buildx build --platform linux/amd64 --load -t <project>-<backend|frontend>:<tag> -f <Dockerfile> <context>`;
3. saves both into one archive named after the project and the service
   version, in that version's release folder:
   `docker save <project>-frontend:<tag> <project>-backend:<tag> -o release/<APP_VERSION>/<project>-<APP_VERSION>.tar`
   (e.g. `release/1.4.0/room-booking-1.4.0.tar`);
4. copies `documentation/deploy/deploy.md` to `release/<APP_VERSION>/DEPLOY.md`;
5. prints the folder, the tar size, and both image names with tags.

The file name carries the version so the releases sit side by side and an
older one is still there for a rollback; a rebuild of the same version
replaces its folder's contents (the build date is in the image tags inside).

`--platform linux/amd64` is explicit: a build on Apple silicon otherwise
produces `arm64` images that do not start on the target servers.
`release/` is in `.gitignore` and `.dockerignore`.

The receiver runs `docker load -i <project>-<APP_VERSION>.tar`; both images
appear with their tags. Put that line, the tag format, the release folder and
the variable table above in the README's «Сборка образов» section.
