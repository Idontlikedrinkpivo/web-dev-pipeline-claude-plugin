---
name: srs-writer
description: >-
  Turns any product or feature description — a brainstorm document, a note,
  a ticket, a chat paste — into a numbered SRS with FR / NFR / BR / UC ids
  and Given/When/Then acceptance criteria, or updates the existing SRS in
  place. Use when the user asks for an SRS, requirements, use cases or
  acceptance criteria — «напиши ТЗ», «оформи требования» — or a brainstorm
  is ready to become a contract. Not for deciding what to build
  (`brainstorm`), grilling (`grill-me`), or architecture, API or DB design.
---

# SRS Writer

Turns already-settled product decisions into a **Software Requirements Specification** — the formal document that sits between "what we decided to build" (`brainstorm`) and the schema and API that are written from it. Architecture reads those later, when it lays out the code.

**This skill does not invent product decisions.** It reads whatever the user gave — a file in any format, a paste, or a description in the chat — and:
1. Extracts the settled product shape and systematizes it into IDed, unambiguous requirements.
2. Adds the sections a short description usually omits: Non-Functional Requirements, Business Rules/Invariants, and full Use Cases with main/alternative/exception flows.
3. Attaches a Given/When/Then acceptance criterion to every scenario.

A short, messy, or differently headed description is still input: write the SRS from it, and put what it does not say in `open-questions.md` beside the file. This skill formats and completes; it does not decide.

## Orchestrator (session)

The session writes no SRS file. `srs-author` settles it and nests
`doc-typist` to print it. A report whose `DELEGATED` is not `doc-typist`
comes back once.

1. Resolve the source (Input Resolution, steps 1–3). If there is neither a file nor a description, route to `brainstorm`. Do not invent the product.
2. **Fix the iteration's version before the dispatch.** Greenfield: `0.1.0`, no question. On an increment this is usually the iteration's first stage. An open `documentation/plans/<version>/` (no `summary.md`) is the current iteration: reuse it. None open: fix the version per `pipeline` → Service version, which owns the rule — propose the number with its level and a one-line reason (MAJOR is proposed when the increment adds a new capability group to §3), ask, and create the folder on the answer. Paste the version into the packet's INPUTS. A greenfield SRS is born at it; an increment leaves `version` to the stamping commit.
3. Read `executor-catalog`. Dispatch exactly one writer with `executor-catalog/references/srs-writer-prompt.md`. The executor is `srs-author`. Before the `Agent` call, write `srs-author | srs-author`, then dispatch `subagent_type: "srs-author"` with no `model`: the agent file holds it. A dispatch on `general-purpose` or with a typed `model` is a failed dispatch. A missing agent or a rejected alias is a stop per the catalog's Dispatch contract and Slug hygiene. Do not write the file on the session model to save a dispatch. A failed dispatch is reported, not replaced.
4. On `STATUS BLOCKED` for a product decision, ask the user (options go through `grill-me` → "How a question is shown"), then dispatch `srs-author` again with the answer pasted. Do not fill the gap yourself.
5. **Grill gate — after the file exists, before it is declared done.** The order is deliberate: `grill-me` works against an artifact. Ask first, per `pipeline` → "Asking before a transition". Run: read `grill-me` and follow it. Skip: name it in the report and ask about `doc-review`. Stop: stop. The subject is what this stage settled — NFRs, invariants, use-case flows, exception paths, the security sub-checklist. Not the interface: a question about screens, controls or wording belongs to the mockups (`ui-design`). Decisions that arrived already grilled with the business-requirements document are not re-litigated. Increment mode grills the new feature only. Stop after each round and wait. When the grill reverses a line, dispatch `srs-author` again with `MODE grill-reversal` and the reversals pasted. The session does not edit the file. The writer does not add `grilled:`, `reviewed:`, `status`, or `sources`. Grill edits stay on the last committed version. Do not bump. Do not add a changelog row.
6. After the grill closed or was skipped, ask about `doc-review` the same way. A run or a skip is named in the report. Neither writes `status`, `grilled:`, or `reviewed:` into the file. An SRS handed downstream ungrilled without the user being asked is a failed gate, not a draft; a skip the user chose is not.
7. Report the artifact path, the writer's counts, and what the grill changed, in one line. Then read `pipeline` and follow "Asking before a transition". Do not name a next step from memory.

## Writer (dispatched)

Follow this half only. Do not run `grill-me`, `doc-review`, or `pipeline`.

