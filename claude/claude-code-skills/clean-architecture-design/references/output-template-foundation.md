# Output template — foundation (`documentation/architecture/architecture.md`)

Read this when writing or editing the foundation document (mode
`foundation`). Use these sections in this order; skip an empty one with a
single line saying why. Sub-items marked *(Full)* appear only at that
level. Omit a `sources:` pin for a stage the pipeline skipped (no schema,
no HTTP). `<версия>` is the open iteration's service version (`0.1.0` on
greenfield); each pin names the version of the source it was read at.

The notes under each heading are writer instructions, not text to copy.
Headings and words the file never contains are listed once, in SKILL.md →
Guardrails.

What this document does **not** hold, because another document owns it:
entities, value objects, named errors, the invariant table, boundary
checks (domain model); use cases, their steps, queries and read models
(scenarios of each area). The foundation names those by count or by
pointer, never by copying.

```markdown
---
version: <версия>
updated: YYYY-MM-DD
sources:
  - documentation/requirements/srs/srs.md@<версия SRS>
  - documentation/db/schema.md@<версия схемы>
  - documentation/api/openapi.yaml@<версия API>
---

# Архитектура: <система / фича>

## Описание системы
<один–два абзаца: что это, кто пишет и кто читает, что вне скоупа>

## Журнал изменений

| Версия | Дата | Изменение | Тип | Кого затрагивает |
|---|---|---|---|---|
| <версия> | <дата> | первый выпуск | — | — |

## 1. Состав системы
Сразу под заголовком — `![Контекст](diagrams/context.svg)`, под ним
`![Контейнеры](diagrams/containers.svg)` или одна фраза «Один процесс —
`<имя>`; схемы контейнеров нет.». Под таблицей «Хранилища» —
`![Хранилища](diagrams/stores.svg)`. Дальше таблицы, одна строка — один
факт: Акторы · Хранилища · Внешние системы · API · Стек · Решения по безопасности *(всегда: каждый из одиннадцати
пунктов — решение или `Не применимо — <причина>`)* · Принятые риски
*(только когда пользователь принял риск по находке аудита безопасности:
Риск · Находка — версия аудита и её id, `0.1.0 F-1` · Почему принят —
словами пользователя · Дата; таблицы нет, пока рисков нет)* · Решения по NFR
*(каждая не-security строка SRS §4)* · Ключевые решения *(всегда: Уровень,
Стек, затем только решения с названной альтернативой)*. Списки в ячейке
через `;` не склеивать. Акторы — имена (`Anonymous`, `Admin`).
Хранилища — store + для чего в этом проекте,
не каталог таблиц. Внешние системы — партнёры, которыми мы не владеем;
наша БД и объектное хранилище сюда не входят; нет партнёров — одна строка
«нет». API — только живые входы (REST, CLI, очередь, cron), второй вход —
ещё одна строка; строк «нет» не писать. Стек — рантайм с мажорными
версиями, «Почему эта» — 2–4 предложения: единственное место, где
объяснён выбор технологий; строка СУБД — копия первой строки
`documentation/db/schema.md` «Решения по базе» со ссылкой на неё (СУБД и её
версию решает этап схемы, не этот документ); локальный запуск — §5
«Локальный запуск», линтер границ — §6.
Уровень и стек — строки «Ключевых решений», не отдельные разделы; строка
«Стек» там записывает выбор и отвергнутые варианты, а в «Почему» — кто
выбрал и `см. §1 «Стек»`, без повтора причин. Сущностей, сценариев и чтений здесь нет — они в доменной модели
и в документах сценариев.

## 2. Модули и функциональные области
Таблица, строка на область, всегда (даже одна область):
Область · Модуль (папка §5) · Группы SRS · Сценарии · Владеет
состоянием · Берёт у других областей · Потребители контракта. Область — kebab-case на английском
(`bookings`), совпадает с папкой модуля и с `<area>` в пути документов
сценариев. Группы SRS — жирные подзаголовки групп FR, которые область
реализует, дословно. Сценарии — папка `scenarios/<area>/`: в ней документ
на каждую группу, `scenarios/<area>/<group>.md`. Владеет состоянием — имена
сущностей из доменной модели, без описаний. Потребители контракта — кто
сломается при смене контракта области: версия API, партнёр, другая
область, задание. Берёт у других областей — типы, порты и сценарии
другой области по именам (`PaymentId` из `top-ups`, `Wallet` из `ledger`)
или «—»; заполняется по набросанным сценариям и сигнатурам сущностей.
Общий модуль (у которого берут несколько областей) сам ничего у областей
не берёт: тип, который принимает его метод, лежит в нём или в
`shared/domain`. Импорт или вызов одной области из другой — только тот,
что назван в этой таблице; §6 разрешает ровно его, не шире. Под таблицей —
`![Модули](diagrams/modules.svg)` при двух и более областях, иначе одна
фраза «Одна область; схемы модулей нет.».

## 3. Границы и поток данных
Состав слоёв: ячейка артефактов — счётчик и ссылка (доменная модель §1–§3
/ документы сценариев / §4 / §5), не список имён и не подгруппы через
`<br>`. Под составом слоёв — `![Слои](diagrams/layers.svg)`. Правило
зависимостей — кто что импортирует, без лекции про поток управления и
интерфейс.

## 4. Порты и адаптеры
Каждый порт — сигнатуры, и поля каждого именованного типа в сигнатуре,
если это не тип доменной модели (тот определён там) · Порт → адаптер ·
Отказ внешнего вызова · Откат и уборка (одна политика: что откатывается, в каком порядке, что если откат не
удался; один помощник и его модуль — сценарии ссылаются на него) · Форматы файлов (колонка → поле → пустая ячейка) ·
Сборка · Конфигурация (переменная · тип · обязательна · если нет; у
HTTP-сервиса всегда есть `LOG_LEVEL` и `SHUTDOWN_TIMEOUT_SEC`) · Служебные
каналы (путь · владелец · что вызывает; у HTTP-сервиса всегда
`GET /health/live`, `GET /health/ready`, `GET /metrics` — их нет в OpenAPI) · таблица «именованная
ошибка → HTTP» (имена — из доменной модели §3 и из `code` в
`documentation/api/openapi.yaml`) — одна на всё приложение, в одном модуле
перевода; маршруты не переводят ошибки сами, а сбой с потерянным ответом
пишет одну строку в лог с причиной — и абзац: охрана маршрутов (механизм — токен,
middleware; кто какую операцию вызывает — строка «Доступ» в сценарии),
где лежит wire-схема, коды адаптера без доменного имени (поле не прошло
схему → 422 `VALIDATION_ERROR`, неразбираемый запрос → 400, лимит → 429,
неименованное → 500 — как в `documentation/api/openapi.yaml`). Перечень маршрутов
(метод, путь, код успеха, тело) не писать — им владеет OpenAPI. Схему БД
не проектировать.

## 5. Дерево файлов
Конкретные имена, без `…` и плейсхолдеров, по области, затем по слою.
Строкой здесь — файлы, которыми владеет этот документ: порты, адаптеры,
мапперы, модели хранения, `bootstrap/`, конфиг. Папки `domain/` и
`application/` каждой области — строкой-папкой с комментарием, где их
файлы: `# файлы сущностей — domain.md`, `# файлы сценариев —
scenarios/<area>/<group>.md`. Один артефакт на файл.

### Локальный запуск
Под деревом, всегда: Compose или нет и какие процессы он поднимает (база,
приложение, фронтенд); как применяются миграции из
`documentation/db/migrations/` (команда — её подключает `repo-scaffold`);
порты по умолчанию. Нет хранилища — одна строка «базы нет». `repo-scaffold`
строит запуск и проверяет миграции по этому разделу.

## 6. Проверки и тесты
Направление импортов · правила линта таблицей (откуда → что нельзя
импортировать), для каждой части — фронтенда тоже (страница и компонент не
ходят в сеть мимо слоя запросов), без файла конфига — его пишет `repo-scaffold`;
пороги качества — строкой «как в `repo-scaffold/references/quality-gates.md`»
или своими значениями, если строже; файл сценария не импортирует другой — общие
шаги в модуле, который назван в §5; при двух и
более областях — запрет импорта между областями, кроме названного в §2
«Берёт у других областей» · структурные тесты · план тестов: строка на
тестовый файл или на группу по слою («тест сущности на каждую строку
инвариантов доменной модели»), не строка на проверку; правило — по id
(`BR-3`), не значением. Строка инварианта над множеством значений — формат,
диапазон, преобразование туда и обратно, «кто правит — тот видит» — получает
тест свойства («для любых входов…», `fast-check` / `hypothesis`); строки с
бизнес-правилами — ещё и мутационную проверку их тестов
(`repo-scaffold/references/quality-gates.md`).
```

