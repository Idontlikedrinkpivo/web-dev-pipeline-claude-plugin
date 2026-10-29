# Where am I

Read when the user asks «где я», «что дальше», «на чём остановились» with no
stage just closed in this sitting, in a fresh session, after a compaction,
and when `continue` runs. Memory of an earlier session is not evidence; the
files on disk and git are.

## Read the state

Run `python3 "<pipeline skill folder>/scripts/where_am_i.py"` from the
project's root and answer from its output. It prints, in this order:

1. **The branch** and whether the tree has uncommitted changes.
2. **The iterations.** The open one (`plans/<version>/` with no
   `summary.md`) and the closed ones. **Two open** — the first thing to do
   is one question: which iteration is current; nothing is stamped or
   committed before the answer. When the older one still has work and the
   newer one is under way in this folder, offer to finish the older one in a
   worktree of its own (`work` → `references/run-hygiene.md` → Finishing an
   older iteration) — never by switching this folder's branch back and forth. **No `plans/`** (a fresh clone, or a
   project before its first iteration): the tags `v<version>` name the
   closed iterations and the `Plan-Unit:` trailers since the last tag the
   units already landed; what stages 10–14 left is unknown — say so rather
   than guessing. **An iteration branch the script names** («Итерация …
   открыта по ветке») is the open iteration — a fresh clone, or work
   another person pushed: entering it with the printed `open_iteration.py`
   command comes first, and no version number is asked.
3. **A resume note** — `resume.md` in the open folder means a long run
   (`work`, the UI test run, the security audit) stopped mid-way. Read it
   before anything else and check its claims against git, the tree and
   `docker ps` (`references/pause-and-resume.md` → Picking up); the answer
   is to continue that run from its «Следующий шаг».
4. **Progress files with unfinished rows** — a stage that stopped half
   way (`⏳ ждёт`, `🔄 в работе`, `🔍`, `🔁`, `⛔` rows). A half-done
   stage is not a done one, even when its document exists. Give its line
   with `scripts/progress_link.py` when you name it.
5. **The documents in chain order**, each with its version and gates:
   - business requirements: `grilled:`; a document `updated:` after it was
     grilled has an unrun grill for its current text;
   - the SRS: its last stamp commit names both gates — `прошёл`,
     `пропущен` (the user chose to skip: not offered again), or
     `не запускался` (the session stopped before the question was
     answered: offer it). Commits or uncommitted edits after the stamp are
     named; a grill on them has not run;
   - every other document with a `doc-review` gate: `reviewed:`
     (`info.x-reviewed` on OpenAPI); absent means skipped or never run —
     the files cannot tell, so offer it rather than assume either;
   - **pins**: a pin behind its source with a «ломает» row after it is
     **stale** — that stage comes back first (`doc-versioning` →
     Staleness and cascade); behind by «добавляет» only is for stage 10,
     not a stale stage; «уточняет» only — the next stamp refreshes it;
   - **«написан в итерации …, этап не закрыт»** — the document was
     committed on this iteration's branch and never stamped with its
     version: its stage stopped after the writer (`SKILL.md` → Commit each
     document as soon as it is written), here or on another person's
     machine. That stage is open and resumes: the documents of its set not
     written yet (the architecture's scenarios per area, a screen spec per
     frame), then its gates, then its stamp. A document already committed
     is not written again, and its old pins are refreshed by that stamp,
     not by a rewrite.
6. **The open iteration's checks**: the document-set check (its verdict,
   and whether any file of the set changed after it — then stage 10 has
   not run for the current set), the plan and `plan-review` (verdict, and
   «план изменён после проверки» when the plan changed since — `plan`
   runs the review again before `work`), the units with `Plan-Unit:` on
   the branch, the UI run's and the audit's verdicts (`DEFECTS` / `FIX` —
   a fix plan, `plan` MODE fix).
7. **Open points in order** — the list the answer is built from.

## The answer

The earliest unfinished point wins: a stopped run (resume note, then an
unfinished progress file), else a stage left open after its writer
(«этап не закрыт»), else a stale document's stage, else the next
stage of a branch that is not done (for the design branch the frames
register, `ui/screen-specs/` and `ui/test-cases/`, read from `origin` when
stages were handed to others — `references/team.md`; both branches as
options when both are open — equal ones, with no «(рекомендую)» between
them unless the user said whose session this is: which branch is theirs is
not in the files, and a guess from a git name or a habit sends the
designer to the API; one line says so. Their shape: one option per
branch's next stage, tagged «[Дизайн]» / «[Бэкенд]», then the earliest
unrun gate, then «Остановиться»; several letters run both branches in this
session), else stage 10, with the unrun gates as
options. An unrun gate may have been skipped on purpose: list the unrun
gates in one line and offer the earliest as an option, never as the only
way forward.

Ask it as one transition, per `pipeline` → "Asking before a transition".
Do not list every remaining stage.

Example — a fresh session, the user asks «что дальше?»; the script printed
(shortened):

```text
Ветка: iteration/1.3.0 · незакоммичено: ничего
Итерации: открыта 1.3.0; закрыты 1.2.0
Документы:
  1. бизнес-требования: допрос 2026-05-02
  2. SRS: 1.3.0 · допрос: прошёл · ревью: прошёл
  3. схема БД: 1.2.0 · ревью: 2026-05-06 · устарел: srs.md@1.2.0, сейчас 1.3.0 — ломает: BR-3: бронь не дольше 4 часов
  4. API (OpenAPI): нет
Открытые пункты (по порядку):
  - устарел документ «схема БД» — этап 3 обновляет его по журналу источника
```

The answer:

```text
**Что дальше: обновить схему базы данных**

В новой версии требований бронь теперь не длиннее 4 часов, а таблицы в
базе построены по прошлой версии: такую длинную бронь база ещё примет.
`db-schema-design` прочитает, что изменилось в SRS после 1.2.0 (правило
BR-3), и обновит схему; без этого API построится на старых таблицах.

  A. Запустить db-schema-design (рекомендую)
  B. Остановиться

Рекомендую A: всё дальше по цепочке опирается на схему.

Ответьте сообщением: буква или свой текст.
```
