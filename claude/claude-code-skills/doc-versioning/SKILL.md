---
name: doc-versioning
description: >-
  The convention for evolving project documents: one canonical file per
  type, edited in place in Russian, stable ids, a `version` that names the
  service release the document last changed in, changelog rows typed
  ломает / добавляет / уточняет, `sources:` pins as `path@version`, all
  stamped only in a commit the user asks for. Use when a feature lands on a
  system that already has requirements, API, DB, UI, architecture or plan
  documents, when asked to version or publish documents, or to find stale
  citations. Read by the writer stages as a reference; it does not write
  the contract body.
---

# Document Versioning

A second feature is not a second product. When documents already exist, the
pipeline runs the same path — requirements, DB, API, architecture, mockups, screen specs, plan —
but each stage **evolves its document** instead of writing a new one beside it.

The reason is citation integrity. Architecture cites `SRS UC-2`; a plan cites
`scenarios/<area> <UseCase>`; a review dismisses a finding because `Docs` said so. A second SRS
for the same system breaks every one of those references silently: both files
look current, and nothing says which one the code implements.

So: **one canonical document per type per system, edited in place.** Its
`version` is the service release (`pipeline` → Service version) in which
the document last changed, and it is a claim that a commit published that
change — not that a writer ran, not that a gate polished a draft, and not
that the file was saved. Every correction before that commit stays on the
last committed number.

## Document language

Every artifact this collection writes is in **Russian**: prose, titles,
explanatory table cells, changelog bodies, grill questions, review
findings, architecture rationale, OpenAPI `description` / `summary` /
`example`, DBML `Note` / `COMMENT ON`.

Do not translate **cited tokens**: ids (`UC-1`, `FR-2`, `A-n`), table and
column names, `operationId`, paths, type names, file paths, stack
identifiers. They stay as the design named them.

**Frozen headings stay as the stage skill names them.** Frontmatter keys
(`version`, `migration`, `sources`, `grilled`) stay English. The DB schema
freezes `## Changelog`; every other versioned document `## Журнал
изменений`, all with the same five Russian columns; a plan has none. SRS
and architecture freeze their Russian headings in `srs-writer` and
`clean-architecture-design` (`## 1. Кратко`, `## 1. Состав системы`, …).
Translating a frozen heading breaks parsers and citations.

**Report shapes are frozen the same way.** Review and run reports print a
template. Its headings, verdict tokens, and fixed lines stay exactly as the
template writes them: `Verdict: PASS`, `## Plan review — <path> — <verdict>`,
`### Review U<n> — <verdict>`, `## Full-plan review — <path> — <verdict>`,
`## Document Review Results`, `### Coverage`, `Review complete.` Only the
prose inside is Russian. This matters for two reasons. `work` and `pipeline`
read `Verdict:` as a gate, and a missing line means the gate did not pass. Later
stages and the user find a report by its heading, so a translated heading
reads as a missing report.

This rule is the artifact, not the skill file and not the source code.

## What, not how it looks

Every contract written before the mockups — SRS, DB schema, OpenAPI, the
architecture foundation, the domain model, the scenarios —
describes **what** the product does and holds: actions, data, rules,
states, outcomes, and what each text must convey. None of them records a
visual or UX-pattern decision, or the exact wording of a label or a
message: a widget (button, dropdown, context menu,
tabs), a presentation (modal, side panel, own page, toast, banner),
layout, density, colour, icon, size, or how a layout changes at a narrow
width. Those are decided on the Figma frames by `ux-patterns`, by the
skill or by a designer, and they change often. A contract that names
one has to be edited every time the designer decides differently, and
it silently overrules the designer until it is.

| In the contract | On the frame only |
|---|---|
| «резидент отменяет свою бронь» — an action | a button, a menu item, a swipe; its label «Отменить» |
| «выбор одной переговорной из списка» — input of a kind | dropdown, radio group, segmented control |
| «вложенный шаг M1 «Отмена брони»» | modal, side panel, separate page |
| «сообщение об успехе (смысл: бронь отменена)», «ошибка у поля» | toast, banner, inline line above the table; the wording «Бронь отменена» |
| «для каждой брони: переговорная, дата, время» | table, cards, list rows |
| «поддерживаемые ширины: 1280+ и 375» | table → cards at 375 |

