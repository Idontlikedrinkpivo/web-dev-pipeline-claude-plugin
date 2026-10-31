---
name: doc-review
description: >-
  Reviews one finished document (BRD, SRS, schema, OpenAPI, architecture, screen spec) with reviewer personas. Use for
  «покритикуй ТЗ», «найди дыры в требованиях», «проверь схему». The whole set: docs-consistency.
---

# Document Review

Takes a finished document and reviews it. Does not write the first draft.
Write findings and the review report in Russian. Do not translate cited
tokens, persona ids, or the report shape's headings and fixed lines
(`## Результаты ревью документа`, `### Охват`, `Review complete.`). See
`doc-versioning` → `references/writing-rules.md` → Document language.
Dispatches specialist reviewers through `executor-catalog` (Phase 2),
silently applies one-right-answer fixes, and asks what to do with
everything else.

**This is a pipeline gate the stage asks about.** The document stages
`pipeline` names offer it before they are done. On a yes,
the stage is done when this review ran and its findings are applied or
explicitly waived; on a skip, the stage says so in its report, the document
stays as written, and the stage goes on to its next transition. This file
owns what happens once it starts. It is also run directly whenever the user asks to
review, critique, or improve an existing document.

## Scope

**USE when:**
- A stage in `pipeline` closes with this gate: an SRS, DB schema, OpenAPI
  spec, architecture document, or screen spec was just written or changed
- Any of those documents already exists and the user wants it reviewed
- The user asks to improve, critique, or find gaps in a named file

**NOT for:**
- Exploring what to build — that is `brainstorm`, then `srs-writer`
- Interviewing the user to surface silent assumptions in something already
  written — that is `grill-me`
- Writing architecture, API, or database design from scratch
- Reviewing an implementation plan — that is `plan-review`, whose lenses are
  commit atomicity, dependency graph, and grade calibration; no persona here
  has any of them
- Reviewing source code (diff or whole-repo)

## Phase 0 — Mode

Strip any `mode:` token from the arguments. The remainder, if any, is the
document path.

- `mode:non-interactive` (alias `mode:headless`): apply silent fixes; return
  remaining findings as structured text; do not ask routing questions.
- Otherwise: interactive. After the report, ask how to handle remaining
  findings — see `references/routing.md`.

Non-interactive without a path: stop with
`Review failed: non-interactive mode requires a document path.`

## Phase 1 — Resolve the document

1. **Explicit path** — read it. If unreadable, stop and name the path.
   Do not dispatch reviewers.
2. **No path, interactive** — under `<repo-root>/documentation/`, take the
   most recently committed file of a reviewable type (`doc-versioning` →
   Registry; `git log -1 --format=%cI -- <file>` per candidate):
   `requirements/srs/srs.md`,
   `requirements/business-requirements/business-requirements.md`,
   `architecture/architecture.md`, `architecture/domain.md`,
   `architecture/scenarios/<area>/<group>.md`, `ui/screen-specs/S-*.md`,
   `db/schema.md`, or `api/openapi.yaml`. Name it and ask the user to
   confirm or name another; with none, ask which file to review. Do not
   invent a path.
3. **No path, non-interactive** — already handled in Phase 0.

Resolve `<repo-root>` via `git rev-parse --show-toplevel`; fall back to cwd.
The documents live only under `documentation/`; a file found elsewhere
is not a pipeline document.

### Classify the document

Classify by **content shape**, not folder. Pass the type to every reviewer.
Do not re-classify later.

| Type | Signals |
|---|---|
| `business-requirements` | `## Goal Capsule` and `## Product Contract`, requirement rows `R<n>`; `business-requirements/business-requirements.md` |
| `srs` | Numbered sections 1–8, IDs `A-` `FR-` `NFR-` `BR-` `UC-`, Given/When/Then acceptance criteria; `requirements/srs/srs.md` with its `areas/` files, reviewed as one document. No open-questions section |
| `screen` | One screen `# S-<n>. …` with `figma:` in the frontmatter, sections Загрузка и вызовы / Элементы (№ · Элемент · Поведение по условиям · Метод и поля · Кадр) / Состояния экрана / Ошибки ответов / Производные значения / Разрывы; `ui/screen-specs/S-<n>-*.md` |
| `architecture` | Foundation: Состав системы, modules and functional areas, ports and adapters, file tree, lint rules; `architecture/architecture.md` |
| `domain` | Value objects, entity sketches, named errors, the invariant table; `architecture/domain.md` |
| `scenarios` | One SRS group of a functional area: use cases as sections with Вход / Шаги / Выход / Ошибки / Операция API; `architecture/scenarios/<area>/<group>.md` |
| `api` | `openapi: "3.0.3"` (or 3.0.x), `paths:`, `components:`; `api/openapi.yaml` with the `paths/` and `components/` files it references, reviewed as one document |
| `db` | DBML table blocks; `db/schema.md`. The files in `db/migrations/` are reviewed with it as one document: read them all (a migration path given alone resolves to `db/schema.md`). A committed migration file is never edited — a fix it needs is a finding for `db-schema-design` (the next file), not an applied fix |

