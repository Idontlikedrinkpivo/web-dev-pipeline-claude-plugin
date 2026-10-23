# The deploy document and its sync test

Read this in Step 8 while writing `documentation/deploy/deploy.md`, in
Step 7 while writing its sync test, and in Step 7b for the stand's proof
(the service check and the resource measurement for «Ресурсы»).

The operators receive one folder per release: the image archive,
`DEPLOY.md`, the variables file `<project>.env.example`, the API contract
`openapi.yaml`, and `OPERATIONS.md` when the operations document exists.
They do not receive `docker-compose.prod.yml` — they run the images in
their own way (their compose, their orchestrator, their secrets store), so
they need the facts, not this project's file. So `DEPLOY.md` names no file
the folder does not hold: an operator told to fill `.env.prod.local` or to
start `docker-compose.prod.yml` has neither (ai-initiatives, 2.1.0). The
compose file stays in the repo as the source those facts are taken from and
as a way to run the prod shape locally; the sync test keeps the two from
drifting.

The sections answer a platform team's preflight for a service entering
their cluster — non-root, probes, resources, dependencies, DBA facts, logs,
metrics, shutdown — so they can write their manifests from this file alone,
without asking.

## Where it lives

- Source: `documentation/deploy/deploy.md`, in Russian, in git. **Unversioned**
  (`doc-versioning` → Registry): it is derived from the compose file, the
  Dockerfiles and the config layer, and the sync test — not a version
  number — is what keeps it true. No `version`, no changelog, no `sources:`.
- Hand-over copy: `scripts/build-images.sh` copies it to
  `release/<version>/DEPLOY.md` beside the archive, replacing the
  placeholders `<версия>` and `<тег>` with this build's version and image tag,
  so the folder carries the instructions as they were for that build. The
  source keeps the placeholders — a version written into it by hand goes
  stale with the next release.

## What it holds

Every section is filled from what the project actually has; a section that
does not apply says so in one line («Томов нет: всё состояние в базе и S3»)
rather than disappearing — an operator reading a missing section cannot tell
"none" from "forgotten".

Write it to be scanned (`doc-versioning` → `references/readable.md`): a cell is one fact, a run of cases is a table, a procedure is a numbered list, a paragraph at most four sentences.

````markdown
# Развёртывание room-booking <версия>

Комплект: `room-booking-<версия>.tar` (образы `room-booking-backend:<тег>`,
`room-booking-frontend:<тег>`), этот файл, `room-booking.env.example` —
переменные прода с пометками, и `openapi.yaml` — контракт API.

Загрузка образов: `docker load -i room-booking-<версия>.tar`

## Карточка сервиса

| Что | Значение |
|---|---|
| Образы | `room-booking-backend:<тег>`, `room-booking-frontend:<тег>` |
| Архитектура | linux/amd64 |
| Образ | с оболочкой (alpine) |
| Пользователь | backend и migrate — UID 1000, frontend — UID 101; root не нужен |
| Порты | backend 3000 — API, проверки, метрики; frontend 8080 — вход, 8081 — его проверка |
| Проверки | backend: живость `GET /health/live`, готовность `GET /health/ready`; frontend: `GET /_healthz` на 8081 |
| Метрики | `GET /metrics` на backend:3000, формат Prometheus |
| Переменные | раздел «Переменные»; образец — `room-booking.env.example` |
| Ресурсы | backend: 100m и 128Mi, лимит памяти 256Mi; frontend: 50m и 64Mi, лимит 64Mi (замерено 2026-10-23) |
| Зависимости | PostgreSQL 17, S3-совместимое хранилище, почтовый сервис — раздел «Внешние зависимости» |
| Заметки | миграции — контейнер `migrate`, один раз перед `backend`; остановка по SIGTERM за 25 с; томов нет — состояние в PostgreSQL и S3 |

## Контейнеры

| Контейнер | Образ | Команда | Запуск |
|---|---|---|---|
| migrate | room-booking-backend:<тег> | `node dist/src/migrate.js` | разово, до успешного завершения |
| backend | room-booking-backend:<тег> | по умолчанию (`node dist/src/index.js`) | постоянно |
| frontend | room-booking-frontend:<тег> | по умолчанию (nginx) | постоянно |

