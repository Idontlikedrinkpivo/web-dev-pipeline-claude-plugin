# The handover check — what the chat settled is on disk

Read in a nested session (`references/parent-session.md`) before it closes its stage or hands it over. The next
stage starts in a fresh session that knows only the files and git; a decision the user made in this chat and no file
holds is lost with the chat. The rule «write every decision down before the close» (`references/decision-changes.md`)
is the session's own; this check is a second reader that did not write the stage.

## When

- Before «ЭТАП <stage> ЗАКРЫТ» — after the stage's commits, before the message to the parent.
- Not in a session without a parent (a terminal run keeps its chat), and not for a stage that asked the user
  nothing: no answer, no decision to lose.

## How

1. The conversation, as a digest, by this session's title (its first message names it):
   `python3 "${CLAUDE_SKILL_DIR}/../reflect/scripts/sessions.py" mine "$PWD" "<the session's title>" "$(git rev-parse --path-format=absolute --git-common-dir)/pipeline-work/handover-<key>.md"`, `<key>` the stage's key (`scripts/subsessions.py` → Stage keys).
   A non-zero exit — the session's transcript not found — skip the check; step 4 says so with `--no-transcript`.
2. Dispatch `handover-checker` (`executor-catalog` → Dispatch contract, `subagent_type:
   "dev-pipeline:handover-checker"`, no `model`) with the packet below, and save its report as it came, beside the
   digest: `handover-<key>-report.md`.
3. Each finding: write the decision where it belongs — its document by `references/decision-changes.md`, or a row
   of the document's `open-questions.md` when it is a question still open — and commit it. Then close. `ALL ON
   DISK` — close.
4. The close message is printed, not typed: `python3 "${CLAUDE_SKILL_DIR}/scripts/subsessions.py" <project>
   <version> closing <key> <the stages next | «ждёт: …» | «остановиться»>` — it refuses with no digest, no
   report, or a MISSING report with no commit after it, then runs the stage's leftovers check (below) and prints
   the line to send the parent as it is. `--nothing-asked` for a stage that asked the user nothing. A screen-spec
   stage once sent «ЭТАП … ЗАКРЫТ» with no check although the user had answered three questions in it
   (ai-initiatives 2.3.0).

## The stage's leftovers

Every stage, nested or not, before its close report — «ЭТАП … ЗАКРЫТ», `work`'s run report, a UI run's verdict:

1. Remove what the stage started — the note's «Запущено» (`references/pause-and-resume.md` → The note): stand
   copies (`scripts/e2e-stands.sh down`, or `docker compose -p <copy> down -v`), stream containers (`docker rm -f
   <project>-s<k>-pg`), worktrees (`git worktree remove`), buckets, temporary databases (`DROP DATABASE` of the
   `tmp_test_` ones on the stand's server). Only its own: the main stand the next stage waits for, another live
   stage's worktree, the user's `dev` stay — and nothing is pruned wholesale.
2. Check: `python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/leftovers.py" .` lists the project's containers and volumes beside
   the main stand, the worktrees beside the main one, and temporary databases on its postgres. What it lists is
   removed if the stage's, or named with whose it is.
3. Its last line goes into the close report — «стенды удалены: …», or what is left and why. A stage that skips
   this leaves the next one a slower machine: 79 dead test databases held 3.5 GB of the Docker VM, and stream
   containers outlived their streams (ai-initiatives 2.3.0).

## The packet

```
You check that a stage's decisions are on disk. You read; you change nothing.

DIGEST          <absolute path of the digest from step 1>
STAGE           <the stage, e.g. «схема БД»; the version>
FILES           <repo-relative paths the stage wrote or changed: its documents (every part of a split one), their
                open-questions.md, the frames register, the plan, the progress file — and `git log --stat` of the
                stage's commits, so a file it touched is not missed>
REPORT          exactly the fields below, nothing after them
```

## The report

```
STATUS          ALL ON DISK | MISSING
MISSING         one line per decision not on disk: «<the user's words, quoted> — <what it settles> — где должно
                быть: <file and section>», or none
DIFFERENT       one line per decision on disk in another form than the chat settled: «<the words> — в файле: <what
                the file says>», or none
```
