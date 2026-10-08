---
name: docs-consistency
description: >-
  Checks that the finished documentation set agrees across documents — SRS,
  DB schema, OpenAPI, architecture, domain model, scenarios and screen specs
  read together: every requirement has a home, nothing exists without a
  requirement, and every shared name, field, enum, limit, status, error and
  role means the same thing. Use where the two pipeline branches meet,
  before `plan`, or when the user asks whether the documents agree. Not a single-document review (`doc-review`) or a
  plan review.
---

# Docs Consistency

Each contract passes its own `doc-review` when it is written. That review
reads one document against itself and, for the architecture and the UI
spec, checks that a cited table or `operationId` exists upstream. Nothing
reads the set as a whole. The defects that survive are the ones between
documents: an FR with no operation, a screen that sends a field the API
does not accept, a `CHECK (amount > 0)` the SRS says is `≥ 0`, a 409 the
architecture maps to an error the OpenAPI never declares, an enum with
four values in the schema and three in the UI. Each document is fine on
its own; `work` finds the contradiction in code, where it costs a unit and
a review.

This skill is that whole-set pass, once, after the last contract is
written and before a plan is cut from the set. Write findings and the
report in Russian. Do not translate ids, `operationId`s, table and column
names, paths, or the `Verdict:` line (`doc-versioning` → Document
language).

## Not this skill's job

| Not here | Owner |
|---|---|
| Whether one document agrees with itself, is feasible, is right | `doc-review` |
| How serious a pin behind its source is — stale, behind, refresh | `doc-versioning` → Staleness and cascade. This skill reads the verdict: stops on stale, checks homes on behind |
| Whether the plan covers the documents | `plan-review` |
| Editing a contract beyond an aligned name (see Step 4) | the stage that owns the document |
| Whether code matches the documents | `code-review-full` |

## Inputs

Find the set by `doc-versioning` → Registry, in chain order (paths under
`documentation/`):

| Document | Required |
|---|---|
| SRS `requirements/srs/srs.md` | **yes** — without it there is nothing to trace to; say so and stop |
| DB schema `db/schema.md` (+ the migration files in `db/migrations/`) | when stage 3 ran |
| OpenAPI `api/openapi.yaml` | when stage 4 ran |
| `architecture/architecture.md` (its diagrams embedded), `architecture/domain.md`, `architecture/scenarios/<area>/<area>.md` of every area | when stage 5 ran |
| `ui/frames-register.md` and every `ui/screen-specs/S-<n>-*.md` | when stage 8 ran |
| Business requirements, `ui-wishes.md` | no — the SRS absorbed the first; wishes are never grounds for a finding |

At least two contracts besides the SRS, or there is no set to check: say
so and stop. A skipped stage is not a gap — read the stage's skip line
(no storage, no HTTP, no screen) from the SRS or the stage reports and
pass it to the checker, so it does not report missing screen specs on an
API-only service.

Several candidates for one row: stop and ask, as `doc-versioning` →
Registry says. Never pick one.

## Workflow

### Step 0. The version folder

The report lives in the open `documentation/plans/<version>/` (no
`summary.md`). The iteration is normally already open — its first stage
that changed a versioned document opened it. Only when no folder is open
does this stage open it, per `pipeline` → Service version (the number with
its level and reason, asked as a question; the folder created on the
answer). `plan` then reuses it.

### Step 1. Pins first

Read every `sources:` pin in the set (`info.x-sources` in OpenAPI), as
`path@<version>` (a legacy `@vN` per `doc-versioning` → Moving from the old
numbers). For each pin behind its source's `version`, read the source's
changelog rows after the pin (`doc-versioning` → Staleness and cascade):

- **any «ломает» → stale.** A P1 finding owned by the dependant, axis
  «Pins»: `document → source@<pin> (current <version>): ломает <tokens>`,
  with the stage that re-derives it. When any pin is stale, write the
  report with those rows as the findings table, the earliest owner in
  chain order first, and stop with `Verdict: RETURN_TO_STAGE` before the
  dispatch: checking a stale document against its newer source reports the
  cascade the stage was going to do anyway.
- **only «добавляет» → behind.** Not a finding. Collect the new tokens from
  those rows into NEW TOKENS for the checker, which checks that each has a
  home in the dependant or the document that should hold it.
- **only «уточняет»** — nothing; the dependant's next stamp refreshes the pin.