## Порядок запуска

1. `migrate` — применяет миграции базы и завершается с кодом 0. Ненулевой код — остановиться:
   `backend` на непримененной схеме не запускать. Повторный запуск безопасен: применённые миграции
   пропускаются.
2. `backend` — после успешного `migrate`.
3. `frontend` — после того как `backend` отвечает на проверку готовности.

## Сеть и проверки

| Контейнер | Тип | Путь | Порт | Ответ | Таймаут | Период | Порог отказов |
|---|---|---|---|---|---|---|---|
| backend | liveness | `GET /health/live` | 3000 | 200 | 2 с | 10 с | 3 |
| backend | readiness | `GET /health/ready` | 3000 | 200; 503 — не готов | 3 с | 10 с | 3 |
| frontend | liveness | `GET /_healthz` | 8081 | 200 | 1 с | 10 с | 3 |
| frontend | readiness | `GET /_healthz` | 8081 | 200 | 1 с | 10 с | 3 |
| migrate | — | — | — | код выхода 0 | — | — | — |

Живость не обращается к базе: её недоступность не перезапускает поды. Готовность проверяет базу
с таймаутом 2 с, поэтому таймаут пробы — 3 с. Проверка запуска (startup) не нужна: backend готов
через 3 с (раздел «Ресурсы»).

Наружу публикуется только `frontend:8080`. Служебные пути backend — `/health/live`, `/health/ready`,
`/metrics` — доступны только внутри кластера на порту 3000: `frontend` проксирует к бэкенду лишь
`/api/`. TLS и внешний прокси перед `frontend` — на стороне эксплуатации; `frontend` работает по
HTTP, а адрес бэкенда получает из `BACKEND_SERVICE`.

## Ресурсы

| Контейнер | CPU: покой / обычно / пик | Память: покой / обычно / пик | Готов через | requests: CPU, память | limits: память |
|---|---|---|---|---|---|
| backend | 1m / 60m / 210m | 72Mi / 95Mi / 140Mi | 3 с | 100m, 128Mi | 256Mi |
| frontend | 0m / 2m / 15m | 6Mi / 8Mi / 12Mi | < 1 с | 50m, 64Mi | 64Mi |
| migrate | не замерялся (разовый) | — | — | как у backend | как у backend |

Замерено 2026-10-23 на тестовом стенде: Docker 28, 8 ядер, образы собраны под linux/arm64 этой
машины (без эмуляции); `docker stats` каждые 2 с. Покой — 30 с без запросов. Обычно — постоянные
5 запросов/с 2 мин: профиль из требований, NFR-4 — до 50 пользователей, запрос раз в 10 с. Пик —
e2e-тесты (42 теста, 6 мин). Это нагрузка стенда, а не прода.

requests — обычное значение, округлённое вверх; лимит памяти — пик × 1,5, округлённый до 64Mi.
Лимит CPU не рекомендуем: с ним процесс притормаживается квотой (throttling) даже на свободном
узле; если политика кластера его требует — не ниже пика.

## Переменные

### backend и migrate

| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |
|---|---|---|---|---|
| APP_ENV | да | нет | `prod` | окружение; без него приложение не стартует |
| DATABASE_URL | да | да | `postgres://user:***@host:5432/db?options=-c%20search_path%3Droom_booking` | подключение к PostgreSQL, схема `room_booking`. У `backend` — учётка backend (только данные), у `migrate` — учётка migrate (владелец схемы): значения разные |
| LOG_LEVEL | нет | нет | `info`; допустимо `trace`, `debug`, `info`, `warn`, `error`, `fatal` | подробность логов |
| SHUTDOWN_TIMEOUT_SEC | нет | нет | `25` (секунды) | сколько `backend` после SIGTERM дожидается текущих запросов |
| … | | | | |

### frontend

| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |
|---|---|---|---|---|
| BACKEND_SERVICE | да | нет | `backend:3000` | адрес бэкенда |
| BACKEND_PROTOCOL | да | нет | `http` | протокол до бэкенда |
| SECURE_MODE | да | нет | `plain` или `secure` | `plain` — HTTP, TLS на прокси эксплуатации; `secure` — TLS в самом контейнере, сертификаты в `/etc/nginx/ssl/`. Другое значение — nginx не стартует |

