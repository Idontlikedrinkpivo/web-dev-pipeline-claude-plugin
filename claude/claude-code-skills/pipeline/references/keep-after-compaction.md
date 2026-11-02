# What a stage must not lose after a compaction

Printed by the session-start hook after a compaction (`scripts/keep_rules.py`): the section of the stage skill the
session ran last, found in its transcript. A compaction keeps a summary, not the skills read before it, and the
reflect reports keep finding the same rules broken right after one — a progress file written from the shell, the
security audit not offered, a question asked in a card. Each section is the few rules a stage broke after a
compaction, or would cost most to break; the stage's skill stays the whole truth — read it again. One section per
stage skill, its heading the skill's folder name; a stage with no section gets «pipeline».

## pipeline

- Before every next stage, ask (`SKILL.md` → Asking before a transition); the questions go in the chat, never in a
  choice card (`references/question-format.md`).
- A decision made in the chat goes into its document before the stage closes (`references/decision-changes.md`).
- A document stage ends with its close commit — `docs: <документ> <version> · review: <состояние>`, empty when
  nothing was stamped (`doc-versioning` → `references/version-birth.md`).
- The iteration closes in `scripts/close_iteration.py`'s order: audit, stamp, site, summary, tag, reflect to the
  end, servers. Never merge into main or delete `iteration/<version>` before the tag.
- In a nested session: report to the parent «ЭТАП … ЗАКРЫТ · дальше: …» after the handover check
  (`references/handover-check.md`); unsure of the stage — `scripts/subsessions.py … whoami <own id>`.

## brainstorm

- Deferring a question to open-questions.md does not pause the stage. Continue with the next independent question
  or the remaining phases; end only on an explicit question, explained blocker, requested pause or stage handoff.

- Commit the business requirements as soon as written; on a new project with `documentation/.dev-pipeline.json`
  and the site the hook built (`docs-site` → `rebuild.py . --wait`, stage `documentation/_web-docs`).
- The grill gate is asked; its state goes into the commit: `docs: бизнес-требования · допрос: прошёл | пропущен |
  не запускался`.
- Who runs the design, when asked: `"design"` in `documentation/.dev-pipeline.json` (`pipeline` →
  `references/design-owner.md`).

## srs-writer

- The session writes no SRS: `srs-author` settles and prints it. The document is «SRS», never «ТЗ».
- Commit it as soon as written; ask the grill, then `doc-review`; close with `docs: SRS <version> · grill: … ·
  review: …` (empty when nothing to stamp).
- Every answer the user gave in the chat is in the SRS or its `open-questions.md` before the close.

## db-schema-design

- The session writes no schema: the design writer does (`design-lite` prints itself, Mid and High through
  `doc-typist`).
- A committed migration is never edited — a change is a new numbered file. `table_docs.py --check` and
  `doc_check.py --only documentation/db/` are clean before the commit.
- Close: `docs: схема БД <version> · review: <состояние>`.

## openapi-spec-generator

- The session writes no spec: the design writer does. `redocly lint` is clean before the commit; three or more
  lines of a check go to `doc-typist` `MODE revise`, one or two you fix yourself.
- Close: `docs: API <version> · review: <состояние>`.

## clean-architecture-design

- One writer settles every document of the sitting; the session inspects each and writes none. No progress file.
- Each document is committed as it lands; `doc-review` is asked once for all of them.
- Close: `docs: архитектура <version> · review: <состояние>`.

## repo-scaffold

- `progress-scaffold.md` rows change with Edit only; the page computes the bar.
- The skeleton runs green (its lint, typecheck and tests) before its commit; `documentation/project-map/` is
  written with it.

## ui-design

- The Figma builder draws; the session checks each screen against the frames register and the UX checklists
  (`ux-patterns`) and writes its row in `progress-design.md` with Edit.
- The register header holds «Кадры рисует» and «Дизайн ведёт».

## screen-spec

- `screen-writer` writes each spec; the session checks it and commits each spec as it lands; rows of
  `progress-screen-specs.md` change with Edit.
- `doc-review` is asked; a decision from the chat is in the spec before the close.

## ui-test-cases

- Write: `check_trace.py` and `check_coverage.py` run at the close; a section's row changes with Edit.
- Run: the runner uses only its own browser and closes it; `test-run.md` is the runner's; a `DEFECTS` verdict
  offers a fix plan (`plan` `MODE fix`).

## docs-consistency

- One `docs-consistency-checker` dispatch; its findings are the user's to settle, each into its document.
- At the close: its own edits committed, then `push_branch.py` — on every verdict — then the plan is offered, not
  started.

## plan

- The session writes no plan: a `plan-*` writer does. `plan_lint.py` is clean, then `plan-review` runs on its own,
  round by round, until `PASS`.
- A product that calls a stubbed external service gets an early «Проверка на настоящем <сервис>» unit; new
  migrations over an existing release get «Обновление поверх v<prev>» (`references/writer.md` → Step 2).

## work

- `progress.md` changes with Edit or `progress_set.py` — never from the shell; the line `progress_link.py` prints
  goes to the chat as printed.
- A unit: the executor, `run_check.py`, `code-review-unit`, then its own commit with `Plan-Unit:` and
  `Co-Authored-By:` in the last paragraph — never chained to a check.
- A parallel unit works in its worktree with repo-relative paths.
- After each unit, the context check (`pipeline` → `references/context.md`): over 300,000 tokens, hand over — the parent clears this session and starts it again; after «продолжай здесь», no more hand-overs in this stage.
- No `sleep` — `run_in_background` or Monitor; every watcher stopped when its work ends.
- The close: `code-review-full`, the run report, `resume.md` deleted, then the question about the next stage the
  chain names — the UI run, else the security audit.

## security-audit

- `security-audit.md` starts with its verdict line; rows change with Edit; the scanners first, then one auditor per
  area.
- `FIX` offers a fix plan; an accepted risk is written with its date under «Принятый риск».
- Before the verdict, the live check (Shannon) is asked — never run unasked, only against the local stand; each of
  its exploited findings is re-checked by a request before it enters (`references/live-pentest.md`).

## deploy-topology

- Step 1: no `security-audit.md` — ask «провести сейчас / собирать без него» before any release work; a skip goes
  into the summary's «Безопасность» row.
- `progress-deploy.md` rows change with Edit.

## operations-doc

- Every query and journal command in the document is proven on the test stand before it is written down.

## ci-pipeline

- The workflow runs the same checks as the project's own scripts; after it, the pipeline ends — the close
  (`pipeline` → End of the pipeline) runs next.
