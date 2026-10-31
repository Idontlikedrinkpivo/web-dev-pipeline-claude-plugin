---
name: pipeline
description: >-
  Order of the pipeline from idea to release: gates, next stages, skips, how a transition is asked. Use at each
  stage's close and for «где я», «что дальше», «на чём остановились», «продолжим», also in a new session (user
  command: /dev-pipeline:continue).
---

# Pipeline

Which stage runs when: the chain, its gates and skips, the iteration a
stage works in, and how a transition is asked. Stages name their successor
here and nowhere else. Changing the order, a gate or a stage: read
`references/maintaining.md` first.

## Names

Skills and agents here belong to the `dev-pipeline` plugin; short names
(`work`, `ui-design`) are for reading. A transition invokes a skill by its
full name, `dev-pipeline:<skill>` in the `Skill` tool, so a same-named skill
from another plugin is never picked (`executor-catalog` → Names); named to
the user as a command, it is `/dev-pipeline:screen-spec`.

Everything the user sees is in the user's language — the answers and the short
lines between tool calls too («Коммичу архитектуру», not «Commit the
architecture change»). A working note to yourself is not printed.

## Parent session and nested sessions

In Claude Desktop the session the user opens is the iteration's **parent**: it runs no stage itself, opens
each stage in a **nested session** with a fresh context (`mcp__ccd_session__start_session`, often deferred —
load it with ToolSearch first), and opens the next one when a nested session reports its stage closed or
handed over. A session whose first message names a parent is a nested one: it runs its stage and, on the
user's answer to the transition question, opens the next stage's nested session itself (the app lets a
session open one only in a turn the user began) and reports to the parent. For the turns without the user,
the parent keeps a reserve of waiting sessions, opened in the user's turns and woken by message. Without that tool the
session runs the stages itself. All of it: `references/parent-session.md`.

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
gate was never meant to buy. A later sitting can still run it. Where a
record names the gate (the SRS stamp), a skip the user chose is
`пропущен`; a gate whose question was never answered — the sitting stopped
first — is `не запускался`, and "Where am I" offers it again.

## The chain

After the SRS the pipeline runs **two branches**. The backend branch needs
the SRS, the schema and the API; the design branch needs only the SRS, so it
can run in parallel — while mockups are drawn, the backend is designed and
scaffolded. They meet before the plan.

