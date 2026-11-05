# Sharing an iteration with other people

Read when the user says another person goes on — «отдать дизайн
дизайнеру», «дальше продолжит аналитик» — and in any session of a person
who picks work up from the iteration's branch.

Who takes which stage is decided between the people, case by case, not by
the plugin (the user's decision, 2026-11-05): one person finishes a stage,
committed and pushed; another pulls, writes «продолжи» and picks a stage from
the list of the remaining ones. So the plugin never asks «which stages go to
whom», writes no per-person hand-off text, and never records or guesses who
owns a stage — a guess sends the wrong person to the wrong stage, and a
recorded owner goes stale the moment the people agree otherwise.

The branch carries everything stages 1–9 make: each document is committed
the moment it is written (`SKILL.md` → Commit each document as soon as it
is written), the gates are in the stamps, and `scripts/where_am_i.py` reads
both. So any person can take any of those stages — the requirements, the
schema, the API, the architecture, the repository skeleton, the mockups,
the screen specs, the test cases — run it with the same plugin on their own
machine, and stop; the next person, or the same one tomorrow, pulls the
branch, runs `/dev-pipeline:continue` and goes on. Stage 10 and after it too:
the plan, its review, the progress files, `resume.md` and the reports are in
`plans/`, committed and pushed at every stage's close and every stop
(`references/service-version.md` → The iteration's files in git), so a run stopped on one machine
goes on on another from `resume.md`.

Everyone works in the **iteration's branch** (`iteration/<version>`). No
personal branches: at any time a stage's documents belong to one person, so
commits never collide, and `git pull --rebase` before every push (the plugin's
`scripts/push_branch.py` does it) is all the coordination the branch needs. `main` gets the iteration once, at the end.

A push goes only through `scripts/push_branch.py`; by hand only when the script says the command to run, and then the
proof is git's ref-update line (`<old>..<new> <branch> -> <branch>`) — «Everything up-to-date» proves nothing, as the
2.2.1 run showed: the session said the commit was on the server, and it was not.

## What a stage needs on the branch

| Stage | Needs before it starts |
|---|---|
| `db-schema-design` (3) | the SRS |
| `openapi-spec-generator` (4) | the SRS; the schema when there is storage |
| `clean-architecture-design` (5) | the SRS, the schema, the API |
| `repo-scaffold` (6) | the architecture |
| `ui-design` (7) | the SRS |
| `screen-spec` (8) | the frames register and the API |
| `ui-test-cases` write (9) | the screen specs |
| `docs-consistency` (10) | every document of stages 2–9 the iteration has — the meeting point |

An example of how people may share, not a rule: the designer draws the
mockups; an analyst writes the schema, the API and the architecture while
the designer draws, then pulls the frames and writes the screen specs; the
person who runs the plan takes stage 10 and everything after it.

## Handing over

A hand-over is «everything of this stage is committed and pushed» — the
stage's close already does it (`SKILL.md` → Commit each document;
`scripts/push_branch.py`) — plus one line in the chat, ready to forward:
«<этап> готов и запушен в `iteration/<version>`; у вас: git pull, затем
«продолжи» — выберите этап из списка», and, when the stage is the mockups, «; если поправите кадры —
«макеты поменялись»», so the designer's later edits reach the documents. Nothing else: no question about who
goes on, no per-person text — the next person's `continue` reads the branch
and lists what is left.

## In a session that picks work up

- **The iteration comes from the branch.** `where_am_i.py` names it;
  `open_iteration.py <version>` switches to it and creates `plans/<version>/`
  for the progress files. Never open a new version, never switch to another
  branch.
- **Inputs come from the branch.** `git pull --rebase` before a stage
  starts; when an input the table names is not there yet, say what is
  missing and which stage writes it, and stop — nothing here can replace it.
- **The stage runs as usual** — its gates and its stamp included, with this
  person answering. Each document is committed at once, and pushed once it
  is final — its reviews and their fixes done (`SKILL.md` → Commit each
  document; `scripts/push_branch.py` takes the others' commits first).
- **A changed decision** in a document whose stage another person runs right
  now is not edited here: write it in the chat as a request to that person,
  ready to forward («Нужно решение: …»), mark the item `⛔ остановлено: ждёт
  решения`, go on with the rest, and pull once it has landed. In any other
  document it lands as `references/decision-changes.md` says, and is pushed.
- **After a stage**, offer the next stage as usual (`SKILL.md` → Asking
  before a transition); the person decides whether to take it or stop.
- **Done** — when the person stops: the stage's close plus the line to
  forward from Handing over.

## When someone reports done, and «где я»

`git pull --rebase` (or `git fetch` and read `origin/iteration/<version>`),
then `where_am_i.py`: which documents are on the branch, which stage is
still open (written, not stamped), which input a stage still waits for.
Check what came: the commits change only that stage's documents; every
screen spec has `reviewed:` or a named skip. Say what is on the branch and
which stage the files make next — the screen specs once the frames and the
API are there, the test cases once the screen specs are. The meeting point
(stage 10) waits until every stage of 2–9 the iteration has is on the branch.
