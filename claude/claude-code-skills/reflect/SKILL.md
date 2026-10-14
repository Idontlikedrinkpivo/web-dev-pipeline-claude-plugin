---
name: reflect
description: >-
  Reads this project's Claude Code sessions of the closing iteration and
  writes down where the dev-pipeline plugin itself worked badly — the user
  correcting a stage («а где ссылка?», «прогресс не обновляется»), a stage
  doing what its skill forbids or skipping what it requires, a rule
  forgotten after a compaction, time lost on something the rules should
  have said — each with the user's own words as evidence, the skill and
  rule it touches, and the change it suggests. Appends the findings to one
  feedback file per project outside the repository, which the plugin's
  maintainer reads. Runs on its own at the end of an iteration (`pipeline`
  → End of the pipeline) and when the user asks «разбери сессии для
  плагина», «что в плагине сработало не так», «/reflect». Not a review of
  the project's code or documents, and it never edits the plugin.
---

# Reflect

The plugin improves when what went wrong in real work reaches the people
who maintain it. Until now that was a person copying chat fragments by
hand; most of what went wrong was never copied. This skill reads the
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

1. **Scope.** The open iteration's folder (`documentation/plans/<version>/`)
   gives the window: from the iteration's first commit (or the folder's
   date) to now. List this project's sessions in it:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/sessions.py list "$PWD" --since <YYYY-MM-DD>`.
   Only this project's sessions — never another project's. When the
   project's folder was renamed or moved during the iteration, add its old
   path with `--also <old path>`; when the first session found starts after
   the iteration opened, say so in the report — sessions may sit under a
   path not passed. The script lists a session copied under both paths once,
   and skips one that a later session continued (its messages are the start
   of the longer one) as «повтор».
2. **Digest.** For each session:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/sessions.py digest <session.jsonl> <tmp>/<n>.md`
   — the user's typed messages, Claude's replies, the skills and agents
   run, and the compaction marks, in order; tool output is left out.
3. **Review.** Read `executor-catalog` and resolve `session-reviewer`.
   Dispatch one per digest, in parallel, in the foreground, with the packet
   in `references/reviewer-prompt.md`: the digest path, the plugin's skills
   folder (`${CLAUDE_SKILL_DIR}/..`), the plugin version installed now.
   A digest over ~400 KB goes to one reviewer that reads it in parts.
4. **Merge.** Collect the reviewers' findings; merge the same failure seen
   in several sessions into one finding with each occurrence; drop what
   «What counts» excludes; for each, check the current skill text — a rule
   that already says the right thing is marked «уже в правилах с <version>,
   нарушено» rather than proposed again.
5. **Write.** Append one section to
   `~/.claude/dev-pipeline-feedback/<project folder's basename>.md` (create the
   folder and the file when missing; never rewrite earlier sections). Shape
   below. Nothing is written into the project and nothing is committed.
6. **Report** in one line: the file as a clickable link, how many findings,
   how many sessions read. With none, write the section anyway, saying so —
   the maintainer sees the iteration was reviewed.

## The section

```markdown
## <project> · итерация <version> · <YYYY-MM-DD>

Сессий прочитано: <n> (<first date> — <last date>) · версия плагина: <x.y.z> · находок: <k>

### 1. <short title>
- **Что случилось:** <one or two sentences>
- **Слова пользователя:** «<quote>» — <session id short>, <date time>
- **Скилл и правило:** `<skill>` → <section or rule>
- **Почему:** правила нет | правило есть, нарушено | правило неверно | потеряно после сжатия
- **Предложение:** <the change in one or two sentences>
- **Закрепить:** текстом правила | скриптом / проверкой: <which>
- **Повторялось:** <n> раз (<sessions>)
```

Order by cost to the user: repeated corrections first.
