# Run report — `test-run.md`

Read before the session creates the report of mode run, and by the runner
before its first edit of it. It is the one place for the report's shape:
`SKILL.md` → Mode run and `references/runner-prompt.md` point here instead
of repeating it.

## Where and what

`documentation/plans/<version>/test-run.md`, in the version folder of the
current iteration — the open `plans/<v>/` folder, the one without
`summary.md`. Overwritten each run (several UI products: one section per
product). Each pass reads top-down — its title, the bar and the count right
under it, its table; under the last table the `Verdict:` line — `идёт
прогон` while the run is on, `PASS | DEFECTS | BLOCKED` after pass 2 — with
the commit and the update time.

**The `Verdict:` line always tells what is true now.** The moment anything
starts running again — a re-run block, a new run after a fix plan — it
turns `Verdict: идёт перепрогон · прошлый: DEFECTS, коммит 6e96d58 ·
обновлено …`, and the new verdict replaces it only when that run ends. An
old verdict standing under a run that is going on reads as its result.

**The page counts the main table, one row per case.** The status chips at
the top of `test-run.html` count the statuses of the pass-1 table — the
first table with a «Статус» column under the main bar — one per row. A
case named again elsewhere (pass 2, a re-run block, the lists under the
verdict) is not counted twice, so those places may repeat its status
freely; the pass-1 table must hold every case exactly once, with its
current status.

## The bars

The bars follow `work` → `references/progress-file.md` → The progress bar
(a hundred cells in a code block, every case weighing the same, filled
cells = the percent shown after them).

- **The main bar, under the title, shows the share of automated cases that
  pass** — ⌊passed × 100 / (all cases − не автоматизированы)⌋ — not the
  share checked: it grows during pass 1 as cases pass, and again with
  every re-run round as fixed tests turn green, so the user watches the one
  number that matters climb. Cases that cannot be automated are left out of
  the percent, so a run with no failures shows 100% and the bar never
  suggests a defect that is not there; blocked cases stay in it — they are
  a gap to close.
- Its count line is always labelled: «Проверено: N из M · успешно … · не
  прошли … · заблокировано … · не автоматизированы …» — «не прошли» counts
  only real failures.
- Pass 2's bar is the share triaged, «Разобрано: N из M» with the results
  so far; a re-run block's bar is the share of its cases re-run.

## Every re-run gets its own block

A pass's bar does not move while cases are being re-run, and a bar that
stands still for twenty minutes reads as a hang. So any re-run — the cases
of a shared-break pause, or a round of re-runs in pass 2 after tests were
fixed — opens its own block in the report the moment it starts, written so
a reader who never saw the run understands it:

- a heading that says which re-run it is and what kind: «Перезапуск после
  починки общего помощника» or «Перезапуск — круг N: проверка
  исправленных тестов» (the rounds go on while a fixed test turns green or
  its failure changes);
- «Что исправлено перед перезапуском:» — what changed in the tests or
  helpers, in plain words and with how many tests («исправлено 18 тестов:
  кнопки искались по тексту вместо роли, тест не ждал загрузки кабинета»);
- «Что перезапускается:» — which cases and where they came from («54
  кейса, не прошедших в круге 1»);
- its own bar over just those cases, and «Перезапущено: N из M · прошли …
  · снова не прошли …»;
- at the end «Итог круга:» — what the numbers mean («30 падений были
  ошибками в тестах, теперь проходят; 24 снова не прошли: 17 — дефекты
  приложения, 7 — в круг 2»), and the heading gets «— завершён».

While a re-run is on, a line under the pass's count says so — «Сейчас:
перезапуск, круг 2 — 26 из 28. Основная полоса двинется после него.» — so
the reader sees what is happening right where they look. The re-run cases
keep their row in the pass table until their new result is in; a case that
passes on a re-run turns `✅ прошёл после исправления теста` there, and the
main bar grows with it.

## Example

````markdown
# Прогресс прогона по кейсам — итерация <version>

```text
██████████████████████████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░ 78%
```

Проверено: 24 из 24 · успешно 18 · не прошли 4 · заблокировано 1 · не автоматизированы 1

