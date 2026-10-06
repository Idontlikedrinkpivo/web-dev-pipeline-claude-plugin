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

**What a case set must hold:**

- One case per acceptance criterion that a person can reach through the
  interface — main flow, every Alt and every Exc. An AC with no screen (a
  scheduled job, an email content check) is listed under «Без интерфейса»
  with the reason, not dropped.
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

**Artifact:** `documentation/ui/test-cases.md`, beside the frames register
and `screen-specs/` (with several UI products, one per
`documentation/ui/<product>/`), with `sources:` pinning the SRS and every
screen spec as `path@<version>`, and `updated:`. Unversioned: an increment edits it in
place, keeps every `TC-` id, and gives a new case the next free number.

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

The file ends with a coverage table: every AC id → its `TC-` ids, or the
«Без интерфейса» line. An AC with neither is the writer's failure, not the
reader's.

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

**The report is live.** Before the dispatch, create the report (path
below) with every case of the run `⏳ ждёт`, the progress bar at 0% and
`Verdict: идёт прогон` on the first line, and post its link in the chat as a
clickable Markdown link with its repo-relative path — the user opens it once
and watches the cases turn over. The runner then changes it with the Edit
tool the moment a case changes status — never from the shell (`python`,
`sed`, `cat >`): the user's file pane redraws only on edit-tool changes.

**Dispatch:** resolve `ui-test-runner` through `executor-catalog` with
`references/runner-prompt.md`. The runner:

1. writes one Playwright spec per screen or flow under the project's E2E
   folder (`e2e/` unless the project has one), each test titled with its
   `TC-` id, using role- and label-based locators from the screen spec's element
   names, following `playwright-cli` → test generation;
2. adds or keeps the `test:e2e` script, so `ci-pipeline` can run the
   suite;
3. runs the cases one at a time (`npx playwright test --grep "TC-7\b"`),
   so each result reaches the report as it happens; for each case takes a
   screenshot of the screen under test and compares it with the frame
   (`get_screenshot` of the cited `nodeId`) for layout, texts, and states —
   not pixel equality; without Figma access the comparison is skipped and
   the report says so;
4. triages each failure: **app defect** (the app contradicts the spec),
   **test defect** (fixed in the test, then re-run), or **spec gap** (the
   spec never said). It never edits application code.

**Report:** `documentation/plans/<version>/test-run.md`, in the version
folder of the current iteration — the open `plans/<v>/` folder, the one
without `summary.md`. No open version folder → say so and ask per
`pipeline` → "Asking before a transition" which version this run belongs
to; do not invent one. Overwritten each run (several UI products: one
section per product). The first line is `Verdict: идёт прогон` while the run
is on and `Verdict: PASS | DEFECTS | BLOCKED` at its end; the progress bar
follows the rules of `work` → `references/progress-file.md` → The progress
bar — a hundred cells, one per percent, every case weighing the same —
counting a case done once it has a final status:

```markdown
Verdict: идёт прогон

# Прогон пользовательских тестов · <version>

Прогресс: █████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 37%

Коммит 1a2b3c4 · Сделано: 9 из 24 · прошли 7 · дефекты 1 · расхождения с кадром 1 · Обновлено: 2026-10-06 14:32

| TC | Экран | Кейс | Статус | Что увидели / ожидалось | Скриншот |
|---|---|---|---|---|---|
| TC-1 | S-1 | Список комнат на сегодня | ✅ прошёл | | |
| TC-7 | S-3 | Отмена начавшейся брони | ❌ дефект | «Ошибка 409» / «Бронь уже началась, отменить нельзя» | e2e/artifacts/TC-7.png |
| TC-8 | S-3 | Отмена за час до начала | 🔧 тест исправлен, перезапуск | | |
| TC-9 | S-3 | Отмена чужой брони | ▶️ выполняется | | |
| TC-10 | S-3 | Пустой список броней | ✍️ пишется тест | | |
| TC-11 | S-1 | Закрытая комната не видна | ⏳ ждёт | | |
```

Statuses: in progress — `⏳ ждёт`, `✍️ пишется тест`, `▶️ выполняется`,
`🔧 тест исправлен, перезапуск`; final — `✅ прошёл`, `❌ дефект` (the app
contradicts the spec), `🖼 расхождение с кадром`, `❓ пробел в ТЗ`,
`⛔ заблокирован: <причина>`. At the end the runner sets the first line to
the verdict and the counters to the final numbers.

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
  every case has a result; no application file changed; the report's first
  line is the verdict.

## References

- `references/writer-prompt.md` — packet for `ui-test-writer`.
- `references/runner-prompt.md` — packet for `ui-test-runner`.
- `playwright-cli` — locators, test generation, traces, screenshots.
- `ux-patterns` — what a frame comparison may flag besides the spec.
- `pipeline` — where both modes sit.
