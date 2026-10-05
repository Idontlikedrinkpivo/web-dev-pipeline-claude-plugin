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

The security table keeps the decision («секрет только в env»). This
table is the inventory. A missing required variable means the process
does not start. An environment variable mentioned in prose and missing here
is a defect: the inventory is only useful if it is complete.

## Служебные каналы

One row per служебный path from §1. No scenario in any scenarios
document. If the channel touches a store, an existing port gains the
method (`ready() -> bool`), and §5 has a line for the file that mounts
the probe. Response shape
stays in OpenAPI.

| Путь | Владелец | Что вызывает |
|---|---|---|
| `GET /healthz` | `bootstrap/` | ничего |
| `GET /readyz` | `bootstrap/` | проверка хранилища, `ready()` порта |

A `/healthz`-class path in §1 with no row here, or a readiness check that
touches a store and adds no port method, is a service path without an
owner.

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