## §1 «Ключевые решения»

The last §1 table: Решение · Выбрано · Вместо · Почему. Row 1 is always
`Уровень` (name the Full trigger when one fired); row 2 is `Стек`,
«Вместо» naming the cards not picked, «Почему» saying who picked it and
citing §1 «Стек» — the reasons live in its «Почему эта» column only.
Add a row only for a choice with a named alternative — DTO vs entity (its proof stays a «Проверки границ»
row in the domain model), outbox vs in-request (the transaction model),
each port the level does not include by default (`Clock`, `UnitOfWork`,
`IdGenerator`) with the test or rule that needs it. One sentence per
cell; no ADR files. An increment edits a row only when the decision
changed. `plan`, the domain and scenarios writers, and later increments
read the level here, so it must be in the file, not only in a report.

## Open questions

Live `(ДП-n)` guesses and grill/review questions go to
`documentation/architecture/open-questions.md`, not into this file. A
retired assumption is one sentence there («снято: стало решением
OQ-…»), not a struck-through list. The body may tag `(ДП-n)`; the list
lives only in that file. The three documents share one
`open-questions.md`.

## Diagrams

The D2 views belong to this document and live in
`documentation/architecture/diagrams/`: Контекст, Контейнеры, Слои,
Хранилища и интеграции, Модули. Each is embedded where the template
above says, in the section whose rows it draws; there is no separate
diagram file. Shapes, skip rules and rendering: `architecture-diagram.md`;
a finished set of embeds: `architecture-diagram.example.md`.
