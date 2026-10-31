# Run hygiene — the shared tree, the database, commits

Read at Step 1 of every run. Each rule here comes from a run that lost hours or
data without it: the tree, the test database and the stand are shared by the
orchestrator, the executors and the reviewers, and nothing else keeps them apart.

## The database

- **Tests never touch the stand's database.** A test that creates, migrates,
  truncates or cleans a schema runs on a database of its own — the test service
  of `docker-compose.test.yml`, or a temporary database the helper creates — never
  on the one the running stand (`dev`, `demo`, the e2e stand) serves. The test
  helper reads `TEST_DATABASE_URL` and **fails when it is unset, when the
  database name has no «test», or, outside CI, when it equals `DATABASE_URL`**;
  it never falls back to a default address. Locally the host's tests get a
  database of their own on the test server (`<project>_test_host`, created once
  — the verify skill's doctor names both and says they differ), not the one the
  e2e stand serves
  (`pytest-patterns` → conftest template, `vitest` → the database helper). A
  helper in the project that falls back is fixed before the run goes on — a unit
  of its own, or the first fix of the run, asked once.
- **`run_check.py` holds both rules below the model:** it refuses a test run whose `TEST_DATABASE_URL`
  equals `DATABASE_URL` or names a database without «test», and a second run on a test database another
  `run_check` is still using (exit 3, the line says who holds it). Run every suite through it.
- **One test-suite run at a time on a shared database.** Before starting a suite
  on the shared test database, make sure the previous one has ended (its task is
  done, no process holds the port). Never `&` a suite in Bash, and never start one
  in the background while another runs in the foreground. While a suite runs, a
  reviewer's packet says not to run tests that use the database. Two runs at once
  give deadlocks and foreign-key failures that look like defects and cost a full
  rerun.

## Commits

The plugin's hook (`hooks/guard.py`) refuses the three commit mistakes below before they land — a commit chained
to a check, a `Plan-Unit:` line git cannot read, a commit on `main` while an iteration is open — and says why.
A refusal is not an error to work around: fix the command as it says.

- **Commit only after reading the checks.** `git commit` is its own call, after
  the output of Step 5.3 has been read and is green — never chained in one
  command with a test run (`npm test && git commit`, `…; git commit`): a red line
  in an output nobody read lands in history.
- **The trailer is git's trailer.** `Plan-Unit: <version>/<id>` stands in the
  message's **last paragraph**, together with `Co-Authored-By:` and with no blank
  line between them:

  ```text
  U7: отмена брони владельцем

  Plan-Unit: 2.1.4/U7
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

  A blank line between them makes git drop `Plan-Unit` from the trailers, and
  every tool that asks git for trailers — `where_am_i.py` on a fresh clone,
  `code-review-full` mapping commits to units — sees the run as unmapped. After
  the run's first commit check it once:
  `git log -1 --format='%(trailers:key=Plan-Unit,valueonly)'` prints the id.

## Files the plan did not list

When an earlier unit split, moved or renamed a file that a later unit's `Файлы`
names, or left sites for it («отложено до U<N>», a Cross-unit watch line naming
U<N>), correct U<N>'s file list **in its packet** before the dispatch — no
`BLOCKED` round for it — and write one line in the run report: «Поправка
«Файлов» U<N>: <old> → <new> (по U<K>)». The plan stays byte-identical; the review
reads the run report. Only a file whose need nothing in the run explains still
goes the Step 6 way (re-dispatch with the corrected list, or a scope question).

## What reaches the orchestrator

The orchestrator keeps everything it reads for the rest of the session, and every later call pays for it again:
in a measured run its context grew by ~100,000 tokens per unit, a third of it agents' reports. So:

- **Agents' reports are short; their details are files.** An executor's report and a reviewer's report come
  back in about 2,000 characters; the long part sits in `$(git rev-parse --git-dir)/pipeline-work/<version>/`
  (`U<n>-details.md`, `U<n>-review-<pass>.md`) — the packet names each path. Paste the short report into the
  reviewer's packet with the path; the reviewer reads the file.
- **When the orchestrator opens the details file itself:** a High or risk-floor unit; any status but `DONE`;
  NEEDS FROM ORCHESTRATOR other than «нет»; files changed outside the unit's `Файлы`; and when
  `python3 "${CLAUDE_SKILL_DIR}/scripts/report_alarm.py" <details file> --concerns "<CONCERNS and NEEDS>"`
  exits 1 — an alarm word (skipped, not run, a workaround, TODO) with nothing in CONCERNS. A missing details
  file or a report without NEEDS goes back to the executor unread.
- **Checks run through `scripts/run_check.py <name> -- <command>`** — the unit's tests, `lint`, `typecheck`, the
  критерии готовности: the log goes to a file, the summary (exit code, counts, failures, «⚠» when tests got fewer
  or skipped grew) into the context. A failure is read in full from the log, the passing rest is not.
- **Other long output goes to a file too** — a search, a diff, a listing: `> <file>`, then read the part needed.

## Context — handing over to a fresh session

The same rule holds for every stage (`pipeline` → `references/context.md`); what is particular to `work`:

After each unit's commit (Step 5.6) run
`python3 "${CLAUDE_SKILL_DIR}/../reflect/scripts/context_size.py" "$PWD"`. Over the limit (300,000 tokens by
default; exit 2), hand over at this boundary — the unit is committed, nothing is in flight — rather than let the
host compact the session, which loses rules:

1. Refresh `resume.md` (`pipeline` → `references/pause-and-resume.md`), the run report and the progress line,
   as at any stop. The run report says where the next session starts («продолжать с U18»).
2. **Run by a parent session** (its first message named one): send the parent «ПРОГОН <version> ПЕРЕДАН ·
   после U<n> · контекст <N> тыс. · продолжать с U<m>» and stop. The parent opens the next nested session
   (`pipeline` → `references/parent-session.md`).
3. **No parent, and the host can start a session** (Claude Desktop: `mcp__ccd_session__start_session` — often a
   deferred tool: load it with ToolSearch `select:mcp__ccd_session__start_session` before deciding it is absent):
   start one locally, in this folder, with a fresh context, no worktree, the title «<version> · часть <n+1>» and the prompt «продолжи прогон <version>;
   родительская сессия — <this session's name>; по закрытии, остановке или передаче пиши ей» — then this
   session becomes its parent: it waits, relays questions to the user, and opens the next part when told.
4. **Neither:** tell the user in one line to open a new session in this folder and write «продолжи прогон
   <version>», and stop.

The new session starts from git, the run report and `resume.md` (Step 1) — it repeats nothing. The script
cannot tell two sessions working in one project apart: it reads the newest, and its line names that session.

## The orchestrator's own commits

A commit no unit made — a stand made copyable (`stand`), the verify skill
(`verify-skill`), a changed decision (`decision-<n>`), a review fix
(`review-fix-<n>`), a contract edit — passes the same checks a unit does before it
is committed: the tests it can break, `lint`, `typecheck`. An OpenAPI edit
regenerates what is generated from it on **both** sides — the backend's schema or
types and the frontend's client — in the same commit (`contract:generate` or the
project's equivalent in each part), and runs the contract test.

The критерии готовности of Step 7 are taken on HEAD **after the last commit**. A
commit that lands after a criterion ran — a fix, a stand change — reruns every
criterion it can affect before the review reads them.

## The review range of a second run

`BASE` of a run is the HEAD that the **last whole review** (`code-review-full`)
covered, not the HEAD at the run's start: commits made between two runs — a stand,
the e2e suite, decision documents — belong to the next review. The run report
names where BASE came from («BASE = HEAD финального ревью прогона 1, a1b2c3d»).
An iteration closed after several runs gets one review of the whole iteration,
from the previous iteration's tag, before the close — offered, as Step 7's
question, when any commit of the iteration lies outside every review range.

## The environment as a reason to stop

Before deferring a unit or stopping a run for the environment — a proxy, a network,
a port, a missing image — check the cause with a live command now (`docker pull` of
a small image, `curl` to the source, `lsof -i :<port>`). A trap written in the
verify skill (`.claude/skills/verify/`, «Ловушки») is a hypothesis until its check
fails: each trap carries the command that shows it (`deploy-topology` →
`references/verify-skill.md`), and a trap whose check passes is removed from the
skill in the same run, its own commit with `Plan-Unit: <version>/verify-skill`.

## Executors in the shared tree

A parallel unit's executor works in its own worktree (`WORKTREE yes` in its
packet): every path the packet or a file it reads gives is relative to the
repository root, never the main tree's absolute path — an absolute one sends
its edits into the main tree, and the harness refuses them.

The packet says it (`executor-catalog/references/worker-prompt.md` → RULES); the
orchestrator checks it when the unit returns:

- in the main tree an executor never runs `git stash`, `git reset`, `git checkout --`
  (the hook refuses `git stash` of everything, `reset --hard`, `clean -f`, `checkout -- .`, and an edit from a
  worktree into the main tree; `git checkout -- <file>` by name passes)
  or `git clean`;
- a link to installed dependencies (`ln -s …/node_modules`) is made only inside the
  executor's own worktree, and only where no folder of that name exists;
- a worktree is removed only after its unit is committed — before that the executor
  may still be resumed for a review fix;
- a shared registry that parallel units would all edit — the lint ratchet list, a
  shared config, a barrel file — is not edited by the units: each reports its lines,
  and the orchestrator writes them once when it brings the wave home;
- an executor stops every background task it started (a watch, a `run_in_background`
  command) before its report — the plugin's hook (`hooks/watchers.py`) keeps an agent from ending while one it
  started still runs, and names it. When the agent still shows as running after its report,
  stop it (`TaskStop`) — a finished executor left «running» holds the panel for hours.

## Finishing an older iteration while a newer one is open

When an iteration still has units to finish and the user has started the next one
in the same folder, the older one is finished in a worktree of its own, never by
switching the main tree back and forth:

1. `git worktree add ../<repo>-<old version> iteration/<old version>`;
2. link its plans folder: `ln -s <main tree>/documentation/plans/<old version>
   ../<repo>-<old version>/documentation/plans/<old version>` (plans are out of
   git, so the worktree has none);
3. install dependencies there (`npm ci` / `uv sync`), copy the local test settings
   (`.env.test.local`) and regenerate the generated files the build needs
   (a bundled OpenAPI, the client);
4. run `work` from that folder: `plan_state.py` takes the linked plans folder;
5. one stand per machine: stop the newer iteration's stand before raising the
   older one's, and say so.

The `where` line of Step 1 stops only on a worktree with **no** plans folder; a
worktree with the linked folder is this case.
