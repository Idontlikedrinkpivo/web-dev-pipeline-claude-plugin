# Pause and resume

Read by `work`, `ui-test-cases` mode run and `security-audit` — the long
runs — and by any session that picks one up. Adapted from pstack's
`pause-safely` / `session-pickup`.

Git and the progress file already say what is done: a unit with its
`Plan-Unit:` commit, a case with its row. What they do not hold is what was
in the head of the session that stopped: the fixes already tried for an open
finding and why they failed, an executor's diff that never reached a
commit, the stands and watchers still running, a decision taken mid-run that
has not reached its document yet. Without it the next session repeats the
failed fixes, loses the diff or trips over a stand it did not start. The
resume note holds exactly that.

## The note

`documentation/plans/<version>/resume.md` — out of git like the rest of
`plans/`. Created when the run starts, written with the Edit tool, kept
short, refreshed after each item (a unit committed, a case run, an area
audited) so an abrupt end — the app quit, a compaction, a lost connection —
still leaves it current. **Removed when the run ends** — finished, or
closed with its report: a note left behind tells the next session that a
run stopped mid-way when none did (`scripts/where_am_i.py` reports any note
it finds as a stopped run).

```markdown
# Продолжение — <stage> · <version>

Обновлено: <YYYY-MM-DD HH:MM> · прогресс: [<progress file>](<path>) · база: <BASE sha>

- **Сейчас:** <the item in flight and who has it — «U14 у impl-medium, круг 2»>
- **Следующий шаг:** <the exact next action>
- **Открытые замечания и что пробовали:** <F-id — attempt 1 → result; attempt 2 → result; premise checked: …>
- **Незакоммиченное:** <<git dir>/pipeline-work/<version>/U14.patch — what it holds> | нет
- **Запущено:** <stands by compose project, watchers by task id> | ничего
- **Решения по ходу, ещё не в документах:** <decision → its owner document> | нет
- **Подвохи:** <what the next session must know that no file says>
```

## Pausing

On a stop («стоп», «подожди», «остановись»), a planned restart, or the user
saying they are leaving with the run unfinished:

1. Stop at a safe boundary: let the item in flight finish if it is close,
   otherwise stop its executor (TaskStop) and confirm it stopped — an agent
   reported «completed» may still have children running.
2. Save what is not committed without breaking «one unit, one commit»,
   new files included, in the repository's own git folder (a worktree has
   its own):

   ```bash
   d="$(git rev-parse --git-dir)/pipeline-work/<version>"; mkdir -p "$d"
   git ls-files --others --exclude-standard -z | xargs -0 git add --intent-to-add --
   git diff --binary > "$d/<item>.patch"
   git reset -q                       # undo the intent-to-add; the files stay
   ```

   Check the patch holds every changed and new file, then restore the tree
   to the last commit. No `wip:` commit on the iteration branch.
3. Stop the watchers; stands follow the stage's cleanup rule, or stay up
   and are named in the note when the user said they resume soon.
4. Bring the note up to date and post its link with the progress line.

## Picking up

A session that finds a `resume.md` in the open iteration — at start, after a
compaction, on «продолжай» or «где я» — reads it before anything else, then
checks each of its claims against the live state before relying on it: the
commits in `git log` since its base, `git status`, the patch file, `docker
ps` for the stands, the task list for the watchers. Reality wins over the
note; say in one line what differed. Then continue from «Следующий шаг»:
nothing already committed is redone, no attempt the note lists is repeated
without a new reason, a patch is reapplied with `git apply` (new files
come back with it) before its item is redispatched. Refresh the note right
after.