### Перезапуск после починки общего помощника — завершён

Что исправлено перед перезапуском: общий помощник входа под ролью не
дожидался перехода в кабинет — добавлено ожидание.

Что перезапускается: 6 кейсов, которые упали из-за этого помощника.

```text
████████████████████████████████████████████████████████████████████████████████████████████████████ 100%
```

Перезапущено: 6 из 6 · прошли 6 · снова не прошли 0

Итог: все 6 падений были из-за помощника, теперь проходят.

| TC | Кейс | Статус | Файл теста / комментарий |
|---|---|---|---|
| TC-1 | Список комнат на сегодня | ✅ прошёл | rooms.spec.ts |
| TC-7 | Отмена начавшейся брони | ❌ не прошёл | bookings.spec.ts · «Ошибка 409» вместо «Бронь уже началась, отменить нельзя» · e2e/artifacts/TC-7.png |
| TC-12 | Вход через SMS | ⛔ заблокирован: нет тестовой заглушки SMS | |
| TC-19 | Ошибка при недоступном хранилище файлов | ⏭ не автоматизирован: остановка хранилища сломает общий стенд | вручную: остановить хранилище на отдельном стенде, загрузить файл, ждать «Не удалось сохранить файл, попробуйте позже» |

## Проход 2 — разбор упавших

```text
████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%
```

Разобрано: 2 из 5 · тест исправлен 1 · дефект приложения 1

Сейчас: перезапуск, круг 1 — 1 из 2. Полоса разбора двинется после него.

### Перезапуск — круг 1: проверка исправленных тестов

Что исправлено перед перезапуском: 2 теста — кнопка искалась по тексту
вместо роли, тест не ждал загрузки списка броней.

Что перезапускается: 2 кейса, где разбор нашёл ошибку в тесте.

```text
██████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 50%
```

Перезапущено: 1 из 2 · прошли 1 · снова не прошли 0

| TC | Кейс | Итог прохода 1 | Разбор | Статус |
|---|---|---|---|---|
| TC-7 | Отмена начавшейся брони | ❌ не прошёл | приложение отвечает 409 без текста из ТЗ | ❌ дефект приложения |
| TC-8 | Отмена за час до начала | ❌ не прошёл | локатор кнопки по тексту, а не по роли | ✅ тест исправлен, прошёл |
| TC-9 | Отмена чужой брони | ❌ не прошёл | — | 🔍 проверка |
| TC-15 | … | ❌ не прошёл | | ⏳ ждёт |

Verdict: идёт прогон · коммит 1a2b3c4 · обновлено 2026-10-06 14:32
````

The comment cell holds the spec file, and for a failure what was seen
against what was expected and the screenshot path.

## Statuses

- **Pass 1:** `⏳ ждёт`, `🔄 в работе`, then the outcome `✅ прошёл`,
  `❌ не прошёл`, `⛔ заблокирован: <причина>`, `⏭ не автоматизирован:
  <причина>`, and later `✅ прошёл после исправления теста` for a case a
  re-run turned green. The count line is «Проверено: N из M · успешно … ·
  не прошли … · заблокировано … · не автоматизированы …», always with the
  «Проверено:» label.
- **Pass 2:** `⏳ ждёт`, `🔍 проверка`, then `✅ тест исправлен, прошёл`,
  `⛔ тест не удалось исправить`, `❌ дефект приложения`, `🖼 расхождение с
  макетом`, `❓ пробел в ТЗ`; its count line is «Разобрано: N из M» with the
  results that occurred.

## The verdict and the lists under it

After pass 2 the runner sets the `Verdict:` line: `PASS` when every
automated case passed (directly or after a test fix), `DEFECTS` when any
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

With the Edit tool, one Edit per status change, the bars and the count it
touches in the same Edit. Never from the shell (`python`, `sed`, `cat >`):
the plugin's hook rebuilds the report's `.html` page — the one the user
watches — only after an Edit or Write call, so a shell write leaves that
page stale (`pipeline` → `references/progress-files.md` → Rules for every
file, «The page» and «How»).