```
1 → 2 ─┬─ 3 → 4 → 5 → 6 ─────────┐
       └─ 7 → 8 → 9 ─────────────┴→ 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17
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
| 9 | UI test cases | `ui-test-cases` — mode write | no reviewer — two scripts at its close: `check_trace.py`, `check_coverage.py` | the meeting point — see "Two branches" |
| 10 | Document set check | `docs-consistency` | none — it is the check | `plan` |
| 11 | Implementation plan | `plan` | `plan-review` — **automatic, do not ask**; its findings are fixed round by round until it passes | `work` |
| 12 | Execution | `work` | `code-review-unit` per unit → `code-review-full` once — **automatic, do not ask** | `ui-test-cases` (run) when the product has screens, else `security-audit` |
| 13 | UI acceptance run | `ui-test-cases` — mode run | none | a fix plan — `plan` `MODE fix` over the report's defect rows — when the verdict is `DEFECTS`, else `security-audit` |
| 14 | Security audit — the whole application, once per iteration | `security-audit` | none — it is the check | a fix plan — `plan` `MODE fix` over the report's `FIX` rows — when the verdict is `FIX`, else `deploy-topology` |
| 15 | Compose topology | `deploy-topology` | none | `operations-doc` |
| 16 | Operations document — journals, jobs, alarms, how to see each | `operations-doc` | none — its queries are proven on the test stand | `ci-pipeline` |
| 17 | CI workflow | `ci-pipeline` | none | nothing — the pipeline ends; see "End of the pipeline" |

### Two branches

- **After the SRS** (stage 2) ask one question about the order of the
  branches: both in parallel, one after the other in either order, only
  one of them, or stop — the options, the recommendation and how two
  branches run in one session are in `references/branch-order.md`. The
  backend branch starts at its first applicable stage (`db-schema-design`
  when something must survive a restart, else `openapi-spec-generator`
  when there is HTTP, else `clean-architecture-design`); the design branch
  at `ui-design` when a human faces a screen. A stage or a branch someone
  else takes is handed over by `references/team.md`: any stage of 1–9 can
  be, since its documents travel on the branch.
- **`screen-spec` needs the API.** When stage 7 ends and stage 4 has not
  run, offer the backend branch's next stage and say that the screen specs
  wait for the contract.
- **The meeting point.** Stages 6 and 9 offer stage 10 when the other
  branch is done (its documents on the branch — `git pull --rebase` first
  when other people work on it), else the other branch's next unfinished
  stage. A product
  without screens has no design branch: stage 6 offers stage 10 directly.
- Stage 10 is a stage, not a gate, but it is skippable like one: B on its
  question goes on to `plan` and the skip is named in the report.
- **A fix plan** (rows 13 and 14) goes through `plan-review` and `work`
  like any plan; after its `work`, offer the check that sent it — the UI
  run or the audit — so it re-runs over the fixes.

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

One number, `MAJOR.MINOR.PATCH`, names the release: the manifest's
`version`, the folder `documentation/plans/<version>/`, the branch
`iteration/<version>`, and the tag `v<version>` that closes the iteration.
MAJOR is the owner's call on a big new capability; MINOR and PATCH are
computed from the iteration's typed changes. Levels, the re-check in
`plan`, `plans/` out of git and the API's own version:
`references/service-version.md` — read it when a stage opens an iteration.

**The iteration opens at its first stage that commits anything or writes
into `plans/`** (`brainstorm` on its document, else usually `srs-writer`);
an open `plans/<version>/` (no `summary.md`) is the current iteration and
every later stage reuses it. So is an iteration branch with no tag and no
folder here — a fresh clone, or work another person pushed —
`scripts/where_am_i.py` names it, and `open_iteration.py <version>` only
switches to it and creates the folder: no number is proposed. Opening it: the number (greenfield `0.1.0`
unasked, otherwise proposed with its level and one question), then
`python3 "${CLAUDE_SKILL_DIR}/scripts/open_iteration.py" <version>` — it
updates `main`, creates or switches to `iteration/<version>`, creates the
folder and keeps `plans/` out of git. Its exit 2 or 3 is a question for
the user (an earlier iteration not merged, another one open, no git
repository yet), never something to work around. Then, for a product with screens, the one question who runs
the design (`references/design-owner.md`).

**One branch per iteration.** Every stage of the iteration, by everyone who
works on it (`references/team.md`), commits on `iteration/<version>`;
nothing is committed to `main` during the iteration. Only that branch is
pushed — by the plugin itself once a document of the stages before `work`
is final (its reviews and their fixes done), by the user for the rest — and `main` receives the iteration
once, when the user merges it on GitHub.

## End of the pipeline

The pipeline ends after stage 17, or after the last stage that ran when 14–17 were skipped. The
stage that ran last hands over to this section; it does not end the sitting itself. In this order:

1. **The last stamp.** First, what only a working file still holds moves into its owner document
   through `references/decision-changes.md`: an accepted risk of `security-audit.md` missing from
   architecture §1 «Принятые риски», a decision recorded only in a run report — those files are
   removed in step 7, and the tag must carry what the project relies on. Then: a decision changed after
   the plan, a fix after the UI run or the audit, sits in the contract documents unstamped; the tag
   must carry its rows. Run the stamp over every contract document that differs from its last stamped
   state (`doc-versioning` → `references/version-birth.md`, the iteration's close) — nothing differs,
   nothing is committed.
2. **The site.** Rebuild the documentation site (`docs-site`) and commit it when it changed.
3. **The summary** — `references/summary.md`; on disk only, like the rest of `plans/`.
4. **The tag** `v<version>` on the current commit — the baseline the next iteration's pins and
   diffs read against. Steps 1–4 also run when the user asks «итог», «как отработал пайплайн» or
   «сводка» after `work`. They close the version: a folder with `summary.md` is done.
5. **`reflect`**, unasked.
6. **The closing lines**, in Russian: the work is done and committed on `iteration/<version>`; the
   command that pushes the branch and its tag (`git push origin iteration/<version> v<version>`); the
   merge into `main` is the user's, on GitHub. Offer no other stage.
7. **The working files** — `references/closing-cleanup.md`: one question, below the closing lines; it
   ends the message with its own last line (`references/question-format.md`) and stops the servers.
   With nothing to remove there is no question, and the closing lines end the message.

### The summary

Its shape, where each number comes from, and the two tables the user fills:
`references/summary.md`.

No skill in this pipeline opens a PR or merges on its own. It pushes only
the iteration's branch, and only finished documents of the stages before
`work` — after their reviews and fixes (`scripts/push_branch.py`) — so that
people working on the branch see each other's documents once they are final. The code of `work`, the tag and the
iteration's close are pushed by the user, who reviews the whole result first;
the user merges the branch into `main` on GitHub.

## Where am I

When asked «где я», «что дальше» or «на чём остановились» with no stage just
closed in this sitting — a fresh session, after a compaction, `continue` —
read the state before answering; memory of an earlier session is not
evidence. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/where_am_i.py"` from the
project's root and answer from its output, by `references/where-am-i.md`:
two open iterations are a question first; a `resume.md` is read first and
its run continued; a progress file with unfinished rows is a stage not
done; a stale document's stage comes before the next one; unrun gates are
options, never the only way forward. Ask the answer as one transition
("Asking before a transition"); do not list every remaining stage.

