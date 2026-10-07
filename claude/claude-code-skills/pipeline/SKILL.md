---
name: pipeline
description: >-
  The order of the development pipeline: after the SRS a backend branch
  (schema, API, architecture, skeleton) and a design branch (mockups, screen
  specs, test cases) that meet at docs-consistency before the plan; which
  gates and next stage follow each stage, the skip rules, and how a
  transition is asked — run, skip, or stop. Use at the
  close of any stage, when the user asks «что дальше» or «где я» (including
  in a fresh session, by reading the documents on disk), or when adding,
  reordering or retiring a stage. Writes no document.
---

# Pipeline

Stages name their **successor** here and nowhere else. Reordering or
retiring a *stage* is a one-table edit. Gates are not: `grill-me` and
`doc-review` are still invoked from the writer skills that own the
artifact, so inserting or retiring a gate is this table **plus** those
hardcoded calls. Do not claim a single-file gate edit.

This is the discipline `executor-catalog` applies to models: a finished
stage resolves to the next stage and its gates in one table. A stage that
hardcodes "now run X" is a second source of truth, and the two drift the
first time the order changes.

## Names

Skills and agents here belong to the `dev-pipeline` plugin; short names
(`work`, `ui-design`) are for reading. A transition invokes a skill by its
full name, `dev-pipeline:<skill>` in the `Skill` tool, so a same-named skill
from another plugin is never picked (`executor-catalog` → Names); named to
the user as a command, it is `/dev-pipeline:screen-spec`.

## Two kinds of transition

The distinction is load-bearing. Outside `work`, both kinds are questions.
Inside `work`, the reviews in the Gates cell stay automatic.

| Kind | Meaning |
|---|---|
| **gate** | the check listed for this stage (`grill-me`, `doc-review`). Ask before starting it; every question inside it — each grill question, each review finding — is the user's to answer. `plan-review` and the code reviews are not asked: they run on their own, because every product decision is already settled in the documents, so what the review finds is the pipeline's own work to fix. A recommendation, not a lock: the user runs it, skips it and goes on, or stops. A skipped gate is named in the stage's report and blocks nothing. |
| **offer** | the one next stage in the table. Ask before starting it. A declined offer stops the sitting. |

The exception is stage 12: `work` invokes `code-review-unit` per unit and
`code-review-full` once at the end without asking. Those calls are inside
the run, not transitions; nothing outside `work` schedules them. The offer
after `work` is still a question.

A skipped gate is not a passed gate, and it is not a stop either. Say
which gate did not run, leave its field unset (`grilled:`, `reviewed:`,
`docs-consistency.md`), and ask the next transition. The user owns the
trade-off: a small, fully specified change often has nothing for a gate
to find, and making them sit through it anyway is the inflexibility the
gate was never meant to buy. A later sitting can still run it.

## The chain

After the SRS the pipeline runs **two branches**. The backend branch needs
the SRS, the schema and the API; the design branch needs only the SRS, so it
can run in parallel — while mockups are drawn, the backend is designed and
scaffolded. They meet before the plan.

```
1 → 2 ─┬─ 3 → 4 → 5 → 6 ─────────┐
       └─ 7 → 8 → 9 ─────────────┴→ 10 → 11 → 12 → 13 → 14 → 15
```

| # | Stage | Skill | Gates (ask, in order) | Then offer (ask) |
|---|---|---|---|---|
| 1 | Business requirements | `brainstorm` | `grill-me` | `srs-writer` |
| 2 | SRS | `srs-writer` | `grill-me` → `doc-review` | a branch: the backend branch's first applicable stage, or `ui-design` — see "Two branches" |
| 3 | DB schema | `db-schema-design` | `doc-review` | `openapi-spec-generator` when the surface is HTTP, else `clean-architecture-design` |
| 4 | API contract | `openapi-spec-generator` | `doc-review` | `clean-architecture-design` |
| 5 | Architecture — foundation, domain model, scenarios by area | `clean-architecture-design` | `doc-review` on each document written | `repo-scaffold` |
| 6 | Repository skeleton | `repo-scaffold` | none — also writes `documentation/project-map/project-map.md` | the meeting point — see "Two branches" |
| 7 | Mockups | `ui-design` | none — frames are not a document | `screen-spec` once the API exists, else the backend branch's next stage; after a restyle of screens already built, `plan`; after a redraw on a new page, `screen-spec` for every screen |
| 8 | Screen specs (ТЗ на экран) | `screen-spec` | `doc-review` | `ui-test-cases` (write) |
| 9 | UI test cases | `ui-test-cases` — mode write | none | the meeting point — see "Two branches" |
| 10 | Document set check | `docs-consistency` | none — it is the check | `plan` |
| 11 | Implementation plan | `plan` | `plan-review` — **automatic, do not ask**; its findings are fixed round by round until it passes | `work` |
| 12 | Execution | `work` | `code-review-unit` per unit → `code-review-full` once — **automatic, do not ask** | `ui-test-cases` (run) when the product has screens, else `deploy-topology` |
| 13 | UI acceptance run | `ui-test-cases` — mode run | none | a fix plan (`plan`) when the verdict is `DEFECTS`, else `deploy-topology` |
| 14 | Compose topology | `deploy-topology` | none | `ci-pipeline` |
| 15 | CI workflow | `ci-pipeline` | none | nothing — the pipeline ends; see "End of the pipeline" |

