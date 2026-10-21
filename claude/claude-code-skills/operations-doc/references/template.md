# The operations document

`documentation/operations/operations.md`, unversioned (`doc-versioning` →
Registry), Russian. One document for two readers: the person who runs the
system reads the task columns; the developer on duty reads the «Где в
системе» column. Sections in this order; a section with nothing in it
says so in one line («Фоновых процессов нет»), never disappears.

Example: the room-booking sample — bookings, maintenance blocks, a queue of
cancellation letters to the mail service A-3, a nightly purge.

````markdown
# Эксплуатация room-booking

Как жить с системой после запуска: что она записывает, где это смотреть,
что делать при сбоях. Установка и обновление — в [DEPLOY.md](../deploy/deploy.md).
Запросы проверены на тестовом стенде: <YYYY-MM-DD>.

## Доступы

| Что нужно | Кому | Как получить |
|---|---|---|
| Экраны администратора | администратор коворкинга | claim `role=admin` в SSO |
| Чтение БД | дежурный разработчик | отдельной роли только для чтения в системе нет — читать под ролью приложения, только запросами этого документа (в отчёт: завести роль) |
| Логи контейнера `backend` | эксплуатация | сборщик логов площадки; формат — JSON по строке |

## Обязательные журналы

Журналы, которые система обязана вести. Их нельзя отключать, чистить раньше срока или
давать смотреть кому угодно.

| Журнал | Основание | Что в записи | Срок: требуется / в системе | Кто может смотреть | Как посмотреть | Где в системе |
|---|---|---|---|---|---|---|
| Кто и когда отменил бронь | требования безопасности заказчика | бронь, кто отменил, когда, причина | столько же, сколько бронь / 12 мес. после окончания брони — совпадает | администратор, дежурный разработчик | что бронь отменена — экран «Расписание»; кто и почему — только SQL — экрана нет; запрос З-1 | `bookings.cancelled_by_account_id`, `cancelled_at`, `cancel_reason` |
| Кто закрыл переговорную | требования безопасности заказчика | переговорная, интервал, причина, кто закрыл | столько же, сколько блокировка / 12 мес. — совпадает | администратор, дежурный разработчик | интервал — экран «Расписание», вид администратора; кто закрыл — только SQL — экрана нет; запрос З-3 | `maintenance_blocks` |

## Журналы

Что ещё система записывает о своей работе и где это увидеть.

| Журнал | Что в записи | Кто пишет | Сколько хранится | Как посмотреть | Где в системе |
|---|---|---|---|---|---|
| Письма об отмене | бронь, статус отправки, попытки, когда следующая | отмена из-за блокировки | 12 мес. | только SQL — экрана нет; запрос З-2 | `cancellation_emails`, `src/maintenance/adapters/jobs/cancellation-email-relay.ts` |

### Запросы

**З-1. Кто и когда отменил бронь.** `$1` — `booking_id` из API или с экрана.

```sql
SELECT b.public_id, b.status, b.cancelled_at, b.cancel_reason, a.full_name AS cancelled_by
FROM room_booking.bookings b
LEFT JOIN room_booking.accounts a ON a.id = b.cancelled_by_account_id
WHERE b.public_id = $1;
```

Имя отменившего показано, потому что задача — найти автора; email не выводится.

**З-2. Письма, которые не ушли.** Без параметров; последние 50.

```sql
SELECT e.id, b.public_id AS booking_id, e.status, e.attempts, e.next_attempt_at, e.created_at
FROM room_booking.cancellation_emails e
JOIN room_booking.bookings b ON b.id = e.booking_id
WHERE e.status = 'pending'
ORDER BY e.created_at
LIMIT 50;
```

**З-3. Кто закрыл переговорную.** `$1` — `block_id`.

```sql
SELECT m.public_id, m.starts_at, m.ends_at, m.reason, a.full_name AS closed_by, m.created_at
FROM room_booking.maintenance_blocks m
JOIN room_booking.accounts a ON a.id = m.created_by_account_id
WHERE m.public_id = $1;
```

**З-4. Записи старше срока хранения.** Без параметров; после ночной очистки — 0.

```sql
SELECT (SELECT count(*) FROM room_booking.bookings WHERE ends_at < now() - interval '12 months')
     + (SELECT count(*) FROM room_booking.maintenance_blocks WHERE ends_at < now() - interval '12 months') AS overdue;
```

## Логи

Контейнер `backend` пишет JSON по строке в stdout; любой сборщик логов их принимает.
У каждой строки есть `reqId` — по нему собираются все строки одного запроса.
ФИО и email в логи не пишутся.

