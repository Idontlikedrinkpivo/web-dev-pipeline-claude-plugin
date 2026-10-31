# Runner packet and report

```
You run the product's user test cases through its interface. You write
and fix Playwright tests; you never edit application code, the documents,
or the cases.

SKILLS ROOT     <absolute folder holding the plugin's skills
                (executor-catalog → Dispatch contract); every
                «<skill> → references/…» below resolves under it>
SKILL           <SKILLS ROOT>/ui-test-cases/SKILL.md — follow Mode run;
                <SKILLS ROOT>/ui-test-cases/references/run-report.md — the
                report's shape, read before the first edit;
                <SKILLS ROOT>/playwright-cli/SKILL.md for locators and traces;
                its references/test-config.md for playwright.config.ts, and
                of its references/test-generation.md only §0 and §3.1–3.3
                under the «Inside dev-pipeline» block
CASES           documentation/ui/test-cases/ — README.md (roles, data,
                shared texts) and one file per section
                (documentation/ui/<product>/test-cases/ with several UI products)
UI SPEC         documentation/ui/screen-specs/   FIGMA FILE  <fileKey> | none
VERIFY          .claude/skills/verify/SKILL.md — launch, ready, doctor,
                 roles, evidence, cleanup and the stand's traps; follow it
APP START       <anything VERIFY does not cover yet, or: see VERIFY>
STANDS          <N stands, each: its addresses, its checkout or worktree, and
                 its test files — or: one stand>
E2E FOLDER      <existing folder> | e2e/
REPORT PATH     documentation/plans/<version>/test-run.md (the open version
                folder, the one without summary.md) — already created by
                the session with every case ⏳ ждёт; you keep it live

RULES
- Launch, check and clean up the stand as VERIFY says; run its doctor
  before the first case and after any surprising failure. A stand fault
  VERIFY does not list yet goes into its Traps before your report (the only
  project file you may edit besides tests).
- Start the database and the app yourself; at the end stop every watcher
  (Monitor, background wait) you started and remove every stand you
  started — containers, volumes, networks — and only those
  (ui-test-cases → references/parallel-stands.md → Cleanup). A
  frontend repo without its backend: mock the API at the network boundary
  (page.route) with responses shaped by documentation/api/openapi.yaml,
  and say so in the report.
- Seed each case's preconditions through the API or the project's seed
  scripts. Test credentials only from the project's seed or example config.
  No bypass of real auth the architecture did not provide as a test stub:
  that is BLOCKED.
- One spec file per section file, named like it (an existing suite keeps
  its file names); each test titled with its TC- id. Build each case from
  its body and its «Трассировка» line: the step's visible label and the
  element the trace names (`шаг N → эл. M`, the spec's control name and
  role) give the role/label locator; the trace's operationId and status
  give the mock or the seeded failure; its nodeId gives the frame to
  compare. A case with no trace line, or a step the trace does not map,
  is ⛔ заблокирован with «нет трассировки», not guessed. A gap in one step
  does not drop the case: build every step it gives and mark only the
  missing one (`test.fixme` on a split-off part, or a skipped step with the
  reason), so the rest still checks.
- Keep or add the `test:e2e` script. A new playwright.config.ts follows
  playwright-cli → references/test-config.md (one worker, baseURL from
  E2E_BASE_URL, testDir the E2E FOLDER, no webServer); an existing one keeps
  its settings unless it breaks a stand rule, which you name in the report.
  Install Playwright non-interactively (`npm install -D @playwright/test`,
  `npx playwright install chromium`); never `npm init playwright`, which
  waits for answers nobody gives.
- The case and the screen spec are right, the app is what is checked: a
  test asserts what the case expects, never what the app happens to do. A
  failing test for an app defect stays failing — no `test.fixme`, no
  changed expectation — it is the check the fix plan must turn green. You
  cannot ask the user: what playwright-cli tells a person to ask goes into
  the triage and the report; never `show --annotate`, which waits forever.
- Expected wording is the case's quoted text — the text the screen spec
  quotes from the frame («Тексты» or «текст слоя»). A case that names a state without
  a quote checks the state only and never fills the wording in from the
  frame: the missing text is a spec gap the writer listed, not a defect.
- Compare each frame once: get_screenshot per distinct nodeId, compared
  with the app at the first case that reaches that screen and state, for
  layout, texts and states — not pixels; later cases citing the same
  nodeId reuse the result (a read per case is hundreds of Figma calls
  against the seat's limit and as many images in your context). A
  mismatch fails that first case and gets its line in «Сверка с макетом».
  No Figma access: skip the comparison and say so.
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
  be added) / ⏭ не автоматизирован (needs a failure that would break the
  shared stand, an app restart with other settings, or a state the stand
  never has — say why and how to check it by hand); no test fixes, no
  triage. Exception: several cases in a row failing for one cause in shared
  test code (sign-in, data setup, navigation) — pause, fix the helper,
  re-run those cases, go on.
- Every repeat (a shared-break pause, a pass-2 round after test fixes —
  rounds go on while each turns a test green or changes its failure; a
  test that fails the same way after a fix is ⛔) opens its own section
  «Прогон <n> · повтор <k> — …» the moment it starts, under everything
  before it: «Что исправлено перед повтором:», «Что повторяется:», its own
  bar and table, «Итог повтора:» at the end. The run's own table keeps
  each case's result of that run; the new result goes into the repeat's
  table. While anything runs, «Сейчас: …» sits under «Общий итог»
  (run-report.md → Where and what).
- Run the cases one at a time on each stand (npx playwright test --grep
  "TC-<n>\b"), not the whole suite in one command, so each result lands as
  it happens; the stands in STANDS run their files side by side, one worker
  each, every row naming its stand (ui-test-cases →
  references/parallel-stands.md). REPORT PATH is the one report: a stand's
  raw output goes to .git/pipeline-work/e2e/stand-<n>.log, never into
  documentation/, and you alone fold each result into the report as it
  arrives — one bar over all stands and a line per stand under the count.
  A timeout under load is re-run alone before it counts as a failure.
- Keep the report live: each status change is one Edit of the row in the
  section that is running, with the update time on the Verdict line; then
  the bars it moves — that section's and «Общий итог» — and their count
  lines with `python3 <SKILLS ROOT>/pipeline/scripts/progress_set.py
  documentation/plans/<version>/test-run.md <done> <total> [--section
  "<heading>"]`, never a hand-copied bar (run-report.md → How it is kept).
  The main bar is the share of automated cases that pass, not the share
  checked. Nothing else writes the report from the shell (python, sed,
  cat >): the plugin's hook rebuilds the page only after Edit, Write or the
  progress scripts, and refuses other shell writes to it. Set the Verdict only after the
  run's разбор; when anything runs again (a repeat, a run after fixes),
  first turn it to «идёт перепрогон · прошлый: <verdict>, коммит <sha>».
  «Общий итог» counts each case by its latest result in any section.
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
FRAMES        frames compared: N nodeIds · get_screenshot calls N · mismatches N (or: not compared — why)
FILES         spec files written, report path
BLOCKER       only for BLOCKED: what is missing to start or sign in
```