You settle the SRS. You do not print it. When every decision this
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. A
gap this skill calls BLOCKED returns before that dispatch. Read the
file back. One correction dispatch, then the report. Do not type the
correction, and do not paste the finished SRS into the typist's prompt.

## Scope

**USE this skill when:**
- Any existing description of a product or feature needs an SRS — a business-requirements draft, a note, a ticket, a spec in another shape
- The user states requirements directly, in whatever shape they have
- An SRS for this system already exists and must be updated in place

**NOT for:**
- Deciding what to build, exploring approaches, or resolving open product scope when nothing has been written down — that's `brainstorm`
- Tables, HTTP, layers — `db-schema-design` and `openapi-spec-generator` read this file next; `clean-architecture-design` reads all three later

## Input Resolution

Resolve the source of truth before writing anything:

1. **Explicit path given** — read that file. Headings, language, and format do not have to match this skill's sections.
2. **Text in the chat** — a paste or the recent dialogue. Use it as it is. Do not ask the user to reshape it into the business-requirements shape (`## Goal Capsule`, `## Product Contract`, `R<n>` rows).
3. **Nothing at all** — the orchestrator already stopped. If the packet has no source, return `STATUS BLOCKED`. Do not invent the product.

Extract actors, requirements, and scope from the pasted source. **Never fill a gap by guessing a product decision.** A missing Actor, an unstated NFR, an ambiguous requirement becomes a row in `open-questions.md` beside the SRS, never a silent assumption and never a section of the SRS. A question the skill says to ask before writing the row (a generic actor, a contradiction with an existing requirement) is `STATUS BLOCKED` with that question as `BLOCKER`. Do not ask the user yourself. Silent-filling here defeats the entire point of a formal spec: a downstream reader (or `clean-architecture-design`) treats every line as decided.

## Behaviour, not interface

The SRS says what the system does and what the actor gets, never how the
screen looks or how the actor operates it. The interface is decided
later, by `ui-design` and the designer, and they must be free to decide it
differently. A screen, a button, or a message wording in the SRS reads
downstream as a requirement: it boxes the designer in, and every design
change then forces an SRS edit and a cascade through the contracts.

| Stays in the SRS | Goes out |
|---|---|
| what the actor can do, and what the system does in response | screens, pages, tabs, menus, navigation, the order of steps on screen |
| what information the actor gets or provides — as data: «название и вместимость переговорной», «интервал брони» | controls and gestures: button, field, dropdown, checkbox, click, tap, drag, «нажимает «Отменить»» |
| the rule, the limit, the named error (`BOOKING_OVERLAP`) | the wording of labels, hints and messages the actor reads |
| that the actor is informed, and through which channel when it is outside the product (email, push) | modal, toast, banner, badge, colour, icon, layout, density, look |
| NFR: accessibility level (WCAG 2.2 AA), supported devices and platforms, languages | UX patterns: confirm vs undo, pagination vs infinite scroll, autosave |

Rewrite the binding into behaviour:

- «Пользователь нажимает «Отменить» в расписании» → Триггер: «пользователь отменяет свою бронь».
- «Свои брони помечаются «Моя бронь»» → «система указывает, какие брони в расписании принадлежат текущему резиденту».
- «Тогда показывается тост «Бронь создана»» → «Тогда бронь создана со статусом «активна»».

Interface wishes in the source are not lost and not requirements: put
each in `ui-wishes.md` beside the SRS — one line per wish, quoting the
source and naming the FR or UC it relates to. `ui-design` reads that file
as input and may decide otherwise; the SRS does not change when it does.
A wish that is really a constraint (a legal text that must be shown
verbatim, a mandatory confirmation by regulation) stays in the SRS as a
BR or NFR in behaviour terms, citing the regulation.

## Grill reversals

Do not run `grill-me`. On `MODE grill-reversal`, replace each contradicted line in place — never beside it. Do not set `grilled:`, `reviewed:`, `status`, or `sources`. Do not bump. Do not add a changelog row. When a reversal contradicts an upstream draft, name that in `CONCERNS`; do not silently rewrite the business-requirements document.

## Artifact Root and Resume

Write into `<repo-root>/documentation/requirements/srs/`: `srs.md` — the index and every section the whole product shares — plus `areas/NN-<slug>.md`, one file per capability group with its requirements and use cases (Document Structure → Layout). One living SRS per project; the paths carry no date and no topic name. Resolve `<repo-root>` via `git rev-parse --show-toplevel` (fall back to cwd if not a git repo). Create that folder if missing. Questions go in `open-questions.md` and interface wishes in `ui-wishes.md`, both in that same folder, not into the SRS.

