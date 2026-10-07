---
name: doc-review
description: >-
  Reviews a finished SRS, DB schema, OpenAPI contract, architecture
  document (foundation, domain model, scenarios), screen spec or
  business-requirements draft with parallel reviewer personas, applies
  one-right-answer fixes, and asks about the rest one finding at a time. Use
  when a document stage offers its review gate, or whenever the user asks to
  review, critique, find gaps in, or improve one of those documents. Not for
  writing the first draft, grilling assumptions (`grill-me`), the whole
  document set (`docs-consistency`), plans (`plan-review`), or code.
---

# Document Review

Takes a finished document and reviews it. Does not write the first draft.
Write findings and the review report in Russian. Do not translate cited
tokens, persona ids, or the report shape's headings and fixed lines
(`## Document Review Results`, `### Coverage`, `Review complete.`). See
`doc-versioning` → Document language.
Dispatches specialist reviewers through `executor-catalog` (Phase 2),
silently applies one-right-answer fixes, and asks what to do with
everything else.

**This is a pipeline gate the stage asks about.** The document stages offer
it before they are done — SRS, DB schema, API contract, the architecture
documents, the screen specs. On a yes,
the stage is done when this review ran and its findings are applied or
explicitly waived; on a skip, the stage says so in its report, the document
keeps its status, and the stage goes on to its next transition. The `pipeline` skill owns which stages those are; this file
owns what happens once it starts. It is also run directly whenever the user asks to
review, critique, or improve an existing document.

## Scope

**USE when:**
- A stage in `pipeline` closes with this gate: an SRS, DB schema, OpenAPI
  spec, architecture document, or screen spec was just written or changed
- Any of those documents already exists and the user wants it reviewed
- The user asks to improve, critique, or find gaps in a named file

**NOT for:**
- Exploring what to build — that is a separate requirements-writing step
- Interviewing the user to surface silent assumptions in something already
  written — that is a separate grilling step
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
2. **No path, interactive** — look under `<repo-root>/documentation/` for
   the newest file of a reviewable type (`doc-versioning` → Registry):
   `requirements/srs/srs.md`,
   `requirements/business-requirements/business-requirements.md`,
   `architecture/architecture.md`, `architecture/domain.md`,
   `architecture/scenarios/<area>/<area>.md`, `ui/screen-specs/S-*.md`,
   `db/schema.md`, or `api/openapi.yaml`. If several candidates exist, or
   none do, ask which file to review. Do not invent a path.
3. **No path, non-interactive** — already handled in Phase 0.

Resolve `<repo-root>` via `git rev-parse --show-toplevel`; fall back to cwd.
The documents live only under `documentation/`: do
not read another workflow's config or docs root (for example a
compound-engineering config, or `docs/plans/`) — a file found there is
not a pipeline document.

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
| `scenarios` | One functional area: use cases as sections with Вход / Шаги / Выход / Ошибки / Операция API; `architecture/scenarios/<area>/<area>.md` |
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
Read `doc-versioning` (language, changelog table, change types
ломает / добавляет / уточняет, parking lot, unversioned BRD) and flag only what that file — or the stage
skill that wrote the document — already forbids.

Read `references/convention-checks.md` and run it. Each miss is a P1
omission, Reviewer `convention`, confidence high; carry the misses into
Phase 3 and merge them with persona findings. That file also says which
misses may be fixed silently.