### Two branches

- **After the SRS** (stage 2) ask one question with both branches as
  options: the backend branch's first applicable stage (`db-schema-design`
  when something must survive a restart, else `openapi-spec-generator`
  when there is HTTP, else `clean-architecture-design`) and `ui-design`
  when a human faces a screen. Recommend the backend branch first when the
  user has no designer waiting; either order is correct.
- **`screen-spec` needs the API.** When stage 7 ends and stage 4 has not
  run, offer the backend branch's next stage and say that the screen specs
  wait for the contract.
- **The meeting point.** Stages 6 and 9 offer stage 10 when the other
  branch is done, else the other branch's next unfinished stage. A product
  without screens has no design branch: stage 6 offers stage 10 directly.
- Stage 10 is a stage, not a gate, but it is skippable like one: B on its
  question goes on to `plan` and the skip is named in the report.

`work`, the design writers (`db-schema-design`, `openapi-spec-generator`,
`clean-architecture-design`), `ui-design`'s Figma builders and
`screen-spec`'s writer resolve executors through `executor-catalog`. That
lookup is inside the stage, never an offer.

## Skips

A skipped stage is announced with its reason, never silently dropped — the next
reader has to be able to tell "not applicable" from "forgotten":

| Skip | When |
|---|---|
| stage 3 | no storage |
| stage 4 | no HTTP surface. Screen specs then have no operations: their elements cite local behaviour only |
| stages 7, 8, 9, 13 | no human-facing surface (API-only, jobs, library). Say so once, after the SRS |
| stages 1–9 | brownfield: the repo's code *is* the design and the user wants work planned against it. Enter at stage 11; `plan` marks every unit's `Docs` as `code:<path>` and dispatches `code-explorer` for the inventory |

Entering mid-chain is normal — a user who already has an SRS starts at stage 2's
offer. What is not normal is entering mid-chain and *assuming* the earlier
artifacts exist: each stage states its own required inputs and stops when one is
missing. This file decides order, not whether an input is present.

## Service version

The service has one number, `MAJOR.MINOR.PATCH`: the manifest's `version`,
the name of `documentation/plans/<version>/` (the iteration's plan, reports,
summary), the git tag `v<version>` that closes the iteration — the
**baseline**, the documents and code of that release — and the prefix of
the image tag `deploy-topology` writes. A document's `version` is the
release it last changed in (`doc-versioning` → What a version is).

| Level | When | Who decides |
|---|---|---|
| MAJOR | a big new capability that really extends the service: a new functional area, a new kind of user, a new way of working with it | the owner. Propose it when the iteration adds a new capability group (a new area) to the SRS, or the owner called the change big; the owner confirms |
| MINOR | new functionality inside existing areas: scenarios, screens, operations, fields | computed: at least one change typed «добавляет» or «ломает» in a versioned document |
| PATCH | fixes only: behaviour brought to what the documents already say | computed: only «уточняет» changes and code fixes |

A «ломает» alone makes a MINOR, not a MAJOR. Before the first release
versions are `0.x.y` (a manifest with no version → `0.1.0`); the owner says
when the first release, `1.0.0`, is.

