# What to offer at a close

Read at the close of every document stage (2–9), before the transition
question (`pipeline` → Asking before a transition). The chain table's
"Then offer" cell is the default order; the offer itself comes from
readiness, so that a stage is never offered ahead of its inputs, offered
twice, or offered while another session runs it. The design branch once
closed its mockups while the schema was still being written in the other
session and offered the API — a stage out of order and a second copy of the
backend branch (live run 2026-11-05).

## Read the state

Run `scripts/where_am_i.py`. Its block «Готовность этапов» says, for stages
3–10:

- **можно начать сейчас** — every input the stage needs is on the branch
  and its stage is closed (`references/team.md` → What a stage needs);
- **ждёт входов** — which input is missing, and whether that input is being
  written in a nested session or is written but not closed;
- **идёт в подсессии** — a stage a nested session holds now, from
  `plans/<version>/sessions.md` (rows «идёт» or «передан»);
- **не закрыт здесь** — written and committed, its gates and close commit
  not done.

A document on disk is not a done stage: the close commit is
(«написан, этап не закрыт» is open). The script does not know which stages
the product has: drop a stage the project skips — no storage, no schema; no
HTTP, no API; no screens, no design branch — and say which and why.

## The offer

1. **Offer every stage that can start now**, the table's order first. Two or
   more ready at once — after the API the architecture and the screen specs
   — are offered together: under a parent session each in its own nested
   session, in one session one after the other, and the user picks one,
   both, or the order.
2. **A stage another session holds is named, never offered**: «схема БД
   делается в сессии «<title>»». Offering it starts a second copy of the
   stage.
3. **A stage that waits is named with what it waits for**: «ТЗ на экраны
   ждут контракт API». Its inputs' stages are the offer when they can start
   here; when they run elsewhere, the line says so.
4. **Nothing can start here** — every stage left waits for work in another
   session: say what is waited for and where it is being done, and end the
   sitting with «Остановиться» as the only option besides waiting. Under a
   parent, the close report says «ЭТАП <stage> ЗАКРЫТ · ждёт: <stage> после
   <stage>» (`references/parent-session.md` → What comes back), and the
   parent starts that row when the stage it waits for closes.

Examples from the design branch:

- mockups closed, the schema runs in the other session: «ТЗ на экраны ждут
  API; схема БД делается в сессии «1.2.0 · 03 схема БД»; здесь работу
  завершаем» — options: wait, stop;
- mockups closed, the backend not started: «для ТЗ на экраны нужен API, а
  для него схема БД; не сделано: схема БД, API» — offer the schema;
- the API closed, the architecture and the screen specs not done: offer
  both, in parallel.
