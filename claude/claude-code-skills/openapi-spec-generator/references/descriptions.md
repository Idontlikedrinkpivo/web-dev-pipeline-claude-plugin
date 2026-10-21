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
