# Frames register — template and example

Read before writing `documentation/ui/frames-register.md` (or
`documentation/ui/<product>/frames-register.md` when there are several UI
products) the first time. Later runs edit the existing file in place and
keep its shape.

## Template

```markdown
---
title: <Продукт> — реестр кадров
updated: YYYY-MM-DD
sources:
  - documentation/requirements/srs/srs.md@<версия SRS>
---

# <Продукт> — реестр кадров

Не контракт: карта макета. Номера экранов S-n назначает дизайн; ТЗ на экран
(`screen-spec`) ссылается сюда. Как выглядит экран — только в Figma.

- **Figma:** <figma.com URL> (fileKey `<key>`)
- **Дизайн ведёт:** мы | дизайнер с плагином | дизайнер без плагина
- **Кадры рисует:** ui-design | дизайнер
- **Тип продукта:** B2B | B2C | по областям: <область — тип>, …
- **Ширины:** <десктопная ширина>, <более узкие ширины>
- **Доступность:** WCAG 2.2 AA
- **Визуальное направление:** «<имя>» — primary <hex>, <шрифты>, плотность <компактная | обычная>, тема <светлая | светлая и тёмная>; токены — страница `🎨 Tokens`; выбрано YYYY-MM-DD; отклонены: «<имя>», … | по библиотеке <имя> | по макетам дизайнера
- **Слои по действиям:** да | нет        ← только при «Кадры рисует: дизайнер»
- **Прежние кадры:** страница «<имя>» — <кто рисовал>; не используются        ← только после «нарисовать заново»

## Экраны

| S-n | Экран | Сценарии | Акторы | Кадр | Состояния | Вложенные шаги | Статус |
|---|---|---|---|---|---|---|---|
| S-1 | <объект или задача> | UC-…, UC-… | A-… | <nodeId> | <состояние> → <nodeId>; … | M1 <назначение> → <nodeId>; … | черновик \| готово к разработке |

## Общие состояния

| Состояние | Когда | Кадр |
|---|---|---|
| Сессия истекла | <смысл, из SRS или NFR> | <nodeId> |
| Слишком много запросов | … | <nodeId> |
| Ошибка сервера | … | <nodeId> |
| Нет сети | … | <nodeId> |
```

Cell rules:

- **Визуальное направление** — written by the visual-direction step
  (`references/visual-direction.md`); a restyle adds `прежнее: «<имя>»`.

- **Экран** — the object or job, never a widget (`Мои брони`, not
  `Таблица броней`).
- **Сценарии** — UC ids only; the flows inside a use case are covered by the
  frames, checked by Полнота макета, not listed here.
- **Состояния** — every non-Default state frame: `Loading`, `Empty`,
  `Error`, `Forbidden`, and named ones for flows (`Отменена (UC-3 Alt-1)`).
  A state the screen cannot have is absent, not `—`.
- **Вложенные шаги** — `M<n> <назначение> → nodeId`, numbered per screen,
  append-only. Each narrower-width frame goes in Состояния as `<width> → nodeId` (`375 → 12:48`).
- **Статус** — `черновик` until the frames resolve and the screen's
  completeness items pass; then `готово к разработке`. A screen dropped by a
  redesign keeps its row: `черновик`, «снят в редизайне YYYY-MM-DD», frames
  in `🗄 Архив`.
- No `operationId`, column, HTTP status, or description of looks in any
  cell.

## Example

```markdown
---
title: Бронирование переговорных — реестр кадров
updated: 2026-10-04
sources:
  - documentation/requirements/srs/srs.md@0.1.0
---

# Бронирование переговорных — реестр кадров

Не контракт: карта макета. Номера экранов S-n назначает дизайн; ТЗ на экран
(`screen-spec`) ссылается сюда. Как выглядит экран — только в Figma.

- **Figma:** https://www.figma.com/design/AbC123/Rooms (fileKey `AbC123`)
- **Кадры рисует:** ui-design
- **Тип продукта:** B2B
- **Ширины:** 1440, 375
- **Доступность:** WCAG 2.2 AA
- **Визуальное направление:** «Спокойный синий» — primary #2563EB, Inter, плотность компактная, тема светлая; токены — страница `🎨 Tokens`; выбрано 2026-10-04; отклонены: «Тёплый графит»

## Экраны

| S-n | Экран | Сценарии | Акторы | Кадр | Состояния | Вложенные шаги | Статус |
|---|---|---|---|---|---|---|---|
| S-1 | Вход | UC-1 | A-1, A-2 | 10:2 | Error → 10:9; 375 → 10:14 | — | готово к разработке |
| S-2 | Расписание переговорных | UC-2, UC-4 | A-1 | 12:34 | Loading → 12:40; Empty → 12:41; Error → 12:42; Занято (UC-4 Exc-1) → 12:44; 375 → 12:48 | M1 Новая бронь → 12:50 | готово к разработке |
| S-3 | Мои брони | UC-3, UC-5 | A-1 | 14:1 | Loading → 14:6; Empty → 14:7; Error → 14:8; 375 → 14:12 | M1 Отмена брони → 14:20; M2 Продление → 14:24 | готово к разработке |
| S-4 | Переговорные | UC-6, UC-7 | A-2 | 16:1 | Loading → 16:5; Empty → 16:6; Error → 16:7; Forbidden → 16:8 | M1 Новая переговорная → 16:11 | черновик |

## Общие состояния

| Состояние | Когда | Кадр |
|---|---|---|
| Сессия истекла | сессия закончилась, введённое сохраняется до повторного входа (NFR-4) | 20:1 |
| Слишком много запросов | система временно ограничила запросы | 20:5 |
| Ошибка сервера | запрос не выполнен по вине системы | 20:9 |
| Нет сети | соединение потеряно | 20:13 |
```

`open-questions.md` beside it, for the S-4 draft:

```markdown
# Открытые вопросы

Не источник поведения. Контракт — соседний файл.

| Вопрос | Класс |
|---|---|
| S-4: нет кадра для UC-7 Exc-1 (переговорную с будущими бронями нельзя удалить) — дорисовать состояние или вложенный шаг? | Блокирует старт |
```