Each writer names this rule in its own terms; `doc-review` checks it on
every type; a binding found later is rewritten as behaviour, and the
visual choice stays on the frame.

Two documents are exempt because they are written **after** the mockups
and describe them: the frames register and the screen specs (`screen-spec`).
They cite frames, variants and the wording from the frame's «Тексты»
table — by reference, never by describing colours or sizes in words.
`ui-wishes.md` is input to the design, never a contract: a frame or a
document that departs from a wish is not a discrepancy anywhere.

## Which mode am I in

Before writing anything, look for the canonical document for this stage
(registry below). Then:

| Found | Mode | What the stage does |
|---|---|---|
| nothing | **greenfield** | the writer skill creates the file at `version: <iteration version>` — the open `plans/<version>/` folder's name, `0.1.0` on a new product — with one «первый выпуск» row typed «—». The gates that follow leave both alone |
| a document for this system | **increment** | edit that file in place. Leave `version`, `updated`, and the changelog untouched — writer, grill, and review alike. Grill still sets `grilled:` and review sets `reviewed:` when its gate closes, except on an SRS, which has neither field. `doc-versioning` types the changes once, when the user invokes it. An unversioned row (Registry): edit in place, no rows, no version |
| a document for a *different* system in the same repo | greenfield for this system | monorepo: canonical path is per system, not per repo — each system has its own `documentation/` tree |
| several candidates | **stop and ask** | never guess which one is canonical — picking wrong makes the real one stale invisibly. Follow `grill-me` → "How a question is shown": explain each file in the chat, one question, then stop |

Increment mode is the default in any repo with a `documentation/` tree. A
stage that writes `documentation/requirements/billing-srs/` while
`documentation/requirements/srs/srs.md` already exists has failed this
check, not "kept history".

### When a version is born

Read `references/version-birth.md` when this run may create a document's
first version or stamp a new one.

### Commits that are not stamps

Two commits of a contract document need no request from the user and stamp
nothing: the move of a single file into its split layout (the stage that
splits it), and a decision changed after the document was finished
(`pipeline` → `references/decision-changes.md`). Both leave `version`,
`updated`, `info.version`, the changelog and the pins as they were. The
next stamp compares each document with its last stamped state, not with
`HEAD`, so the changes these commits carry get their rows then.

## Registry