## Внешние зависимости

| Что | Адрес в переменной | Порт, протокол | Направление | Требования |
|---|---|---|---|---|
| PostgreSQL 17 | `DATABASE_URL` | 5432, TCP | backend, migrate → база | раздел «Для DBA» |
| S3-совместимое хранилище | `S3_ENDPOINT` | 443, HTTPS | backend → хранилище | бакет `room-booking-files`, чтение и запись |
| Почтовый сервис (внешняя система) | `MAIL_API_URL` | 443, HTTPS | backend → интернет | ключ — `MAIL_API_KEY` |
| Прокси эксплуатации | — | 8080, HTTP | прокси → frontend | TLS завершается на прокси |

DNS-имена и адреса — ваши: приложение берёт их только из переменных. Других исходящих
соединений нет.

## Для DBA

| Что | Значение |
|---|---|
| СУБД | PostgreSQL 17 |
| Схема | `room_booking` (не `public`); создаёт DBA, владелец — учётка migrate |
| Расширения | `citext` — доверенное: учётка migrate создаёт его сама по праву CREATE на базу. Недоверенные (`postgis`) DBA создаёт заранее |
| Учётка migrate | владелец схемы и право CREATE на базу: создаёт и меняет таблицы; её адрес — в `DATABASE_URL` контейнера `migrate` |
| Учётка backend | только данные: SELECT, INSERT, UPDATE, DELETE, использование последовательностей; её адрес — в `DATABASE_URL` контейнера `backend` |
| Подключений | backend — до 10 на реплику (размер пула, по умолчанию 10) × число реплик; migrate — 1 на время запуска |
| Кодировка, часовой пояс | UTF8; время хранится в `timestamptz`, сессии — в UTC |

Подготовка базы (имена учёток можно поменять, пароли — ваши; `<база>` — имя базы из `DATABASE_URL`).
Право CREATE на базу нужно учётке migrate и при уже созданной схеме: первая миграция начинается с
`CREATE SCHEMA IF NOT EXISTS`, а PostgreSQL проверяет это право раньше, чем наличие схемы.

```sql
CREATE ROLE room_booking_migrate LOGIN PASSWORD '<секрет>';
CREATE ROLE room_booking_backend LOGIN PASSWORD '<секрет>';
GRANT CREATE ON DATABASE <база> TO room_booking_migrate;
CREATE SCHEMA room_booking AUTHORIZATION room_booking_migrate;
GRANT USAGE ON SCHEMA room_booking TO room_booking_backend;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA room_booking TO room_booking_backend;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA room_booking TO room_booking_backend;
ALTER DEFAULT PRIVILEGES FOR ROLE room_booking_migrate IN SCHEMA room_booking
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO room_booking_backend;
ALTER DEFAULT PRIVILEGES FOR ROLE room_booking_migrate IN SCHEMA room_booking
  GRANT USAGE ON SEQUENCES TO room_booking_backend;
```

Те же права у учёток тестового стенда, ни одна из них не суперпользователь: миграции прошли под
учёткой migrate, `backend` работал только с данными.

## Логи

- backend и migrate пишут в stdout по одной JSON-записи на строку: `time` (ISO-8601, UTC), `level`,
  `msg`, `logger`, `request_id`; у ошибки — `err` с типом, сообщением и стеком. Уровень — `LOG_LEVEL`.
- Секретов, токенов и персональных данных в логах нет.
- `request_id` сквозной: берётся из заголовка `X-Request-Id` (его ставит `frontend`) или создаётся,
  и возвращается в ответе.
- frontend (nginx) пишет журнал запросов JSON-строками в stdout (`@timestamp`, `status`,
  `request_time`, `request_id`, …), ошибки — в stderr.

## Метрики