**The iteration's version is fixed when the iteration opens**, by its first
stage that changes a versioned document or writes into `plans/`: on
greenfield `0.1.0`, without asking; on an increment usually `srs-writer`,
else `docs-consistency` or `plan`. An open `plans/<version>/` (no
`summary.md`) is the current iteration, and every later stage reuses it.
Otherwise the stage proposes the number after the manifest's, with its
level and a one-line reason («MINOR: новые UC-5, UC-6 в бронированиях»), as
a question per "Asking before a transition" (`A. <версия> (Recommended)`,
`B. Остановиться`, or another number), and creates the folder on the
answer. Every stamp of the iteration writes that number.

`plan` re-checks the level once every change is known, from the
iteration's typed changes: its changelog rows, plus any change not stamped
yet, typed the same way from the diff since the last tag. A changed level is asked again; on a yes the session
renames the open folder and replaces the old number in that iteration's
`version` fields, rows and pins in one commit (`docs: итерация <old> →
<new>`) — it was never released, so nothing outside the iteration names
it. The plan's last unit bumps the manifest's `version` to the folder's
name; `summary.md` and the tag close the iteration (End of the pipeline).

**Plans stay out of git.** `documentation/plans/` is in `.gitignore`:
the plan, its review, the progress files, the stage reports
(`docs-consistency.md`, `test-run.md`) and `summary.md` are working files
on this machine. Git keeps what outlives the run — the code, the
contract documents, a `Plan-Unit:` trailer on every unit commit, and the
tag `v<version>` at the close. The first stage that writes into `plans/`
checks `.gitignore` and adds `documentation/plans/` if it is missing; if
the folder is already tracked, it untracks it with
`git rm -r --cached documentation/plans` (the files stay on disk) in its
own commit. No stage stages a file under `plans/`.

**The API's own version.** Called only by the project's own client, the API
has no separate number: `info.version` is the service version. With
external consumers (Full trigger "versioned partner API") it has its own
SemVer and its major in the path — `openapi-spec-generator` → Contract version.

## End of the pipeline

The pipeline ends after stage 15. If stages 14 and 15 were skipped or
declined, it ends after the last stage that ran. At that point, say in the
chat, in Russian, that the work is done and committed on the current branch
(name it), and that push and the PR are the user's step. Do not offer
another stage.

Before that line, write the iteration's summary (on disk only, like the
rest of `plans/`) and tag the current commit `v<version>` — the baseline
the next iteration's pins and diffs read against. Also do both
when the user asks «итог», «как отработал пайплайн», or «сводка» after
`work`. They close the version: a `plans/<version>/` folder with
`summary.md` is done.

### The summary

`documentation/plans/<version>/summary.md`, beside the plan — one
iteration, one page, so the user judges the pipeline by numbers rather
than by impression, and sees which stage to fix when something slipped.
The session writes it from the reports already on disk; it reads no code
and dispatches nothing. A report that is missing gives a `—` cell with the
reason (stage skipped, gate skipped), never a guess.

```markdown
# Итог итерации — <version>

| Этап | Показатель | Значение | Источник |
|---|---|---|---|
| Документы | противоречий найдено до плана | 4 (P0 2, P1 2) → исправлено | docs-consistency.md |
| План | грейд · вердикт plan-review с первого раза · доработок | Mid · FIX_THEN_PROCEED · 1 (plan-lite) | plan-review.md |
| Код | юнитов · вернулось на переделку · эскалаций · исправлений грейда | 12 · 2 · 1 · 1 | run report (`.git/pipeline-work/<version>-run.md`) |
| Ревью | находок P0/P1 по юнитам · вердикт финального ревью | 3 · PASS | run report, Full-plan review |
| UI-тесты | кейсов · прошли с первого прогона · дефектов пережило ревью | 22 · 19 · 2 | test-run.md |
| Гейты | пропущены | grill-me (S-13, маленькая правка) | отчёты этапов |
| Цена | токены / деньги / время, если сессия их показывает | — | статистика сессии |

## Проскочившие дефекты
Заполняет пользователь, когда находит дефект после «готово».
| Дефект | Где нашли | Какой этап должен был поймать |
|---|---|---|

## Ручные вмешательства
| Что поправили руками | Документ / план / код | Почему пайплайн не справился |
|---|---|---|
```

Below the table, one line naming the weakest stage of this iteration (the
most returns, defects, or interventions), or «слабых мест не видно». The
two lower tables start empty; the user fills them later. Escaped defects
are the main measure of the pipeline: each one names the stage whose skill
needs a fix.