| Document | Canonical path | ID namespaces to preserve | Downstream |
|---|---|---|---|
| Business requirements | `documentation/requirements/business-requirements/business-requirements.md` | R (product) — **unversioned** | SRS (offer; not a version cascade) |
| SRS | `documentation/requirements/srs/srs.md` — the index, one version and journal — and `areas/NN-<slug>.md`, one per capability group | A · FR · NFR · BR · UC · AC | DB schema, OpenAPI, domain model, scenarios, mockups (`ui-design`) |
| Interface wishes | `ui-wishes.md` beside the SRS | none — **unversioned**; one line per wish with its source quote and FR/UC | `ui-design` reads it as input; never a contract, never grounds for a finding |
| DB schema | `documentation/db/schema.md` — DBML and notes, the whole current schema, no SQL; ER `diagrams/er.d2` / `.svg` beside it | table and column names | OpenAPI, domain model, plan. Not the design branch |
| Migrations | `documentation/db/migrations/NNNN_<snake_slug>.sql` (`0001_init.sql`, …) | none — **unversioned** files, never edited after commit; the schema document carries the version and names the last file it covers in `migration:` | the application's migration tool runs them from this folder |
| OpenAPI | `documentation/api/openapi.yaml` — the root, one version — and the `paths/` and `components/` files it references | `operationId` · schema names — `info.version` is the service version, or the contract's own SemVer when the API has external consumers (`pipeline` → Service version) | scenarios, screen specs, plan, generated clients |
| Architecture — foundation | `documentation/architecture/architecture.md`; its D2 views in `diagrams/` beside it, embedded in the sections they illustrate | module and area names · port signatures · assumptions `A-n` | scaffold when the tree or stack moved, scenarios that use a changed port, plan |
| Domain model | `documentation/architecture/domain.md` | entity and value-object names · invariant rows · named errors | scenarios that cite a changed rule, plan |
| Scenarios of an area | `documentation/architecture/scenarios/<area>/<area>.md`; key-scenario diagrams `diagrams/<use-case-kebab>.puml` (PlantUML) / `.svg` beside it | use-case names | plan |
| Frames register | `documentation/ui/frames-register.md` | screen ids `S-n` · nested-step ids `M-n` — **unversioned**; Figma file, product type, widths, accessibility target, frame `nodeId`s | screen specs of changed screens |
| Screen spec | `documentation/ui/screen-specs/S-<n>-<screen-slug>.md`, one per screen | element numbers · `operationId` cites | UI test cases, plan |
| UI test cases | `documentation/ui/test-cases/` — `README.md` and one file per section | `TC-` ids, across the set — **unversioned**, `README.md`'s `sources:` pins the SRS and the screen specs | `ui-test-cases` mode run; the E2E suite |
| Project map | `documentation/project-map/project-map.md` | none — index, **unversioned** | nobody; `repo-scaffold` writes it |
| Deploy document | `documentation/deploy/deploy.md` | none — **unversioned**; derived from `docker-compose.prod.yml` and `.env.example`, kept true by `deploy-topology`'s sync test | the operators, as `release/<version>/DEPLOY.md` |
| Implementation plan | `documentation/plans/<version>/plan.md`, one folder per service version | U-ids, per plan | the `work` skill |
| Plan review | `plan-review.md` in the version folder | none — a check result, **unversioned**; first line `Verdict:` | `plan`, `work` and `pipeline` read it |
| Plan progress | `progress.md` in the version folder | none — a view of git, **unversioned** | nobody; `work` updates it as each unit lands |
| Docs consistency report | `docs-consistency.md` in the version folder | none — a check result, **unversioned**; first line `Verdict:`, a `checked:` hash per document path | nobody; `docs-consistency` overwrites it, `pipeline` and `plan` read it |
| UI test run | `test-run.md` in the version folder (last run; a `Verdict:` line under the cases table) | none — **unversioned** | nobody; `ui-test-cases` mode run overwrites it |
| Iteration summary | `summary.md` in the version folder; its presence closes the version | none — **unversioned**; numbers from the stage reports, plus the user's escaped-defects and interventions tables | nobody; `pipeline` writes it at the end of an iteration |

Everything under `documentation/plans/` — plan, plan review, progress, the
stage reports and the summary — is out of git (`.gitignore`); see `pipeline` →
Plans stay out of git.

Several UI products (client and admin) put the same `ui/` content in
`documentation/ui/<product>/`; one product keeps it straight in `ui/`.

Paths carry no date and no project or topic name — the repository already
names the project. Do not rename a file on a stamp: the path is what every
citation points at.

**Unversioned rows** — business requirements, the diagrams, the migration
files, the frames register, the test cases, the project map, the plan
folder's reports, and each document's `open-questions.md` — are working
material, not contracts: no `version`, no changelog, no typed rows;
`updated:` moves on every write; downstream `sources:` cite them by path
with no `@<version>`, so no pin, stale banner, or cascade applies. All of
that is for the contracts — SRS, OpenAPI, DB schema, the three architecture
documents — and the screen specs.

**Two rows behave differently:** a plan is never versioned — each service
version is a **new plan folder**, with no `version` and no changelog — and
the database changes only by **appending a migration file**. Read
`references/exceptions.md` when the document is a business-requirements
draft, the project map, a diagram, a plan, or a DB schema — it holds each
one's own rules.

## One folder per document

A document's file is named like its folder (`requirements/srs/srs.md`,
`scenarios/bookings/bookings.md`), with no date and no topic. The
exceptions are the Registry's own: a plan folder is named by the service
version; screen specs sit one file per screen in `ui/screen-specs/`; files
beside a folder's main document keep their own names (`domain.md`,
`open-questions.md`, `ui-wishes.md`, `schema.md` with `migrations/`,
`openapi.yaml`, `frames-register.md`); test cases sit in `ui/test-cases/`,
one file per section beside its `README.md`. Diagrams sit in a
`diagrams/` subfolder next to the document that shows them, created only
when it has something. None of these is a second document — nor are the
files a large document is split into: the SRS's `areas/`, the OpenAPI
`paths/` and `components/`, the test cases' section files. Each set is one
document with one version (where it has one) and one journal, kept in its
index file — `srs.md`, `openapi.yaml`, `test-cases/README.md`.

## Открытые вопросы