## Increments

A second feature does not restart the pipeline, and it does not run all of it
either. `doc-versioning` is what decides the difference. Writers, `grill-me`,
and `doc-review` edit an existing document in place and never touch its
`version` or changelog; the stamp at the stage's close writes both, one typed
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
no version change, unasked: `references/decision-changes.md`. **A code
change asked in the chat between stages** is not typed by the session: it
goes through `work` → "A change asked in chat outside a run" (an executor,
a review, the affected tests on the branch).

The plan is the exception `doc-versioning` already names: every iteration
gets a **new** `plans/<version>/` folder with its own plan and U-ids,
pinned (`path@<version>`) to the documents it was built from. A closed
version's plan is never edited.

## Asking before a transition

This is the only way a stage outside `work` starts its gate or the next
stage. One transition per question, shown as every question is —
`references/question-format.md`: what the person gets in plain words with
an example first, then the skill's real name and what it means, the
options, the recommendation, «Ответьте сообщением». Before a gate
question, `references/gates.md` says why that gate sits there and what it
costs. In a nested session the answer goes to the parent, which opens the next stage
(`references/parent-session.md`); otherwise, before a transition, check the context
(`references/context.md`): a session over the limit hands the next stage to a fresh one instead of
starting it here. When the user wants the next iterations to run without them, the
questions are asked once, before the first (`references/unattended.md`).

Explain the skill in the user's terms: `grill-me` is the interview that
tries to knock down assumptions in the document; `doc-review` is a review
of the written document by several checks, and it spends model calls;
`docs-consistency` reads all the documents together and finds where they
contradict each other or leave a requirement without a home; the next
stage is the writer named in this table's offer cell, including a skip (no
UI, no storage, no HTTP) — name the skill the skip selects and why the
skipped ones do not apply.

