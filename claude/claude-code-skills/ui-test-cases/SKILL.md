---
name: ui-test-cases
description: >-
  User test cases for a product with screens, in two modes. write — after
  the screen specs: turns SRS acceptance criteria and the screen specs into
  numbered cases (steps by action, expected states and texts from the
  frames, frame ids). run — after `work` and its reviews: turns
  the cases into Playwright tests, runs them against the app started
  locally, compares screens with the frames, and reports. Use when the
  stage offers it, or the user asks for «тест-кейсы», «пользовательские
  сценарии», «протыкай приложение», acceptance or E2E testing through the
  UI. Not for unit or API tests, and not for fixing the app.
---

# UI Test Cases

The SRS says what the system must do; the mockups and the screen specs say
how a person does it on screen; nothing so far says how anyone will check, through the
interface, that the built product does both. A unit test proves a method,
an API test proves a status code, and neither notices that the «Отменить»
button never appears, that the error text differs from the spec, or that a
screen looks nothing like its frame. These cases close that gap: written
once from the documents while the design is fresh, run once the code
exists, kept as a Playwright suite that CI repeats on every change.

Write cases and reports in Russian. Do not translate ids (`TC-`, `UC-`,
`AC-`, `S-`), `operationId`s, paths, or the `Verdict:` line.

## Not this skill's job

| Not here | Owner |
|---|---|
| Unit, use-case, adapter, or API tests | the plan's units in `work` |
| Deciding how a screen behaves | `ui-design` and `screen-spec` — a case that needs a decision the screen spec did not make is a gap, not a guess |
| Fixing the app when a case fails | a new plan increment (`plan` → `work`); this skill reports |
| CI wiring | `ci-pipeline` runs `test:e2e` when it exists |

## Which mode

The stage that offers this skill names the mode. Opened directly: no
cases file beside the screen specs → write; cases exist and the app's code
exists → run; asked for both («составь и прогони») → write, then run in
the same sitting. Unclear → one question.

## Mode write

**When:** after `screen-spec` finished. Without screen specs, stop and name
`screen-spec`: there is nothing to step through.

**Inputs:** the SRS `documentation/requirements/srs/srs.md` when this repo
has it (acceptance criteria, BRs, roles; a frontend repo whose SRS lives
elsewhere works from the screen specs alone, and its coverage table lists UC
and state rows instead of AC ids), every screen spec (elements and their
conditions, «Поля ввода», «Состояния экрана», «Ошибки ответов», exact texts
quoted from the frames, Figma ids), the frames register (screens, app-wide
states). Not `ui-wishes.md`: it is never a source of expected behaviour.

**Dispatch:** resolve `ui-test-writer` through `executor-catalog` and dispatch
it under the Dispatch contract with `references/writer-prompt.md`, without
asking which model. The session writes no case file.

**Progress file.** Before the dispatch, create
`documentation/plans/<version>/progress-test-cases.md` per
`pipeline` → `references/progress-files.md` — one row per section of the
set (below) plus «Без интерфейса», all `⏳ ждёт` — post its link in the
chat, and pass it to the writer as `PROGRESS FILE`. A full set runs to
hundreds of cases; the writer marks each section as its cases are
written.

**What a case set must hold:**

- One case per acceptance criterion that a person can reach through the
  interface — main flow, every Alt and every Exc. An AC with no screen (a
  scheduled job, an email content check) is listed under «Без интерфейса»
  with the reason, not dropped. So is a check the interface cannot reach —
  input the client itself never sends (a malformed email the form blocks
  before sending): «Без интерфейса — проверяется API-тестами», not a UI case
  that a run would later have to drop.
- One case per row of «Состояния экрана» (Empty, Error, Forbidden,
  Loading where it is observable) and per user-causable row of «Ошибки
  ответов» that no AC case already covers.
- One case per «Поля ввода» rule: an invalid value, the moment it is
  checked, the exact error text.
