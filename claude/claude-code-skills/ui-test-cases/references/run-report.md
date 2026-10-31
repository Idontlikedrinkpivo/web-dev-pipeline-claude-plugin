# Run report — `test-run.md`

Read before the session creates the report of mode run, and by the runner
before its first edit of it. It is the one place for the report's shape:
`SKILL.md` → Mode run and `references/runner-prompt.md` point here instead
of repeating it.

## Where and what

`documentation/plans/<version>/test-run.md`, in the version folder of the
current iteration — the open `plans/<v>/` folder, the one without
`summary.md` (several UI products: one file part per product, each shaped
as below).

**Every run and every repeat is its own section, one under the other, each
with its own table and its own bar** — nothing is rewritten in place. A
reader sees at the top where the whole set stands and, below, what each
run and each repeat did; the page (`test-run.html`) draws every bar at its
top, labelled by its section's heading: «Общий итог», then «Прогон 1 — все
кейсы», «Прогон 1 · повтор 1 — …», «Прогон 2 — после исправлений …».

1. **The top — «Общий итог».** Under the title, the main bar and its count
   line, no table: the share of automated cases that pass **by their
   latest result** in any section below — ⌊passing × 100 / (all cases − не
   автоматизированы)⌋. It grows as a run's cases pass and again with every
   repeat that turns a case green, so the user watches the one number that
   matters climb. Cases that cannot be automated are left out of the
   percent, so a run with no failures shows 100%; blocked cases stay in it —
   they are a gap to close. The count line: «Общий итог: проходят N из M
   автоматизированных · не проходят … · заблокировано … · не
   автоматизированы …». While anything runs, a line under it says what:
   «Сейчас: прогон 2 — 40 из 52».
2. **«## Прогон 1 — все кейсы · коммит <sha> · идёт | завершён».** Its bar
   is the share of the run's cases checked; its count «Проверено: N из M ·
   успешно … · не прошли … · заблокировано … · не автоматизированы …»; its
   table holds every case once (each case × mode its own row) with the
   result **of this run**. When the run ends, the table stays as it is: a
   case that passes in a later repeat keeps its `❌ не прошёл` here and
   shows its new result in that repeat's table.
3. **«## Прогон 1 · разбор упавших»** — pass 2, under the run, its bar the
   share triaged, «Разобрано: N из M» with the results so far, one row per
   failed case.
4. **«## Прогон 1 · повтор <n> — <what kind>»** — every repeat (a pause for
   a shared break, a round of test fixes in pass 2) — the moment it starts:
   - «Что исправлено перед повтором:» in plain words and with how many tests
     («исправлено 18 тестов: кнопки искались по тексту вместо роли»);
   - «Что повторяется:» — which cases and where they came from («54 кейса,
     не прошедших в повторе 1»);
   - its bar over just those cases, and «Повторено: N из M · прошли … ·
     снова не прошли …»;
   - its table: `TC | Кейс | Было | Статус | Комментарий`, «Было» the case's
     result before this repeat;
   - at the end «Итог повтора:» — what the numbers mean («30 падений были
     ошибками в тестах, теперь проходят; 17 — дефекты приложения, 7 — в
     повтор 3»), and the heading gets «· завершён».
5. **«## Прогон 2 — после исправлений <what> · коммит <sha>»** — a later run
   in the same iteration (after a fix plan, after changed decisions) is
   appended under everything before it, never written over it: the fix
   plan cites this file's rows. «Что исправлено:», «Что прогоняется:» (the
   cases and why), then its bar, count and table as in run 1, its own
   разбор and повторы under it as «Прогон 2 · …».
6. **The `Verdict:` line, last**, always tells what is true now: `идёт
   прогон` while the first run is on; `PASS | DEFECTS | BLOCKED` after its
   разбор; the moment anything runs again, `идёт перепрогон · прошлый:
   DEFECTS, коммит 6e96d58`, until that run's разбор gives the new one.
   With the commit and the update time.

The bars follow `work` → `references/progress-file.md` → The progress bar
(a hundred cells in a code block, filled cells = the percent shown after
them); set them with `progress_set.py <file> <done> <total> [--section
"<heading>"]`, never by hand. The page's status counts come from each
section's own table, one per row, so the lists under the verdict and the
other sections may repeat a case freely.

## Example

````markdown
# Прогресс прогона по кейсам — итерация 2.4.0

```text
███████████████████████████████████████████████████████████████████████████████████████░░░░░░░░░░░░░ 87%
```

Общий итог: проходят 151 из 173 автоматизированных · не проходят 22 · заблокировано 0 · не автоматизированы 6

Сейчас: прогон 2 — 40 из 52.

## Прогон 1 — все кейсы · коммит 6e96d58 · завершён

```text
████████████████████████████████████████████████████████████████████████████████████████████████████ 100%
```

Проверено: 179 из 179 · успешно 144 · не прошли 29 · заблокировано 0 · не автоматизированы 6

