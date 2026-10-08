# The report — `security-audit.md`

Read before creating the report (Progress and report). It lives in
`documentation/plans/<version>/`, out of git; it is the stage's progress
file and its result. The first line is the verdict, so `pipeline` and
`deploy-topology` read it like the other check reports.

````markdown
Verdict: идёт аудит
# Аудит безопасности — итерация 1.2.0

```text
██████████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 62%
```

Сделано: 5 из 8 · P0 0 · P1 2 · P2 3 · P3 1

| Шаг | Статус | Итог |
|---|---|---|
| Зависимости (osv-scanner) | ✅ готово | 2 уязвимости, 1 в коде прода |
| Секреты (gitleaks) | ✅ готово | 0 |
| Шаблоны (semgrep) | ✅ готово | 7 срабатываний → разбор |
| Область «Бронирования» | ✅ готово | P1 1 |
| Область «Обслуживание» | 🔍 аудит | |
| Приложение целиком | ⏳ ждёт | |
| Проверка находок | ⏳ ждёт | |

## Матрица доступа

| Операция | Метод и путь | Кто может | Чьи данные | Проверка в коде |
|---|---|---|---|---|
| `cancelBooking` | POST /bookings/{booking_id}/cancel | автор брони (BR-4) | владелец брони | ❌ F2 — владелец не проверяется |
| `viewMyBookings` | GET /me/bookings | резидент | свои | ✅ `my-bookings/adapters/http/routes.ts:21` |

## Находки

| F | Важность | Где | Что | Решение |
|---|---|---|---|---|
| F2 | P1 | `bookings/application/cancel-booking.ts:34` | любой резидент отменяет чужую бронь: `POST /bookings/<чужой id>/cancel` | исправить |
| F4 | P2 | `bootstrap/error-handler.ts:12` | в ответе 500 — текст SQL-ошибки | в отчёт |

Под таблицей — каждая P0/P1 подробно: как воспользоваться, что нарушает,
как исправить.

## Принятый риск

| F | Почему принят | Кто решил |
|---|---|---|

## Отклонено при проверке

| F | Почему не подтвердилось |
|---|---|

Состояние: аудитор области «Обслуживание» · обновлено 2026-10-08 14:20
````

The first line moves `идёт аудит` → `PASS` or `FIX` (open P0/P1). An open
P0 adds `· релиз заблокирован`; the user's «собирать всё равно» is written
under «Принятый риск» with the date. A scanner that did not run adds
`· не запускался: <сканер>` to the verdict line.

Rows: `⏳ ждёт`, `🔄 в работе` (a scanner), `🔍 аудит` (an auditor
dispatched), `✅ готово`, `⚠️ не запускался: <причина>`. The bar counts
`✅` and `⚠️`. «Решение» per finding: `исправить`, `риск принят`,
`отложено`, `в отчёт` (P2/P3).

`deploy-topology` adds a section «Образы» when it scans the built images
(Step 8): image, HIGH/CRITICAL count, what the base image update fixes.

A re-audit after a fix plan rewrites the verdict line and the rows it
re-ran, marks fixed findings `✅ исправлено <commit>`, and keeps the rest.