Tie-breaker: dominant shape wins. If still ambiguous, ask once.

**Upstream source** (extract once, pass as `{origin_path}`):
- Frontmatter `sources:` (`info.x-sources` in OpenAPI) — first
  list item that is a repo-relative path. Strip a trailing `@<version>` pin (or a legacy `@vN`). The literal `stated-directly` is not a path.
- An architecture / API / DB document that names its SRS or
  business-requirements path in `sources:` or in the digest
- Otherwise the literal `none`

Do not read a singular `source:` key. Writers in this collection emit
`sources:` only; an unpinned legacy `source:` is treated as Origin `none`.

A path here means the premise was already written down upstream. Personas
that challenge "what to build" must not re-litigate that premise on a
downstream document.

### Convention checks (session, not a persona)

Do this on the session after the file is read, **before** dispatch. These
are not a new reviewer and not a second copy of the versioning rules.

1. **What code decides, first:** run
   `python3 "${CLAUDE_SKILL_DIR}/../doc-versioning/scripts/doc_check.py" . --only <document path>`
   from the project's root — frontmatter keys, the changelog's columns,
   order, first-row version and change types, pins, lost ids, migrations,
   OpenAPI references, `open-questions.md` shape. Each line it prints about
   this document's files is a convention miss; lines about other documents
   are not this review's.
2. **Then the rows the script cannot decide:** read
   `references/convention-checks.md` and run its rows. When a row fails,
   read the owner section it names (in `doc-versioning` or the stage skill
   that wrote the document) for the rule and its reason — not the whole
   `doc-versioning` skill on every review — and flag only what that owner
   already forbids.

Each miss is a P1 omission, Reviewer `convention`, confidence high; carry
the misses into Phase 3 and merge them with persona findings.
`references/convention-checks.md` also says which misses may be fixed
silently.

A silent fix, or any other fix this review applies, edits the body only;
the frontmatter is touched once, by Closing, which sets `reviewed:`.
Leave `version`, `updated`, and the changelog exactly as they are, in every
mode. A review is not a new version. A restamped `updated` makes the
document look re-published when nothing was decided. Only `doc-versioning`
moves those fields.

### Select personas

Always dispatch:
- `coherence-reviewer`
- `feasibility-reviewer`

Add a persona only when its signal is present:

| Persona | Activate when |
|---|---|
| `product-lens-reviewer` | Challengeable claims about what to build or why, or work with strategic weight. Not on a document with no product choice left — a schema, API, or architecture that transcribes settled requirements |
| `design-lens-reviewer` | UI/UX, screens, forms, navigation, controls. **Always on a `screen` document** — a screen spec reviewed without this lens has no reviewer looking at the elements |
| `security-lens-reviewer` | Auth, sessions, API exposure, PII, payments, tokens, credentials, third-party trust, or an SRS Security NFR checklist |
| `scope-guardian-reviewer` | Priority tiers, >8 requirements or use cases, stretch / future-work, or scope that looks misaligned with the summary |
| `adversarial-document-reviewer` | The document rests on **2+** contestable, load-bearing assumptions — premise claims, a new abstraction or architectural pattern, a pick among stated alternatives — that would topple it if wrong. A single auth / PII / payments mention does not trigger it; that is `security-lens-reviewer`'s signal. Do **not** activate on a routine `architecture` / `domain` / `scenarios` / `api` / `db` / `screen` document whose `{origin_path}` is a path and that stays in scope |

Announce the team and, for each conditional persona, the one-line reason.

### On a `screen` document

The screen spec is written from finished mockups and the API; the premise —
which use cases exist, what each guarantees — was settled in the SRS, and
how the screen looks was settled on the frames. What is reviewable is the
mapping, so point the lenses at it:

| Lens | On a screen spec |
|---|---|
| `coherence-reviewer` | every element cites a use case or sits in Разрывы; every condition in «Поведение по условиям» has an outcome; Производные значения defined once and cited the same way everywhere; element numbers continuous |
| `design-lens-reviewer` | an element whose behaviour an implementer could not build from; a state the frames register lists with no row; a role-dependent element with no rule for the other role |
| `feasibility-reviewer` | an `operationId` or a field not in the OpenAPI spec; data the screen shows that no response returns; a «Ошибки ответов» table missing a declared status of an operation the screen calls |
| `security-lens-reviewer` (when it activated) | a Forbidden state absent where the SRS declares an authorization exception; an element that reaches an operation the actor's role does not allow; a field marked sensitive shown to a role that was never granted it |

Visual detail described in words (colours, sizes) where a frame reference
belongs is a finding; widget names and exact texts are not — this document
is written after the design. `ui-wishes.md` is never grounds for a finding.

## Phase 2 — Dispatch

Read `executor-catalog` before the first dispatch. Resolve each activated
persona to an executor through its **Document-review routing** table, then
to its agent through its dispatch contract (`subagent_type` is
`dev-pipeline:<executor>`; the model lives in that agent's file) — copy both, do not re-decide
them. That table is the only persona → executor mapping; a copy here would
drift from it.

Before the first `Agent` call, write one row per activated persona in this
turn: `Persona | Executor | subagent_type` for the catalog assignment
(you may append each executor's model and effort, read from its agent
file), and dispatch it without asking which model. Announce the team with
those executors, not personas alone. Then follow the catalog dispatch
contract: each call passes the executor as `subagent_type` and no `model`,
unless the user named one. A persona on `general-purpose`, on a typed `model`, or on the
session model to "save a dispatch" is a failed dispatch.

Do not reuse `review-medium` / `review-hard` / `review-full-plan` here —
those review a code diff. If an executor's agent is not installed, or the
harness rejects the alias in its file, the review stops, as the
catalog's Dispatch contract says: name the executor and
tell the user to install or update the `dev-pipeline` plugin. Do not
substitute a neighbour, and do not run the review with the personas that
happened to resolve — a review missing its lens reads as a clean one.

Build each reviewer prompt from `references/subagent-template.md`. The
reviewer reads the files itself; the packet carries their paths and only
what this session computed:

| Slot | Value |
|---|---|
| `{persona_path}` | Absolute path of the persona file: `${CLAUDE_SKILL_DIR}/references/personas/<persona>.md` |
| `{format_path}` | Absolute path of `${CLAUDE_SKILL_DIR}/references/findings-format.md` |
| `{document_files}` | Every file of the document, one repo-relative path per line: the index and its parts (`srs.md` and `areas/*.md`; `openapi.yaml`, `paths/`, `components/`; `schema.md` and `migrations/*.sql`) |
| `{document_type}` | Type from Phase 1 |
| `{document_path}` | Path being reviewed |
| `{origin_path}` | Path or `none` |
| `{decision_primer}` | Round-1 empty block, or the prior-round decisions from the review ledger (see below) |
| `{active_personas}` | Comma-separated ids of every persona dispatched this round |
| `{skills_root}` | `SKILLS ROOT`: the absolute folder holding the plugin's skills, the parent of `${CLAUDE_SKILL_DIR}` (`executor-catalog` → Dispatch contract) |

Never paste the document, the persona or the format into the prompt.

Dispatch the resolved subagents in parallel, bounded by the harness cap.
Each `Agent` call carries its executor from the printed table as
`subagent_type`, and no `model` unless the user explicitly picked one. Queue
the rest. A capacity error is backpressure, not failure. If one reviewer
fails, continue with the others and note it in Coverage.

Do not invoke other skills from a reviewer. Reviewers are read-only.
Synthesis and the silent `safe_auto` pass stay on this session — that is
orchestration, not a persona.

**Decision primer.** Round 1:

```
<prior-decisions>
Round 1 — no prior decisions.
</prior-decisions>
```

Later rounds list applied / rejected findings with an `Evidence:` snippet
(first evidence quote, ~120 characters). Skip and Defer count as rejected.
After a round whose fixes were applied, the user is asked whether to run
the next one (`references/routing.md` → Re-review); there is no limit on
rounds.

**The review ledger.** Decisions held only in context are lost with a
compaction, and the user is asked them again. So every decision on a
finding — applied, deferred, skipped — is kept in a file outside the repo by
`grill-me`'s script (`L` is `python3
"${CLAUDE_SKILL_DIR}/../grill-me/scripts/ledger.py"`, run from the
project's root): `L open --kind review --doc <document's main file>` at
round 1 and first thing in a resumed session — `state: resumed` or
`changed` prints the logged lines: read them before anything else and never
ask a logged finding again (`changed` is expected after an applied round);
`restarted` means a past iteration's review was deleted: round 1. Each
decision the moment it is made: `L add --kind review --doc <file> "Круг N ·
<title> · применено | отложено | пропущено · Evidence: <~120 characters>"`.
The primer is built from `L show …`. `L close …` when the review closes.
The primer rule inside each persona only reduces noise; synthesis step
3.3a is what drops a re-raised rejection and checks that an applied fix
landed.

## Phases 3–5 — Synthesize, present, route

After every dispatched reviewer returns, follow `references/synthesis.md`,
then present using the report shape below. Interactive routing, Apply,
and Defer live in `references/routing.md`. Do not load that file before
dispatch finishes.

A parked finding — option C, or `отложи` / `потом` / `в open questions`
in chat after the report — always goes to
`open-questions.md` in the reviewed document's folder (a scenarios document
into `architecture/`, a screen spec into `ui/`), never into the reviewed
document; the steps are `references/routing.md` → Defer. The finding the user is
being asked about is one question in the chat. The user answers by
sending a message. Do not open a question card. Writing it only into
`open-questions.md` is a failed question.