No skill in this pipeline pushes, opens a PR, or merges. Everything stays
local until the user ships it, so the user decides when the branch leaves
the machine and reviews the whole result first, not a half-finished one.

## Where am I

When asked "what is the next step" with no stage just closed in this
sitting, read state before answering. Memory of an earlier session is not
evidence; the files on disk are.

1. Probe the canonical paths in `doc-versioning` → Registry, in chain
   order. Note which exist, and the open `documentation/plans/<version>/`
   (no `summary.md`, see "Service version"): it holds stages 10–13 so far.
   `plans/` is not in git, so a fresh clone has none: then the tags
   `v<version>` name the closed iterations, the `Plan-Unit:` trailers
   since the last tag name the units already landed, and the state of
   stages 10–13 is unknown — say so rather than guessing.
2. For each versioned document found, compare its `sources:` pins
   (`info.x-sources` in OpenAPI) with the sources' current `version`. A pin
   behind with a «ломает» row after it is stale — say which, per
   `doc-versioning` → Staleness and cascade; behind by «добавляет» only is
   for stage 10, not a stale stage.
3. A business-requirements document with no `grilled:` has an unrun
   gate. An SRS has no `grilled:`, `reviewed:`, `status`, or
   `sources`; do not read their absence as an unrun gate. Any other
   document whose row lists `doc-review`, with no `reviewed:`
   (`info.x-reviewed` for OpenAPI), had its review skipped or never
   run — offer it rather than assuming either. An open version folder
   with `plan.md` and no `plan-review.md`, or one whose first line is not
   `Verdict: PASS`, has an unrun `plan-review` gate. When both branches are
   done (or the design branch does not apply), a `docs-consistency.md` in
   the open folder that is missing, has a first line other than
   `Verdict: PASS`, or lists a `checked:` hash that no longer matches
   `git hash-object` of that path means stage 10 has not run for the
   current set.
   An unrun gate may have been skipped on purpose; the files cannot tell.
   List unrun gates in one line and offer the earliest as an option of
   the question below, never as the only way forward.
4. Report both branches: the last stage present on each (for the design
   branch `documentation/ui/frames-register.md`, `ui/screen-specs/` and
   `ui/test-cases/`). The answer is the earliest
   unfinished point: a stale document's stage, else the next stage of a
   branch that is not done (both as options when both are open), else
   stage 10, with the unrun gates from step 3 as options.
   Ask it as one transition, per "Asking before a transition". Do not
   list every remaining stage.

Example — a fresh session, the user asks «что дальше?»:

```text
Найдено:
  documentation/requirements/business-requirements/business-requirements.md  grilled: 2026-05-02
  documentation/requirements/srs/srs.md  version: 1.3.0
  documentation/db/schema.md  sources: …srs/srs.md@1.2.0, reviewed: 2026-05-06
  documentation/api/openapi.yaml — нет
  documentation/plans/ — 1.2.0 закрыт (summary.md), 1.3.0 открыт

Шаг 2: схема закреплена за SRS 1.2.0, а в SRS 1.3.0 есть строка «ломает»
(BR-3) — схема устарела.
Шаг 4: самая ранняя незаконченная точка — схема, раньше непройденных гейтов
и следующего оффера.

Чат: в SRS 1.3.0 изменилось правило BR-3, а схема БД построена по 1.2.0.
`db-schema-design` прочитает строки журнала SRS после 1.2.0 и обновит
схему; без этого API будет строиться на старых таблицах.

Ответьте сообщением: буква или свой текст.
  A. Запустить db-schema-design (Recommended)
  B. Остановиться
```

## Where each gate comes from, and why it is there

Read `references/gates.md` before asking a gate question: why `grill-me`,
`doc-review`, `docs-consistency` and `plan-review` sit where they do, and
what each question says about the gate's cost.

## Asymmetries, on purpose

Each of these looks like an omission and is not. Do not "fix" one without
changing this file:

| Looks missing | Why it is not |
|---|---|
| No `doc-review` on business requirements | Stage 1's artifact is the least formal in the pipeline and every line of it is re-examined when `srs-writer` reads it. The grill is the stronger instrument there, and it runs. |
| No `grill-me` on mockups | The user judges mockups by looking at them in Figma; a grill interrogates written decisions, and the decisions the frames embody are written down by `screen-spec`, whose `doc-review` checks them. |
| No `grill-me` on architecture, DB, or API | Those decisions are technical, not product, and the user is not the one who settles them. `doc-review` already carries the right instruments: `adversarial-document-reviewer` challenges the premise and `security-lens-reviewer` the security decisions. |
| No gate on the Figma file | Frames are not a document. `ui-design` checks the returned `nodeId`s and its completeness checklist; `screen-spec`'s sync check (frame ↔ action ↔ API) and `doc-review` cover the rest. |
| No whole-codebase audit stage | Deliberately not a stage. This pipeline reviews what a run produced: `code-review-full`'s `Drift` and `Superseded code` lenses cover technical debt introduced by the plan, and its security lens covers both declared requirements and the surface the diff introduced. A standing audit of code no plan touched is a different activity with a different cadence, and no stage here depends on one. |

## Increments

A second feature does not restart the pipeline, and it does not run all of it
either. `doc-versioning` is what decides the difference. Writers, `grill-me`,
and `doc-review` edit an existing document in place and never touch its
`version` or changelog; the stamp the user asks for writes both, one typed
row per change (ломает / добавляет / уточняет). `plan` does not call it.
The writer names each change with its type and a **downstream verdict per
consumer** in its report — must update, or unaffected with the reason, for
a «ломает»; where the new thing lands, for a «добавляет» — and offers the
next stages from it. The stamp copies that line into `Кого затрагивает`.
Stage 1 (`brainstorm`) has no `version`; a rewritten business-requirements
draft is not a cascade — offer `srs-writer` when the user wants the
contract updated.

Read that verdict and offer only the stages it named:

| Changed | Names |
|---|---|
| SRS | the documents whose ids it touched: schema, API, domain model, the scenarios of the touched areas, `ui-design` for screens a changed use case appears on |
| schema | API, domain model |
| API | scenarios that call the changed operations, screen specs that cite them |
| domain model | scenarios that cite the changed rules |
| scenarios of an area | `plan` |
| architecture foundation | `repo-scaffold` when the tree or the stack moved, the scenarios that use a changed port, `plan` |
| mockups (frames) | screen specs of the changed screens; after a restyle none — `plan`, for the theme unit |
| screen spec | `ui-test-cases` (write), `plan` |

The architecture foundation is not named by a feature unless the feature
changes a fundamental decision. Any change re-opens stage 10 before `plan`. Each skip is a line in
that report, not a guess from the row numbers.

Two rules keep this honest:

- **The verdict decides, not the chain.** Offering the API stage because it
  follows the schema, on an increment that changed no column, burns a
  `doc-review` on an unchanged document.
- **A missing verdict is a stop.** If an increment's report does not say
  what it made stale, ask its stage to say so rather than guessing
  downstream, and do not wait for a changelog row the commit has not
  written yet.

**A decision changed after its stage closed** (in `work`, a later stage, the
chat) goes straight into the documents that state it, committed at once with
no version change, unasked: `references/decision-changes.md`.

The plan is the exception `doc-versioning` already names: every iteration
gets a **new** `plans/<version>/` folder with its own plan and U-ids,
pinned (`path@<version>`) to the documents it was built from. A closed
version's plan is never edited.

## Asking before a transition

This is the only way a stage outside `work` starts its gate or the next
stage. One transition per question. Follow `grill-me` → "How a question is
shown".

In the chat, in Russian, name the skill and what it will do to the artifact
just written. Keep the skill's real name. Explain it: `grill-me` is the
interview that tries to knock down assumptions in the document; `doc-review`
is a review of the written document by several checks, and it spends model
calls; `docs-consistency` reads all the documents together and finds where
they contradict each other or leave a requirement without a home; the next stage is the writer named in this
table's offer cell, including a skip (no UI, no storage, no HTTP) — name
the skill the skip selects and why the skipped ones do not apply.

One question, then stop. The user answers by sending a message. Do not
open a question card.

For a **gate**, three options:

- `A. Запустить <gate>`
- `B. Пропустить и перейти к <the next transition>`
- `C. Остановиться`

Mark one `(Recommended)` and put it first, and say why in one line. Judge
by what the stage just decided, not by habit: a new document, a security
or money decision, or a reversal worth falsifying → recommend running the
gate; a small, fully specified change (a field, a control, an edit the
user already spelled out) → recommend skipping, and say the gate would
have little to find.