**Then the test cases' trace**, when the set has user test cases: run
`python3 ${CLAUDE_SKILL_DIR}/../ui-test-cases/scripts/check_trace.py --docs documentation --quiet`
and fix what it finds before the dispatch, without asking: dispatch
`ui-test-writer` (`ui-test-cases` → its writer packet, `MODE increment`)
with the broken cases, to rewrite each one's trace from the current spec,
then run the script again. What a rewrite cannot fix — the case needs an
element, a frame or an operation the documents no longer have — is a P1
finding, axis «Трассировка», owned by the screen spec's stage or by
`ui-test-cases` when the case itself is wrong. A hand edit of a case is
caught here as surely as the agent's own.

### Step 2. Dispatch the checker

Resolve `docs-consistency-checker` through `executor-catalog` and
dispatch it under that file's Dispatch contract, without asking which
model. One dispatch for the set. Build the packet from
`references/checker-prompt.md`: document paths (the checker reads the
files itself — do not paste them), the skip lines, NEW TOKENS from Step 1,
and the prior report's findings on a re-check.

Do not run the matrix on the session model to save the dispatch: reading
the whole set end to end is the volume the row exists to carry.

A reply not in the packet's format is re-dispatched once with the format
restated. A second off-format reply ends the check as not done: say so,
and do not write a `PASS`.

### Step 3. The matrix the checker runs

Every axis below runs when both of its documents exist. An axis whose
document was skipped gets one line saying so.

| Axis | Checks |
|---|---|
| **SRS → downstream** | every FR / UC has an operation (HTTP), a scenario (scenarios of its area) and, when a human does it, a screen element (screen specs); every entity the SRS stores has a table; every BR has an invariant row (domain model) or a constraint; every NFR with a number or a security rule has a foundation §1 row or a schema / API mechanism |
| **Downstream → SRS** | every table, operation, scenario and screen traces to an SRS id. An orphan is scope the SRS never asked for, or a requirement the SRS is missing — the finding says which is likelier |
| **Schema ↔ OpenAPI** | field names, types, nullability vs `required`, enum values, lengths and ranges, uniqueness ↔ a 409, id format, money and time representation |
| **OpenAPI ↔ screen specs** | every `operationId` a screen cites exists and fits the action; every field in «Метод и поля» exists in that operation's request or response; input rules ↔ request schema (required, limits, enum options); every declared status of every operation a screen calls has a row in «Ошибки ответов»; data a screen shows that no response returns is a P1 owned by the API or the design |
| **Domain model ↔ the rest** | every invariant row cites an SRS BR and matches the schema constraint it names; named errors ↔ OpenAPI error codes; entities ↔ tables |
| **Scenarios ↔ the rest** | every scenario cites an operation that exists and only ports the foundation declares; every rule it relies on is an invariant row (cited, not restated); its errors are named errors of the domain model; roles ↔ SRS actors ↔ OpenAPI `security`; tenancy ↔ schema columns and RLS |
| **One meaning per word** | the same concept has one name across the set, and the same number (a limit, a timeout, a page size, a retention period) has one value |
| **No visual binding** | no SRS, schema, API or architecture document names a widget, a presentation (modal, toast, side panel), layout, colour, icon, or a narrow-width layout change (`doc-versioning` → What, not how it looks). A binding is a P1 owned by the document that holds it; the fix rewrites it as behaviour. Screen specs and the frames register are exempt: they are written from the frames |

Where the set already fixes a convention, the checker reads that, not a
generic rule: the error envelope, the case of JSON fields, the collection
shape. A convention two documents state differently is itself a P0.

### Step 4. Judge the findings

| Level | Meaning |
|---|---|
| **P0** | two documents state different facts about the same thing: a type, a nullability, an enum, a limit, a status, a rule. `work` would implement one and contradict the other |
| **P1** | a gap: a requirement with no home where its stage ran, an orphan with no requirement, a user-caused error with no screen state |
| **P2** | naming drift that does not change behaviour: a synonym, a label that differs from the SRS term. A field, `operationId`, status, or enum value that differs is never P2 — code built from it sends or expects the wrong thing |
| **P3** | nit |

Each finding names its **owner** — the document that should change. The
default owner is the downstream one: the SRS is the contract the others
follow. The owner is upstream when the downstream document is plainly
right and the upstream forgot it (an SRS that never mentions a field
every later document needs), and then the finding says why.

Two dismissal rules, each written in the report:

1. **A recorded decision.** A downstream document that departs from
   upstream and says why (an assumption `A-n`, a changelog line) is not
   a contradiction. A recorded **upstream gap** is different: an
   open-questions row that says another document is wrong or silent
   (`upstream gap: db-schema-design`) is a finding owned by that
   document, because nothing else routes it to its stage. So is a row
   that hands a check to this skill or to another document («должен
   совпасть», owner `docs-consistency`): check it, never dismiss it. A
   recorded decision never dismisses a missing part of the system — screen
   specs exist and the architecture leaves the client «вне документа» is a
   P1 owned by the architecture.