| Что | Значение |
|---|---|
| Где | `GET /metrics` на backend:3000, без авторизации; через `frontend` наружу не доступен |
| Формат | Prometheus, текстовый |
| Основные | `http_request_duration_seconds` — гистограмма длительности запросов с метками `method`, `route` (шаблон пути), `status_code`; стандартные метрики процесса (`process_cpu_seconds_total`, `process_resident_memory_bytes`, …) |
| frontend | метрик нет |

## Остановка

- backend по SIGTERM перестаёт принимать запросы, дожидается текущих не дольше
  `SHUTDOWN_TIMEOUT_SEC` (по умолчанию 25 с), закрывает пул соединений с базой и завершается с кодом 0.
- Рекомендуем `terminationGracePeriodSeconds` не меньше 30 (25 + 5).
- migrate — разовый, останавливать не нужно.
- frontend (nginx) останавливается сигналом образа SIGQUIT и дожидается текущих запросов.

## Безопасность пода

| Контейнер | runAsUser | Пишет на диск |
|---|---|---|
| backend, migrate | 1000 | только `/tmp` |
| frontend | 101 | `/tmp`, `/etc/nginx/conf.d` |

Для всех: `runAsNonRoot: true`; `readOnlyRootFilesystem: true` с `emptyDir` на каждый путь из
таблицы; `allowPrivilegeEscalation: false`; capabilities — drop ALL; `seccompProfile: RuntimeDefault`.
Все порты выше 1024. Тестовый стенд работает с теми же ограничениями.

## Трассировка

Нет.

## Состояние и тома

Томов нет: всё состояние в базе и S3. Контейнеры можно пересоздавать в любой момент.

## Первый запуск

Как появляется первый администратор (или начальные данные) — по шагам.

## Обновление на новую версию

1. `docker load -i room-booking-<новая версия>.tar`.
2. Запустить `migrate` нового образа, дождаться кода 0.
3. Перезапустить `backend` и `frontend` на новом теге.

Откат: предыдущий комплект лежит в своей папке выпуска; откат версии с миграцией,
которая меняет или удаляет данные, согласовывается отдельно.
````

Where each section comes from:

| Section | Source |
|---|---|
| Комплект | what `scripts/build-images.sh` puts in the release folder: the tar, `DEPLOY.md`, `<project>.env.example`, `openapi.yaml`, and `OPERATIONS.md` only when `documentation/operations/operations.md` exists |
| Карточка сервиса | the sections below, one line each; «Архитектура» — `PLATFORM` in the build script; «Образ» — the project's answer (`images.md` → Shell or no shell); «Пользователь» — each image's numeric `USER` |
| Контейнеры | `docker-compose.prod.yml` services, the Dockerfiles' `CMD`, the migrate command |
| Порядок запуска | `depends_on` conditions in `docker-compose.prod.yml` |
| Сеть и проверки | the container ports, the published port, the service endpoints; timings by the rules below; a startup row from «Ресурсы»' time to ready |
| Ресурсы | the measurement in Step 7b (below); the load profile from the SRS NFRs, or «в требованиях не задан» |
| Переменные | each service's `environment:` / `env_file` in `docker-compose.prod.yml`, and `.env.example`'s markers for required / secret (`env-and-config-contract.md` → Markers in `.env.example`); `[infra]` keys never appear |
| Внешние зависимости | what `docker-compose.prod.yml` points outside itself, each with the variable that holds its address; the external systems of architecture foundation §1 as outgoing rows; versions from the architecture |
| Для DBA | `schema.md` «Решения по базе» (DBMS and major, schema, collation); `CREATE EXTENSION` in `documentation/db/migrations/`; the grants of `docker/db-init/roles.sql`, the database grant written with `<база>`; the pool size the config layer sets |
| Логи | the fields the app's JSON formatter writes; nginx's `json_combined` |
| Метрики | `/metrics`, the request histogram, the stack's default process metrics |
| Остановка | `SHUTDOWN_TIMEOUT_SEC`'s default in the config layer; the frontend image's stop signal (`docker image inspect --format '{{.Config.StopSignal}}'`) |
| Безопасность пода | each Dockerfile's `USER`; each app service's `tmpfs:` paths in `docker-compose.prod.yml` |
| Трассировка | «Нет.», or the `OTEL_` variables when the project chose tracing |
| Состояние и тома | `volumes:` in `docker-compose.prod.yml` |
| Первый запуск | the architecture or SRS (how the first admin or seed data appears); ask the user when neither says |
| Обновление | fixed text above, with the project's names |

