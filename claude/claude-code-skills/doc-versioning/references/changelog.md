# Changelog table

Read before a commit stamps a row, and when `doc-review` checks one.
Placement and the one-row-per-change rule are in `SKILL.md` → Changelog;
the types are in `SKILL.md` → What a version is. This file holds the
columns, the example, and what each cell must carry.

## Where the table lives

On the SRS the table is `## Журнал изменений`, immediately after the H1.
On the DB schema it is `## Changelog`, immediately after the H1 (after a
stale banner, if any). On the architecture foundation it is
`## Журнал изменений`, after `## Описание системы` the architecture skill
requires — not the first body block. The domain model, the scenarios of an
area and each screen spec put `## Журнал изменений` right after the H1. A
plan has none.

The headings stay as each stage froze them; the columns are the same five
on every document.

Unversioned rows (`SKILL.md` → Registry) and the parking lot have no table;
neither do `*.d2`, `*.puml` and rendered `*.svg`.

## Shape

Newest row first; the first row's `Версия` matches `version` in the
frontmatter. A greenfield document starts with one «первый выпуск» row at
the iteration's version, typed «—».

```markdown
# Бронирование переговорных — SRS

## Журнал изменений

| Версия | Дата | Изменение | Тип | Кого затрагивает |
|---|---|---|---|---|
| 1.2.0 | 2026-10-05 | UC-5 «Отмена брони» — новый сценарий | добавляет | OpenAPI (операция отмены), сценарии bookings, экран S-2 |
| 1.2.0 | 2026-10-05 | BR-3: лимит 4 ч → 6 ч. Было 4 ч; заказчик продлил рабочий день переговорных | ломает | доменная модель — обновить инвариант брони; ТЗ S-1 — обновить текст ошибки; схема БД — не затронута (лимит не хранится) |
| 1.2.0 | 2026-10-05 | FR-9 устарел, заменён FR-13 | ломает | сценарии bookings — убрать путь FR-9; OpenAPI — операция `listSlots` помечается `deprecated` |
| 1.1.0 | 2026-09-20 | FR-2 переформулировано, смысл прежний | уточняет | — |
| 0.1.0 | 2026-09-01 | первый выпуск | — | — |
```

Cell prose is Russian; the `Тип` cell is exactly one of `ломает`,
`добавляет`, `уточняет`, or `—` on the «первый выпуск» row. An empty field
is `—`, not a blank cell and not omitted.

## What each cell must carry

- **`Версия`** is the iteration's version (the open `plans/<version>/`),
  the same on every row a commit of that iteration writes.
- **`Изменение` names the cited token and the delta.** On a «ломает» row it
  also says what it was and why it changed: a future reader needs to know
  whether a rule was wrong or the product moved. A deprecation names what
  replaces it; a genuine removal is prefixed `удалён:` with where you
  looked (`SKILL.md` → ID stability).
- **One row per changed cited token**, or a tight group of tokens that
  changed for one reason (`FR-12–FR-14 — новые требования к отмене`). A
  commit with three unrelated changes writes three rows, each typed on its
  own: a «добавляет» must not hide inside a «ломает» row, or the other way
  round, because the service level and the cascade are read from the type.
- **`Кого затрагивает`** comes from the writer's downstream verdict:
  - «ломает» — a verdict per consumer from the registry row: must update
    (and what), or unaffected *with the reason*. "TBD" is not a verdict.
  - «добавляет» — where the new thing is expected to land (the operation,
    the scenario, the screen); `docs-consistency` checks it did.
  - «уточняет» — `—`.
- No process exhaust. Not "reviewed the document", not "ran the skill".
- A token that already has a row of this version gets that row amended,
  not a second row (`SKILL.md` → When a version is born).
- Do not also keep a changelog at the end. One table, one place.

## OpenAPI

`documentation/api/openapi.yaml` has no markdown table. Its number is
`info.version` and its rows are the list `info.x-changelog`, newest first,
with the same five fields; the stamp writes both.

```yaml
info:
  version: "1.2.0"
  x-changelog:
    - version: "1.2.0"
      date: 2026-10-05
      change: "cancelBooking — новая операция"
      type: добавляет
      affects: "сценарии bookings, экран S-2"
    - version: "0.1.0"
      date: 2026-09-01
      change: первый выпуск
      type: "—"
      affects: "—"
```

When only the project's own client calls the API, `info.version` is the
service version and a «ломает» row may ship in any release. When the API
has external consumers, `info.version` is the contract's own SemVer and the
rows carry that number: a «ломает» row exists only together with a new path
prefix (`/v2`), and the stamp raises the contract's major; «добавляет»
raises its minor, «уточняет» its patch.

A change of the spec does not add a row to the architecture journal, the
schema journal, or the SRS journal, and an operation-only change is not
parked in the schema changelog.

## Old tables

A document written before the service-version scheme has a table with the
columns `Версия · Дата · Класс · Добавлено · Изменено · …` (or `Version ·
Date · Class · …`), rows `3.0` / `major`. Nothing converts it in bulk. The
commit that next stamps the document puts the five-column table in the
frozen place and leaves the old table directly below it, unchanged, under
the line «Журнал до перехода на версии сервиса:». Readers take an old
`major` row as «ломает» and a `minor` row as «уточняет»; an old number
precedes every service version, whatever its digits (`SKILL.md` → Moving
from the old numbers).

A document that still has its changelog at the bottom, or `### v…` blocks,
is moved to this table on its next stamp — not on a change with no row.
