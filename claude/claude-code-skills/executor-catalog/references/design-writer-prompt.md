# Design-writer packet and report

A subagent gets one design document — or, for `clean-architecture-design`,
every architecture document of the sitting — and no conversation
history. What is not in the packet does not exist for it.

The orchestrator fills every slot from
`executor-catalog/references/design-complexity.md` and the stage skill.
The writer follows the **Writer** half of that skill, not the Orchestrator
half. The documents go by path, every part of each; only what is on no
disk is pasted (`executor-catalog` → Dispatch contract → Paths, not pasted
documents). A writer handed `srs.md` alone reads a table of contents and
designs without most of the requirements.

## The packet

```
You settle the design document(s). You do not print them, and you do
not write production code. When every decision the templates need is
settled — on `clean-architecture-design`, for every document in MODE
before printing any — nest `doc-typist` with
`<SKILLS ROOT>/executor-catalog/references/doc-typist-prompt.md`, one per document
(in parallel when there are several). Each writes its OUTPUT PATH and
the files at its DIAGRAM PATH: on `clean-architecture-design`
`foundation`, the D2 views (`.d2` / `.svg`), each embedded in its
section of the document; on `scenarios:<area>`, one PlantUML sequence
`.puml` / `.svg` per key scenario; on `db-schema-design`, the ER `.d2`
and its `.svg` (the migration files are part of its OUTPUT PATH). A gap the
skill calls BLOCKED returns before that dispatch. Read the files back. One
correction dispatch per document, then the report. Do not type the
correction. Do not paste a finished document into the typist's prompt.
Writing those files yourself is a failed print.

SKILLS ROOT     <absolute folder holding the plugin's skills — the parent
                of the stage skill's base directory (executor-catalog →
                Dispatch contract)>
SKILL           <SKILLS ROOT>/<stage>/SKILL.md
                Follow the Writer half and its references; every
                `<skill>/…` path in them resolves under SKILLS ROOT. Skip
                the Orchestrator half. Do not run doc-review. Do not
                offer the next pipeline stage. Do not commit.

STAGE           clean-architecture-design | db-schema-design | openapi-spec-generator
COMPLEXITY      Low | Mid | High  (<why the cascade fired>; architecture:
                one line per document, dispatched at the highest)
EXECUTOR        design-lite | design-medium | design-hard

MODE            greenfield | increment
                clean-architecture-design adds the documents after a
                dot, in order: `greenfield · foundation, domain,
                scenarios:top-ups, scenarios:refunds`, `increment ·
                domain, scenarios:bookings`. Follow each mode's section
                of the skill.

OUTPUT PATH     <repo-relative path the file must land at, by document:
                architecture (one line per document of MODE):
                  foundation        documentation/architecture/architecture.md
                  domain            documentation/architecture/domain.md
                  scenarios:<area>  documentation/architecture/scenarios/<area>/<group>.md,
                                    one line per SRS group of the area
                db-schema-design: documentation/db/schema.md, plus
                  documentation/db/migrations/<NNNN>_<slug>.sql —
                  greenfield 0001_init.sql; an increment adds the next
                  number and never edits a committed file.
                openapi-spec-generator: documentation/api/openapi.yaml and
                  the paths/ and components/ files it references
                  (openapi-spec-generator → Step 8 → Layout)>
DIAGRAM PATH    <by document; a `diagrams/` folder next to the document:
                clean-architecture-design foundation:
                  documentation/architecture/diagrams/<view>.d2 for the
                  views in `architecture-diagram.md` (context, containers,
                  stores, modules, layers), each embedded in its section.
                clean-architecture-design domain: `none`.
                clean-architecture-design scenarios:<area>:
                  documentation/architecture/scenarios/<area>/diagrams/<use-case-kebab>.puml
                  per key scenario, or `none` when the area has none.
                db-schema-design: documentation/db/diagrams/er.d2.
                openapi-spec-generator: `none`>

READ FROM DISK  <repo-relative paths, every part of each document — read them
                all before deciding anything:
                SRS: documentation/requirements/srs/srs.md and every
                  documentation/requirements/srs/areas/*.md (srs.md alone
                  is the table of contents).
                schema — openapi-spec-generator when the system stores
                  data; clean-architecture-design when that stage ran:
                  documentation/db/schema.md and every
                  documentation/db/migrations/*.sql.
                API — clean-architecture-design when that stage ran:
                  documentation/api/openapi.yaml and every file under
                  documentation/api/paths/ and documentation/api/components/.
                architecture: the foundation's §1 «Стек» when the stack is
                  a fact; on a split greenfield's second dispatch, the
                  foundation and the domain model the first one wrote.
                increment: the current files of the documents in MODE —
                  for architecture every architecture document (a name may
                  have to be added to one outside MODE) and the `.d2` /
                  `.puml` files of the documents being edited; say which
                  file wins if a diagram and its document disagree.>

ANSWERS         <pasted — the only text here: each answer the user gave in
                this session that the stage asks for before dispatch, one
                line with its question. db-schema-design: the DBMS and its
                major version, a field's classification (§6), how an
                existing database is documented. openapi-spec-generator:
                the auth scheme, the status of an exception the SRS left
                open, whether anyone outside the project calls the API.
                clean-architecture-design: the stack pick. Or: none>

POPULATED       <db-schema-design on an increment: one line per existing
                table the slice changes — `rows: yes` (its creating
                migration is in a released tag), `rows: no` (created in
                this unreleased iteration), or the user's answer. Picks
                the safe migration sequence (`migration-safety.md`).
                Otherwise: none>

PROGRESS FILE   <architecture: documentation/plans/<version>/progress-architecture.md;
                otherwise none. With the Edit tool, set each document's
                Статус cell as you go — `🔄 в работе: решения` when you start it,
                `🔄 в работе: печать` when you hand it to doc-typist, `🔍 проверка`
                when the typist returns it — and change nothing else there>
STACK           <chosen row from ANSWERS, or: already a fact — the
                foundation §1 «Стек» or the manifest named in READ FROM DISK>
                If the architecture skill is waiting on a stack pick,
                you should not have been dispatched. Stop and report
                BLOCKED.

INCREMENT       <when MODE is increment: type each change first —
                 ломает / добавляет / уточняет / no row
                 (`doc-versioning` → What a version is) — and report
                 each with its downstream verdict; do not write the row,
                 the stamping commit does. The changelog stays where it
                 is: `## Журнал изменений` after `## Описание системы`
                 (architecture foundation), or immediately after the H1
                 (domain model and scenarios: `## Журнал изменений`;
                 db schema: `## Журнал изменений` too), newest row first — not a
                 block at the end. OpenAPI's rows are `info.x-changelog`.
                 The body is still the complete document: carry unchanged
                 sections over verbatim from the current file on disk.
                 Never write "как в 1.1.0", "без изменений", "см. git".>