The image without a shell changes three places: «Образ» says «без
оболочки (distroless)», the UIDs are 65532, and the frontend has no
variables — its table says «Переменных нет: адрес бэкенда `backend:<port>`
и протокол заданы при сборке образа» and the network section tells the
operators to name the backend's service `backend` or mount their own
`/etc/nginx/conf.d/upstream.conf` (`images.md` → Frontend image — without a
shell). Its frontend writes only `/tmp`.

**Probe timings.** Liveness: timeout 2 s, period 10 s, failure threshold 3.
Readiness: timeout 3 s — above the 2 s database ping it waits for — period
10 s, threshold 3. The frontend's `/_healthz`: timeout 1 s. A startup probe
row (`GET /health/live`, period 5 s) only when the measured time to ready
exceeds 10 s; its failure threshold × period is at least twice that time,
so a slow start on a busy node is not killed by liveness.

Secrets never appear with values — a format with `***` in place of the secret
part, or `<секрет>`. A variable with a fixed set of values lists exactly
that set in «Пример / формат»; `SECURE_MODE` is `plain` or `secure`, because
the image's nginx includes `${SECURE_MODE}.conf` and has only those two
(`references/images.md`).

**Files it names.** Only the bundle's: `<project>-<версия>.tar`, `DEPLOY.md`,
`<project>.env.example`, `openapi.yaml`, `OPERATIONS.md`, or a file a
numbered step of the document itself tells the operator to create
(«создайте файл с переменными по образцу `room-booking.env.example`»).
Never a file of the repository — `docker-compose.*.yml`, `.env.example`,
`.env.*.local`, `roles.sql`, a script. A file the operator creates is named
on a line with «создайте», which the build script's check skips; a path
inside a container (`/etc/nginx/ssl/`) holds a `/` and is not checked; and
only names with a known extension count as files (sync test, item 9).

## The stand's proof (Step 7b)

It needs only the test stand up (`up-test`), not the verify skill: after
Step 7a it runs on the stand that proof brought up, before the cleanup;
alone, it brings the stand up and down itself. Below, `p=<project>-test`
and `f=docker-compose.test.yml`.

### The service check in the container

`repo-scaffold`'s gate, run against the `backend` container instead of a
local process — the same probes, metrics, request id, JSON lines and
SIGTERM exit, now under the read-only root, the dropped capabilities and
the image's `USER`:

```bash
docker compose -p "$p" -f "$f" stop backend
python3 "${CLAUDE_SKILL_DIR}/../repo-scaffold/scripts/service_check.py" \
  --port "${APP_PORT:-<app-port>}" --expect-ready --shutdown-timeout <SHUTDOWN_TIMEOUT_SEC> \
  -- docker start -a "$(docker compose -p "$p" -f "$f" ps -aq backend)"
docker compose -p "$p" -f "$f" start backend
```

- `docker start -a` attaches the container's stdout and stderr, passes the
  check's SIGTERM on to the container, and exits with the container's own
  code — so the exit check is the app's.
- Not `docker compose run` or `up`: compose writes its own lines to stderr
  («Container … Creating», a platform warning), and the «every line is
  JSON» check fails on them.
- The variables the script sets reach the `docker` client, not the
  container: `--shutdown-timeout` is the compose file's
  `SHUTDOWN_TIMEOUT_SEC`.
- A failure is a defect of the image or the app — fixed before the
  hand-over, never written around in DEPLOY.md.

### Measuring resources

1. **This machine's architecture.** Compose builds the stand's images for
   the machine it runs on (`docker image inspect --format
   '{{.Architecture}}' <project>-backend:test`). An image of another
   architecture runs emulated — `amd64` on Apple silicon — and its CPU
   comes out several times too high: build the same Dockerfiles natively
   for the measurement, or write «под эмуляцией, CPU завышен» beside the
   numbers.
