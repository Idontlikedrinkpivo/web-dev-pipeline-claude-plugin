# Sharing an iteration with other people

Read when the user hands work to another person — «отдать дизайн
дизайнеру», «схему, API и архитектуру сделает аналитик», «ТЗ на экраны
сделает аналитик» — and in any session of a person who picks work up from
the iteration's branch.

The branch carries everything stages 1–9 make: each document is committed
the moment it is written (`SKILL.md` → Commit each document as soon as it
is written), the gates are in the stamps, and `scripts/where_am_i.py` reads
both. So any person can take any of those stages — the requirements, the
schema, the API, the architecture, the repository skeleton, the mockups,
the screen specs, the test cases — run it with the same plugin on their own
machine, and stop; the next person, or the same one tomorrow, pulls the
branch, runs `/dev-pipeline:continue` and goes on. Stage 10 and everything
after it run on one machine: the plan, its review and its run live in
`plans/`, which is not in git (`references/service-version.md` → Plans stay
out of git).

Everyone works in the **iteration's branch** (`iteration/<version>`). No
personal branches: at any time a stage's documents belong to one person, so
commits never collide, and `git pull --rebase` before every push (the plugin's
`scripts/push_branch.py` does it) is all the coordination the branch needs. `main` gets the iteration once, at the end.

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

A typical split: the designer takes the mockups; an analyst takes the
schema, the API and the architecture while the designer draws, then pulls
the frames and writes the screen specs; the person who runs the plan takes
stage 10 and everything after it.

## Handing over (the session of the person handing)

1. When the user hands work over — at the fork after the SRS (`SKILL.md` →
   Two branches) or at any message — ask which stages go to whom: one
   question per person, the stages from the table. When the iteration's
   design owner is a designer with the plugin
   (`references/design-owner.md`), `ui-design` is theirs without asking.
2. Make sure everything those stages read is committed on the iteration
   branch and pushed (`scripts/push_branch.py`) — finished documents only,
   their reviews and fixes done.
3. Write the hand-off text in the chat, ready to forward, one per person:
   clone the repository (or pull), install the plugin (README → Установка),
   `git switch iteration/<version>`, the Figma file link when the stage
   draws, and `/dev-pipeline:continue`. Add which input is not there yet
   and who brings it («ТЗ на экраны начнёте, когда на ветке появятся
   макеты»).

The person handing goes on with what stays theirs, committing and pushing
each finished document so the others can pull it.

## In a session that picks work up

- **The iteration comes from the branch.** `where_am_i.py` names it;
  `open_iteration.py <version>` switches to it and creates `plans/<version>/`
  for the progress files. Never open a new version, never switch to another
  branch.
- **Inputs come from the branch.** `git pull --rebase` before a stage
  starts; when an input the table names is not there yet, say what is
  missing and from whom, and stop — nothing here can replace it.
- **The stage runs as usual** — its gates and its stamp included, with this
  person answering. Each document is committed at once, and pushed once it
  is final — its reviews and their fixes done (`SKILL.md` → Commit each
  document; `scripts/push_branch.py` takes the others' commits first).
- **A changed decision** in a document whose stage another person runs right
  now is not edited here: write it in the chat as a request to that person,
  ready to forward («Нужно решение: …»), mark the item `⛔ остановлено: ждёт
  решения`, go on with the rest, and pull once it has landed. In any other
  document it lands as `references/decision-changes.md` says, and is pushed.
- **Between this person's own stages**, offer the next of them as usual
  (`SKILL.md` → Asking before a transition). A stage someone else took is
  not offered: name who has it.
- **Done** — after the last stage this person took: its close plus one line,
  ready to forward: «<этапы> готовы и запушены в `iteration/<version>`:
  <что сделано>. Дальше: <следующий этап> — <кто>».

## When someone reports done, and «где я»

`git pull --rebase` (or `git fetch` and read `origin/iteration/<version>`),
then `where_am_i.py`: which documents are on the branch, which stage is
still open (written, not stamped), which input a stage still waits for.
Check what came: the commits change only that stage's documents; every
screen spec has `reviewed:` or a named skip. Say who can start now — the
analyst once the frames are there, the test cases once the screen specs are
— with the line to forward. The meeting point (stage 10) waits until every
stage of 2–9 the iteration has is on the branch.
