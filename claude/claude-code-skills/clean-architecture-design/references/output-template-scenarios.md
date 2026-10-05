# Output template — scenarios of one area (`documentation/architecture/scenarios/<area>/<area>.md`)

Read this when writing or editing a scenarios document (mode
`scenarios:<area>`). One living document per functional area, edited in
place by every increment that touches the area; a new area gets a new
folder `scenarios/<area>/`. Use these sections in this order; skip an empty one with a single
line saying why.

`<area>` is the area's kebab-case English name from foundation §2 — the
same word as the module folder in foundation §5 and the SRS group it
covers.

What this document does **not** hold: a business rule (it cites the
domain model's invariant row by rule id), a named error's definition
(domain model §3), an HTTP status (foundation §4), a port signature
(foundation §4), a route, path or body (OpenAPI). Why use cases, queries
and side effects take this shape: `use-cases-and-boundaries.md`.
`<версия>` is the open iteration's service version (`0.1.0` on
greenfield; a new area born later takes that iteration's); each pin names
the version of the source it was read at.

```markdown
---
version: <версия>
updated: YYYY-MM-DD
sources:
  - documentation/requirements/srs/srs.md@<версия SRS>
  - documentation/api/openapi.yaml@<версия API>
  - documentation/architecture/architecture.md@<версия фундамента>
  - documentation/architecture/domain.md@<версия доменной модели>
---

# Сценарии: <область>

## Журнал изменений

| Версия | Дата | Изменение | Тип | Кого затрагивает |
|---|---|---|---|---|
| <версия> | <дата> | первый выпуск | — | — |

## Область

| | |
|---|---|
| Область | `<area>` |
| Группа SRS | <жирный подзаголовок группы FR, дословно>; UC-n, … |
| Модуль | `<root>/<area>/` (фундамент §5) |
| Сущности | <имена из доменной модели §2, которыми владеет область> |

## Сценарии
Указатель, если сценариев больше четырёх: Сценарий · Операция API · одна
фраза. Дальше — подраздел на каждое действие, меняющее состояние.

### <UseCaseName> — `<root>/<area>/application/<file>.<ext>`

| | |
|---|---|
| Вход | `<UseCaseName>Input` — актор, id, значения пользователя. Не транспортный запрос |
| Доступ | кто может вызвать (роль из §1 фундамента), id правила SRS; проверка владения — шаг 1 |
| Выход | `<UseCaseName>Result`, сущность или `unit` — в пределах уровня |
| Операция API | `operationId` из `documentation/api/openapi.yaml` (или вход из §1 «API»: CLI, очередь, cron) |
| Последовательность | [<use-case-kebab>](diagrams/<use-case-kebab>.svg) — Markdown-ссылка, только у ключевого сценария |

| N | Шаг | Порт / метод сущности | Транзакция |
|---|---|---|---|
| 1 | загрузить `<Entity>` | `<Entity>Repository.get` | — |
| 2 | спросить сущность (BR-3) | `<Entity>.<method>` | — |
| 3 | сохранить; записать намерение доставки | `<Entity>Repository.save`, `Outbox.add` | начало ┐ |
| 4 | … | … | конец ┘ |

| Ошибка | Шаг | Состояние / политика |
|---|---|---|
| `<NamedError>` | 2 | остаётся ли состояние |
| внешняя система | 4 | outbox (по умолчанию для «должен») или в запросе; что если она недоступна |

## Запросы

| Запрос | Сигнатура | Модель | Операция API | Источник строк |
|---|---|---|---|---|
| `<Area>Queries.<method>` | `(...) -> <ReadModel> \| not found` | `<ReadModel>` | `operationId` | сценарий `<Name>` / сид / константа / внешний синк / вне этого инкремента |

Модели чтения — поля каждой модели, один раз, таблицей под запросами:
Модель · Поле · Тип · Откуда (колонка схемы / метод сущности).
```

## Per-section rules

- **Шаги** — the Порт / метод column names methods only; every port
  signature is written once, in foundation §4, and every entity method
  once, in the domain model. A rule is cited by its id (`BR-3`) at the
  step that asks the entity; the rule's words stay in the domain model.
  The Транзакция column marks where the transaction opens and closes;
  a step outside it says `—`. A transaction that spans an external call
  is a key scenario (below).
- **Ошибки** — only names from domain model §3. A name missing there is
  added there (SKILL.md → Writer, `ALSO CHANGED`), not defined here. No HTTP
  status in this table. The policy column is a contract: whether state
  remains; in-request / must / outbox.
- **Idempotent request** — the repeat returns what the first call
  returned (stored with the key); say so in Ошибки.
- **Запросы** — reads are not use cases and never return the entity.
  «Источник строк» names the scenario that writes the rows; a read with
  no write scenario anywhere names where its first row comes from. An
  empty cell is a hole.
- **Доступ** — the access policy for this operation is homed here, with
  its BR id. The guard mechanism (token, middleware) is foundation §4.

## Key scenarios and their sequence diagrams

A scenario is **key** when any of these holds: it calls three or more
ports or external systems; it makes calls in parallel; a transaction
spans an external call; it retries or deduplicates (idempotency key,
provider event id); it runs long (a job, a poll, a multi-step
operation). A key scenario gets a sequence diagram
`scenarios/<area>/diagrams/<use-case-kebab>.puml` (PlantUML) and its
`.svg`, next to this document, linked from the «Последовательность» row
by a Markdown link, `[<use-case-kebab>](diagrams/<use-case-kebab>.svg)`
(a path in backticks is not a link). A plain read-and-return or
load-ask-save scenario gets no diagram and no row, and an area with no
key scenario has no `diagrams/` folder.

The diagram shows the same steps as the Шаги table, with the same port
and method names, and nothing else. Shape and render:
`architecture-diagram.md` → Sequence view.
