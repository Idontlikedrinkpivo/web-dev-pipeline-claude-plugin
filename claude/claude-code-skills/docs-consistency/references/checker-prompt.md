# Checker packet and reply

One packet to `docs-consistency-checker`. The checker reads the documents
itself from the paths given; the session does not paste them.

## The packet

```
You check that a set of finished project documents agrees across
documents. You do not judge whether any one document is good, and you do
not edit anything. Findings only.

DOCUMENTS (read every one in full before the first finding)
  SRS:           documentation/requirements/srs/srs.md and its areas/ files
  DB schema:     documentation/db/schema.md, plus every file in
                 documentation/db/migrations/ | skipped: <reason>
  OpenAPI:       documentation/api/openapi.yaml and the files it references | skipped: <reason>
  Architecture:  documentation/architecture/architecture.md (diagrams embedded) | skipped: <reason>
  Domain model:  documentation/architecture/domain.md | skipped
  Scenarios:     documentation/architecture/scenarios/<area>/<area>.md, one per area | skipped
  Screens:       documentation/ui/frames-register.md, plus every
                 documentation/ui/screen-specs/S-<n>-*.md | skipped: <reason>

AXES (run each one whose documents both exist; a skipped one gets one line)
  1 SRS → downstream     every FR / UC has an operation, a scenario and, when a
                         human does it, a screen element; every stored entity
                         has a table; every BR has an invariant row or a
                         constraint; every NFR with a number or a security rule
                         has a home
  2 Downstream → SRS     every table, operation, scenario, screen traces to an
                         SRS id; an orphan says whether it looks like scope creep
                         or a requirement the SRS is missing
  3 Schema ↔ OpenAPI     names, types, nullability vs required, enums, lengths
                         and ranges, uniqueness ↔ 409, id format, money and time
  4 OpenAPI ↔ screens    cited operationIds and fields exist; input rules ↔
                         request schema; every declared status of a called
                         operation has an outcome row; shown data the API never
                         returns is P1 (owner API or design)
  5 Domain ↔ rest        invariant rows ↔ SRS BRs and schema constraints; named
                         errors ↔ OpenAPI error codes; entities ↔ tables
  6 Scenarios ↔ rest     operations exist; only foundation ports used; rules cited
                         as invariant rows, not restated; errors are named
                         domain errors; roles ↔ actors ↔ security; tenancy;
                         every cross-area call: the caller's step (arguments,
                         result type) against the callee's Вход / Выход field
                         by field; screen specs exist → the foundation places
                         the client (stack, module, folder, lint, tests)
  7 One meaning per word one name per concept, one value per number (limits,
                         timeouts, page sizes, retention) across the set
  8 No visual binding    no SRS, schema, API or architecture document names a
                         widget, a presentation, layout, colour, icon or a
                         narrow-width layout change; each one is P1, owned by
                         that document. Screen specs and the frames register
                         are exempt (written from the frames)

NEW TOKENS  (from pins behind their source by «добавляет» rows only)
  <source · token · row text — check each has a home where the row's
   «Кого затрагивает» says it should land; a missing home is P1 on axis 1,
   owned by that document — or "none">

PRIOR FINDINGS  (re-check only)
  <one line per finding from the last report, or "none">

SEVERITY
  P0  two documents state different facts about the same thing
  P1  a requirement with no home where its stage ran; an orphan; a user-caused
      error with no screen state
  P2  naming drift with no behaviour change: a synonym, a label. A different field,
      operationId, status or enum value is P0 or P1, never P2
  P3  nit

OWNER  the document that should change. Default: the downstream one. Upstream
       only when the downstream is plainly right and upstream forgot it — say why.

DO NOT REPORT
- Anything inside one document only (that was its doc-review).
- A departure the downstream document records itself with its reason: an
  assumption A-n, a changelog line. List it under dismissed. An open-questions
  row that names an upstream gap (another document is wrong or silent) IS a
  finding, owned by that other document. A row that says two documents
  «должны совпасть» or names docs-consistency as owner is a check to run,
  not a decision; a part of the system left «вне документа» while other
  documents need it is never dismissed.
- A gap for a stage marked skipped.
- Style, wording, or a better design.
- Anything measured against `ui-wishes.md`: a frame or document that departs
  from a wish is not a discrepancy.
```

## The reply

The checker's last message is this labelled text and nothing else:

```
finding: 1
severity: P0 | P1 | P2 | P3
axis: <1–8 and its name>
where: <ids, names, sections in each document, e.g. "schema invoices.amount_cents · openapi Invoice.amount">
issue: <what disagrees or is missing, one sentence, in Russian>
owner: SRS | DB schema | OpenAPI | Architecture | Domain model | Scenarios:<area> | Screen spec:<S-n> | Design
fix: <the change in the owner document, or: decision needed — <the two readings>>
evidence:
- "<path>: <quoted line>"
- "<path>: <quoted line>"

finding: 2
...

clean_axes: <axis numbers with no findings, or: none>
skipped_axes: <axis numbers and why, or: none>
dismissed:
- <what, and which rule: recorded decision | skipped stage — or: none>
```

With no findings, `finding` blocks are omitted and `clean_axes` lists
every axis that ran.

A finding without two quoted lines (one per document) or, for a gap, one
quoted line and the place searched, is dropped in synthesis.