| TC | Кейс | Статус | Файл теста / комментарий |
|---|---|---|---|
| TC-1 | Список комнат на сегодня | ✅ прошёл | rooms.spec.ts |
| TC-7 | Отмена начавшейся брони | ❌ не прошёл | bookings.spec.ts · «Ошибка 409» вместо «Бронь уже началась, отменить нельзя» · e2e/artifacts/TC-7.png |
| TC-8 | Отмена за час до начала | ❌ не прошёл | bookings.spec.ts · кнопка «Отменить» не найдена |
| TC-19 | Ошибка при недоступном хранилище файлов | ⏭ не автоматизирован: остановка хранилища сломает общий стенд | вручную: остановить хранилище на отдельном стенде, загрузить файл, ждать «Не удалось сохранить файл, попробуйте позже» |

## Прогон 1 · разбор упавших

```text
████████████████████████████████████████████████████████████████████████████████████████████████████ 100%
```

Разобрано: 29 из 29 · тест исправлен 7 · дефект приложения 20 · пробел в ТЗ 2

| TC | Кейс | Разбор | Статус |
|---|---|---|---|
| TC-7 | Отмена начавшейся брони | приложение отвечает 409 без текста из ТЗ | ❌ дефект приложения |
| TC-8 | Отмена за час до начала | локатор кнопки по тексту, а не по роли | ✅ тест исправлен, прошёл |

## Прогон 1 · повтор 1 — исправленные тесты · завершён

Что исправлено перед повтором: 7 тестов — кнопки искались по тексту
вместо роли, тест не ждал загрузки списка броней.

Что повторяется: 7 кейсов, где разбор нашёл ошибку в тесте.

```text
████████████████████████████████████████████████████████████████████████████████████████████████████ 100%
```

Повторено: 7 из 7 · прошли 7 · снова не прошли 0

| TC | Кейс | Было | Статус | Комментарий |
|---|---|---|---|---|
| TC-8 | Отмена за час до начала | ❌ не прошёл | ✅ прошёл | bookings.spec.ts |

Итог повтора: все 7 падений были ошибками в тестах, теперь проходят.

## Прогон 2 — после исправлений U57–U66 и решений 35–38 · коммит a1b2c3d

Что исправлено: 20 дефектов приложения (план исправлений U57–U66), 2
пробела в ТЗ закрыты решениями 35–38.

Что прогоняется: 52 кейса — 22 не проходящих и 30 на тех же экранах.

```text
████████████████████████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 76%
```

Проверено: 40 из 52 · успешно 38 · не прошли 2

| TC | Кейс | Было | Статус | Комментарий |
|---|---|---|---|---|
| TC-7 | Отмена начавшейся брони | ❌ не прошёл | ✅ прошёл | bookings.spec.ts |
| TC-31 | Закрытие окна по Esc | ✅ прошёл | ❌ не прошёл | admin.spec.ts · фокус не вернулся на «Действия с бронью» |
| TC-40 | … | ❌ не прошёл | ⏳ ждёт | |

Verdict: идёт перепрогон · прошлый: DEFECTS, коммит 6e96d58 · обновлено 2026-10-31 11:20
````

The comment cell holds the spec file, and for a failure what was seen
against what was expected and the screenshot path.

## Statuses

- **A run, a repeat:** `⏳ ждёт`, `🔄 в работе`, then the outcome
  `✅ прошёл`, `❌ не прошёл`, `⛔ заблокирован: <причина>`,
  `⏭ не автоматизирован: <причина>`. A run's count line is «Проверено: N
  из M · успешно … · не прошли … · заблокировано … · не автоматизированы …»,
  a repeat's «Повторено: N из M · прошли … · снова не прошли …».
- **Разбор (pass 2):** `⏳ ждёт`, `🔍 проверка`, then `✅ тест исправлен, прошёл`,
  `⛔ тест не удалось исправить`, `❌ дефект приложения`, `🖼 расхождение с
  макетом`, `❓ пробел в ТЗ`; its count line is «Разобрано: N из M» with the
  results that occurred.

## The verdict and the lists under it

After a run's разбор the runner sets the `Verdict:` line: `PASS` when every
automated case passes by its latest result (directly or after a test fix), `DEFECTS` when any
app defect, mockup mismatch, spec gap or screen-check breach remains,
`BLOCKED` when blocked cases leave a screen unchecked. Under it:

- «Проверить вручную» names every `⏭ не автоматизирован` case with its
  reason and the manual steps — they are not a defect, but nobody has
  checked them yet;
- «Проверка экрана» names each breach of the screen check with its screen
  and `UX-n` («S-2 · 375 — страница прокручивается вбок — UX-74»). A
  breach is an app defect: it makes the verdict `DEFECTS` without changing
  any case's status;
- «Сверка с макетом» — one line per frame compared (`nodeId` · the cases
  that reached it · совпадает | what differs), or «не сверялось: нет
  доступа к Figma».

## How it is kept

With the Edit tool, one Edit per status change — the row in the section
that is running — then the bars it moves (its section's and «Общий итог»)
with `progress_set.py`. Never from the shell (`python`, `sed`, `cat >`):
the plugin's hook rebuilds the report's `.html` page — the one the user
watches — only after an Edit or Write call, so a shell write leaves that
page stale (`pipeline` → `references/progress-files.md` → Rules for every
file, «The page» and «How»).
