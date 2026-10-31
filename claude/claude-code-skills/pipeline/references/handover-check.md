# The handover check — what the chat settled is on disk

Read in a nested session (`references/parent-session.md`) before it closes its stage or hands it over. The next
stage starts in a fresh session that knows only the files and git; a decision the user made in this chat and no file
holds is lost with the chat. The rule «write every decision down before the close» (`references/decision-changes.md`)
is the session's own; this check is a second reader that did not write the stage.

## When

- Before «ЭТАП <stage> ЗАКРЫТ» — after the stage's commits, before the message to the parent.
- Before «<stage> ПЕРЕДАН» — the next part starts from the files too.
- Not in a session without a parent (a terminal run keeps its chat), and not for a stage that asked the user
  nothing: no answer, no decision to lose.

## How

1. The conversation, as a digest, by this session's title (its first message names it):
   `python3 "${CLAUDE_SKILL_DIR}/../reflect/scripts/sessions.py" mine "$PWD" "<the session's title>" "$(git rev-parse --git-dir)/pipeline-work/handover-<stage>.md"`.
   A non-zero exit — the session's transcript not found — skip the check and say so in one line.
2. Dispatch `handover-checker` (`executor-catalog` → Dispatch contract, `subagent_type:
   "dev-pipeline:handover-checker"`, no `model`) with the packet below.
3. Each finding: write the decision where it belongs — its document by `references/decision-changes.md`, or a row
   of the document's `open-questions.md` when it is a question still open — and commit it. Then close. `ALL ON
   DISK` — close.

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