**Resume is increment mode, not a new SRS.** When `documentation/requirements/srs/srs.md` already exists:

1. Read `srs.md` and the area files it lists, and update them in place. A single-file SRS written before this layout is split first, before any change: each capability group's FR rows and the use cases that belong to it go to the group's area file, `srs.md` keeps the rest and gets the two map tables; no id, wording, version or journal row changes. Check it, not by eye: the set of ids and the text of every row and use case are the same before and after. The split is its own commit («docs: SRS разложен по группам»). Do not ask whether to start fresh, and do not write a second SRS anywhere — both files would look current and nothing would say which one the code implements.
2. Read `doc-versioning`. Edit the file in place. This invocation is not a version event: do not change `version`, `updated`, or `## Журнал изменений`. The stamping commit (`doc-versioning`) writes the version and the rows.
3. Keep the path.
4. Keep every existing id. A new row placed between two rows takes a dotted number after the row above (`FR-10.1` between `FR-10` and `FR-11`); a new row at the end of a section takes the next whole number. Never renumber — Document Structure. Name the new ids in the report, and give each new or changed id the change type the edit implies — `добавляет` (a new id), `ломает` (an id whose meaning changed), `уточняет` (same meaning, new wording) — so the stamp can type its changelog rows.
5. When the new feature contradicts an existing requirement, return `STATUS BLOCKED`. It is a product decision, never a silent rewrite.

## Document Structure

Every SRS uses this exact section set and ID scheme. Every id is `<PREFIX>-<n>` with a hyphen: `A-1`, `FR-1`, `NFR-1`, `BR-1`, `UC-1`. Inside one section the numbers are the reading order: the first row is `1`, the next row is `2`, and so on down the section, across capability groups. A later number never sits above an earlier one, and a gap never sits between two rows. The business-requirements draft keeps its own `R<n>`, so an SRS id never collides with a source id.

**An id is permanent; the section still reads in order.** Other documents and the code cite these ids, so a written id never changes number. A row inserted later between two rows takes the number of the row above plus a dotted part: `FR-10.1`, then `FR-10.2` after it; between two dotted rows, one more level (`FR-10.1.1`). A row added at the end of a section takes the next whole number. So a section still reads `FR-10`, `FR-10.1`, `FR-11` from the top, and every citation keeps pointing at the same requirement. A row that no longer applies stays in place, marked deprecated, and keeps its id. A file that already has gaps or out-of-order ids is left as it is — renumbering it would break the citations this rule protects.

```
---
title: <Name> - SRS
date: YYYY-MM-DD
updated: YYYY-MM-DD
version: <версия>
---

# <Name> — SRS

## Журнал изменений

| Версия | Дата | Изменение | Тип | Кого затрагивает |
|---|---|---|---|---|
| <версия> | <дата> | первый выпуск | — | — |

## 1. Кратко
### 1.1 Глоссарий
## 2. Акторы
## 3. Функциональные требования
## 4. Нефункциональные требования
## 5. Бизнес-правила
## 6. Сценарии использования
## 7. Границы
## 8. Допущения и зависимости
```

### Layout

The SRS is one document in several files, so a reader opens the group it
works on instead of the whole product:

```text
documentation/requirements/srs/
├── srs.md               frontmatter and «Журнал изменений»; 1 Кратко (1.1
│                        Глоссарий); 2 Акторы; 3 — the groups table; 4
│                        Нефункциональные требования; 5 Бизнес-правила, all of
│                        them; 6 — the use-case table; 7 Границы; 8 Допущения
├── areas/
│   ├── 01-<slug>.md     one capability group: its FR rows and its use cases
│   └── …
├── open-questions.md
└── ui-wishes.md
```

- **`srs.md` is the map.** §3 holds the table `№ | Группа | Файл | FR`
  (the id range or list); §6 holds `UC | Название | Файл`, deprecated use
  cases included. Every group file and every use case is in them.
- **An area file** has no frontmatter of its own — the version, journal and
  pins are `srs.md`'s — and reads: `# <Группа> — <Name>, SRS`, the line
  «Часть SRS: версия, журнал, акторы, нефункциональные требования и
  бизнес-правила — в `../srs.md`.», then `## Функциональные требования`
  (the §3 table for this group) and `## Сценарии использования` (the §6
  subsections of its use cases).
