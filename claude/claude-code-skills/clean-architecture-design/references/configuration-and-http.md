# Foundation §4 tables: configuration, service channels, HTTP errors

Read this while writing foundation §4 «Порты и адаптеры». Ports and their
signatures come first (SKILL.md → Mode `foundation`); these three tables
sit beside the composition root (сборка).

## Конфигурация

A table next to сборка, one row per переменная окружения (environment
variable) mentioned anywhere in the three architecture documents:

| Переменная | Тип | Обязательна | Если нет |
|---|---|---|---|
| `SESSION_SECRET` | string | да | процесс не стартует |
| `LOG_LEVEL` | string | нет | `info` |
| `SHUTDOWN_TIMEOUT_SEC` | integer | нет | `25` |

The security table keeps the decision («секрет только в env»). This
table is the inventory. A missing required variable means the process
does not start. An environment variable mentioned in prose and missing here
is a defect: the inventory is only useful if it is complete. Every HTTP
service has the `LOG_LEVEL` and `SHUTDOWN_TIMEOUT_SEC` rows: `repo-scaffold`
wires them (the log level; how long a stop may finish in-flight requests).

## Служебные каналы

The paths the platform calls — its probes and its metrics scraper. Every
HTTP service has the same three, on the app port, outside the OpenAPI
contract and outside auth; the frontend's proxy never forwards them.
`repo-scaffold` builds them and fixes their answers (its SKILL.md §5), so
neither OpenAPI nor a scenario describes them. One row each, plus one per
other служебный path §1 names:

| Путь | Владелец | Что вызывает |
|---|---|---|
| `GET /health/live` | `bootstrap/` | ничего — ни базы, ни партнёров: отказ базы не должен перезапускать каждый под |
| `GET /health/ready` | `bootstrap/` | пинг базы с таймаутом 2 с; `ready()` порта каждого другого хранилища, без которого приложение не обслуживает; никогда сторонний API |
| `GET /metrics` | `bootstrap/` | ничего — метрики процесса и гистограмма `http_request_duration_seconds` по шаблону маршрута |

The database ping runs on the pool `bootstrap/` already owns; another
store the readiness check needs (object storage, a queue) gives its
existing port the method `ready() -> bool`. §5 has a line for the file
that mounts the three. A service path in §1 with no row here, or a
readiness check that touches a store other than the database and adds no
port method, is a service path without an owner.

## HTTP

§4 does not inventory routes. Methods, paths, success codes, and bodies
belong to the OpenAPI spec. §4 owns one table, one row per named error
of domain model §3 (domain errors and use-case errors such as `not
found`, `Forbidden`). On greenfield the foundation is written first, so
it takes the names from the SRS rules and the error `code`s
`documentation/api/openapi.yaml` declares; the domain model then uses exactly those
names, and a name a later document needs is added here by the same
writer:

| Именованная ошибка | HTTP |
|---|---|
| `DuplicateSlug` | 409 |

Plus one paragraph: how routes are guarded (the mechanism — token,
middleware; which role may call which operation is the «Доступ» row of
each scenario), where the wire schema lives,
and the adapter codes that have no domain name, as `documentation/api/openapi.yaml`
declares them — a field failing its schema → 422 `VALIDATION_ERROR`, an
unparsable request → 400, rate limit → 429, anything unnamed → 500. A
scenario's Ошибки table names the error and the state policy. It does
not repeat the status.
