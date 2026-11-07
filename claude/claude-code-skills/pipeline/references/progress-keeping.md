# Keeping a progress file

- [Before the first step and after each item](#before-the-first-step-and-after-each-item)
- [How the file is changed](#how-the-file-is-changed)
- [Subagents and watchers](#subagents-and-watchers)

Read this with `references/progress-files.md` (which stages keep a file,
its form, the statuses, the templates) before the first step of a stage
that keeps one, and again after a context compaction: the rule that the
file changes only through Edit and the scripts is the first one lost. The
file is the user's window on a long stage; these are the duties that keep
the window true while the stage runs. How the run itself keeps going
while the user is away is `references/unattended.md` → Keeping the run
moving.

## Before the first step and after each item

- **When.** Create the file before the first step or dispatch, every row
  `⏳ ждёт`, run the script (`scripts/progress_link.py`, the chat line —
  `references/progress-files.md` → The chat line), open the link in the built-in browser
  yourself when there is one, and paste the line before the first step
  starts. A run resumed after a break or a context compaction rebuilds
  the rows from what is on disk, sets anything half-done back to
  `⏳ ждёт`, and pastes the line again before it goes on. The script
  prints its warnings on stderr — a status word nobody defined, a bar that
  disagrees with the count, no count line — and the stage fixes the file
  before it pastes the line.
- **After each item.** Every time an item is finished — its row reaches
  done, stopped or returned — run the script and paste its line, so a user
  who closed the page or stepped away reopens it from the last message,
  not by scrolling to the start. A stop or a question to the user carries
  the line too, as its last line. Any message that mentions the progress
  file carries the line; a file name in plain text or in backticks opens
  nothing. **The plugin's Stop hook holds this** (`hooks/progress-line.py`):
  a turn that changed a progress file — an Edit or Write of it,
  `progress_set.py`, `progress_e2e.py`, `progress_link.py`, or any shell
  command naming a file that changed during the turn — cannot end without the line, and
  no turn ends with a link to the `.md` in place of the page; the block
  says what to run. A live run went a whole hand-over without one line
  until the user asked «где файл прогресса?», with the rule in its packet.
- **The file is never named without its line.** «Обновил прогресс в
  progress-design.md — файл можно открыть» is wrong: the name opens
  nothing, and the user has to search for the file. Where a subagent
  changes the rows (the Figma builder, the test writer, the test runner),
  paste the script's line each time its dispatch returns.
- **The server** is stopped at the iteration's close
  (`references/closing-cleanup.md`) or when the user says they are done
  watching: `python3 "<pipeline skill folder>/scripts/progress_server.py"
  documentation/plans/<version> --stop`.

## How the file is changed

- **How.** Change it with the **Edit** tool the moment a row changes — one
  call per row or line, the bar and the count together with the row — and
  **Write** only to create it (a shell write to a progress file is refused by the plugin's hook,
  `hooks/guard.py`). Never from the shell (`python`, `sed`,
  `cat >`), and never by a script that rewrites the file on a timer: the
  page is rebuilt by the plugin's hook on Edit and Write only, so a file
  changed any other way is fresh on disk and stale on the page the user
  watches. Four scripts are the exception, and all redraw the page
  themselves: `progress_e2e.py` (`work` → `references/progress-file.md` →
  The e2e section), `progress_mutation.py` (the top of
  `progress-mutation.md`, from the mutation logs),
  `progress_set.py <file> <done> <total> [--section
  "<heading>"]`, which sets the bar, the count line and the section's
  «обновлено» time — never copy a
  hundred-cell bar into an Edit by hand: one cell off and the Edit fails,
  and an Edit that carries a bar is refused by the plugin's hook
  (`hooks/guard.py`: a hand-copied bar came out 104 cells long with no
  percent) — and `progress_link.py`, which stamps the file's «обновлено»
  time as it prints the chat line.
  Rows still change with Edit, after a fresh Read of the file. After a
  compaction this rule is the first one lost: re-read it before the next
  change of the file; `progress_link.py` names a bar that disagrees with the
  count, and remembers `--desktop` beside the file. A script may compute the numbers; the agent writes them. The bar is printed, not counted by
  hand: `python3 -c "d,t=<done>,<total>;p=d*100//t;print('█'*p+'░'*(100-p),f'{p}%')"`.
- **A subagent** that changes rows gets the path in its packet as
  `PROGRESS FILE` and changes only its rows, the bar and the count line;
  the title, the other sections and the state line stay the session's.

## Subagents and watchers

- **A subagent's rows are watched, not trusted.** A subagent deep in its
  task forgets the progress file, and then the user sees a hang. So while
  a dispatch that owns rows runs and writes files, the session watches its
  output folder with the Monitor tool — a loop that prints each file as it
  changes, e.g. `while sleep 20; do git status --porcelain --
  documentation/ui/test-cases; done | awk '!seen[$0]++'` — and on each new
  line sets that item's row to `🔄 в работе` if the subagent has not
  (without Monitor: a background `sleep 30`, then the same check). When
  the dispatch returns, it reconciles every row, the bar and the count
  with what is on disk before the chat line, and says in that line what it
  corrected. Output that is not files (Figma) is reconciled on return,
  from the report.
- **Every watcher ends with its work.** A Monitor or a background wait the
  run starts carries its own end: it watches until a condition that the
  work's end makes true (the queue's last result, a done marker, the
  process gone) and then exits, never only until its timeout. The run keeps
  the ids of the watchers it started and, when it ends — finished, failed
  or stopped — stops any still running (TaskStop) before its last line. A
  watcher left behind keeps waking the session for nothing; an agent that tries to end with one still running
  is held back by the plugin's hook (`hooks/watchers.py`) until it stops it.
- **Results from background work** (stands, long commands) wake the agent,
  and the agent edits: watch their output with the Monitor tool, which
  wakes the session on each new line, or — without it — a background
  `sleep 30` whose finish wakes the session to edit what changed and start
  the next one.
