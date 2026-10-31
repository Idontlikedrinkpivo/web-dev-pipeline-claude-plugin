---
name: ui-test-cases
description: >-
  UI acceptance. write: SRS criteria and screen specs become test cases; run: Playwright tests on the local app,
  checked against the frames. Use for «тест-кейсы», «протыкай приложение», «протестируй в браузере», «e2e». One-off
  check: playwright-cli.
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

**Handed to another person?** In the session of a person who took
mode write (`pipeline` → `references/team.md`): the version comes from the
branch `iteration/<version>`, inputs arrive by `git pull --rebase`, only this
stage's documents are written — each committed the moment it is finished,
with the push command after it — and the stage closes as usual, its stamp
included. After the last stage this person took, the «готовы и запушены»
line replaces the offer of a stage someone else has.

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
asking which model. The session writes no case; it only moves an old
single file first (Artifact below). A `BLOCKED` with a question only the
user can answer: ask it in the chat (`executor-catalog` → Escalation),
paste the answer into the packet's `ANSWERS` and dispatch the writer again.

**Progress file.** Before the dispatch, create
`documentation/plans/<version>/progress-test-cases.md` per
`pipeline` → `references/progress-files.md` — one row per section of the
set (below) plus «Без интерфейса», all `⏳ ждёт` — and pass it to the
writer as `PROGRESS FILE`. A full set runs to hundreds of cases; the
writer marks each section as its cases are written. For the chat, run
`python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/progress_link.py"
documentation/plans/<version>/progress-test-cases.md` (add `--desktop`
when the session has the built-in browser) and paste the line it prints as
is — before the dispatch and each time one returns; each time one returns, check the context too
(`pipeline` → `references/context.md` → When to hand over). It carries
the count and the link to the page that reloads itself; a link written by
hand opens the Markdown source or a page that never refreshes.

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

**Two readers, two layers.** A case is read by a person — a tester, an
analyst, the owner checking what will be tested — and turned into a test
by the runner. The body is written for the person; everything only the
runner needs goes into one «Трассировка» line under it.

- **The body speaks the user's language.** Roles and screens by name, the
  id in brackets on first mention («Резидент», «Расписание переговорных
  (S-1)»). Steps are things a person does, named by the label the user
  sees on the screen, without a widget, a gesture, CSS or coordinates:
  «Выбрать «Отменить бронь»», not «нажать красную кнопку справа» and not
  «выполнить действие эл. 13». A designer who turns a dropdown into a
  context menu must not have to rewrite a case; a label survives that, and
  the e2e test finds the element by the same accessible name.
- **Every step is an action**; «Посмотреть на …» when the step only reads
  the screen, never a bare «Проверить эл. 4».
- **Take the path a test can walk.** When several paths reach the same
  state, step through controls the screen spec names (a field, a button
  with its label) rather than one it leaves without an accessible name (a
  free cell of a grid, an icon with no label). A state reachable only
  through an unnamed element still gets its case, and the gap goes to the
  set's spec gaps («эл. 9 без доступного имени»), so `screen-spec` can fix
  it.
- **Real values, never placeholders.** Dates, times, names and counts in
  steps and expected texts are concrete, computed from the preconditions
  («завтра, 21.10», «Отменено 2 брони»); a date relative to the run is
  written relative («Д+1») and defined once in the README. `{дата}` or
  «по кадру» inside an expected text is a case the runner cannot check.
