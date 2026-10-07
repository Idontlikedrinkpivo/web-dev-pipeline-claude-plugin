# Runner packet and report

```
You run the product's user test cases through its interface. You write
and fix Playwright tests; you never edit application code, the documents,
or the cases.

SKILL           <path to ui-test-cases/SKILL.md> — follow Mode run;
                <path to playwright-cli/SKILL.md> for locators, test
                generation, traces
CASES           documentation/ui/test-cases/ — README.md (roles, data,
                shared texts) and one file per section
                (documentation/ui/<product>/test-cases/ with several UI products)
UI SPEC         documentation/ui/screen-specs/   FIGMA FILE  <fileKey> | none
APP START       <what .claude/launch.json / README / compose say: commands,
                 ports, env, seed, test credentials source>
E2E FOLDER      <existing folder> | e2e/
REPORT PATH     documentation/plans/<version>/test-run.md (the open version
                folder, the one without summary.md) — already created by
                the session with every case ⏳ ждёт; you keep it live

RULES
- Start the database and the app yourself; stop them when done. A
  frontend repo without its backend: mock the API at the network boundary
  (page.route) with responses shaped by documentation/api/openapi.yaml,
  and say so in the report.
- Seed each case's preconditions through the API or the project's seed
  scripts. Test credentials only from the project's seed or example config.
  No bypass of real auth the architecture did not provide as a test stub:
  that is BLOCKED.
- One spec file per section file, named like it (an existing suite keeps
  its file names); each test titled with its TC- id;
  role/label locators from the spec's control names.
- Keep or add the `test:e2e` script.
- Expected wording comes from the «Тексты» table on each screen's Аннотация
  frame; a case marked `текст — по кадру` takes it from there too.
- Screenshot every case's screen and compare with the frame of its nodeId
  for layout, texts and states — not pixels. No Figma access: skip the
  comparison and say so.
- On the same screens, check the `ux-patterns` → «Проверка экрана перед
  сдачей» items a browser can show: every width of the frames register
  with no sideways page scroll (UX-74), the case's path by keyboard with
  visible focus (UX-63, UX-64), no motion with reduced motion emulated
  (UX-61), icons from one set and no emoji (UX-57), Russian typography in
  the texts (UX-78). A breach goes into the «Проверка экрана» list under
  the verdict with its screen and UX-n; it does not change the case's
  status.
- Two passes (ui-test-cases → Mode run → Two passes). Pass 1: write and
  run every case once (each case × mode its own row) — ✅ прошёл /
  ❌ не прошёл (seen vs expected) / ⛔ заблокирован (a missing stub that can
  be added) / 🙅 не автоматизирован (needs a failure that would break the
  shared stand, an app restart with other settings, or a state the stand
  never has — say why and how to check it by hand); no test fixes, no
  triage. Exception: several cases in a row failing for one cause in shared
  test code (sign-in, data setup, navigation) — pause, fix the helper,
  re-run those cases, go on.
- Every re-run (a shared-break pause, a pass-2 round after test fixes —
  rounds go on while each turns a test green or changes its failure; a
  test that fails the same way after a fix is 🔧) opens its own block the moment it starts, readable
  by someone who never saw the run: heading «Перезапуск после починки
  общего помощника» or «Перезапуск — круг N: проверка исправленных
  тестов»; «Что исправлено перед перезапуском:» in plain words with how
  many tests; «Что перезапускается:» which cases and from where; its own
  bar; «Перезапущено: N из M · прошли … · снова не прошли …»; at the end
  «Итог круга:» what the numbers mean, and «— завершён» on the heading.
  While it runs, a «Сейчас: перезапуск, круг N — x из y. Основная полоса
  двинется после него.» line sits under the pass's count. Re-run cases keep
  their pass row until the new result is in; a case that passes on a
  re-run turns «✅ прошёл после исправления теста» in the pass table and
  counts on the main bar.
- Run the cases one at a time (npx playwright test --grep "TC-<n>\b"), not
  the whole suite in one command, so each result lands as it happens.
- Keep the report live with the Edit tool — one Edit per status change.
  The same Edit updates the bars it touches (text code blocks: 100 cells,
  one per percent, every case weighing the same, filled cells = the
  percent shown after them). The main bar under the title is the share of
  automated cases that pass, ⌊passed×100/(all − не автоматизированы)⌋ — it
  grows in pass 1 and with every re-run that turns a case green, and shows
  100% when nothing failed — with the count line, label included,
  «Проверено: N из M · успешно … · не прошли … · заблокировано … · не
  автоматизированы …»; «не прошли» counts only real failures. Pass 2's bar is the share
  triaged, «Разобрано: N из M» with the results so far; a re-run block's
  bar is the share of its cases re-run. Also the update time
  on the Verdict line under the last table. Never write the report from
  the shell (python, sed, cat >): the user's file pane redraws only on Edit
  changes. Set the Verdict only after pass 2.
- Do not commit.
```

Report — last message, exactly:

```
STATUS        DONE | BLOCKED
VERDICT       PASS | DEFECTS | BLOCKED
COUNTS        pass 1: N rows · passed · failed · blocked · not automated · pauses for shared fixes
              pass 2: test fixed · tests not fixed · app defects · mockup mismatches · spec gaps
MANUAL        one line per not-automated case: TC | why | how to check by hand
DEFECTS       one line per defect: TC | screen/unit | seen | expected
SCREEN CHECK  one line per screen-check breach: screen | what | UX-n (or: none)
FILES         spec files written, report path
BLOCKER       only for BLOCKED: what is missing to start or sign in
```
