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

- **One set of statuses** in every progress file (below), so the user reads
  every file the same way.
- **The file is never named without its link.** Any message that mentions
  the progress file — an update, a resume, «запускаю следующего» — carries
  the clickable Markdown link with the repo-relative path. «Обновил
  прогресс в progress-design.md — файл можно открыть» is wrong: the name in
  plain text or in backticks opens nothing, and the user has to search for
  the file. Write `[progress-design.md](documentation/plans/2.1.1/progress-design.md)`.

  Where a subagent changes the rows (the Figma builder, the test writer,
  the test runner), write the line each time its dispatch returns. A stop
  or a question to the user carries the line too, as its last line.
- **How.** Change it with the **Edit** tool the moment a row changes — one
  call per row or line, the bar and the count together with the row — and
  **Write** only to create it. Never from the shell (`python`, `sed`,
  `cat >`), and never by a script that rewrites the file on a timer: the
  user's file pane redraws only on edit-tool changes, so such a file is
  fresh on disk and stale on screen until reopened. A script may compute
  the numbers; the agent writes them. The bar is printed, not counted by
  hand: `python3 -c "d,t=<done>,<total>;p=d*100//t;print('█'*p+'░'*(100-p),f'{p}%')"`.
- **A subagent's rows are watched, not trusted.** A subagent deep in its
  task forgets the progress file, and then the user sees a hang. So while
  a dispatch that owns rows runs and writes files, the session watches its
  output folder with the Monitor tool — a loop that prints each file as it
  changes, e.g. `while sleep 20; do git status --porcelain --
  documentation/ui/test-cases; done | awk '!seen[$0]++'` — and on each new
  line sets that item's row to `🔄 в работе` if the subagent has not
  (without Monitor: a background `sleep 30`, then the same check). When
  the dispatch returns, it reconciles every row, the bar and the count
  with what is on disk before the chat line, and says in that line what it
  corrected. Output that is not files (Figma) is reconciled on return,
  from the report.
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


## Statuses

Every row of every progress file — a unit, a screen, a document, a
section, a scanner, a fix, a stand — uses only these seven. A stage may add
a short detail after a colon (`🔄 в работе: печать`, `🔍 проверка: ревью`),
never a new word or emoji:

| Status | Means |
|---|---|
| `⏳ ждёт` | not started |
| `🔄 в работе` | started: dispatched, drawing, writing, running, being fixed |
| `🔍 проверка` | done by its maker, being checked: the session's inspection, a review, an audit, a triage |
| `✅ готово` | finished and accepted; the bar counts these |
| `🔁 возвращено: <что>` | sent back for rework after a check |
| `⛔ остановлено: <причина>` | cannot go on without a decision or a missing input, or could not run |
| `⏭ пропущено: <почему>` | not needed, out of the run's scope, or moved to the report |

The one exception is a test case's **outcome** in a UI test run's
`test-run.md`, whose table is the defect report: `✅ прошёл`,
`❌ не прошёл`, `⛔ заблокирован: <причина>`, `⏭ не автоматизирован:
<причина>`, and the triage results (`ui-test-cases` → Statuses). While a
case waits or runs it uses `⏳ ждёт` and `🔄 в работе` like any row.

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
  `⛔ остановлено`. Never end a turn on prose alone, and never on
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
| A «Спокойный синий» | 501:2 | ✅ готово |
| B «Тёплый графит» | — | 🔄 в работе |

Выбор: ждёт ответа

## Экраны

```text
██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 18%
```

Готово: 2 из 11

| S-n | Экран | Работа | Статус | Кадр |
|---|---|---|---|---|
| S-1 | Вход | редизайн | ✅ готово | 412:10 |
| S-2 | Расписание переговорных | редизайн | ✅ готово | 415:2 |
| S-3 | Мои брони | редизайн | 🔄 в работе | — |
| Общее | Общие состояния | draw | ⏳ ждёт | — |

Состояние: рисует figma-opus, страница «✅ Экраны · «Спокойный синий»» · обновлено 2026-10-07 14:20
````

«Направление» appears only when the visual-direction step runs; its rows
change `⏳ ждёт` → `🔄 в работе` → `✅ готово`, and «Выбор» names the
chosen option. Screen statuses: `⏳ ждёт`, `🔄 в работе`, `✅ готово`
(the builder), `🔁 возвращено: <что>`, `⛔ остановлено: <причина>` (the
session, when its check of a drawn screen fails). «Работа» is the screen's mark
(`новый экран`, `правка`, `редизайн`, `перекраска`, `переименование слоёв`).
The bar counts `✅ готово`.

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
| S-3 | Мои брони | 🔄 в работе | | |
| S-4 | Переговорные | ⏳ ждёт | | |

Ревью ТЗ: не запускалось · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `🔄 в работе` (dispatched), `🔍 проверка` (the
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
| 1 | Вход, сессия и выход | 01-login-session.md | ✅ готово | 38 |
| 2 | Расписание переговорных | 02-room-schedule.md | 🔄 в работе | |
| — | Без интерфейса | README.md | ⏳ ждёт | |

Состояние: пишет ui-test-writer · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `🔄 в работе`, `✅ готово`. The «Без интерфейса» row
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
| Основа — architecture.md | ✅ готово | — |
| Доменная модель | ✅ готово | — |
| Сценарии: бронирования | 🔄 в работе: печать | — |
| Сценарии: переговорные | ⏳ ждёт | — |

Состояние: пишет design-medium · обновлено 2026-10-07 14:20
````

Statuses: `⏳ ждёт`, `🔄 в работе: решения`, `🔄 в работе: печать`,
`🔍 проверка` (the writer, then the session's inspection), `✅ готово`,
`⛔ остановлено: <причина>` (the session). «Ревью» takes the `doc-review` verdict of that document when the
gate runs. The bar counts `✅ готово`.

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
`🔄 в работе`, `✅ готово`, `⏭ пропущено: <почему>`, `⛔ остановлено:
<причина>`. The state line carries the closing check: the quality gate for
the scaffold, the compose-contract tests and the release folder for the
topology.