- Roles: a case for every forbidden action per role the SRS names (the
  resident who tries to cancel someone else's booking).
- Expected results quote the exact text the screen spec takes from the
  frame's «Тексты» table, and name the state row.
- Steps name actions and data by the spec's names and screen ids, never a
  widget, a gesture, CSS or coordinates: «На S-1 выполнить отмену своей
  брони», not «нажать кнопку» or «выбрать в выпадающем меню». A
  designer who turns a dropdown into a context menu must not have to
  rewrite a case; the e2e test finds the element by its accessible role
  and name on the built screen. Expected results name the state row.
- Preconditions name the data the case needs («у резидента активная бронь
  на завтра»), so the runner can seed it.

**Artifact:** the folder `documentation/ui/test-cases/`, beside the frames
register and `screen-specs/` (with several UI products, one per
`documentation/ui/<product>/`). A full set runs to hundreds of cases and
thousands of lines; one file per section lets the writer, the runner and a
reviewer read only the part they work on, and keeps a change to one screen
in one or two files.

```text
documentation/ui/test-cases/
├── README.md                  index and everything the sections share
├── 01-login-session.md        1. Вход, сессия и выход — TC-1 … TC-25
├── 02-home-not-found.md       2. Главная и неизвестный адрес
└── …
```

- **`README.md`** — the frontmatter (`title`, `updated`, `sources:`
  pinning the SRS and every screen spec as `path@<version>`); «Как читать
  кейс», the roles and test data, the general handler's texts — whatever
  every section shares; the «Разделы» table `№ | Файл | Экраны и сценарии |
  Кейсы` (the `TC-` range and the count); then the coverage table, the
  screen-states → cases table, «Без интерфейса» and the spec gaps found
  while writing.
- **One file per section**, `NN-<slug>.md` with a Latin slug: the heading
  `# N. <Раздел> (S-ids, UC-ids)` and its cases, nothing shared repeated.
  A section holds one screen's flow or a tight group of flows; a screen with
  many flows spans several sections, and a section past ~600 lines is
  split.
- **`TC-` ids run across the whole set**, never renumbered or reused; a
  new case takes the next free number, in the section where it belongs.
- Unversioned: an increment edits the files in place.
- **An existing single `test-cases.md`** (written before this layout) is
  moved into the folder on the next write run, before anything else: its
  `## N.` sections become section files, the shared parts and the closing
  tables go to `README.md`, every case is copied unchanged with its id,
  and the old file is deleted in the same change (git keeps its history).
  The move rewrites no case; changes the run makes come after it.

```markdown
## TC-7. Резидент не может отменить начавшуюся бронь

**Источник:** UC-2 AC-Exc-2 · BR-4   **Экран:** S-1 → M2   **Кадр:** 12:160   **Роль:** A-1
**Предусловия:** резидент вошёл; у него бронь «Байкал», начавшаяся 10 минут назад

| # | Шаг | Ожидается |
|---|---|---|
| 1 | Открыть S-1 на сегодня | бронь видна как своя |
| 2 | Выбрать свою бронь | открылся шаг M2 «Отмена брони» |
| 3 | Выполнить «Отменить бронь» | в M2 текст «Бронь уже началась, отменить нельзя»; бронь осталась активной |
```

`README.md` ends with the coverage table: every AC id → its `TC-` ids, or
the «Без интерфейса» line. An AC with neither is the writer's failure, not
the reader's.

## Mode run

**When:** after `work` closed its run and `code-review-full` passed (or the
user chose to go on without it). Cases must exist; without them, offer
mode write first.

**The app must start locally.** Read `.claude/launch.json`, the README, and
the compose file `repo-scaffold` wrote for the test database. The runner
starts the database and the app, seeds the preconditions through the API
or the seed scripts the project has, and signs in with test credentials
from the project's seed or example config. External sign-in (SSO, SMS)
uses the test stub the architecture names; when there is none, that is a
`BLOCKED` with the gap, not an improvised bypass.

**A frontend repo without its backend** (the API is a separate service): the
runner mocks the API at the network boundary (Playwright `page.route`) with
responses shaped by `documentation/api/openapi.yaml` — each case's
preconditions become the mocked data, each error case the mocked status. The
report says the screens were checked against the contract, not a live
backend.

**Two passes.** The run is two passes with a bar each, so the user always
sees how far the full picture is:

1. **Pass 1 — the whole set, once.** Every case is written and run once and
   gets a pass-1 result: `✅ прошёл`, `❌ не прошёл` (with what was seen
   against what was expected), `⛔ заблокирован: <причина>` (a missing
   piece that can be added — a test stub for sign-in or SMS), or
   `🙅 не автоматизирован: <причина>` (the case cannot be checked honestly
   by an interface test on the shared stand — it needs a storage failure
   that would break the stand for everyone, an app restart with other
   settings, or a state the stand never has; the comment says how to check
   it by hand). No test is
   fixed and nothing is triaged in this pass — the point is the whole set at
   100% first, so repeated causes show up as repeats instead of being fixed
   one case at a time. When the cases run in several modes (two sign-in
   modes, two roles of one case), each case × mode is its own row and its
   own unit of the bar.
2. **The one exception — a shared break.** When several cases in a row fail
   for one cause in shared test code (sign-in under a role, data setup,
   opening a section), the pass pauses: the shared helper is fixed and the
   cases it failed are re-run, then the pass goes on. Hundreds of identical
   failures say nothing about the app.
3. **Pass 2 — triage of the failed.** A second section of the same report,
   with its own bar over the pass-1 `❌ не прошёл` cases. Each is triaged:
   **test defect** — the test is fixed and the case re-run, at most two
   attempts (`✅ тест исправлен, прошёл` or `🔧 тест не удалось исправить`);
   **app defect** — the app contradicts the spec (`❌ дефект приложения`);
   **mockup mismatch** — works, but the screen differs from the frame
   (`🖼 расхождение с макетом`); **spec gap** — the spec never said
   (`❓ пробел в ТЗ`). App defects are not re-run: a fix plan fixes them.

The verdict is set only after pass 2.

**Every re-run gets its own bar.** A pass's bar does not move while cases
are being re-run, and a bar that stands still for twenty minutes reads as a
hang. So any re-run — the cases of a shared-break pause, or a round of
re-runs in pass 2 after tests were fixed — opens its own block in the
report the moment it starts, written so a reader who never saw the run
understands it:

- a heading that says which re-run it is and what kind: «Перезапуск после
  починки общего помощника» or «Перезапуск — круг N из 2: проверка
  исправленных тестов» (pass 2 allows two attempts per test, so two rounds
  at most);
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

**The report is live.** Before the dispatch, create the report (path below)
with every case of the run `⏳ ждёт`, the pass-1 bar at 0% and `Verdict:
идёт прогон` under the table, and post its link in the chat as a clickable
Markdown link with its repo-relative path — the user opens it once and
watches the cases turn over. Pass 2's section is added under pass 1 when
pass 1 reaches 100%, and the link is posted again. A run resumed after a
break or a context compaction keeps the report: every case without a result
in the current pass goes back to `⏳ ждёт`, the link is posted again, and
only then the runner goes on. The runner changes the report with the Edit
tool the moment a case changes status — never from the shell (`python`,
`sed`, `cat >`): the user's file pane redraws only on edit-tool changes.

**Dispatch:** resolve `ui-test-runner` through `executor-catalog` with
`references/runner-prompt.md`. The runner:

1. writes one Playwright spec per section file of the cases, named like it
   (`01-login-session.spec.ts`; an existing suite keeps its file names), under the project's E2E
   folder (`e2e/` unless the project has one), each test titled with its
   `TC-` id, using role- and label-based locators from the screen spec's element
   names, following `playwright-cli` → test generation;
2. adds or keeps the `test:e2e` script, so `ci-pipeline` can run the
   suite;
3. pass 1: runs the cases one at a time (`npx playwright test --grep
   "TC-7\b"`), so each result reaches the report as it happens; for each
   case takes a screenshot of the screen under test and compares it with the
   frame (`get_screenshot` of the cited `nodeId`) for layout, texts, and
   states — not pixel equality; a mismatch is a `❌ не прошёл` with what
   differs; without Figma access the comparison is skipped and the report
   says so. On the same screens it checks the items of `ux-patterns` →
   «Проверка экрана перед сдачей» a browser can show: every width of the
   frames register with no sideways page scroll (UX-74), the case's path
   by keyboard with visible focus (UX-63, UX-64), no motion under reduced
   motion (UX-61), icons from one set and no emoji (UX-57), Russian
   typography in the texts (UX-78);
4. pass 2: triages each failed case as above. It never edits application
   code.

**Report:** `documentation/plans/<version>/test-run.md`, in the version
folder of the current iteration — the open `plans/<v>/` folder, the one
without `summary.md`. No open version folder → say so and ask per
`pipeline` → "Asking before a transition" which version this run belongs
to; do not invent one. Overwritten each run (several UI products: one
section per product). Each pass reads top-down — its title, the bar and the
count right under it, its table; under the last table the `Verdict:` line —
`идёт прогон` while the run is on, `PASS | DEFECTS | BLOCKED` after pass 2 —
with the commit and the update time. The bars follow `work` →
`references/progress-file.md` → The progress bar (a hundred cells in a code
block, every case weighing the same). **The main bar, under the title, shows
the share of automated cases that pass** — ⌊passed × 100 / (all cases −
не автоматизированы)⌋ — not the share checked: it grows during pass 1 as
cases pass, and again with every re-run round as fixed tests turn green, so
the user watches the one number that matters climb. Cases that cannot be
automated are left out of the percent, so a run with no failures shows
100% and the bar never suggests a defect that is not there; blocked cases
stay in it — they are a gap to close. Its count line is always labelled:
«Проверено: N из M · успешно … · не прошли … · заблокировано … · не
автоматизированы …» — «не прошли» counts only real failures. The bars
of pass 2 and of each re-run measure their own work, as described above:

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
| TC-19 | Ошибка при недоступном хранилище файлов | 🙅 не автоматизирован: остановка хранилища сломает общий стенд | вручную: остановить хранилище на отдельном стенде, загрузить файл, ждать «Не удалось сохранить файл, попробуйте позже» |

## Проход 2 — разбор упавших

```text
████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%
```

Разобрано: 2 из 5 · тест исправлен 1 · дефект приложения 1

Сейчас: перезапуск, круг 1 — 1 из 2. Полоса разбора двинется после него.

### Перезапуск — круг 1 из 2: проверка исправленных тестов

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
| TC-9 | Отмена чужой брони | ❌ не прошёл | — | ▶️ разбирается |
| TC-15 | … | ❌ не прошёл | | ⏳ ждёт |

Verdict: идёт прогон · коммит 1a2b3c4 · обновлено 2026-10-06 14:32
````

The comment cell holds the spec file, and for a failure what was seen
against what was expected and the screenshot path.

Statuses. Pass 1: `⏳ ждёт`, `✍️ пишется тест`, `▶️ выполняется`, then
`✅ прошёл`, `❌ не прошёл`, `⛔ заблокирован: <причина>`,
`🙅 не автоматизирован: <причина>`, and later `✅ прошёл после исправления
теста` for a case a re-run turned green; the main count line is
«Проверено: N из M · успешно … · не прошли … · заблокировано … · не
автоматизированы …», always with the «Проверено:» label. Pass 2:
`⏳ ждёт`, `▶️ разбирается`, then `✅ тест исправлен, прошёл`,
`🔧 тест не удалось исправить`, `❌ дефект приложения`,
`🖼 расхождение с макетом`, `❓ пробел в ТЗ`; its count line is «Разобрано:
N из M» with the results that occurred. After pass 2 the runner sets the
`Verdict:` line: `PASS` when every automated case passed (directly or
after a test fix), `DEFECTS` when any app defect, mockup mismatch, spec gap or screen-check
breach remains, `BLOCKED` when blocked cases leave a screen unchecked. Under
it, a «Проверить вручную» list names every `🙅 не автоматизирован` case
with its reason and the manual steps — they are not a defect, but nobody
has checked them yet — and a «Проверка экрана» list names each breach of
the screen check with its screen and `UX-n` («S-2 · 375 — страница
прокручивается вбок — UX-74»). A breach is an app defect: it makes the
verdict `DEFECTS` without changing any case's status.

A `DEFECTS` verdict names, per defect, the unit or screen it points at, so
the next step is one increment plan of fix units, not a hunt. Ask about that
per `pipeline`; do not fix here.

The session commits the suite, `test(e2e): пользовательские тесты
<version>`, so CI and the next run start from it. The report stays on disk
in the version folder — `documentation/plans/` is out of git.
A failing test for a real defect stays in the suite: it is the check the
fix plan must turn green.

## Before you finish

- write: every AC has a `TC-` or a «Без интерфейса» line; every state row,
  user-causable response outcome and «Поля ввода» rule has a case; steps name actions, not widgets; expected texts come
  from the frame's «Тексты» table or are marked `текст — по кадру`.
- run: the suite is committed-ready under the E2E folder with `test:e2e`;
  pass 1 reached 100% and every failed case went through pass 2; no
  application file changed; the `Verdict:` line under the last table is the
  verdict.

## References

- `references/writer-prompt.md` — packet for `ui-test-writer`.
- `references/runner-prompt.md` — packet for `ui-test-runner`.
- `playwright-cli` — locators, test generation, traces, screenshots.
- `ux-patterns` — what a frame comparison may flag besides the spec.
- `pipeline` — where both modes sit.