- **A group** is a capability group of §3. Every FR and every use case
  belongs to exactly one; a use case goes to the group whose FRs its flows
  carry. A new group takes the next `NN`; a group past ~600 lines splits by
  capability, ids unchanged.
- **Business rules stay in `srs.md` §5** — they hold across use cases.
- **Ids are unique across the SRS** and keep the ordering rule above
  inside each file. Citations stay `srs.md@<version>`; a search for an id
  runs over the folder.

`<версия>` is the service version of the open iteration, the name of its `documentation/plans/<version>/` folder (`0.1.0` on greenfield), given in INPUTS. A greenfield SRS is born at it with the one «первый выпуск» row. An increment does not touch `version` or the changelog.

### 1. Кратко

1-3 lines taken from what the source actually says about the product. If the source has a Summary section, carry that shape. If it does not, write the lines from the description you were given. Do not invent scope the source did not state.

### 1.1 Глоссарий

| Термин | Значение в этом продукте |
|---|---|

Define every domain noun used in FR, BR, and UC once, in Russian, and use it verbatim everywhere else — no synonyms, because a second name for the same thing reads downstream as a second entity. Carry terms from `CONCEPTS.md` when it exists; do not redefine them. Actors stay in section 2.

### 2. Акторы

| Идентификатор | Актор | Тип (человек / система) | Что нужно от продукта |
|---|---|---|---|

**Quality rule — no generic actors.** `A-1. User` is a defect, not a placeholder. Every actor is a specific role or system with a distinct relationship to the product ("trial user," "warehouse scanner device," "billing cron job"). If the source material only says "the user," return `STATUS BLOCKED` and ask which specific role in `BLOCKER` — a generic actor propagates ambiguity into every Use Case that references it.

### 3. Функциональные требования

The rows live in their group's area file; `srs.md` §3 holds the groups
table (Layout).

| Идентификатор | Требование | Приоритет |
|---|---|---|

Group by capability (bold inline sub-headers), not by discussion order. Number the rows afterward, top to bottom, `FR-1` then `FR-2`, including across groups. Each requirement is **one sentence of intent plus at most one qualifier** — if a requirement needs two outcomes ("either A or B"), split it or send the fork to `open-questions.md`.

Write each FR in one EARS shape, clauses in this order, so a vague wish like «система должна быть удобной» has no shape to hide in:
- always: «Система должна <реакция>.»
- event: «Когда <событие>, система должна <реакция>.»
- state: «Пока <состояние>, система должна <реакция>.»
- unwanted: «Если <нежелательное условие>, то система должна <реакция>.»
- optional feature: «Где <функция включена>, система должна <реакция>.»

Zero or one trigger and one response. A «Пока» clause joined to a «Когда» is the one qualifier. An event or unwanted FR names the trigger its UC starts from, or the condition of its Exception Flow.

**Приоритет** is `must`, `should`, or `could`, taken from the source or from the user in this run — never guessed. The `must` rows form the first release: every `must` FR, with its use cases, is deliverable and testable without any `should` or `could` row. If the source gives no priorities, write `—` in the cell and add one row to `open-questions.md`, classed «Можно решить при архитектуре» and worded as a question to the user: priority is a product decision, so a later stage asks it and never decides it.

**Completeness check (adapted from INVEST):** before closing this section, check each requirement is *Independent* (doesn't silently depend on another unstated requirement), *Estimable* (concrete enough that `clean-architecture-design` could size it), and *Testable* (a Use Case or Acceptance Criterion downstream can prove it's met). A requirement that fails Testable gets an AC gap flagged, not a pass.

### 4. Нефункциональные требования

| Идентификатор | Категория | Требование | Как проверяется |
|---|---|---|---|

Fixed category checklist — every category gets a row or an explicit «Не применимо» row with a one-line reason. Write the category cell in Russian. Do not skip a category silently:

- **Производительность** (latency, throughput)
- **Надёжность и доступность**
- **Безопасность** (see sub-checklist below — always expands to more than one row)
- **Масштабируемость**
- **Соответствие и аудит**
- **Наблюдаемость**

Stack constraints belong here only as limits, not as a chosen framework:
team language, "this repo already runs X", hosting, latency that rules a
runtime out. Do not write "use Nest" / "use FastAPI" unless the source
material or the user already committed to that name. The stack itself is
proposed and picked later, during architecture.

