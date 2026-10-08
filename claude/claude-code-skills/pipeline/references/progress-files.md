# Progress files

Read this before a stage that keeps a progress file creates it. A long stage —
one that works through many items of one kind (screens, documents, cases,
units, steps) while the user waits — keeps one, so the user sees where it is
without asking and can tell a slow step from a stuck one.

## Which stages keep one

| Stage | File in `documentation/plans/<version>/` | One row per | Who changes the rows |
|---|---|---|---|
| `ui-design` — style tiles, drawing, restyle, redraw | `progress-design.md` | screen, plus the direction tiles | the Figma builder as it draws each screen; the session as it verifies |
| `screen-spec` | `progress-screen-specs.md` | screen | the session, around each dispatch |
| `ui-test-cases` write | `progress-test-cases.md` | section of the case set, plus «Без интерфейса» | the writer, as it finishes each section |
| `ui-test-cases` run | `test-run.md` | case | the runner — `ui-test-cases` → Mode run |
| `security-audit` | `security-audit.md` (the report itself) | scanner, area, the verify pass | the session — `security-audit` → `references/report.md` |
| `clean-architecture-design` | `progress-architecture.md` | document | the writer as it settles and prints each document; the session as it inspects and reviews |
| `repo-scaffold` | `progress-scaffold.md` | step | the session |
| `work` | `progress.md` | unit, then fix | the session — `work` → `references/progress-file.md` |
| `deploy-topology` | `progress-deploy.md` | step | the session |

The stages that only ask questions (`grill-me`, `doc-review`,
`docs-consistency`) keep no file: the chat is their progress, and each
question names its place («Замечание 3 из 8»). A stage that writes one
document keeps none.

## Rules for every file

- **Where.** In the iteration's open folder `documentation/plans/<version>/`,
  out of git like everything there. Creating the file writes into
  `plans/`, so a stage that finds no open folder fixes the iteration's
  version first (`pipeline` → Service version) — for a person who took a
  handed stage, from the branch name (`pipeline` → `references/team.md`).
