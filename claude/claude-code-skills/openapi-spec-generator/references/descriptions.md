# Writing descriptions people can read

The contract's descriptions are read in the documentation site's Swagger page by the people who call the API — a
frontend developer, a tester, an analyst, an integrator. Write for them: what the operation does, who may call it,
what to send, what comes back and when. A description that walks through the server's checks step by step, names
tables and hashes and repeats one rule in four places is correct and unreadable.

## Where each thing goes

Swagger shows every part of the contract in its own place; put a fact where the reader looks for it, and only
there.

| Part | What it says |
|---|---|
| operation `description` | what the operation does and for whom; who may call it and when; what the body must be; side effects the caller sees; its rate limit |
| a response's `description` | when this answer comes — every case, in plain words; what was and was not written |
| schema and property `description` | what the value means, its format and limits |
| `info.description` | what every operation shares: roles, signing in, the error bodies, rate limits, caching, service addresses |

An operation's description does not list its error statuses: each response says when it comes. It may name a
status where the sentence needs it — «остальным — `403`».

## What stays out

How the server does it is the architecture's: the order of internal checks, normalization algorithms, table and
column names, hashes, transactions, what goes to the log, retries, timing defences, decision dates, internal class
names. The implementer reads the architecture anyway. Keep what changes what a caller sends or gets back: limits,
error codes and bodies, who may do what, visible side effects, exact numbers.

A rare edge case is generalized, not enumerated: «`login` не похож на email», not five Unicode cases. When an
existing contract is rewritten, check that every detail taken out already lives in the architecture
(`architecture.md`, `domain.md`, the scenarios) or the SRS; one that lives nowhere else stays, in a sentence.

## How to write

1. **Plain sentences in short paragraphs**, two to four sentences each. The first sentence says what the
   operation does, with the use case's id at its end.
2. **Each fact once.** A rule that holds for the whole operation is said once, not again under every case.
3. **A list only for parallel items** — modes, roles, columns, cases of one answer, three or more conditions. Not
   a paragraph chopped into one-sentence bullets, and no bold heading over every two lines. A long description
   (a file format, several concerns) may open a paragraph with a short bold word — «**Файл.**» — and no more.
4. **A table for a mapping**: who → in which statuses, a cause → the response body, an external answer → this
   API's answer.
5. **Ids at the end of the sentence, in brackets** — the site links them and shows their text on hover; the
   sentence must read without them. Not every id: the one or two that define the rule.
6. **Backticks only for literals** — a field, a value, a header, a status, an error body.
7. **Plain Russian**, active verbs, third person: «Возвращает…», «Портал заводит…». No «осуществляет»,
   «данный», «в рамках».

## Example — `bookRoom` (room booking)

Not this — the server's algorithm, every rule with its error inline:

```yaml
description: Создаёт бронь (UC-1). Начало и конец кратны 30 минутам, не короче 30 минут и в рабочих часах (BR-2), сумма активных броней резидента за дату не больше 4 часов (BR-3) — иначе 422 BOOKING_RULE_VIOLATED; не пересекается с активными бронями и блокировками переговорной (BR-1) — иначе 409 BOOKING_OVERLAP; не больше 30 запросов в минуту на резидента (NFR-10), 31-й — 429; владелец — вошедший резидент из токена.
```

This — the operation says what it does and what the interval must be; each response says when it comes:

```yaml
post:
  operationId: bookRoom
  description: |
    Резидент бронирует свободный интервал переговорной на себя (UC-1). Владелец брони — всегда тот, кто вошёл;
    в теле его нет.

    Интервал начинается и заканчивается на границе получаса, длится не меньше 30 минут и целиком лежит в рабочих
    часах (BR-2). Все активные брони резидента на одну дату вместе — не больше 4 часов (BR-3).

    Не больше 30 запросов в минуту на резидента (NFR-10).
  responses:
    '409':
      description: |
        Интервал пересекается с активной бронью или закрытием переговорной (BR-1). Бронь не создана.
    '422':
      description: |
        Интервал нарушает правило брони: не на границе получаса, короче 30 минут, выходит за рабочие часы или
        превышает 4 часа броней резидента за дату (BR-2, BR-3). Бронь не создана.
```

## The API's own description (`info.description`)

It is the first thing a reader meets, above the operations — a short page:

1. **Two or three sentences**: what the product is, who calls this API, what can be read without signing in.
2. **A `###` heading per shared concern**, only those this API has: «Роли», «Вход и сессия», «Ошибки»,
   «Пределы частоты», «Кеширование», «Служебные адреса», «Имена полей».
3. **Under each heading** — a paragraph, or a table where the content is a mapping (role → what it may do,
   status → when, operations → limit). The same rules as above: each fact once, nothing of the implementation,
   nothing a single operation owns.

Example — the room-booking contract:

```yaml
description: |
  API бронирования переговорных коворкинга «Точка сбора». Им пользуется веб-приложение резидентов и
  администратора. Все операции — только после входа (NFR-3).

  ### Роли

  | Роль | Что может |
  |---|---|
  | резидент | смотреть расписание, бронировать переговорные на себя, отменять свои брони |
  | администратор | то же, а ещё отменять любые брони и закрывать переговорные на обслуживание (NFR-4) |

  ### Вход и сессия

  Вход — только через SSO коворкинга. Каждый запрос несёт полученный там токен в заголовке
  `Authorization: Bearer <JWT>`; роль берётся из него: `role=admin` — администратор, иначе резидент (NFR-3).

  ### Ошибки

  Тело ошибки — `application/problem+json` с постоянным `code`; когда приходит каждый ответ, сказано в операции.

  | Ответ | Когда |
  |---|---|
  | `401` | токена нет или он недействителен |
  | `403 BOOKING_NOT_OWNED` | резидент отменяет чужую бронь (NFR-4) |
  | `403 ADMIN_ONLY` | резидент закрывает переговорную (NFR-4) |
  | `429` | превышен предел частоты |

  ### Пределы частоты

  Создание брони — не больше 30 запросов в минуту на резидента (NFR-10). У остальных операций предела нет.
```