For an **offer**, two options: `A. Запустить <skill> (Recommended)` and
`B. Остановиться`.

A runs that skill now and follows it. When it returns, ask the next
unrun transition in the row: the next gate, then the offer. B on a gate
records the skip (see "Two kinds of transition") and asks the next
transition in the same way. C, or B on an offer, stops the sitting. Do
not start a skill the user did not pick. Do not ask the following
transition in the same turn as the one just answered, except after a
skip, where the next question is the answer.

Do not present a menu of every remaining stage. Do not treat "ok" on a
summary as a yes. The user's message is the yes.

Example — the SRS was just written and its grill closed; the next unrun
transition in row 2 is `doc-review`:

```text
Чат: Следующая проверка — `doc-review`. Несколько ревьюеров прочитают
SRS и проверят его на противоречия, пробелы и выполнимость. Это
отдельные вызовы моделей: две постоянные роли плюс условные, здесь
ещё `security-lens-reviewer`, потому что в SRS есть оплата.

Ответьте сообщением: буква или свой текст.
  A. Запустить doc-review (Recommended)
  B. Пропустить и перейти к выбору ветки
  C. Остановиться
```

Example — the SRS gates are done; both branches open:

```text
Чат: SRS готова. Дальше две независимые ветки: бэкенд (схема БД → API →
архитектура → каркас) и дизайн (макеты в Figma по SRS → ТЗ на экраны →
тест-кейсы). Их можно вести параллельно; ТЗ на экраны дождутся API.

Ответьте сообщением: буква или свой текст.
  A. Начать бэкенд: db-schema-design (Recommended)
  B. Начать дизайн: ui-design
  C. Остановиться
```

When a gate produced findings the user chose not to apply, say which gate
and what is outstanding in the next question's chat block. User-deferred
review items live in `open-questions.md` beside that document, not inside the
contract document.

`grill-me` and `doc-review`, when a stage invoked them as a gate, and
`plan-review`, which `plan` runs on its own, report and return. They do not ask the next transition. The stage
that called them asks. When the user opened one of those gates directly,
that gate asks the next transition itself, using this section.

## Changing this file

- **Reorder or insert a stage** — edit the chain table only. No stage skill
  changes, because none of them names its successor.
- **A new stage needs a row and a reason** — what it consumes, what it produces,
  and which gates close it. A stage nobody offers is unreachable; a stage with
  no gate has to say why none applies.
- **A new gate is a cost decision.** Say what it costs per run in the same
  sentence you add it, the way the `doc-review` note above does.
- **Retiring a stage** — remove its row and re-point the neighbours' `Then
  offer` cells in the same edit, otherwise the chain has a hole that reads as a
  dead end.
- **Do not encode content rules here.** What a document must contain belongs to
  its stage; this file only says which stage runs when.

## References

- `references/convergence.md` — fix-and-check cycles repeat until they
  pass; what keeps a round cheap and when lack of progress stops it.
- `references/gates.md` — why each gate sits on its stage and what its
  question says about cost.
- `references/progress-files.md` — which stages keep a progress file in
  `plans/<version>/`, its shape, and the link posted before the first step.
- `references/decision-changes.md` — a decision changed after its stage
  closed: the owner, the cascade, the commit, where it happens.
- `doc-versioning` (skill) — the increment/greenfield decision, the canonical
  path per document type, the downstream verdict this file reads,
  the unversioned business-requirements draft, and document language
  (Russian prose, untranslated cited tokens).
- `ui-design` (skill) — mockups straight from the SRS (stage 7) and the
  frames register; `screen-spec` (skill) — one front-end spec per screen
  from the frames and the API (stage 8).
- `ui-test-cases` (skill) — user test cases from the screen specs (stage 9)
  and their run through the interface after `work` (stage 13).
- `ux-patterns` (skill) — the checkable UI/UX rules (`UX-<n>`, B2B/B2C
  variants) and the completeness checklist that `ui-design`, the Figma
  builders, `frontend` and the design lens apply; the product type comes
  from the frames register.
- `executor-catalog` (skill) — the same one-table discipline for models; every
  gate that dispatches a subagent resolves it there and dispatches the row's
  agent by name, with no `model` on the call. A dispatch on `general-purpose`
  or with a typed `model` is a failed dispatch, same as a rejected alias.