2. **Sample** the app containers back to back for every phase below —
   each `docker stats --no-stream` call takes about 2 s (it waits for a
   second CPU reading), so no `sleep`:

   ```bash
   apps=$(docker compose -p "$p" -f "$f" config --services | grep -xE 'backend|frontend' | tr '\n' ' ')
   ids=$(docker compose -p "$p" -f "$f" ps -q $apps)
   [ -n "$ids" ] || { echo "no app container is running" >&2; exit 1; }   # an empty list would sample every container
   while :; do
     docker stats --no-stream --format '{{.Name}};{{.CPUPerc}};{{.MemUsage}}' $ids | sed "s/^/$(date +%T);/"
   done > documentation/plans/<version>/resources.txt   # stopped after the last phase
   ```

3. **Idle** — 30 s without requests.
4. **Typical** — a fixed request rate for 2 min: the SRS NFRs' load profile
   turned into requests per second (users ÷ seconds between their
   requests), else a modest stated rate (5 requests/s). A saturating load
   would make «typical» the peak and the requests as large as the limits.
5. **Peak** — the fullest load that drives the stand over HTTP: the e2e
   suite, else API tests aimed at the stand's port, else the script below
   at a fixed concurrency (16 clients, 2 min). Tests that call the app
   in-process (`inject`, `TestClient`) put no load on the container.
6. **Time to ready.** Restart each app container and poll its readiness
   every 0.5 s from the host — `backend`'s `/health/ready` on its published
   port, `frontend`'s page on its own:

   ```bash
   docker compose -p "$p" -f "$f" restart backend
   n=0; until curl -fsS -o /dev/null "http://127.0.0.1:${APP_PORT:-<app-port>}/health/ready"; do n=$((n+1)); sleep 0.5; done
   [ "$n" -lt 2 ] && echo "ready after < 1 s" || echo "ready after ~$((n / 2)) s"
   ```

7. **Write «Ресурсы».** Per container: idle; typical — the median of the
   typical phase; peak — the maximum of the peak phase; CPU from
   `CPUPerc` (100% = one core = 1000m), memory from `MemUsage`. Requests =
   typical rounded up (CPU to 50m, memory to 64Mi); memory limit = peak ×
   1.5 rounded up to 64Mi; a CPU limit is a note, not a default. Then the
   date and how: the machine, the images' architecture (and «эмуляция» if
   so), the typical rate and its source, what drove the peak and for how
   long. `migrate` runs too briefly to sample; it gets `backend`'s requests.

The load script — written to `documentation/plans/<version>/load.py` when
nothing else drives the stand, aimed at the read operations a signed-in
user calls most, with a test role's token (the verify skill's `token.sh`,
or the test fixtures' sign-in). It sends GETs only: the how-line says
«нагрузка — только чтение». It counts the app's error answers apart from
connection failures on this machine (Docker Desktop's port forwarding drops
connections under load) — only the first are the app's:

```python
"""load.py (--rate R | --clients C) [--seconds S] URL... — R requests/s, or C clients as fast as they go.
TOKEN in the environment adds `Authorization: Bearer <TOKEN>`. Prints requests, the app's error answers, the
connection failures on this side, and p95 latency."""
import argparse, os, threading, time, urllib.error, urllib.request

ap = argparse.ArgumentParser()
mode = ap.add_mutually_exclusive_group(required=True)
mode.add_argument("--rate", type=float)
mode.add_argument("--clients", type=int)
ap.add_argument("--seconds", type=float, default=120)
ap.add_argument("urls", nargs="+")
args = ap.parse_args()
headers = {"Authorization": f"Bearer {os.environ['TOKEN']}"} if os.environ.get("TOKEN") else {}
lock, took, errors, threads = threading.Lock(), [], [0, 0], []  # [app error answers, connection failures]
end = time.monotonic() + args.seconds


def hit(url: str) -> None:
    started, kind = time.monotonic(), -1
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10).read()
    except urllib.error.HTTPError:  # the app answered with an error status
        kind = 0
    except Exception:  # no answer: a refused, reset or timed-out connection on this side
        kind = 1
    with lock:
        took.append(time.monotonic() - started)
        if kind >= 0:
            errors[kind] += 1


def client(first: int) -> None:
    n = first
    while time.monotonic() < end:
        hit(args.urls[n % len(args.urls)])
        n += 1


if args.rate:
    start, n = time.monotonic(), 0
    while time.monotonic() < end:
        threads.append(threading.Thread(target=hit, args=(args.urls[n % len(args.urls)],)))
        threads[-1].start()
        n += 1
        time.sleep(max(0.0, start + n / args.rate - time.monotonic()))
else:
    threads = [threading.Thread(target=client, args=(i,)) for i in range(args.clients)]
    for t in threads:
        t.start()
for t in threads:
    t.join()
took.sort()
p95 = took[max(0, int(len(took) * 0.95) - 1)] * 1000 if took else 0
print(f"{len(took)} requests in {args.seconds:.0f} s, {errors[0]} app errors, {errors[1]} connection failures, "
      f"p95 {p95:.0f} ms")
```

