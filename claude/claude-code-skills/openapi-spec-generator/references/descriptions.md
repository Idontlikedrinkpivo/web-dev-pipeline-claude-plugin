# Writing a description people can read

An operation's `description` is read by people — in the documentation site's Swagger page, by a frontend
developer, an analyst, a tester — not only by the agent that implements it. One dense paragraph with the rules in
a row and ids in the middle of sentences is correct and unreadable: the reader has to parse it like code. Write
it so the eye finds what it needs.

## The shape

1. **One plain sentence first**: what the operation does and for whom. No codes in it; only the use case's id
   may close it, in brackets.
2. **Short blocks with a bold lead-in** for each distinct concern, a blank line between blocks — «**Проверки по
   порядку.**», «**Режим external.**», «**Ответы.**», «**Ограничения.**». A description of three sentences needs
   no blocks.
3. **Steps and rules as a list**, one per line: an order of checks is a numbered list, independent rules a
   bulleted one. Never «(1) …; (2) …; (3) …» inside a sentence.
4. **Ids at the end of the line, in brackets** — «Пустой `login` не тратит попытку (NFR-10, UC-26 Exc-4).» — not in
   the middle of the sentence. The site links them and shows their text on hover; the sentence must read without
   them.
5. **Codes and literals in backticks only when they are literal** — a field, a value, a header, an error body.
   Not every noun.
6. **A table** (Markdown) for a mapping: an external system's answer → this API's response, a status → its
   meaning.

Schema and parameter descriptions follow the same idea in small: one sentence of meaning, then the limits, ids
last.

## Example — `bookRoom` (room booking)

Not this:

```yaml
description: Создаёт бронь (UC-1). Начало и конец кратны 30 минутам, не короче 30 минут и в рабочих часах (BR-2), сумма активных броней резидента за дату не больше 4 часов (BR-3) — иначе 422 BOOKING_RULE_VIOLATED; не пересекается с активными бронями и блокировками переговорной (BR-1) — иначе 409 BOOKING_OVERLAP; не больше 30 запросов в минуту на резидента (NFR-10), 31-й — 429; владелец — вошедший резидент из токена.
```

This:

```yaml
description: |
  Резидент бронирует свободный интервал переговорной на себя (UC-1).

  **Правила интервала.**
  - Начало и конец кратны 30 минутам, бронь не короче 30 минут и целиком в рабочих часах (BR-2).
  - Все активные брони резидента на эту дату вместе — не больше 4 часов (BR-3).
  - Нарушено одно из этих правил — `422 BOOKING_RULE_VIOLATED`.
  - Интервал пересекается с активной бронью или закрытием переговорной — `409 BOOKING_OVERLAP` (BR-1).

  **Владелец.** Бронь всегда на вошедшего резидента: он берётся из токена, в теле его нет.

  **Ограничение частоты.** Не больше 30 запросов на бронь в минуту на резидента, 31-й получает `429` (NFR-10).
```

## The API's own description (`info.description`)

What every operation shares — roles, signing in, access errors, rate limits, the error body, service addresses —
is written once, here, and Swagger shows it above the operations. It is the first thing a reader meets, so it is
a page, not a paragraph:

1. **Two or three plain sentences**: what the API is for and who calls it. The source documents by name, not as
   a run of paths.
2. **A `###` heading per shared concern**, only those this API has, in this order: «Роли», «Вход и сессии»,
   «Доступ без входа», «Ошибки доступа», «Ограничения частоты», «Ошибки», «Служебные адреса».
3. **Under each heading** — a list or a small table, one rule per line, ids at the end in brackets; the same
   rules as an operation's description.
4. **Nothing an operation owns.** A rule of one operation lives in that operation's description; this one names
   only what repeats.

Example — the room-booking contract:

```yaml
description: |
  API бронирования переговорных коворкинга «Точка сбора». Им пользуется веб-приложение резидентов и
  администратора. Основание — SRS бронирования и схема данных.

  ### Роли
  - **Резидент** — смотрит расписание, бронирует и отменяет свои брони.
  - **Администратор** — отменяет любые брони и закрывает переговорные на обслуживание (NFR-4).

  ### Вход и сессии
  - Вход только через SSO коворкинга; каждый запрос несёт `Authorization: Bearer <JWT>` (NFR-3).
  - Роль берётся из токена: claim `role=admin` — администратор, иначе резидент (NFR-3).

  ### Ошибки доступа
  | Ситуация | Ответ |
  |---|---|
  | нет токена или он недействителен | `401` |
  | резидент отменяет чужую бронь | `403 BOOKING_NOT_OWNED` (NFR-4) |
  | резидент закрывает переговорную | `403 ADMIN_ONLY` (NFR-4) |

  ### Ограничения частоты
  - Создание брони — не больше 30 запросов в минуту на резидента, 31-й получает `429` (NFR-10).

  ### Ошибки
  - Тело любой ошибки — `application/problem+json` со стабильным `code`.
```