When a Use Case's flow touches one of these categories materially (an error path that must be logged, a step with a latency-sensitive user wait), cross-reference it: the Use Case's Exception Flow or step cites the specific NFR-ID, not just the category name.

#### Security sub-checklist (fill per applicable item, one NFR-ID row each)

"Security" is never a single row — treat it as its own fixed checklist, one row per sub-item, each with its own NFR-ID. This table is the **declared security baseline for the whole pipeline**: the architecture turns each row into a decision, and `code-review-full`'s security lens verifies the shipped code against it row by row. Nothing downstream re-derives these requirements, so a sub-item left unaddressed here is a requirement the code will never be checked against.

The eleven sub-items and what each row must state are in `references/security-checklist.md` — read it before writing §4, on every SRS.

Mark a sub-item «Не применимо» with a one-line reason when the product genuinely has no surface for it (e.g., no LLM component) — never omit the row silently, and never leave a sub-item unaddressed just because the source material didn't mention it: send it to `open-questions.md`, or return `STATUS BLOCKED` when the row cannot be written without the answer. Do not skip it.

### 5. Бизнес-правила

| Идентификатор | Правило | Когда применяется |
|---|---|---|

Rules that hold across Use Cases, not scoped to one — cross-cutting invariants. Quote the rule; don't summarize it. `db-schema-design` reads this table and turns a rule SQL can express into `CHECK`, `UNIQUE`, or `FK`. `clean-architecture-design` later copies that choice and puts the rest on an entity method. State the rule precisely: a vague rule becomes either a wrong constraint or a gap.

### 6. Сценарии использования

The subsections live in their group's area file; `srs.md` §6 holds the
use-case table (Layout). One subsection per use case:

```
### UC-<n>. <VerbPhrase>

**Актор:** A-<n>   **Предусловие:** ...   **Триггер:** <intent or event, not a gesture: «резидент отменяет бронь», not «нажимает «Отменить»»>

**Основной поток**
1. ...
2. ...

**Альтернативные потоки**
- **Alt-1** (ответвление на шаге N): ...

**Потоки исключений**
- **Exc-1** (на шаге N, условие): ответ системы ...

**Постусловие:** ...

**Критерии приёмки**
- **AC** (основной поток): Дано ... [и Дано ...] Когда ... Тогда ...
- **AC-Alt-1**: Дано ... Когда ... Тогда ...
- **AC-Exc-1**: Дано ... Когда ... Тогда ...
```

**Finding the Alt/Exception flows systematically** — don't rely on recall; check each Use Case against these categories and only include the ones that actually apply (an empty category is silently skipped, not stated as empty):
- **Happy path** → the Main Flow.
- **Edge cases** (boundary/unusual-but-valid input, empty states, concurrent access) → Alternative Flows.
- **Error scenarios** (invalid input, dependency failure, permission denial) → Exception Flows.
- **Security-sensitive steps** (auth check, data exposure, permission boundary) → an Exception Flow if a rule is violated, citing the specific Security sub-checklist NFR-ID it maps to (e.g. "per NFR-4, authorization / object-level access control") — not a generic reference to "the Security category."
- **Performance-sensitive steps** (a step the user waits on, a bulk operation) → cross-reference to the Performance NFR row; only a new flow if a timeout/degradation path exists.