### Report shape

```markdown
## Результаты ревью документа

**Документ:** <path>
**Тип:** <document_type>
**Ревьюеры:** <activated list, each with its catalog executor; conditional ones also with the one-line reason>

Внесено правок: N. Требуют внимания: K (ошибок X, пропусков Y). Наблюдений: Z.

### Внесённые правки
- ...

### Правка не применилась
| # | Раздел | Прежняя находка | Что осталось |

### P0 — исправить обязательно
#### Ошибки | Пропуски
| # | Раздел | Проблема | Ревьюер | Уверенность | Уровень |

### P1 — стоит исправить
…та же таблица…

### P2 — можно исправить
…та же таблица…

### P3 — слабый сигнал
…та же таблица…

### Наблюдения
| # | Раздел | Наблюдение | Ревьюер | Уверенность |

### Остающиеся сомнения
| # | Сомнение | Источник |

### Отложенные вопросы
| # | Вопрос | Источник |

### Охват
| Персона | Исполнитель | Статус | Находки | Авто | Предложено | Решения | Наблюдения | Сомнения |
```

Rules:
- Escape `|` inside table cells as `\|`.
- Omit empty severity blocks. «Наблюдения», «Остающиеся сомнения», «Отложенные вопросы» omit if empty.
  «Правка не применилась» appears only on round 2+ and only when non-empty.
- «Проблема» leads with the consequence, not a quote sandwich.
- User-facing labels: fixes (`safe_auto`), proposed fixes (`gated_auto`),
  decisions (`manual`), FYI observations (anchor `50`).
- «Уровень» is the only place that still names the enum.
- Coverage counts are post-synthesis. Findings = Auto + Proposed +
  Decisions + FYI. Attribute a merged finding to the highest-anchor persona.

## Closing

Name the document path, the counts, and which catalog executors ran.

When the gate closed — every finding applied, waived, or parked by the
user — set `reviewed: <today>` in the document's frontmatter
(`info.x-reviewed` in OpenAPI). «Только отчёт» (`references/routing.md` →
D) closes it too: the user saw every finding and chose to change nothing,
which waives them all, and the report names them as not applied. An SRS
gets no `reviewed:`, `grilled:`, `status`, or `sources`; the report and
the stamp's `review: прошёл` are the record. That mark is how `pipeline`
knows in a later session that this review ran. It is not a version change;
see `doc-versioning` → Frontmatter. A review stopped midway — the user
left with findings unanswered — sets nothing, and its ledger stays for the
session that resumes it; a closed review deletes its ledger.

When this ran as a pipeline gate, report and return to the stage that
called you. Do not ask the next transition; that stage asks, per
`pipeline` → "Asking before a transition". Say plainly whether the gate
closed clean or left findings the user chose not to apply, and name
`open-questions.md` beside the document when anything was parked there. When
the user opened this review directly, you ask the next transition
yourself after the report. Do not present a menu of other skills.

## References

- `references/personas/*.md` — one file per persona, passed by path as
  `{persona_path}` to the personas selected in "Select personas":
  - `references/personas/coherence-reviewer.md` — always
  - `references/personas/feasibility-reviewer.md` — always
  - `references/personas/design-lens-reviewer.md` — UI signal; always on `screen`
  - `references/personas/security-lens-reviewer.md` — auth, PII, money, tokens
  - `references/personas/scope-guardian-reviewer.md` — priority tiers, large or misaligned scope
  - `references/personas/product-lens-reviewer.md` — challengeable what-to-build claims
  - `references/personas/adversarial-document-reviewer.md` — 2+ contestable load-bearing assumptions
