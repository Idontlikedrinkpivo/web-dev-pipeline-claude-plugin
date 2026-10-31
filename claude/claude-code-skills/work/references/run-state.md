# Run state outside git — the run report, the resume note, the task list, the progress line

Read by `work` at Step 1, and again after every compaction: what the run keeps besides its commits, where each
lives, and when each is written. Where the run stands is still read from git (`plan_state.py`); these hold what
git cannot — who is dispatched now, what was decided, and what the user sees.

**The run report** (`references/run-report.md`) is a file at
`$(git rev-parse --git-dir)/pipeline-work/<version>-run.md` — outside the
tree, so the plan stays byte-identical and no unit's `Файлы` grows; a second
run in the iteration adds its own section under its own BASE. Append to it
after every commit and read it back after a compaction. Its «В работе» line
lists each dispatch still out — `U7 → impl-medium (задача <id>)` — written
before the `Agent` call and cleared when it returns. After a compaction a
unit listed there is still running: wait for its result, or confirm its task
ended, and never send it to a second executor.

**The resume note.** On start read `documentation/plans/<version>/resume.md`
when a run left one (`pipeline` → `references/pause-and-resume.md` → Picking
up). Refresh it after every commit and every stop, and delete it when the run
closes (Step 7): a note left behind sends the next session after a run that
is over.

**The task list** has one task per unit in scope, named from the unit's goal
with the U-id appended (`Add order aggregate (U3)`). Do not edit the plan
document — progress lives in commits, the task list, and the progress file.

**The progress file and its line.** Create — on a resumed run, rebuild from
git — `documentation/plans/<version>/progress.md` per
`references/progress-file.md`; it is never committed (`pipeline` →
`references/service-version.md` → Plans stay out of git). The chat gets it only as **the progress line**: with the file's
count set from `plan_state.py`, run

```bash
python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/progress_link.py" documentation/plans/<version>/progress.md
```

(add `--desktop` when this session has the built-in browser) and paste the
one line it prints, as printed — never a link written by hand. Post it before
the first dispatch, and again after a resume or a compaction before the next
one: a run started without it is invisible until its first commit. Post it
after every Step 5 commit, every stop and every fix of the final review, and
as the run's last message, so a user who closed the page or stepped away
reopens it from the last message.
