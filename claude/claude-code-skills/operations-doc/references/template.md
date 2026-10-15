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

## Журналы

Что система записывает о своей работе и где это увидеть.

| Журнал | Что в записи | Кто пишет | Сколько хранится | Как посмотреть | Где в системе |
|---|---|---|---|---|---|
| Отмены броней | бронь, кто отменил, когда, причина | отмена брони (UC-2), блокировка переговорной (UC-4) | 12 мес. после окончания брони (NFR-7) | что бронь отменена — экран S-1; кто и почему — только SQL — экрана нет; запрос З-1 | `bookings.cancelled_by_account_id`, `cancelled_at`, `cancel_reason` |
| Блокировки переговорных | переговорная, интервал, причина, кто закрыл | администратор (UC-4) | 12 мес. | интервал — экран S-1, вид администратора, и `viewSchedule`; кто закрыл — только SQL — экрана нет; запрос З-3 | `maintenance_blocks` |
| Письма об отмене | бронь, статус отправки, попытки, когда следующая | отмена из-за блокировки | 12 мес. | только SQL — экрана нет; запрос З-2 | `cancellation_emails`, `src/maintenance/adapters/jobs/cancellation-email-relay.ts` |

### Запросы

**З-1. Кто и когда отменил бронь.** `$1` — `booking_id` из API или с экрана.

```sql
SELECT b.public_id, b.status, b.cancelled_at, b.cancel_reason, a.full_name AS cancelled_by
FROM room_booking.bookings b
LEFT JOIN room_booking.accounts a ON a.id = b.cancelled_by_account_id
WHERE b.public_id = $1;
```

Имя отменившего показано, потому что задача — найти автора (NFR-12); email не выводится (NFR-5).

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
ФИО и email в логи не пишутся (NFR-5).

| Событие (`event`) | Когда | Поля | Тревога | Где в системе |
|---|---|---|---|---|
| `booking_rejected` | бронь отклонена | `code` (`BOOKING_OVERLAP`, …), `reqId` | нет; дашборд считает по `code` (NFR-16) | `src/bootstrap/error-handler.ts` |
| `cancellation_email_overdue` | письмо не ушло за 24 ч | `bookingId`, `attempts` | да — см. «Тревоги» | `cancellation-email-relay.ts` |

Отфильтровать по событию (строки stdout в файле или потоке):

```bash
jq -c 'select(.event == "booking_rejected") | {time, code, reqId}' backend.log
```

## Проверки и метрики

| Что | Как | Норма | Где в системе |
|---|---|---|---|
| Жив ли процесс | `GET /healthz` (без токена) | 200 | `src/bootstrap/server.ts` |
| Доступна ли БД | проверки нет — только по ошибкам 500 в логах; запрос готовности в системе нет | — | — |

## Фоновые процессы

| Процесс | Когда | Что делает | Как понять, что работает | Где в системе |
|---|---|---|---|---|
| Отправка писем об отмене | каждые 60 с | шлёт письма из очереди в A-3, повторяет 24 ч | в З-2 нет строк старше 5 мин с `attempts = 0` | `cancellation-email-relay.ts` |
| Очистка старых записей | 03:00 Europe/Moscow | удаляет брони и блокировки старше 12 мес. | З-4 возвращает 0 | `retention-purge.ts` |

## Тревоги

| Сигнал | Что значит | Что делать |
|---|---|---|
| `cancellation_email_overdue` в логах | A-3 не принимает письма больше суток | проверить доступность A-3 и `MAIL_API_KEY` (DEPLOY.md → Переменные); после восстановления письма уйдут сами — проверить З-2 |
| `/healthz` не отвечает | процесс упал или завис | перезапустить контейнер (DEPLOY.md → Порядок запуска); причину искать в последних строках лога |

## Типовые операции

Пронумерованная процедура: когда нужна, условие, точные шаги, как
проверить результат, как откатить. Операция, которой в системе нет,
пишется так, как её делают сегодня, с пометкой «в системе нет».

## Разбор проблем

| Симптом | Куда смотреть | Частая причина |
|---|---|---|
| Резидент не получил письмо об отмене | З-2 по его брони | A-3 недоступен — см. «Тревоги» |
| Бронь пропала из расписания | З-1 | отменена администратором или блокировкой — видно, кем |
````

## Rules

- **Ids.** Queries are `З-<n>`, procedures `П-<n>`, numbered in document
  order; rows refer to them.
- **A query** is read-only (SELECT only), schema-qualified, ordered and
  bounded (`LIMIT`), takes parameters as `$1`, `$2` with a line above
  naming each, and says why a personal field is shown when it is.
- **A log filter** works on JSON lines from the container's stdout — no
  path to a log file inside a container, no collector-specific syntax
  unless `deploy.md` names the collector.
- **«Где в системе»** names the table and columns, the file, or the
  operationId — enough to open the code without searching.
- **«только SQL — экрана нет»** marks a record an SRS role should see but
  no screen or operation shows; the stage's report lists each.