Every open question for a document goes in `open-questions.md` in that
document's folder. The H1 is `# Открытые вопросы`. The contract file has
no open-questions section: not SRS `## 9`, not a screen spec section, not a plan
`## 6`, not an architecture section, not `## Deferred / Open Questions`.

The file holds writer gaps and questions the user deferred (`отложи`,
`потом`, Defer, option C). It is not a contract and it has no `version`.
Appending a row does not stamp the document beside it.

```markdown
# Открытые вопросы

Не источник поведения. Контракт — соседний файл.

| Вопрос | Класс |
|---|---|
| … | Блокирует старт / Можно решить при архитектуре / Отложено |
```

Create the file when the first question appears, never empty, in the
document's folder — not one shared `documentation/open-questions.md`:
`requirements/srs/`, `db/`, `api/`, `architecture/` (foundation, domain
model and scenarios), `ui/`, and `plans/<version>/`.

## What a version is

A document's `version` is the service release in which it last changed:
created or changed in iteration `1.2.0`, it reads `version: 1.2.0` once the
commit stamps it; documents the iteration did not change keep theirs. No
per-document counter. What changed and who has to follow, the changelog
says — one row per change, typed once at the stamp, the same four ways on
every **versioned** registry row.

A **cited token** is anything downstream documents or code name: the
registry's ID namespaces, plus the types, shapes, and rules those ids
carry (a column type, an AC's Given/When/Then, an `operationId`'s
request body).

| Type | Criterion | Dependants |
|---|---|---|
| **ломает** | a cited token (id, operation, field, column, port, rule…) removed, renamed, or changed in meaning / type / shape — something other documents or code already rely on | must update: the cascade |
| **добавляет** | a new cited token; everything that was true stays true | check where the new thing belongs: `docs-consistency` |
| **уточняет** | different wording of the same meaning | not affected |
| (no row) | explanation, typo, formatting, a comment on an existing token | none — the `version` does not move |

The type has to match the change in both directions: «ломает» for a
rewording trains people to ignore the column, and «уточняет» for a changed
contract hides breakage. The service level is computed from these rows
(`pipeline` → Service version), so a mistyped row also mislabels the
release.

### How to type a change

1. List every cited token the diff touches.
2. Removed, renamed, or changed in meaning / type / shape → **ломает**.
   Tightening counts: a field made required, a narrower limit, a new
   mandatory step — something that held before no longer does.
3. New, and everything that held before still holds → **добавляет**.
4. Same meaning, different words, and a later reader would need the row to
   know it was not a silent rewrite → **уточняет**.
5. Else → no row. No token got a row → do not stamp.

Do not mint an «уточняет» to look thorough: if you cannot name the cited
token whose wording moved, there is no row.

Explaining an existing token — a comment, a `description`, a `Note` — is
no row; a removal is always «ломает». The examples per document (SRS,
foundation, domain model, scenarios, screen spec, OpenAPI, DB schema) are in
`references/change-types.md`: read it before typing a change.

### Service version vs document versions

