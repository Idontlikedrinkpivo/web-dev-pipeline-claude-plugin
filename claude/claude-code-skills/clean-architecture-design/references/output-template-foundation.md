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
пунктов — решение или `Не применимо — <причина>`)* · Решения по NFR
*(каждая не-security строка SRS §4)* · Ключевые решения *(всегда: Уровень,
Стек, затем только решения с названной альтернативой)*. Списки в ячейке
через `;` не склеивать. Акторы — имена (`Anonymous`, `Admin`), не `A-n`:
это пространство допущений. Хранилища — store + для чего в этом проекте,
не каталог таблиц. Внешние системы — партнёры, которыми мы не владеем;
наша БД и объектное хранилище сюда не входят; нет партнёров — одна строка
«нет». API — только живые входы (REST, CLI, очередь, cron), второй вход —
ещё одна строка; строк «нет» не писать. Стек — рантайм с мажорными
версиями, «Почему эта» — 2–4 предложения; локальный запуск — §5, линтер
границ — §6. Уровень и стек — строки «Ключевых решений», не отдельные
разделы. Сущностей, сценариев и чтений здесь нет — они в доменной модели
и в документах сценариев.

## 2. Модули и функциональные области
Таблица, строка на область, всегда (даже одна область):
Область · Модуль (папка §5) · Группа SRS · Документ сценариев · Владеет
состоянием · Берёт у других областей · Потребители контракта. Область — kebab-case на английском
(`bookings`), совпадает с папкой модуля и с `<area>` в пути документа
сценариев. Группа SRS — жирный подзаголовок групп FR, дословно. Документ
сценариев — путь `scenarios/<area>/<area>.md`. Владеет состоянием — имена
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
Отказ внешнего вызова · Форматы файлов (колонка → поле → пустая ячейка) ·
Сборка · Конфигурация (переменная · тип · обязательна · если нет) ·
Служебные каналы (путь · владелец · что вызывает) · таблица «именованная
ошибка → HTTP» (имена — из доменной модели §3 и из `code` в
`documentation/api/openapi.yaml`) и абзац: охрана маршрутов (механизм — токен,
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
scenarios/<area>/<area>.md`. Один артефакт на файл.

## 6. Проверки и тесты
Направление импортов · правила линта таблицей (откуда → что нельзя
импортировать), без файла конфига — его пишет `repo-scaffold`; при двух и
более областях — запрет импорта между областями, кроме названного в §2
«Берёт у других областей» · структурные тесты · план тестов: строка на
тестовый файл или на группу по слою («тест сущности на каждую строку
инвариантов доменной модели»), не строка на проверку; правило — по id
(`BR-3`), не значением.
```

## §1 «Ключевые решения»

The last §1 table: Решение · Выбрано · Вместо · Почему. Row 1 is always
`Уровень` (name the Full trigger when one fired); row 2 is `Стек`,
«Вместо» naming the cards not picked. Add a row only for a choice with a
named alternative — DTO vs entity (its proof stays a «Проверки границ»
row in the domain model), outbox vs in-request (the transaction model),
each port the level does not include by default (`Clock`, `UnitOfWork`,
`IdGenerator`) with the test or rule that needs it. One sentence per
cell; no ADR files. An increment edits a row only when the decision
changed. `plan`, the domain and scenarios writers, and later increments
read the level here, so it must be in the file, not only in a report.

## Open questions

Live `(A-n)` guesses and grill/review questions go to
`documentation/architecture/open-questions.md`, not into this file. A
retired assumption is one sentence there («снято: стало решением
OQ-…»), not a struck-through list. The body may tag `(A-n)`; the list
lives only in that file. The three documents share one
`open-questions.md`.

## Diagrams

The D2 views belong to this document and live in
`documentation/architecture/diagrams/`: Контекст, Контейнеры, Слои,
Хранилища и интеграции, Модули. Each is embedded where the template
above says, in the section whose rows it draws; there is no separate
diagram file. Shapes, skip rules and rendering: `architecture-diagram.md`;
a finished set of embeds: `architecture-diagram.example.md`.