**Commit each document as soon as it is written.** The moment a writer
returns a document, the session commits it, before its gates and without
asking: `docs: <документ> — написан, этап не закрыт` (an as-is document
from `upgrade-docs` is born complete: `docs: <документ> <version> — как
есть`, its stamp). A document of several
files (the schema with its migration, the API's parts) is one commit; each
architecture document, screen spec and test-case section is its own. Gate
fixes are committed as they land. The stamp (`doc-versioning` →
`references/version-birth.md`; the frames register and test cases plainly)
follows at the stage's close — once its gates ran or were skipped, or when
the user stops at a gate's or transition's question (the stop line names
the gates not run). A stop, a compaction, or another person who picks the
work up from git (`references/team.md`) then finds every finished document
on the branch, and `scripts/where_am_i.py` reads from the commits what is
written and which stage is still open. **A finished document is sent,
not a draft.** A document is final when the gates of its stage that apply to
it ran or the user skipped them and their fixes are committed, and
`python3 "${CLAUDE_SKILL_DIR}/../doc-versioning/scripts/doc_check.py" . --only <each document of the stage>`
passes before the stamp commit (its lines are fixed first); only then run
`python3 "${CLAUDE_SKILL_DIR}/scripts/push_branch.py"`: at the stage's close,
after the stamp, all its documents at once (the architecture's three too); a
changed decision is final at its own commit;
`docs-consistency`, when its fixes are committed. Drafts stay committed on
this machine until then. Only the stages before `work` push this way. The
script pushes `iteration/<version>` to `origin` when the project has one,
after taking the others' commits (`git pull --rebase`); never `main`, never a
tag, never `--force`. Its one line goes into the message. Exit 1 (no access,
no network) is no stop — say it with the command it prints; exit 2 (the
others' commits conflict with these) is a question to the user before
anything else.

For a **gate**, three options, always these letters:

- `A. Запустить <gate>`
- `B. Пропустить и перейти к <the next transition>`
- `C. Остановиться`

Mark the recommended one «(рекомендую)» where it stands — the letters do
not move — and say why in one line. Judge by what the stage just decided,
not by habit: a new document, a security or money decision, or a reversal
worth falsifying → recommend running the gate; a small, fully specified
change (a field, a control, an edit the user already spelled out) →
recommend skipping, and say the gate would have little to find.

For an **offer**, two options: `A. Запустить <skill> (рекомендую)` and
`B. Остановиться`.

A runs that skill now and follows it. When it returns, ask the next
unrun transition in the row: the next gate, then the offer. B on a gate
records the skip (see "Two kinds of transition") and asks the next
transition in the same way. C, or B on an offer, stops the sitting. A
message that answers neither is not a choice
(`references/question-format.md` → Answers). Do not start a skill the user
did not pick. Do not ask the following transition in the same turn as the
one just answered, except after a skip, where the next question is the
answer.

No menu of every remaining stage; "ok" on a summary is not a yes.

Example — the SRS was just written and its grill closed; the next unrun
transition in row 2 is `doc-review`:

```text
**Проверить требования ревьюерами?**

Несколько независимых проверяющих прочитают требования и найдут места,
где они противоречат себе или их нельзя выполнить: например, бронь «на
любой срок» рядом с лимитом в 4 часа. Это `doc-review`: две постоянные
роли и условные — здесь ещё проверка безопасности, потому что в
требованиях есть оплата; каждая роль — отдельный вызов модели.

  A. Запустить doc-review (рекомендую)
  B. Пропустить и перейти к выбору порядка веток
  C. Остановиться

Рекомендую A: документ новый, в нём деньги.

Ответьте сообщением: буква или свой текст.
```

Example — the SRS gates are done; both branches open (options from
`references/branch-order.md`):

```text
**Что делаем дальше: базу и API или макеты экранов**

Требования готовы. Дальше две независимые ветки: бэкенд — таблицы базы,
API, устройство кода, каркас проекта; дизайн — макеты экранов в Figma,
описание каждого экрана для вёрстки (ТЗ на экран), тест-кейсы. Описания
экранов в любом порядке дождутся API.

  A. Обе ветки параллельно; вопросы помечены [Бэкенд] / [Дизайн] (рекомендую)
  B. Сначала бэкенд (db-schema-design), потом дизайн
  C. Сначала дизайн (ui-design), потом бэкенд
  D. Только бэкенд — дизайн ведёт другой человек или позже
  E. Только дизайн — бэкенд позже
  F. Остановиться

Рекомендую A: правки макетов небольшие, и ветки не мешают друг другу.

Ответьте сообщением: буква или свой текст.
```

When a gate produced findings the user chose not to apply, say which gate
and what is outstanding in the next question's chat block. User-deferred
review items live in `open-questions.md` beside that document, not inside the
contract document.

`grill-me` and `doc-review`, when a stage invoked them as a gate, and
`plan-review`, which `plan` runs on its own, report and return. They do not ask the next transition. The stage
that called them asks. When the user opened one of those gates directly,
that gate asks the next transition itself, using this section.

## Secrets

Binding on every stage. A key, token, password or connection string never
enters the pipeline's files — no document, agent packet, commit, progress
file, command line or reply. Ask *which* provider and *whether* an account
exists, never for the value. Name it by its variable (`FIGMA_TOKEN`,
`DATABASE_URL`): `.env.example` holds the name with an empty value, and the
user writes the value into the git-ignored `.env` themselves. When the user
pastes one anyway — `hooks/secret-in-prompt.sh` names its kind, never the
value — say in one line that it was not saved and is worth revoking, since
it has been in the chat; the user's words around it go on as usual. A
secret found committed is the audit's (`security-audit`, its history
scan).

## References

- `references/question-format.md` — how every question is shown and what
  counts as an answer.
- `references/service-version.md` — the number, opening an iteration
  (`scripts/open_iteration.py`), the branch, the level re-check, `plans/`
  out of git.
- `references/where-am-i.md` — reading `scripts/where_am_i.py` and
  building the answer.
- `references/convergence.md` — fix-and-check cycles repeat until they
  pass; what keeps a round cheap and when lack of progress stops it.
- `references/gates.md` — why each gate sits on its stage and what its
  question says about cost.
- `references/progress-files.md` — which stages keep a progress file in
  `plans/<version>/`, its shape, and the chat line `scripts/progress_link.py`
  prints for it.
- `references/pause-and-resume.md` — the resume note a long run (`work`,
  `ui-test-cases` mode run, `security-audit`) keeps current, and what a
  session that picks up a stopped run reads first.
- `references/decision-changes.md` — a decision changed after its stage
  closed: the owner, the cascade, the commit, where it happens.
- `references/team.md` — an iteration shared with other people: any stage of 1–9 handed over and picked up from
  the branch.
- `references/closing-cleanup.md` — the working files a closed iteration drops.
- `references/context.md` — what a stage session lets into its context
  (short reports, checks summarised, long output in files) and when it
  hands over to a fresh session (over 300,000 tokens at a safe boundary).
- `references/unattended.md` — several iterations without the user: the
  standing answers before the first, the child's «закрыта» message, checking
  instead of answering from memory; a parent session that runs no stage and
  opens nested sessions with a fresh context (`start_session`).
- `reflect` (skill) — the plugin's own failures in the iteration's sessions.
- `references/branch-order.md` — the order of the two branches after the
  SRS, and both branches in one session.
- `references/design-owner.md` — who runs the design, asked at the start.
- `references/maintaining.md` — changing the order, a gate or a stage, and
  the asymmetries that are on purpose.
- `doc-versioning` (skill) — the increment/greenfield decision, the canonical
  path per document type, the downstream verdict this file reads,
  the unversioned business-requirements draft, and document language
  (Russian prose, untranslated cited tokens).
- `ui-design` (skill) — mockups straight from the SRS (stage 7) and the
  frames register; `screen-spec` (skill) — one front-end spec per screen
  from the frames and the API (stage 8).
- `ui-test-cases` (skill) — user test cases from the screen specs (stage 9)
  and their run through the interface after `work` (stage 13).
- `security-audit` (skill) — the whole application's security (stage 14).
- `ux-patterns` (skill) — the checkable UI/UX rules (`UX-<n>`, B2B/B2C
  variants) and the completeness checklist that `ui-design`, the Figma
  builders, `frontend` and the design lens apply; the product type comes
  from the frames register.
- `executor-catalog` (skill) — the same one-table discipline for models; every
  gate that dispatches a subagent resolves it there and dispatches the row's
  agent by name, with no `model` on the call. A dispatch on `general-purpose`
  or with a typed `model` is a failed dispatch, same as a rejected alias.
