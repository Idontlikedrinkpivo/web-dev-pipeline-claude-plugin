# The deploy document and its sync test

Read this in Step 8 while writing `documentation/deploy/deploy.md`, and in
Step 7 while writing its sync test.

The operators receive one folder per release: the image archive and
`DEPLOY.md`. They do not receive `docker-compose.prod.yml` — they run the
images in their own way (their compose, their orchestrator, their secrets
store), so they need the facts, not this project's file. The compose file
stays in the repo as the source those facts are taken from and as a way to
run the prod shape locally; the sync test keeps the two from drifting.

## Where it lives

- Source: `documentation/deploy/deploy.md`, in Russian, in git. **Unversioned**
  (`doc-versioning` → Registry): it is derived from the compose file and the
  config layer, and the sync test — not a version number — is what keeps it
  true. No `version`, no changelog, no `sources:`.
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

```markdown
# Развёртывание room-booking <версия>

Комплект: `room-booking-<версия>.tar` (образы `room-booking-backend:<тег>`,
`room-booking-frontend:<тег>`) и этот файл.

Загрузка образов: `docker load -i room-booking-<версия>.tar`

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

| Контейнер | Порт | Живость | Готовность |
|---|---|---|---|
| backend | 3000 | `GET /health` → 200 | `GET /health` → 200 |
| frontend | 8080 | `GET :8081/_healthz` → 200 | `GET :8081/_healthz` → 200 |
| migrate | — | — | — |

Наружу публикуется только `frontend:8080`. TLS и внешний прокси перед ним — на стороне эксплуатации;
`frontend` работает по HTTP, а адрес бэкенда получает из `BACKEND_SERVICE`.

## Переменные

### backend и migrate

| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |
|---|---|---|---|---|
| APP_ENV | да | нет | `prod` | окружение; без него приложение не стартует |
| DATABASE_URL | да | да | `postgres://user:***@host:5432/db?options=-c%20search_path%3Droom_booking` | подключение к PostgreSQL, схема `room_booking` |
| … | | | | |

### frontend

| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |
|---|---|---|---|---|
| BACKEND_SERVICE | да | нет | `backend:3000` | адрес бэкенда |
| BACKEND_PROTOCOL | да | нет | `http` | протокол до бэкенда |
| SECURE_MODE | да | нет | `false` | HTTPS внутри контейнера |

## Внешние зависимости

| Что | Требования |
|---|---|
| PostgreSQL 17 | отдельная схема `room_booking`; пользователю нужны права на создание таблиц в ней (для `migrate`) |
| S3-совместимое хранилище | бакет `room-booking-files`, чтение и запись |
| … | |

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
```

Where each section comes from:

| Section | Source |
|---|---|
| Контейнеры | `docker-compose.prod.yml` services, the Dockerfiles' `CMD`, the migrate command |
| Порядок запуска | `depends_on` conditions in `docker-compose.prod.yml` |
| Сеть и проверки | the container ports, the `healthcheck` commands, the published port |
| Переменные | each service's `environment:` / `env_file` in `docker-compose.prod.yml`, and `.env.example` for required / secret / format |
| Внешние зависимости | what `docker-compose.prod.yml` points outside itself; the schema name from `db-schema-design`; versions from the architecture |
| Состояние и тома | `volumes:` in `docker-compose.prod.yml` |
| Первый запуск | the architecture or SRS (how the first admin or seed data appears); ask the user when neither says |
| Обновление | fixed text above, with the project's names |

Secrets never appear with values — a format with `***` in place of the secret
part, or `<секрет>`.

## The sync test

Part of the compose-contract tests (Step 7), in the project's own test
runner. Parse `docker-compose.prod.yml` and `.env.example`, parse the tables
of `documentation/deploy/deploy.md` (they are plain Markdown tables with
fixed headers — split rows on `|`), and assert:

1. **Containers.** The set of services in the prod compose file equals the
   set of rows in «Контейнеры».
2. **Variables.** For each service, the variable names in its `environment:`
   and `env_file` (resolved through `.env.example`) equal the names in its
   «Переменные» table — a variable missing from the document, or a document
   row for a variable the compose file no longer sets, fails.
3. **Required and secret.** Each variable's «Обязательна» and «Секрет» cells
   match `.env.example`'s markers for it (whatever marker convention the
   project's `.env.example` uses — e.g. a `# required` / `# secret` comment).
4. **Ports and checks.** Each service's container port and health-check path
   in the compose file appear in its «Сеть и проверки» row.
5. **Volumes.** No `volumes:` in the prod compose file ⇔ the «Состояние и
   тома» section says there are none.

The failure message names the file to fix: «deploy.md: переменная
S3_BUCKET у backend есть в docker-compose.prod.yml, но нет в таблице
"Переменные"». Someone who adds a variable or changes a port and forgets the
document then finds out in CI, not from the operators.