2. **A skipped stage.** No screens on an API-only service is not a gap.

Fixes. This skill edits one kind of thing only: a P2 name in the
downstream document aligned to the upstream spelling when there is
exactly one correct answer. Everything else goes back to the owner
stage, because a contract a checker silently rewrote is no longer a
decision anyone made.

### Step 5. Verdict

Exactly one:

| Verdict | When | Next move |
|---|---|---|
| `PASS` | no P0 / P1 | the next transition per `pipeline` |
| `RETURN_TO_STAGE` | P0 / P1 whose fix is the owner stage's job, or a stale pin (Step 1) | name the **earliest** owner stage in chain order, with its findings — a later stage's fix may depend on it. Ask to run it per `pipeline` → "Asking before a transition"; after it, re-run this check |
| `STOP` | a contradiction only a product decision closes: two readings of the SRS, both reasonable | one question to the user per `grill-me` → "How a question is shown"; the answer is a changed decision — it goes to the SRS and every document that states the other reading, committed at once with no version change (`pipeline` → `references/decision-changes.md`), then the check re-runs. A fix that would reverse a decision a document made on purpose is asked the same way, with that decision quoted, never applied as a fix (`pipeline` → `references/decision-changes.md` → A finding against a settled decision) |

A re-check reads the whole set again, not only the changed document: a fix
in the schema can open a gap in the API.

## Report

Write `documentation/plans/<version>/docs-consistency.md`, overwriting any
earlier one of this version. The first line is the verdict alone;
`pipeline` reads it as the gate. The `checked:` block pins each document
path by its blob hash
(`git hash-object <path>`), because contracts are edited in place and
several commits of one iteration share one version: a hash that no longer
matches the file means the check is stale.

```markdown
Verdict: RETURN_TO_STAGE

checked:
- documentation/requirements/srs/srs.md 3f2a91c
- documentation/db/schema.md 8be0d14
- documentation/api/openapi.yaml 51c7e02
- documentation/architecture/architecture.md 0d4e6c8
- documentation/architecture/domain.md 77a1c20
- documentation/architecture/scenarios/invoices/invoices.md 4c9e118
- documentation/ui/frames-register.md 1d0a5f3
- documentation/ui/screen-specs/S-3-invoice.md a90f3b7
skipped: none

## Согласованность документации — 2026-05-09 — RETURN_TO_STAGE

| # | Sev | Ось | Где | Находка | Владелец | Правка |
|---|---|---|---|---|---|---|
| 1 | P0 | Schema ↔ OpenAPI | `invoices.amount_cents` · `Invoice.amount` | в схеме `CHECK (amount_cents > 0)`, в OpenAPI `minimum: 0` | OpenAPI | `minimum: 1`; SRS BR-4 говорит «больше нуля» |
| 2 | P1 | SRS → downstream | FR-7 | «отмена счёта» есть в SRS и в архитектуре (`CancelInvoice`), операции в OpenAPI нет | OpenAPI | добавить `cancelInvoice` |
| 3 | P1 | OpenAPI ↔ screens | S-3 · «Ошибки ответов» | `payInvoice` отвечает 409 `INVOICE_ALREADY_PAID`, в ТЗ экрана нет исхода для этого кода | ТЗ экрана | строка «409 → …» и состояние на макете |
| 4 | P2 | One meaning per word | SRS «плательщик» · сценарии «клиент» | одно понятие, два слова | Сценарии | исправлено здесь: «плательщик» |

**Первый владелец** — `openapi-spec-generator` (#1, #2), затем `screen-spec` (#3).
**Исправлено здесь** — #4.
**Отклонено** — FR-12 без экрана: в SRS это задача по расписанию, UI не нужен.
**Оси без находок** — Architecture ↔ the rest, Downstream → SRS.
```

## Before you finish

- Every pin was read before dispatch; a stale one («ломает» after the
  pin) stopped the check as a finding for the dependant, and every
  «добавляет» behind a pin went to the checker as a new token — Step 1.
- Every axis has findings, a clean line, or a skip line — Step 3.
- Every finding has an owner, and the earliest owner is named — Steps 4–5.
- Only P2 names were edited, only in the downstream document — Step 4.
- `documentation/plans/<version>/docs-consistency.md` exists with `Verdict:`
  on line 1 and a hash per document path checked — Step 0, Report.

## References

- `references/checker-prompt.md` — the packet and the reply format.
- `executor-catalog` — the `docs-consistency-checker` row.
- `doc-versioning` → Registry (paths), Staleness and cascade (pins).
- `pipeline` — where this gate sits. When a stage invoked this check,
  report and return; when the user opened it directly, ask the next
  transition per `pipeline` → "Asking before a transition".
