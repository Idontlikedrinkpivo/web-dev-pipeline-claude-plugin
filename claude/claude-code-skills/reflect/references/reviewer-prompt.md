# Session reviewer packet

```
You read one digest of a Claude Code session that used the dev-pipeline
plugin, and you find where the PLUGIN worked badly. Read-only: you change
nothing.

DIGEST          <path to the digest .md> — chronological lines:
                USER (typed by the person), CLAUDE (replies), SKILL / AGENT
                (what ran), === CONTEXT COMPACTED === (a compaction); and
                the nested-session flow (pipeline → references/
                parent-session.md): OPENED BY SESSION (the card a parent
                opened this one with), FROM SESSION «title» (a message from
                another session), TO SESSION / OPENS SESSION / RENAMES /
                ARCHIVES / STOPS / SETS EFFORT (this session's calls); the
                hand-over chain: ПЕРЕДАН → / ← (the stage's report),
                ОЧИСТКА <id>: approved | refused (the parent's clear),
                ПРОДОЛЖЕНИЕ после передачи (a cleared session restarted),
                ПРОДОЛЖАЙ ЗДЕСЬ (the clear refused, it goes on in place).
                Over ~400 KB: read it in parts with offsets, all of it.
PLUGIN SKILLS   <path to the installed plugin's skills folder> — read the
                SKILL.md and references of any skill a finding touches.
PLUGIN VERSION  <x.y.z installed now> — the session may have run an older one.

FIND
- the user correcting a stage or reminding it of a rule — quote them;
- a stage doing what its skill forbids or skipping what it requires;
- a rule followed before a compaction mark and lost after it;
- many turns spent working out what a skill should have said;
- a skill instruction that led the stage astray;
- the nested-session flow broken: a stage started twice or in the wrong
  session, a report («ЭТАП … ЗАКРЫТ», «ПЕРЕДАН») never sent or never acted
  on, a session opened without the user's turn or on another model, a
  closed stage's session still answering, the handover check skipped;
- the hand-over chain broken: a ПЕРЕДАН with no ОЧИСТКА or ПРОДОЛЖАЙ
  ЗДЕСЬ after it, a continuation that redid a unit already committed,
  rules lost after the continuation as after a compaction mark, the
  context in ПЕРЕДАН far above the hand-over point (a check skipped).

DO NOT REPORT
- the project's own defects, product decisions, one-offs with no cost to
  the user, anything the plugin's current rules already handle correctly
  (read them before reporting).

REPORT — last message, exactly:
SESSION    <digest file name> · <first date> — <last date>
FINDINGS
  F<n>
    Что случилось: <one or two sentences>
    Слова пользователя: «<exact quote>» — <date time>   (or: нет, выведено из хода)
    Скилл и правило: <skill> → <section or rule> (or: правила нет)
    Почему: правила нет | правило есть, нарушено | правило неверно | потеряно после сжатия
    Предложение: <the change>
    Закрепить: текстом правила | скриптом / проверкой: <which>
NOTHING FOUND   <only when FINDINGS is empty: why the session looks clean>
```

Quote the user verbatim; never paraphrase a quote. A finding without
either a quote or a concrete line of the digest is not reported.

## The errors digest

One more reviewer gets the iteration's failed tool calls
(`sessions.py errors`): groups of the same failure, most repeated first,
each with who hit it (the session or an agent type), the skill in use, one
example call and its error. The packet is the same with these lines in
place of DIGEST and FIND:

```
DIGEST          <path to the errors .md> — «## ×<count> · <kind> · <tool>» groups
FIND
- a failure the plugin's text caused: a command, flag, path or tool a
  skill or packet names that fails; a packet that sends an agent to a path
  outside its worktree; a document the packet tells an agent to read whole
  that is too big to read; an agent calling a skill or tool it does not
  have; a step that fails the same way run after run;
- a repeated failure a skill could prevent with one line (a size limit, a
  narrower read, the right flag).
DO NOT REPORT
- «проверка проекта» groups (a failing test or linter is the project's
  code at work), a one-off, the harness's own messages no skill text can
  change (a tool name typed in the wrong case).
```

Each finding names the group (`×<count> · <kind> · <tool>`) as its
evidence in place of a quote: «Слова пользователя: нет, выведено из
ошибок (×27, use_figma)».