The service version (`MAJOR.MINOR.PATCH` in the manifest, the plan
folder's name, the tag `v<version>`) is the one number. A document's
`version` is not a second counter: it is the release the document last
changed in, so the stamp copies the open iteration's number into it, and a
document never moves the service number. The rule — levels, when the
iteration's number is fixed, the bump unit, the close — lives in
`pipeline` → Service version.

The level is computed from the iteration's rows (those whose `Версия` is
the iteration's version) across every versioned document: any
«добавляет» or «ломает» → at least MINOR; only «уточняет», or no row and
code fixes only → PATCH. MAJOR is the owner's decision about a big new
capability, never a row's type: a «ломает» alone does not make a MAJOR.

An API with external consumers is the exception: its `info.version` is the
contract's own SemVer and its rows carry that number — «ломает» only as a
new API major (new path prefix), «добавляет» its minor, «уточняет» its
patch; pins to it name that number (`openapi-spec-generator`), and its
rows of the iteration are those added since the last tag.

## Frontmatter

```yaml
version: 1.2.0        # the service release this document last changed in; written only by the stamp
updated: 2026-10-05   # moves with that stamp, not on a change with no row and not on a save
migration: 0007       # db/schema.md only: the last file in db/migrations/ this document covers
grilled: 2026-10-05   # only on documents whose stage has a grill gate
reviewed: 2026-10-06  # set by doc-review when its gate closes
sources:              # what this doc was built from, pinned by the source's version
  - documentation/requirements/srs/srs.md@1.2.0
```

**Pin field is `sources:` (plural), always, except on an SRS.** Every other
writer emits it on a new document (`updated:` today, at least one pin or
the literal `stated-directly`); versioned writers also emit
`version: <iteration version>` with its «первый выпуск» row. An SRS emits
`title`, `date`, `updated`, and `version` only. There is no `source:`
field; a document with only legacy `source:` is Origin `none` until someone
migrates the key. `doc-review` treats a trailing `@<version>` (or a legacy
`@vN`) as a pin, not part of the path. `documentation/api/openapi.yaml` has
no frontmatter: its pins are `info.x-sources`, beside `info.x-reviewed`.

**`migration:`** (DB schema only) is set by the writer, not the stamp —
`references/exceptions.md` → DB schema.

**`grilled:` records that the stage's exit gate closed.** Business
requirements carry it. An SRS does not: its header is
`title`, `date`, `updated`, and `version` only — no `status`, `grilled:`,
`reviewed:`, or `sources`. Its value on the documents that have it is
the date the frontier emptied and the user confirmed the shared understanding.

Two rules make the field worth having:

- **Absent means the gate did not close.** A document at `status: ready-*` with
  no `grilled:` is an unfinished stage, not a document someone forgot to
  annotate. Read it as a stop and go close the gate.
- **A grill that reverses a line sets `grilled:` to today and does not stamp.**
  The version number waits for the commit. Do not clear `grilled:` or
  `reviewed:` to justify a new number; the commit that stamps the change
  keeps whatever gate dates the working copy already has.

Every other document omits the field: those stages are gated by
`doc-review` or `plan-review`, and an empty `grilled:` reads as a failed gate.

**`reviewed:` records that `doc-review` closed** on the architecture
documents, the screen specs, and the DB schema. An SRS does not carry it. OpenAPI has no frontmatter, so it
carries `info.x-reviewed` instead. Without it a new session cannot tell a
reviewed document from one whose review never ran. `doc-review` sets it to
the day every finding was applied, waived, or parked by the user; a review
stopped midway sets nothing. Absent means the review did not run or was
declined. A later commit does not clear it: the date is the review of the
working copy being published. Setting it is not a version change.

## Changelog

The change history is **one markdown table** directly after the H1
(`## Журнал изменений`; `## Changelog` on the DB schema; on architecture
`## Журнал изменений` after `## Описание системы`), with the same five
columns on every document: `Версия · Дата · Изменение · Тип · Кого
затрагивает`. It is never at the end and never a stack of `### v…`
headings. **One row per changed cited token, or a tight group — never for a
change with no row**; newest first, and the first row's `Версия` matches
`version`. OpenAPI carries the same rows as `info.x-changelog`. Read
`references/changelog.md` before writing or checking a row — it holds the
columns, a worked example, the OpenAPI form, and what each cell must
carry.

## ID stability

| Situation | Rule |
|---|---|
| New item | next unused number in that namespace; never fill a gap left by a deletion. In an SRS section a row inserted between two rows takes a dotted id after the row above (`FR-10.1`), so the section still reads in order (`srs-writer`) |
| Same prefix in two documents | `A-n` is an SRS actor and an architecture assumption. Outside its own document, cite it with the document: `SRS A-2`, `architecture A-2` |
| Item changes meaning | same id, changed text, a «ломает» row that says what it was, what it is, and why. A renumber breaks every citation, so no document renumbers — the SRS included |
| Item split | original id keeps the original core intent; the split-out part takes the next unused number, and every citation is re-pointed |
| Item no longer applies | mark `[deprecated in 1.2.0 — superseded by FR-13]` in place, with a «ломает» row; keep it. On an unversioned BRD, whose ids keep the `R` prefix: `[deprecated — superseded by R13]` |
| Item genuinely removable | delete only after confirming no document **and no code** cites it. Record it in the row's `Изменение` cell prefixed `удалён:` with the id and where you looked (`удалён: BR-4 — не цитируется в docs/, app/, tests/`). A removal is always «ломает» |

Deprecation over deletion is not tidiness — a plan unit committed last month
cites `BR-4`, and a reviewer will dismiss a real finding as "later unit" if
that row silently vanished.

## Staleness and cascade

Every **versioned** document pins its versioned sources as `path@<version>`:
`documentation/requirements/srs/srs.md@1.2.0` is "built from the SRS as it
was in release 1.2.0". A writer pins the `version` already written in the
source and never mints one to make a pin current. On reading a document,
compare each pin with the source's current `version`:

- **equal** — proceed.
- **behind** — read the source's changelog rows whose `Версия` is after the
  pin. They decide how serious it is:
  - any «ломает» → **stale**. The dependant must be re-checked against
    those rows and updated: that is the cascade. Put a banner as the first
    line of the body and say it in chat:

    ```markdown
    > **Stale** — построено по SRS 1.1.0; текущая 1.2.0 ломает BR-3.
    > Разделы, опирающиеся на BR-3, не пересобраны.
    ```

    A stale document is still usable input, never current. Do not proceed
    silently, and never move the pin without redoing the work.
  - only «добавляет» → **behind**. Nothing the dependant relied on moved;
    `docs-consistency` checks that each new token has a home. No forced
    update and no banner.
  - only «уточняет» → nothing to redo; the dependant's next stamp
    refreshes the pin.

A writer that re-derives a dependant from a source moves that pin to the
source's current `version` in the same edit: it has read those rows.

**Pins see releases, not commits.** Inside one open iteration a pin equal
to its source can still miss a row a later commit added; there the cascade
runs on `Кого затрагивает` and `docs-consistency`'s `checked:` hashes.

**Stale sweep.** When asked to find stale citations, walk every document
under `documentation/` (OpenAPI's `info.x-sources` included), read each
pin, and report `document → source@<pin> (current <version>): stale |
behind | refresh`, naming the rows that decided it. Report only; the banner
goes in when a stage next reads that document.

**Only «ломает» cascades.** For each «ломает» row, walk the registry row's
downstream list and decide **per consumer** — update now, update later, or
unaffected with a reason. The writer puts that verdict in its report; the
commit that stamps the row copies it into `Кого затрагивает`. A «ломает»
with no verdict leaves the tree quietly inconsistent, which is worse than
not recording the change at all. A «добавляет» does not cascade: its cell
names where the new thing is expected to land, and `docs-consistency`
checks it did. «уточняет» does not cascade.

## Increment discipline

The changelog is only verifiable if the diff matches it.

- **Touch only what the feature touches.** Do not re-word untouched
  requirements, reorder tables, normalize headings, or "improve" prose while
  passing through. A diff whose noise exceeds its delta makes the entry
  unreviewable.
- **Do not re-derive settled sections.** An existing decision stands unless the
  feature contradicts it.
- **A contradiction is a product decision, not an edit.** When the new feature
  cannot coexist with an existing requirement, stop and ask the user which one
  wins. Follow `grill-me` → "How a question is shown": the chat says what each
  requirement means and what breaks if the other wins. One question, then
  stop. The user answers by sending a message. Do not open a question
  card. Then record it as a «ломает» row with the reason. Silently rewriting the old
  requirement is the failure this whole convention exists to prevent.
- **A live `operationId` is never broken silently.** When only the
  project's own client calls the API, a breaking change ships in any
  release with front and back changed together and a «ломает» row naming
  the operation. When the API has external consumers it ships only as a new
  API major — a new path prefix beside the old one until its announced
  sunset (`pipeline` → Service version). Never a shape change under the
  same name with no row, which every generated client would absorb without
  warning.
- **Scope creep gets deprecated, not deleted.** Something you noticed that is
  outside this feature goes to that document's `open-questions.md`, not
  into a section of the document.

## Moving from the old numbers

Documents written before this scheme carry `version: N.x`, rows classed
none / minor / major, and `@vN` pins. Nothing is rewritten in bulk. Until a
document is stamped again, read `1.2` as `1.2.0` and `@v3` as `@3.0.0`; the
iteration that next stamps it sets the service version and starts the
five-column table above the old one (`references/changelog.md` → Old
tables). An old number precedes every service version whatever its digits,
an old major row reads as «ломает», a minor as «уточняет».

## When this skill is called

The steps are under "When a version is born". The checklist for each dirty
file is `references/guardrails.md`. A writer, a gate, and `work` do not run
it.