- **«Что должно быть» is what a person sees.** The exact texts the screen
  spec quotes from the frame — its «Тексты» table, or a text layer marked
  «текст слоя» in a designer's file with no annotation — each labelled — «заголовок
  «…», ниже текст «…»», «под полем «Дата»: «…»», «уведомление: «…»». No
  field names, derived values, response bodies, status codes or ARIA
  attributes in the body; accessibility in words: «сообщение зачитывает
  экранный диктор», «следующий Tab — «Повторить загрузку»». A text the
  spec marks missing (`текст — нет в «Тексты»`, or `текст — нет на кадре`
  in a designer's file) is neither composed nor marked «по кадру»: the case names the state without a quote, and the missing text
  goes to the set's spec gaps for `screen-spec`.
- **A server failure is a precondition in words** («сервер не может отдать
  расписание»), its mock goes into the trace line.
- **Preconditions name the data** («у резидента бронь «Байкал» завтра
  10:00–11:00»), so the runner can seed it and a person can set it up.
- **«Проверяет» opens the case**: the requirement ids it proves (AC, BR,
  NFR, or the spec row), so an analyst traces it in a glance.
- **The trace line is mandatory and exact**, in one fixed syntax a script
  can check: `кадр <nodeId>[, <nodeId>]` · the state row · per step
  `шаг N → эл. M[, эл. K] (<nodeId>)` · `` `operationId` → <status> ``
  (`mock` before the status for a forced outcome) · any ARIA expectation.
  A case without it is not done: the runner builds its locators, mocks and
  frame comparison from it.
- **The trace is checked at three points, never trusted.**
  `scripts/check_trace.py` resolves every reference against the current
  documents — the step exists in the table, the element in the screen spec,
  the frame in the spec or the register, the operation and its status in
  the OpenAPI. It runs at this stage's close (below), at the start of
  `screen-spec` (when cases already exist) and in `docs-consistency` before
  the plan; each sends what it finds
  to `ui-test-writer`, which rewrites that case's trace from the current
  spec — never patches a number.

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
├── 02-room-schedule.md        2. Расписание переговорных
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
  moved into the folder by the session before the writer is dispatched (the
  writer does not commit): its `## N.` sections become section files, the
  shared parts and the closing tables go to `README.md`, every case is
  copied unchanged with its id, and the old file is deleted — one commit
  of its own («docs: тест-кейсы разложены по разделам»; a move needs no
  request from the user, git keeps the old file's history). The move
  rewrites no case; the writer then gets the folder.

```markdown
## TC-7. Резидент не может отменить бронь, которая уже началась

**Проверяет:** UC-2 AC-Exc-2 · BR-4
**Кто:** резидент · **Экран:** Расписание переговорных (S-1), окно «Отмена брони»
**Подготовка:** резидент вошёл; у него бронь «Байкал», начавшаяся 10 минут назад

| # | Действие | Что должно быть |
|---|---|---|
| 1 | Открыть расписание на сегодня | бронь «Байкал» отмечена как своя |
| 2 | Выбрать свою бронь «Байкал» | открылось окно «Отмена брони» |
| 3 | Выбрать «Отменить бронь» | в окне текст «Бронь уже началась, отменить нельзя»; в расписании бронь осталась |

<sub>Трассировка: кадр 12:160 · состояние «Уже началась» (M2) · шаг 2 → эл. 11; шаг 3 → эл. 3 (12:160) · `cancelBooking` → 409 BOOKING_STARTED</sub>
```

`README.md` ends with the coverage table, one row per AC: `UC-n AC-…` →
its `TC-` ids, or «Без интерфейса» with the reason. An AC with neither is
the writer's failure, not the reader's.

**Two scripts close the stage, never trusted to the writer's word.** When
the writer returns, the session runs, from the repository root:

- `python3 "${CLAUDE_SKILL_DIR}/scripts/check_trace.py" --docs documentation --quiet`
  — every «Трассировка» resolves: the step, the element, the frame, the
  operation and its status;
- `python3 "${CLAUDE_SKILL_DIR}/scripts/check_coverage.py" --docs documentation`
  — every AC of the SRS has a row naming an existing `TC-` or «Без
  интерфейса», and no row or «Проверяет» line names an AC the SRS lacks
  (a repository without the SRS is not checked).

What either prints goes back to `ui-test-writer` (`MODE increment`, only
those lines), then both run again — round after round while each round
fixes something (`pipeline` → `references/convergence.md`). A line no round
can fix — the case needs an element, a frame or an operation the documents
do not have — is a spec gap in `README.md` and a row in `open-questions.md`,
named at the close. Only with both scripts at exit 0, or every remaining
line written down this way, is the set final: its commit, then the push
(`pipeline` → Commit each document).

## Mode run

**When:** after `work` closed its run and `code-review-full` passed (or the
user chose to go on without it). Cases must exist; without them, offer
mode write first.

**The app must start locally.** Read the project's verify skill
(`.claude/skills/verify/`) and run its doctor first; with none, write and
prove it before the dispatch (`deploy-topology` →
`references/verify-skill.md`), from `.claude/launch.json`, the README and
the test compose file. Pass its path to the runner as `VERIFY`. The runner
starts the database and the app, seeds the preconditions through the API
or the seed scripts the project has, and signs in with test credentials
from the project's seed or example config. External sign-in (SSO, SMS)
uses the test stub the architecture names; when there is none, that is a
`BLOCKED` with the gap, not an improvised bypass.

**Parallel stands.** Tests that share one stand run one at a time; speed
comes from more stands, each with its own database and storage and its
share of the test files. Before the dispatch, read
`references/parallel-stands.md`: measure how many stands this machine
holds, start them with the project's `scripts/e2e-stands.sh`, and pass them to the runner
as `STANDS`. A stand that cannot be copied yet (a fixed port, a
`container_name`, no `scripts/e2e-stands.sh`) is not a reason to run long
on one: when the machine holds more than one stand and the run has more
than one test file, ask once before the run — make it copyable now and run
on N, or one stand (`references/parallel-stands.md` → A stand that cannot
be copied yet).

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
   `⏭ не автоматизирован: <причина>` (the case cannot be checked honestly
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
   **test defect** — the test is fixed and the case re-run, round after
   round while each fix changes the failure (`✅ тест исправлен, прошёл`);
   after two failed fixes on one assumption the assumption is checked
   before a third (`pipeline` → `references/convergence.md` → Attack the
   premise); a test that fails the same way after a fix is `⛔ тест не
   удалось исправить`;
   **app defect** — the app contradicts the spec (`❌ дефект приложения`);
   **mockup mismatch** — works, but the screen differs from the frame
   (`🖼 расхождение с макетом`); **spec gap** — the spec never said
   (`❓ пробел в ТЗ`). App defects are not re-run: a fix plan fixes them.

The verdict is set only after pass 2.

**Every run and every repeat is its own section** of the report, one under
the other, with its own table and bar — a repeat says what was fixed before
it, which cases it repeats, and «Итог повтора:» at the end; a later run in
the iteration (after a fix plan) is appended, never written over the
first. At the top, «Общий итог» — the share of automated cases passing by
their latest result — and the page draws every section's bar at its top
(`references/run-report.md` → Where and what).

**The report is live.** Read `references/run-report.md` — the one place
for the report's shape: path, sections, bars, an example, statuses, the
verdict and the lists under it. Before the first run's dispatch, create the
report: «Общий итог» at 0%, the section «Прогон 1 — все кейсы» with every
case `⏳ ждёт` and its bar at 0%, `Verdict: идёт прогон` last; before a
later run, append its section «Прогон <n> — после …» and turn the verdict
to `идёт перепрогон · прошлый: …`; then run `python3
"${CLAUDE_SKILL_DIR}/../pipeline/scripts/progress_link.py"
documentation/plans/<version>/test-run.md` (add `--desktop` when the
session has the built-in browser) and paste the line it prints in the chat
as is — never a link written by hand (it gives the page that
reloads itself, served in the desktop app). The разбор section is added
under its run when the run reaches 100%, and the line is pasted again — as
it is each time a runner dispatch returns and after each repeat. A
run resumed after a break or a context compaction keeps the report: every
case without a result in the current pass goes back to `⏳ ждёт`, the line
is pasted again, and only then the runner goes on. The runner changes the
report with the Edit tool the moment a case changes status — never from
the shell (`python`, `sed`, `cat >`): the plugin's hook rebuilds the page
the user watches only after an Edit or Write call.

**Dispatch:** resolve `ui-test-runner` through `executor-catalog` with
`references/runner-prompt.md`. The runner:

1. writes one Playwright spec per section file of the cases, named like it
   (`01-login-session.spec.ts`; an existing suite keeps its file names), under the project's E2E
   folder (`e2e/` unless the project has one), each test titled with its
   `TC-` id, using role- and label-based locators from the screen spec's element
   names. From `playwright-cli` it takes `references/test-config.md` (the
   stand-ready config: one worker, `E2E_BASE_URL`, `testDir` the E2E
   folder) and, of `references/test-generation.md`, only §0 and §3.1–3.3
   under its «Inside dev-pipeline» block — the rest of that file is for a
   person at the keyboard: one test per file, the app taken as right,
   «ask the user», `test.fixme` for a known bug, `show --annotate`, `npm
   init`. The E2E folder and the config belong to this suite: `ui-test-cases`
   owns them, and a screen unit in `work` adds no spec there (`frontend` →
   Verification);
2. adds or keeps the `test:e2e` script, so `ci-pipeline` can run the
   suite;
3. pass 1: runs the cases one at a time (`npx playwright test --grep
   "TC-7\b"`), so each result reaches the report as it happens; takes a
   screenshot of the screen under test and compares it with its frame for
   layout, texts and states — not pixel equality. The frame is read once
   per `nodeId` (`get_screenshot`) and compared once, at the first case
   that reaches that screen and state; the cases citing the same `nodeId`
   reuse that result, because a read per case is hundreds of Figma calls
   against the seat's limit and as many images in the context. A mismatch
   is a `❌ не прошёл` with what differs on that first case and a line in
   the report's «Сверка с макетом»; without Figma access the comparison is
   skipped and the report says so. On the same screens it checks the items of `ux-patterns` →
   «Проверка экрана перед сдачей» a browser can show: every width of the
   frames register with no sideways page scroll (UX-74), the case's path
   by keyboard with visible focus (UX-63, UX-64), no motion under reduced
   motion (UX-61), icons from one set and no emoji (UX-57), Russian
   typography in the texts (UX-78);
4. pass 2: triages each failed case as above. It never edits application
   code.

**Report:** `documentation/plans/<version>/test-run.md` in the open version
folder. No open version folder → say so and ask per `pipeline` → "Asking
before a transition" which version this run belongs to; do not invent one.
After pass 2 the `Verdict:` line under the last table is `PASS`,
`DEFECTS` (an app defect, mockup mismatch, spec gap or screen-check breach
remains) or `BLOCKED` (blocked cases leave a screen unchecked); under it
the «Проверить вручную», «Проверка экрана» and «Сверка с макетом» lists
(`references/run-report.md`).

A `DEFECTS` verdict names, per defect, the unit or screen it points at, so
the next step is one increment plan of fix units, not a hunt. Ask about that
per `pipeline`; do not fix here.

A spec gap goes to the user as one plain line per `grill-me` → How a
question is shown — the situation in everyday words, what the screen does
now, the recommendation, and whether it means a spec edit — never as a
bare «пробел в ТЗ S-13». A spec gap, or a defect the user rules is the spec's and not the app's
(«так и должно быть»), is a changed decision: the screen spec — and the SRS
or the API when the rule lives there — and the cases that test it are
fixed and committed at once, with no version change (`pipeline` →
`references/decision-changes.md`), and those cases are re-run against the
new text before the verdict.

The session commits the suite, `test(e2e): пользовательские тесты
<version>`, so CI and the next run start from it. The report stays on disk
in the version folder — `documentation/plans/` is out of git.
A failing test for a real defect stays in the suite: it is the check the
fix plan must turn green.

## Before you finish

- write: `check_trace.py` and `check_coverage.py` exit 0, or each line
  they still print is a spec gap with its `open-questions.md` row; every
  AC has a `TC-` or a «Без интерфейса» line; every state row,
  user-causable response outcome and «Поля ввода» rule has a case; steps name actions, not widgets; expected texts are
  the ones the screen spec quotes, and each text it lacks is a spec gap for
  `screen-spec`, not a case marker.
- run: the suite is committed-ready under the E2E folder with `test:e2e`;
  pass 1 reached 100% and every failed case went through pass 2; no
  application file changed; the `Verdict:` line under the last table is the
  verdict.

## References

- `references/writer-prompt.md` — packet for `ui-test-writer`.
- `references/runner-prompt.md` — packet for `ui-test-runner`.
- `references/run-report.md` — the run report `test-run.md`: bars,
  sections per run and repeat, example, statuses, verdict. Read before creating it.
- `references/parallel-stands.md` — several identical stands for a long
  run: what makes a stand copyable, how many the machine holds, the split.
- `playwright-cli` — `references/test-config.md` (the stand-ready
  config), and §0 and §3.1–3.3 of `references/test-generation.md` under its
  «Inside dev-pipeline» block; locators, traces, screenshots.
- `ux-patterns` — what a frame comparison may flag besides the spec.
- `pipeline` — where both modes sit.