- **Shape.** The title «Прогресс … — итерация <version>»; right under it
  the bar alone in a ```` ```text ```` block — a hundred cells, `█` done,
  `░` the rest, then the percent, ⌊done × 100 / total⌋ (`work` →
  `references/progress-file.md` → The progress bar); then the count line
  with its label; then the table; under the table one state line ending
  «обновлено YYYY-MM-DD HH:MM».
- **When.** Create it before the first step or dispatch, every row
  `⏳ ждёт`. Then post its link in the chat — a clickable Markdown link
  with the repo-relative path — before the first step starts:

  ```text
  Прогресс ТЗ на экраны: [progress-screen-specs.md](documentation/plans/2.1.0/progress-screen-specs.md) — откройте, он обновляется по ходу работы.
  ```

  A run resumed after a break or a context compaction rebuilds the rows from
  what is on disk, sets anything half-done back to `⏳ ждёт`, and posts the
  link again before it goes on.
- **After each item.** Every time an item is finished — its row reaches
  done, stopped or returned — write one line in the chat: the count from
  the file's count line and the same clickable link, so a user who closed
  the file or stepped away reopens it from the last message, not by
  scrolling to the start:

  ```text
  ТЗ на экраны: 5 из 10 · [progress-screen-specs.md](documentation/plans/2.1.0/progress-screen-specs.md)
  ```

  Where a subagent changes the rows (the Figma builder, the test writer,
  the test runner), write the line each time its dispatch returns. A stop
  or a question to the user carries the line too, as its last line.
- **How.** Change it with the **Edit** tool the moment a row changes — one
  call per row or line, the bar and the count together with the row — and
  **Write** only to create it. Never from the shell (`python`, `sed`,
  `cat >`), and never by a script that rewrites the file on a timer: the
  user's file pane redraws only on edit-tool changes, so such a file is
  fresh on disk and stale on screen until reopened. A script may compute
  the numbers; the agent writes them.
- **Results from background work** (stands, long commands) wake the agent,
  and the agent edits: watch their output with the Monitor tool, which
  wakes the session on each new line, or — without it — a background
  `sleep 30` whose finish wakes the session to edit what changed and start
  the next one.
- **A subagent** that changes rows gets the path in its packet as
  `PROGRESS FILE` and changes only its rows, the bar and the count line;
  the title, the other sections and the state line stay the session's.
- **A new run** of the same stage in the same iteration rewrites the file.
  It is never committed and never cited by a document.

## Keeping the run moving

A long stage runs while the user is away — asleep, in a meeting — so a turn
that ends with nothing running stops it for hours: nothing wakes the
session until the user writes again.

- **A turn ends only while the next step runs — or on a question that
  blocks it.** Until the last item is done, every turn ends with the next
  step already started — an executor, a reviewer, a check, dispatched in
  the background, whose completion wakes the session again. The one other
  way to end a turn is a question the run cannot go past without the
  user's answer — one of the stage's own stop cases (a missing decision, a
  review's `STOP`, rounds that stopped making progress): then nothing is
  started, the question is the end of the turn, and the row says
  `⛔ остановлен`. Never end a turn on prose alone, and never on
  «продолжаю…» without the call.
- **Call first, then write.** Start the next step, then write the chat
  line (After each item). Text written before the call can be cut off —
  a dropped connection, a stream that ends mid-sentence — and the call
  after it is lost with it; text after the call costs nothing if it is
  cut. A blocking question has no call after it, so it is simply the last
  thing in the turn.
- **A message that is not a decision does not stop the run.** A stray
  keystroke, «ну?», «ты тут?», a question about progress: answer in one
  line with the count and the link, and go on. Only a stop («стоп»,
  «подожди», «остановись») or a changed decision changes the run — the
  latter through `pipeline` → `references/decision-changes.md`.
- **Never ask whether to continue.** The run was agreed when it started; it
  asks only in its stage's stop cases. A turn that finds the run idle — the
  last one was cut off, the session was compacted, the user wrote into a
  silence — rebuilds the rows from disk and git and starts the next step
  at once, saying in one line that it resumed.

## The files

### `ui-design` — `progress-design.md`

````markdown
# Прогресс макетов — итерация 2.1.0

## Направление

| Вариант | Образец | Статус |
|---|---|---|
| A «Спокойный синий» | 501:2 | ✅ образец готов |
| B «Тёплый графит» | — | 🎨 рисуется |

Выбор: ждёт ответа

## Экраны

```text
████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 36%
```

Нарисовано: 4 из 11 · проверено: 3

| S-n | Экран | Работа | Статус | Кадр |
|---|---|---|---|---|
| S-1 | Вход | редизайн | ✅ проверен | 412:10 |
| S-2 | Расписание переговорных | редизайн | 🖼 нарисован | 415:2 |
| S-3 | Мои брони | редизайн | 🎨 рисуется | — |
| Общее | Общие состояния | draw | ⏳ ждёт | — |

Состояние: рисует figma-opus, страница «✅ Экраны · «Спокойный синий»» · обновлено 2026-10-07 14:20
````

«Направление» appears only when the visual-direction step runs; its rows
change `⏳ ждёт` → `🎨 рисуется` → `✅ образец готов`, and «Выбор» names the
chosen option. Screen statuses: `⏳ ждёт`, `🎨 рисуется`, `🖼 нарисован`
(the builder), `🔍 проверка`, `✅ проверен`, `🔁 дорисовка: <что>`,
`⛔ остановлен: <причина>` (the session). «Работа» is the screen's mark
(`новый экран`, `правка`, `редизайн`, `перекраска`, `переименование слоёв`).
The bar counts drawn screens — `🖼`, `🔍` and `✅`.

### `screen-spec` — `progress-screen-specs.md`

````markdown
# Прогресс ТЗ на экраны — итерация 2.1.0

```text
██████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 50%
```

Готово: 5 из 10 · разрывов: design 9, API 0, SRS 0

| S-n | Экран | Статус | Элементов | Разрывы |
|---|---|---|---|---|
| S-1 | Вход | ✅ готово | 12 | — |
| S-2 | Расписание переговорных | ✅ готово | 41 | design 6 |
| S-3 | Мои брони | ✍️ пишется | | |
| S-4 | Переговорные | ⏳ ждёт | | |

Ревью ТЗ: не запускалось · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `✍️ пишется` (dispatched), `🔍 проверка` (the
session's inspection), `✅ готово`, `🔁 возвращено: <что>`,
`⛔ остановлено: <причина>`. The state line names the `doc-review` gate
over the set: не запускалось → идёт → its verdict.

### `ui-test-cases` write — `progress-test-cases.md`

````markdown
# Прогресс тест-кейсов — итерация 2.1.0

```text
██████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 30%
```

Написано: 3 из 10 разделов · кейсов: 142

| № | Раздел | Файл | Статус | Кейсов |
|---|---|---|---|---|
| 1 | Вход, сессия и выход | 01-login-session.md | ✅ написаны | 38 |
| 2 | Расписание переговорных | 02-room-schedule.md | ✍️ пишутся | |
| — | Без интерфейса | README.md | ⏳ ждёт | |

Состояние: пишет ui-test-writer · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `✍️ пишутся`, `✅ написаны`. The «Без интерфейса» row
counts the acceptance criteria listed there, and is not in the bar.

### `clean-architecture-design` — `progress-architecture.md`

````markdown
# Прогресс архитектуры — итерация 0.1.0

```text
█████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 33%
```

Готово: 2 из 6 документов

| Документ | Статус | Ревью |
|---|---|---|
| Основа — architecture.md | ✅ готов | — |
| Доменная модель | ✅ готов | — |
| Сценарии: бронирования | 🖨 печатается | — |
| Сценарии: переговорные | ⏳ ждёт | — |

Состояние: пишет design-medium · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `✍️ решения`, `🖨 печатается`, `🖨 напечатан` (the
writer), `🔍 проверка`, `✅ готов`, `⛔ остановлен: <причина>` (the
session). «Ревью» takes the `doc-review` verdict of that document when the
gate runs. The bar counts `✅ готов`.

### `repo-scaffold` — `progress-scaffold.md` and `deploy-topology` — `progress-deploy.md`

````markdown
# Прогресс каркаса проекта — итерация 0.1.0

```text
██████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 50%
```

Сделано: 3 из 6

| Шаг | Что | Статус |
|---|---|---|
| 1 | Папки | ✅ готово |
| 2 | Манифест и инструменты | ✅ готово |
| 3 | Правила границ | ✅ готово |
| 4 | Локальный запуск и схема | 🔄 в работе |
| 5 | Точка входа | ⏳ ждёт |
| 6 | Карта проекта | ⏳ ждёт |

Проверка качества: не запускалась · обновлено 2026-10-07 14:20
````

The rows are the stage's own steps: for `repo-scaffold` its sections 1–6,
for `deploy-topology` its Steps 1–8 («Сборка образов» under Step 8 can run
for minutes — its row says so while it runs). Statuses: `⏳ ждёт`,
`🔄 в работе`, `✅ готово`, `⏭ не нужно: <почему>`, `⛔ остановлено:
<причина>`. The state line carries the closing check: the quality gate for
the scaffold, the compose-contract tests and the release folder for the
topology.
