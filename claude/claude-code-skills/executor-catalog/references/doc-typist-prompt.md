# Doc-typist packet and report

The parent is `srs-author`, a `design-*` row, or a `plan-*` row. It has already settled the
document. This row prints. A subagent gets no conversation history. What
is not in the packet does not exist for it.

The parent does not paste the finished document into this prompt. A
settlement that is the document, section for section, is a failed handoff:
the parent spent the output tokens this row exists to save. Send one line
per decision instead.

## The packet

```
You print a document that is already decided. You invent nothing.
You do not nest. You do not commit.

SKILL           <repo-relative path to the stage skill's SKILL.md>
                Follow the Writer half for shape, headings, and ids.
                Skip the Orchestrator half. Do not run grill-me,
                doc-review, or pipeline.

PARENT          srs-author | design-lite | design-medium | design-hard | plan-lite | plan-medium | plan-hard
OUTPUT PATH     <repo-relative path; db schema: documentation/db/schema.md
                plus each documentation/db/migrations/<NNNN>_<slug>.sql
                the parent settled; OpenAPI: documentation/api/openapi.yaml
                plus each paths/ and components/ file it references; SRS:
                documentation/requirements/srs/srs.md plus each areas/ file>
DIAGRAM PATH    <the `diagrams/` files next to the document: architecture
                foundation D2 views (documentation/architecture/diagrams/<view>.d2),
                scenario sequence views
                (documentation/architecture/scenarios/<area>/diagrams/<use-case-kebab>.puml),
                db ER (documentation/db/diagrams/er.d2), or none>
MODE            greenfield | increment | grill-reversal | revise

READ FROM DISK (do not expect them pasted)
  <repo-relative paths of the inputs and, on increment,
   grill-reversal, or revise, the current document>

SETTLEMENT      <one line per decision that is not already a sentence
                 in a file above: an id and its intent, a table cell,
                 a rejected alternative, an open-question row. Not a
                 section of the finished document. Not a paragraph to
                 paste.>

LANGUAGE        Russian prose. Do not translate cited tokens. Template
                headings and frontmatter keys stay as the skill specifies.

RULES
- Write only the OUTPUT PATH and DIAGRAM PATH files, and
  `open-questions.md` (or, for an SRS, `ui-wishes.md`) when SETTLEMENT
  names a row — beside the document, except the architecture's shared
  documentation/architecture/open-questions.md. A foundation embeds each
  D2 view in its section (`![<view>](diagrams/<view>.svg)`); a scenario
  links its sequence view from «Последовательность»
  (`[<use-case-kebab>](diagrams/<use-case-kebab>.svg)`). Render each
  `.svg` with the command in the skill's diagram reference, from the
  diagram's folder: D2 views and the ER with `d2`, sequence views with
  `plantuml` or its Docker image. If the renderer is missing, write the
  source file and say so. A migration file already committed is never
  edited; a schema change is a new numbered file.
- Where an input already states the sentence, carry it. Where
  SETTLEMENT names an id, write that part in the template's shape.
- Do not add an id, a column, an operation, a screen, or a rule that
  SETTLEMENT and the inputs do not contain. An empty template slot
  becomes an open-question row the settlement already named, not a guess.
- Do not change `version`, `updated`, `info.version`, or a changelog:
  the stamping commit writes them. Greenfield starts at
  `version: <iteration version>` — the name of the open
  `documentation/plans/<version>/` (no `summary.md`), `0.1.0` on a new
  product — with one «первый выпуск» row typed «—» (OpenAPI: in
  `info.x-changelog`). Pins are `path@<version>`, the source's current
  `version`. Grill-reversal replaces the contradicted line and touches
  neither.
- Revise (a plan before it ran): keep U-ids, edit only the units
  SETTLEMENT names, leave every other unit byte-identical.
- Do not commit, do not stage.
```

## The report

Last message, exactly these fields:

```
STATUS            DONE | BLOCKED
FILES WRITTEN     every path actually written, or none
LEFT OUT          a settlement line that did not fit the template, or none
```

`BLOCKED` means a settlement line contradicts an input or the template
requires a decision the settlement does not have. Do not paper over it.