| Событие (`event`) | Когда | Поля | Тревога | Где в системе |
|---|---|---|---|---|
| `booking_rejected` | бронь отклонена | `code` (`BOOKING_OVERLAP`, …), `reqId` | нет; дашборд считает по `code` | `src/bootstrap/error-handler.ts` |
| `cancellation_email_overdue` | письмо не ушло за 24 ч | `bookingId`, `attempts` | да — см. «Тревоги» | `cancellation-email-relay.ts` |

Отфильтровать по событию (строки stdout в файле или потоке):

```bash
jq -cR 'fromjson? | select(.event == "booking_rejected") | {time, code, reqId}' backend.log
```

## Проверки и метрики

| Что | Как | Норма | Где в системе |
|---|---|---|---|
| Жив ли процесс | `GET /healthz` (без токена) | 200 | `src/bootstrap/server.ts` |
| Доступна ли БД | проверки нет — только по ошибкам 500 в логах; запрос готовности в системе нет | — | — |

## Фоновые процессы

| Процесс | Когда | Что делает | Как понять, что работает | Где в системе |
|---|---|---|---|---|
| Отправка писем об отмене | каждые 60 с | шлёт письма из очереди в почтовый сервис, повторяет 24 ч | в З-2 нет строк старше 5 мин с `attempts = 0` | `cancellation-email-relay.ts` |
| Очистка старых записей | 03:00 Europe/Moscow | удаляет брони и блокировки старше 12 мес. | З-4 возвращает 0 | `retention-purge.ts` |

## Тревоги

| Сигнал | Что значит | Что делать |
|---|---|---|
| `cancellation_email_overdue` в логах | почтовый сервис не принимает письма больше суток | проверить доступность почтового сервиса и `MAIL_API_KEY` (DEPLOY.md → Переменные); после восстановления письма уйдут сами — проверить З-2 |
| `/healthz` не отвечает | процесс упал или завис | перезапустить контейнер (DEPLOY.md → Порядок запуска); причину искать в последних строках лога |

## Типовые операции

**П-1. Отправить застрявшее письмо, не дожидаясь следующей попытки.** В системе нет — делается
запросом в БД; в отчёт: кнопка у администратора.

- **Когда:** почтовый сервис снова работает, а письмо ждёт следующей попытки (З-2, `next_attempt_at` в будущем).
- **Условие:** письмо в статусе `pending`; `sent` не трогать — уйдёт второе письмо.
- **Шаги:** выполнить, подставив `id` из З-2:

```sql
UPDATE room_booking.cancellation_emails SET next_attempt_at = now()
WHERE id = $1 AND status = 'pending';
```

- **Проверка:** через минуту З-2 по этой строке пуст, у письма `status = 'sent'`.
- **Откат:** не нужен — меняется только время следующей попытки.

## Разбор проблем

| Симптом | Куда смотреть | Частая причина |
|---|---|---|
| Резидент не получил письмо об отмене | З-2 по его брони | почтовый сервис недоступен — см. «Тревоги» |
| Бронь пропала из расписания | З-1 | отменена администратором или блокировкой — видно, кем |
````

Write it to be scanned (`doc-versioning` → `references/readable.md`): a cell is one fact, a run of cases is a table, a procedure is a numbered list, a paragraph at most four sentences.

## Rules

- **Ids.** Queries are `З-<n>`, procedures `П-<n>`, numbered in document
  order; rows refer to them.
- **A query** is read-only (SELECT only), schema-qualified, ordered and
  bounded (`LIMIT`), takes parameters as `$1`, `$2` with a line above
  naming each, and says why a personal field is shown when it is.
- **A log filter** works on JSON lines from the container's stdout — no
  path to a log file inside a container, no collector-specific syntax
  unless `deploy.md` names the collector. It reads raw lines and skips what
  is not JSON (`jq -R 'fromjson? | …'`): a runtime writes its own warnings
  to the same stream, and a plain `jq` stops at the first one. The field
  names come from a real line of the stand's log, not from the logger's
  documentation (one request may be two lines — the address on the first,
  the status on the second).
- **«Обязательные журналы»** comes first after «Доступы» and holds only
  the required records (`required-records.md`); a section with none says
  «Обязательных журналов нет». A required record the system does not keep
  gets a row too: «не ведётся» in «Как посмотреть», and the report.
- **«Где в системе»** names the table and columns, the file, or the
  operationId — enough to open the code without searching.
- **No requirement ids.** No `FR-`, `NFR-`, `BR-`, `UC-`, actor or frame
  ids in the document: its readers run the system, not the project. Say the
  fact itself («хранится 12 месяцев», «email в логи не пишется») and name
  screens by their title («экран «Расписание»»). Ids stay in the stage's
  report, where the gaps are traced back to the SRS.
- **«только SQL — экрана нет»** marks a record an SRS role should see but
  no screen or operation shows; the stage's report lists each.