`python3 load.py --rate 5 --seconds 120 <urls>` for the typical phase,
`--clients 16` for the peak. When it drove a phase, «Ресурсы» says so:
«пик — скрипт нагрузки, 16 клиентов, 2 мин, операции …».

The numbers are the stand's, on the developer's machine — the section
says so, and gives the SRS NFRs' load profile beside them. No Docker here:
say so in the report, and the section reads «Не замерено: <причина>, <дата>»
with the card's «Ресурсы» row the same.

## The variables file

`documentation/deploy/prod.env.example`, in git beside `deploy.md`,
unversioned like it; `scripts/build-images.sh` copies it into the release
folder as `<project>.env.example`. It is what the operator fills — or copies
into their secrets store — so it holds the prod variables only, grouped by
container, each with one comment line:

```bash
# [required] [secret] backend — учётка backend (только данные). Формат: postgres://user:***@host:5432/db
DATABASE_URL=
# у migrate свой DATABASE_URL: учётка migrate (владелец схемы, право CREATE на базу), тот же формат
# backend, migrate — подробность логов: trace | debug | info | warn | error | fatal
LOG_LEVEL=info
# [required] frontend — plain | secure
SECURE_MODE=plain
```

The markers are `.env.example`'s (`env-and-config-contract.md` → Markers
in `.env.example`): `[required]` and `[secret]` where they apply, nothing
for an optional plain value.

No real value of a secret; a non-secret default is written as the value. Not
the repository's `.env.example`, which documents test, dev and prod together
and is read by the bootstrap targets.

## The sync test

Part of the compose-contract tests (Step 7), in the project's own test
runner. Parse `docker-compose.prod.yml`, `.env.example`, the Dockerfiles and
`scripts/build-images.sh`, parse the tables of
`documentation/deploy/deploy.md` (they are plain Markdown tables with fixed
headers — split rows on `|`), and assert:

1. **Sections.** Every `##` section of the template above is present, and
   «Карточка сервиса» is the first.
2. **Containers.** The set of services in the prod compose file equals the
   set of rows in «Контейнеры».
3. **Variables.** A «Переменные» table covers the containers its heading
   names («backend и migrate» covers two). Its names equal the union, over
   those containers, of what the prod compose file gives each: the keys of
   `environment:`, and — for a service with `env_file` — every key of
   `.env.example` not marked `[infra]`. A variable missing from the
   document, or a row the compose file no longer backs, fails. `[infra]`
   keys (the local stores' `POSTGRES_PASSWORD`, the S3 emulator's `AWS_*`)
   are in no table. A container with none has the «Переменных нет» line
   under its heading.
4. **Required and secret.** A row's «Обязательна» is «да» exactly when the
   variable's comment line in `.env.example` carries `[required]`, and
   «Секрет» exactly when it carries `[secret]` — the one marker format of
   `env-and-config-contract.md` → Markers in `.env.example`.
5. **Probes.** Each long-running service has a liveness and a readiness row
   on its container port; `backend`'s paths are `/health/live` and
   `/health/ready`, and its readiness timeout is above 2 s; the path the
   compose `healthcheck` asks is the readiness row's. A startup row exists
   exactly when «Ресурсы»' time to ready exceeds 10 s, and then its
   threshold × period is at least twice that time.