A silent fix, or any other fix this review applies, edits the body only.
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
| `adversarial-document-reviewer` | The document rests on **2+** contestable, load-bearing assumptions — premise claims, a new abstraction or architectural pattern, a pick among stated alternatives — that would topple it if wrong. A single auth / PII / payments mention does not trigger it; that is `security-lens-reviewer`'s signal. Do **not** activate on a routine `architecture` / `api` / `db` / `ui` document whose `{origin_path}` is a path and that stays in scope |

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
to its agent through its dispatch contract (`subagent_type` is the executor
name; the model lives in that agent's file) — copy both, do not re-decide
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
harness rejects the alias in its file, do not substitute a neighbour:
report it with the executor name (a missing agent → `install.sh`, per the
catalog) and continue with the personas that resolved.

Read only the selected files under `references/personas/`. Build each
reviewer prompt from `references/subagent-template.md` with:

| Slot | Value |
|---|---|
| `{persona_file}` | Full content of that persona file |
| `{format}` | Full content of `references/findings-format.md` |
| `{document_type}` | Type from Phase 1 |
| `{document_path}` | Path being reviewed |
| `{origin_path}` | Path or `none` |
| `{document_content}` | The full document |
| `{decision_primer}` | Round-1 empty block, or accumulated prior-round decisions (see below) |
| `{active_personas}` | Comma-separated ids of every persona dispatched this round |

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

Later rounds in the same session list applied / rejected findings with an
`Evidence:` snippet (first evidence quote, ~120 characters). Skip and
Defer count as rejected. A later session on the same file starts
at round 1 with an empty primer. A round 2 starts only from the re-review
question in `references/routing.md`, at most three rounds per session.
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
`open-questions.md` in the reviewed document's folder, never into the reviewed document;
the steps are `references/routing.md` → Defer. The finding the user is
being asked about is one question in the chat. The user answers by
sending a message. Do not open a question card. Writing it only into
`open-questions.md` is a failed question.

### Report shape

```markdown
## Document Review Results

**Document:** <path>
**Type:** <document_type>
**Reviewers:** <activated list, each with its catalog executor; conditional ones also with the one-line reason>

Applied N fixes. K items need attention (X errors, Y omissions). Z FYI observations.

### Applied fixes
- ...

### Fix did not land
| # | Section | Earlier applied finding | Evidence still present |

### P0 — Must Fix
#### Errors | Omissions
| # | Section | Issue | Reviewer | Confidence | Tier |

### P1 — Should Fix
…same table…

### P2 — Consider Fixing
…same table…

### P3 — Low Signal
…same table…

### FYI Observations
| # | Section | Observation | Reviewer | Confidence |

### Residual Concerns
| # | Concern | Source |

### Deferred Questions
| # | Question | Source |

### Coverage
| Persona | Executor | Status | Findings | Auto | Proposed | Decisions | FYI | Residual |
```

Rules:
- Escape `|` inside table cells as `\|`.
- Omit empty severity blocks. FYI / Residual / Deferred omit if empty.
  `Fix did not land` appears only on round 2+ and only when non-empty.
- `Issue` leads with the consequence, not a quote sandwich.
- User-facing labels: fixes (`safe_auto`), proposed fixes (`gated_auto`),
  decisions (`manual`), FYI observations (anchor `50`).
- `Tier` is the only place that still names the enum.
- Coverage counts are post-synthesis. Findings = Auto + Proposed +
  Decisions + FYI. Attribute a merged finding to the highest-anchor persona.

## Closing

Name the document path, the counts, and which catalog executors ran.

When the gate closed — every finding applied, waived, or parked by the
user — set `reviewed: <today>` in the document's frontmatter
(`info.x-reviewed` in OpenAPI). An SRS gets no `reviewed:`,
`grilled:`, `status`, or `sources`; the report is the record. That mark
is how `pipeline` knows in a later session that this review ran. It is
not a version change; see `doc-versioning` → Frontmatter. A review
stopped midway sets nothing.

When this ran as a pipeline gate, report and return to the stage that
called you. Do not ask the next transition; that stage asks, per
`pipeline` → "Asking before a transition". Say plainly whether the gate
closed clean or left findings the user chose not to apply, and name
`open-questions.md` beside the document when anything was parked there. When
the user opened this review directly, you ask the next transition
yourself after the report. Do not present a menu of other skills.

## References

- `executor-catalog` (skill) — persona → executor → agent, and the
  dispatch contract. This skill owns which personas fire; that file owns
  who runs them.
- `doc-versioning` (skill) — language, changelog table, change types
  (ломает / добавляет / уточняет), and the parking lot. Convention checks copy that file; they do
  not re-decide it.
- `references/convention-checks.md` — the session's convention checks, each
  row tagged with the skill that owns the rule. Read before dispatch.
- `references/subagent-template.md` — the packet each persona receives.
- `references/findings-format.md` — the `{format}` slot; the labelled text
  every reviewer returns.
- `references/synthesis.md` — merge, prior rounds, confidence gate, silent
  `safe_auto`. Read after every reviewer returns.
- `references/routing.md` — what to ask after the report (interactive),
  Defer, and the re-review question. Read after the report is shown.
- `references/personas/*.md` — one file per persona, read only for the
  personas selected in "Select personas" and pasted into `{persona_file}`:
  - `references/personas/coherence-reviewer.md` — always
  - `references/personas/feasibility-reviewer.md` — always
  - `references/personas/design-lens-reviewer.md` — UI signal; always on `screen`
  - `references/personas/security-lens-reviewer.md` — auth, PII, money, tokens
  - `references/personas/scope-guardian-reviewer.md` — priority tiers, large or misaligned scope
  - `references/personas/product-lens-reviewer.md` — challengeable what-to-build claims
  - `references/personas/adversarial-document-reviewer.md` — 2+ contestable load-bearing assumptions