LANGUAGE        Russian prose. Do not translate cited tokens (ids, paths,
                table names, operationId, types). Template headings and
                frontmatter keys stay as the skill specifies.

RULES
- `doc-typist` writes OUTPUT PATH and the diagram and migration files
  named above. You write none of them. The typist renders each `.svg`.
  If `d2` or PlantUML is missing, the typist's report says so.
- The document is in Russian. Do not translate cited tokens.
  Template headings and frontmatter keys stay as the skill specifies.
- Do not change `version`, `updated`, `info.version`, or the changelog.
  The version and the typed rows are written only by the stamping commit
  (`doc-versioning`). Greenfield starts at `version: <iteration version>`
  — the name of the open `documentation/plans/<version>/` (no
  `summary.md`), `0.1.0` on a new product — with one «первый выпуск» row
  typed «—»; leave that row alone after creating it. Pins are
  `path@<version>`, the `version` written in each source now.
  Architecture foundation: `## Описание системы` after the H1, then
  `## Журнал изменений`; domain model and scenarios:
  `## Журнал изменений` right after the H1. No `## Сокращения`. DB schema:
  `## Журнал изменений` immediately after the H1. OpenAPI: no frontmatter and no
  markdown table — `info.version`, its «первый выпуск» row in
  `info.x-changelog`, and its source pins in `info.x-sources` (SRS, and the
  schema when it exists); a partner-versioned API's `info.version` is its
  own SemVer (`openapi-spec-generator` → Contract version).
- No widget, presentation, layout, colour or icon in the document — not in
  a row, a Note, a `description`, or prose (`doc-versioning` → What, not
  how it looks). Cite UI by actions, data and outcomes.
- Do not invent requirements, tables, or an auth scheme the inputs
  did not decide.
- Every section states its own content. A reader who has only this
  version must be able to name every layer, port, and file. No section
  defers to an earlier version; no live heading is left empty.
- On clean-architecture-design: write the documents MODE names, each
  with its template's Russian headings (`output-template-<mode>.md`). A
  fact another document owns is cited, never restated — not even a
  rule's value. A name a document outside MODE lacks (port method, named
  error and its HTTP row, config variable, file line, entity method,
  invariant row) is added there and the document is listed under ALSO
  CHANGED; a fundamental change there is HARDER_THAN_EXPECTED.
  Assumptions go to documentation/architecture/open-questions.md; no
  open-questions section. No «Правила по виду», no «агрегат», no
  `## Сокращения`. Foundation: §3 opens with the layer roster (no «Путь
  одного запроса»); §5 is real file names (no `…`, no `<placeholder>`,
  no `a|b|c`); the D2 views are embedded in their sections, no separate
  diagram file; Контейнеры and Модули are drawn or replaced by one
  sentence each. Domain: no section intro, no `from(raw)` gloss, no
  preamble under the invariant table — the only invariant table of the
  three; the constraint column is «Ограничение в схеме», copied from the
  schema when one exists, `none` when that document left the rule
  unconstrained. Scenarios: use-case headings include the file path and,
  if there are more than four, an index table; rules cited by id, errors
  by domain-model name, no HTTP status; a sequence diagram only for a
  key scenario. No Mermaid.
- DESIGN in the inputs wins over your preferences.
- A decision only the user can make and that ANSWERS lacks is STATUS
  BLOCKED with that one question in BLOCKER, worded for the user. The
  session asks it and sends you the answer; do not guess it.
- Do not invoke grill-me, doc-review, or pipeline.
- Do not commit, do not stage.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILE WRITTEN      the output path(s), one per line (db: schema.md and
                  each migration file written), or none
DIAGRAM WRITTEN   architecture foundation: each
                  documentation/architecture/diagrams/<view>.d2.
                  architecture scenarios: each
                  documentation/architecture/scenarios/<area>/diagrams/<use-case-kebab>.puml,
                  or none. architecture domain: none.
                  db: documentation/db/diagrams/er.d2.
                  `none` for OpenAPI. Add `svg: missing` if `d2` or
                  PlantUML did not run.
LEVEL             Framework-first | Modest | Full | n/a (not architecture)
ALSO CHANGED      architecture only: each document outside MODE you
                  added names to, with the names; or none
DOWNSTREAM        increment only: each change with its type (ломает /
                  добавляет / уточняет); for a «ломает», one line per
                  consumer (for architecture, the other two architecture
                  documents too), must update or unaffected with the
                  reason; for a «добавляет», where the new thing lands.
                  Omit on greenfield.
CONCERNS          only for DONE_WITH_CONCERNS
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED; a question for
                  the user is one question, prefixed `ВОПРОС:`
DELEGATED         doc-typist, or none
```
