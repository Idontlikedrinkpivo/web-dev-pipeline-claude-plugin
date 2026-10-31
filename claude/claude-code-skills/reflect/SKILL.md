---
name: reflect
description: >-
  At an iteration's end, finds in its sessions where the dev-pipeline plugin itself failed and what the iteration cost
  by agent. Use for «разбери сессии для плагина», «сколько стоила итерация». One session's tokens: explain-usage.
---

# Reflect

The plugin improves when what went wrong in real work reaches the people
who maintain it. This skill reads the
iteration's sessions and writes the plugin's failures down, with evidence,
in one place the maintainer reads.

Write the findings in Russian. Do not translate skill names, rule names,
file paths or ids.

## What counts

A **finding** is a moment where the plugin, not the project, was the
cause — and it cost the user something:

- the user corrected a stage or reminded it of a rule (the strongest
  signal: their words are the evidence);
- a stage did what its skill forbids, or skipped what it requires;
- a rule was followed until a `=== CONTEXT COMPACTED ===` line and lost
  after it;
- the session spent many turns working out what a skill should have said
  (how to start the stand, which branch, where a file goes);
- a skill's instruction was wrong for the case (it led the stage astray).

Not a finding: the project's own bugs, a product decision, a one-off with
no cost to the user, anything already answered by the plugin's current
rules (check them — the session may have run an older version).

## Steps

1. **Scope.** `python3 "${CLAUDE_SKILL_DIR}/scripts/sessions.py" window "$PWD"` (add `--version <v>` when the
   iteration being closed is not the current branch's) prints the window's start as `--since <…>` — the
   iteration's first commit, or the end of the last «Окно» already in the feedback file when that is later (a
   part read before a restart, a run by hand mid-iteration), so no moment is read twice; exit 1 means neither a
   branch nor a folder names the iteration: ask the user from which date (`YYYY-MM-DD`, or
   `YYYY-MM-DDTHH:MM` for a time). That `--since` goes into every command
   below. List this project's sessions in it:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/sessions.py" list "$PWD" --since <the window's start>`.
   Only this project's sessions — never another project's. The script finds
   them under every name the app gives this project's folder: the plain one,
   a long path shortened with a hash, and the repository's worktrees
   (`git worktree list`, and folders nested in the project), each confirmed by
   the `cwd` its sessions recorded. When the
   project's folder was renamed or moved during the iteration, add its old
   path with `--also <old path>`; when the first session found starts after
   the iteration opened, say so in the report — sessions may sit under a
   path not passed. The script lists a session copied under both paths once,
   and skips one that a later session continued (its messages are the start
   of the longer one) as «повтор».
2. **Digest.** For each session:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/sessions.py" digest <session.jsonl> <tmp>/<n>.md --since <the same start>`
   — the user's typed messages, Claude's replies, the skills and agents
   run, and the compaction marks, in order; tool output is left out. Then
   the failed calls of the whole window, the agents' own logs included:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/sessions.py" errors "$PWD" <tmp>/errors.md --since <the same start>`
   (and the same `--also`) — an agent that fixed its own failed command
   never told the session, and a wrong flag or path a skill gave shows up
   only there.
3. **Review.** Read `executor-catalog` and resolve `session-reviewer`.
   Dispatch one per digest, and one for `errors.md` (its lines in
   `references/reviewer-prompt.md` → The errors digest), in parallel, in the
   foreground, with the packet in `references/reviewer-prompt.md`: the digest path, the plugin's skills
   folder (`${CLAUDE_SKILL_DIR}/..`), the plugin version installed now — the
   `version` field of the plugin's manifest in that same folder,
   `.claude-plugin/plugin.json` (`.codex-plugin/plugin.json` under Codex);
   the same number goes into the section's «версия плагина».
   A digest over ~400 KB goes to one reviewer that reads it in parts.
4. **Merge.** Collect the reviewers' findings; merge the same failure seen
   in several sessions into one finding with each occurrence; drop what
   «What counts» excludes; for each, check the current skill text — a rule
   that already says the right thing is marked «уже в правилах с <version>,
   нарушено» rather than proposed again.
5. **Measure.**
   `python3 "${CLAUDE_SKILL_DIR}/scripts/measure.py" "$PWD" --since <the same start>` (and the same `--also`)
   plus `--progress documentation/plans/<version>/progress.md` for each iteration of the window — at the close
   the file is still there, and the script keeps its numbers outside the project for a later run after the
   cleanup — and `--units <previous tag>..HEAD` — what the iteration's sessions and agents spent, from Claude
   Code's own logs: by group and by agent, the models, the context each agent reached, «Принятие задач» (units
   accepted at the first review, units sent back, the cost of one accepted unit), and the flags it raises. Its output goes into the section unchanged,
   under «### Расход»: the maintainer tunes unit size, reviews and packets from these numbers, and a paraphrase
   loses them. A flag becomes a finding only when a skill caused it (a stage pasting whole documents, a
   session kept for days on a huge context).
   Then `python3 "${CLAUDE_SKILL_DIR}/scripts/guard_report.py" "$PWD" --since <the same start>` — what the
   plugin's command guard (`hooks/guard.py`) refused, per rule with sample commands; its block goes under «###
   Отказы хука» unchanged. Read the samples: a refused command that was right is a finding on the hook (the rule
   is too wide); one rule firing again and again is a finding on the skill that keeps asking for that command.
6. **Write.** Append one section to
   `~/.claude/dev-pipeline-feedback/<project folder's basename>.md` (create the
   folder and the file when missing; never rewrite earlier sections). Shape
   below. Nothing is written into the project and nothing is committed.
7. **Report** in one line: the file as a clickable link, how many findings,
   how many sessions read, the run's total from the measure. With none, write the section anyway, saying so —
   the maintainer sees the iteration was reviewed.

## The section

```markdown
## <project> · итерация <version> · <YYYY-MM-DD>      (mid-iteration: «… · часть <n>, до <what ended it>»)

Сессий прочитано: <n> (<first date> — <last date>) · версия плагина: <x.y.z> · находок: <k>

### 1. <short title>
- **Что случилось:** <one or two sentences>
- **Слова пользователя:** «<quote>» — <session id short>, <date time>
- **Скилл и правило:** `<skill>` → <section or rule>
- **Почему:** правила нет | правило есть, нарушено | правило неверно | потеряно после сжатия
- **Предложение:** <the change in one or two sentences>
- **Закрепить:** текстом правила | скриптом / проверкой: <which>
- **Повторялось:** <n> раз (<sessions>)

### Расход
<measure.py's output from «Окно» on, unchanged>

### Отказы хука
<guard_report.py's table, unchanged>
```

Order by cost to the user: repeated corrections first.

**Comparing two versions of the plugin** («стало ли дешевле после правки»): `references/comparing.md` — several
runs per version, `measure.py --json` and `scripts/compare.py`.

**Asked only what the iteration cost** («сколько стоила итерация», «куда ушли токены за итерацию»): run step 5
alone, from the iteration's first commit or the date the user names, and answer with its tables and flags in plain
words; nothing is written. What this one session spent is `explain-usage`, not this skill.

**`scripts/context_size.py`** is not a step of this skill: it lives beside the other session readers, and
`pipeline` → `references/context.md` and `work` → `references/run-hygiene.md` run it to measure a session's
context.