**A Use Case is warranted only when its Functional Requirement has conditional behavior.** Not every FR needs a Use Case (a static/unconditional FR doesn't), and never invent a Use Case with no FR behind it. The direction is FR → Use Case, never the reverse.

**Acceptance Criteria discipline (Given/When/Then):**
- **Multiple `Given`s are fine** — preconditions stack ("Given I'm logged in" + "Given my cart has items").
- **Exactly one `When` and one `Then` per scenario.** If a scenario needs a second `When` or `Then`, it is actually two scenarios — split it into its own Alt or Exception entry rather than chaining conditions.
- **`Then` must be observable and measurable** at the system's edge: a state, returned data, a named error, a sent message, a time. "Then the user has a better experience" is a defect, and so is "Then the page shows a banner" — that is the interface (Behaviour, not interface). Write what changes or is returned ("Тогда бронь в статусе «отменена»", "Тогда ответ приходит за 2 с").
- One AC per flow: the Main Flow's AC, plus one AC per listed Alt and per listed Exception — never a separate freestanding AC section disconnected from a flow.

### 7. Границы

Taken from whatever the source marks as out of scope. If the source has a Scope Boundaries section, carry it, and add a boundary only when this dialogue stated one. If the source has no such section, write only boundaries it actually stated; unspoken boundaries go to `open-questions.md`.

### 8. Допущения и зависимости

Anything load-bearing that isn't itself a requirement: an external system's guaranteed behavior, a library assumed available, a decision deferred to another team.

The SRS has no open-questions section. Gaps this SRS could not settle, and a finding the user deferred, are rows in `open-questions.md` in this file's folder. Class each row `Блокирует старт` or `Можно решить при архитектуре` or `Отложено`. Never leave a row unclassified.

## Writing Discipline

- **Russian.** Write the SRS in Russian, including every section heading and every table column in Document Structure. Do not translate ids (`A-`, `FR-`, `NFR-`, `BR-`, `UC-`, `AC-`, `Alt-`, `Exc-`) or the priority tokens `must` / `should` / `could`. Frontmatter keys stay English.
- **Plain language.** Write requirements and acceptance criteria so a new team member understands them without a glossary lookup — jargon that isn't already a defined domain term (per section 1.1, or `CONCEPTS.md` if it exists) gets spelled out once.
- **Cite, don't restate.** A rule that lives in a Business Rule or a Non-Functional Requirement is referenced by ID from a Use Case step (`per BR-3`), never copy-pasted into the flow text — one owner per rule, same discipline as the business-requirements document.
- **No process exhaust.** No "captured at step X" notes, no italic provenance lines. Metadata lives in the frontmatter only.

## Quality Gate (run before declaring the SRS done)

1. **Traceable** — every conditional FR has a Use Case; every Main / Alt / Exception flow has exactly one AC with one `When` / `Then` — §6.
2. **No generic actors** — §2.
3. **NFR complete** — six categories and every Security sub-item have a row, filled or «Не применимо» with a reason — §4.
4. **IDs are ordered and permanent** — a new SRS numbers each section `PREFIX-1`, `PREFIX-2`, … down the page with no gap; on an increment no existing id changed, an inserted row has a dotted id after the row above (`FR-10.1`), and a row at a section's end has the next whole number — Document Structure.
5. **No invented decisions** — every requirement, actor, and rule traces to the source or to the user's answer in this run — Input Resolution.
6. **Grill** — not this pass, unless `MODE` is `grill-reversal`. The orchestrator checks that the grill ran or that the user declined. The file has no `grilled:` field.
7. **Consistent as a set** — read every FR, NFR, BR, and UC together, not one at a time; two requirements can each make sense and still be jointly impossible. No NFR bound contradicts an FR or a flow step (a synchronous step that waits on a third party vs. a p95 bound it cannot meet). No Scope Boundary excludes what an FR or UC includes. Every domain noun a requirement uses is in section 1.1 or is an `A-`/`BR-`/`UC-` id.
8. **Unambiguous** — no FR, NFR, BR, or `Then` rests on an unbounded word: «быстро», «удобно», «большой», «надёжно», «безопасно» (alone), «при необходимости», «по возможности», «и т.д.», «и/или», «все»/«никогда» without a scope, superlatives, or a negative-only statement. Replace each with a number, a named condition, or an observable result taken from the source. When the source has none, move the item to `open-questions.md`. An NFR row whose «Как проверяется» cell names no measurement fails this check.
9. **Source covered** — check 5 runs from the SRS back to the source; this one runs the other way. Walk the source once more, item by item: every requirement, rule, acceptance example, scope line, and stated quality (limits, numbers, tone). Each lands on an SRS id, in Scope Boundaries, in `open-questions.md`, or — an interface wish — in `ui-wishes.md`. When the source is a `brainstorm` document, every source `R<n>` and `AE<n>` is reachable that way. An item dropped silently fails this check.

10. **Mapped** — `srs.md`'s groups and use-case tables list every area file and every use case; every FR and every use case sits in exactly one area file — Layout.
11. **No interface** — no FR, UC step, trigger, or `Then` names a screen, a control, a gesture, a message wording, or a visual; each such line is rewritten as behaviour or moved to `ui-wishes.md` — Behaviour, not interface. On an increment, check the rows this pass touched; interface wording found in untouched rows goes to `CONCERNS`, not a silent rewrite.

Fix formatting failures in place. If a fix requires a product decision, return `STATUS BLOCKED` rather than deciding it here.

## Closing

Return the report in `executor-catalog/references/srs-writer-prompt.md`. Do not offer a next stage. The orchestrator does that after the grill.