6. **Volumes.** No `volumes:` in the prod compose file ⇔ the «Состояние и
   тома» section says there are none.
7. **Allowed values.** For a variable with a fixed set — `SECURE_MODE`
   (`plain`, `secure`), `APP_ENV`, `LOG_LEVEL`, a protocol — the value in
   every compose file and in `prod.env.example`, and each value in its
   «Пример / формат» cell, belongs to the set the config layer or the image
   accepts.
8. **The variables file.** The names in `prod.env.example` equal the union
   of the «Переменные» tables, with the same «Обязательна» and «Секрет» marks.
9. **Named files.** A file name is a backtick span with no space or `/`
   ending in a known extension — `.tar .md .yaml .yml .example .pem .crt
   .key .sql .json .txt .env .local`; a logger name (`<project>.migrate`), a
   field (`res.statusCode`) or `schema.table` is not one. Every file name in
   `deploy.md` is one of the
   bundle's — the tar, `DEPLOY.md`, `<project>.env.example`,
   `openapi.yaml`, `OPERATIONS.md` — or is created by a numbered step of
   the document; a repository file (`docker-compose.*`, `.env.example`,
   `.env.*.local`) fails. And the «Комплект» line names every file the build
   script puts in the folder — `DEPLOY.md` as «этот файл», `openapi.yaml`
   included, `OPERATIONS.md` when `documentation/operations/operations.md`
   exists.
10. **Card.** «Архитектура» equals `PLATFORM` in `scripts/build-images.sh`;
    «Образ» says «без оболочки» exactly when the final `FROM` of the
    Dockerfiles is a shell-less base; every UID in «Пользователь» and every
    `runAsUser` in «Безопасность пода» equals that container's Dockerfile
    `USER`.
11. **Pod security.** Every `tmpfs:` path of an app service in the prod
    compose file is a write path of that container in «Безопасность пода».
12. **Resources.** «Ресурсы» has a row per long-running app container with
    the requests and the memory limit filled and a date line — or it reads
    «Не замерено», and so does the card's row.
13. **Dependencies.** Each variable in «Адрес в переменной» is in the
    «Переменные» table of a container its «Направление» names.
14. **DBA.** The PostgreSQL major equals the major of the database image in
    `docker-compose.test.yml`; the schema equals the `search_path` of the
    `migrate` service's `DATABASE_URL` in `docker-compose.test.yml`
    (`.env.example` holds that value empty); every `CREATE EXTENSION` in
    `documentation/db/migrations/*.sql` is named in «Расширения» (or the row
    says «нет» and there is none); every `GRANT` and `ALTER DEFAULT
    PRIVILEGES` statement of `docker/db-init/roles.sql` is in the section's
    SQL, whitespace aside — the database grant, which `roles.sql` builds
    with `format('%I', current_database())`, as `GRANT CREATE ON DATABASE
    <база> TO <migrate account>`; and `roles.sql` creates the migrate
    account itself, so neither app container connects as the database
    image's superuser (`POSTGRES_USER` in `docker-compose.test.yml` is in
    no app service's `DATABASE_URL`).
15. **Stop.** «Остановка» names `SHUTDOWN_TIMEOUT_SEC` with the config
    layer's default and recommends a `terminationGracePeriodSeconds` at
    least 5 s above it; `backend`'s `stop_grace_period` in the prod compose
    file is at least as long.
16. **Tracing.** «Трассировка» says «Нет.» exactly when `.env.example` has
    no `OTEL_` variable.

The failure message names the file to fix: «deploy.md: переменная
S3_BUCKET у backend есть в docker-compose.prod.yml, но нет в таблице
"Переменные"», «deploy.md: SECURE_MODE = false, допустимо plain или secure»,
«deploy.md: файл docker-compose.prod.yml в комплект не входит»,
«deploy.md: runAsUser backend 0, в Dockerfile USER 1000».

The test reads the document; whether the built folder really holds the
files is checked at build time — `scripts/build-images.sh` ends by looking
up each file `DEPLOY.md` names in `release/<version>/` and fails naming the
one that is missing. Someone who adds a variable, changes a port or a
`USER`, or adds an extension and forgets the document then finds out in CI,
not from the operators.
