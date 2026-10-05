# Markdown Rendering

This is a format-rendering reference — it describes how to render any
artifact in markdown, independent of which skill is producing it.

It is paired with a section contract (`plan-sections.md`,
`brainstorm-sections.md`, etc.) that describes *what* the artifact contains.
This reference describes *how* markdown specifically presents it. The same
content rendered by different skills shares the same markdown principles.

## Hard invariants

These hold regardless of which skill produced the artifact.

- **YAML frontmatter at the top of the file.** Standard `---` delimited block
  containing the artifact's stable metadata (title, date, type, etc.
  — exact fields are per-skill, defined in the section contract).
- **ASCII identifiers in anchors.** Markdown headings auto-generate anchors
  from the heading text. Keep headings ASCII so anchors are predictable
  (`#implementation-units`, not `#implementación-units`).
- **Repo-relative paths for file references.** Always. Never absolute paths
  — they break portability across machines, worktrees, teammates.
- **No HTML mixed in.** Keep the markdown pure. No `<div>`, no `<details>`,
  no inline `<style>`. The only exception is a contract-defined invisible
  semantic marker such as `<!-- ce-section: work-relationships -->`; it carries
  section meaning for downstream agents and does not create layout. Markdown
  stays markdown.
- **No fixed-width line wrapping.** Do not hard-wrap prose to a column (e.g.
  80 chars). Write one sentence per line, or let each paragraph flow as a
  single line. The artifact is read rendered and shared, where fixed wraps add
  nothing and only produce noisy mid-sentence diffs; markdown joins soft line
  breaks within a paragraph, so wrapping never changes the rendered output.
- **Unified plan sections use stable headings.** For unified plan artifacts,
  render the required sections with exact ASCII headings so agents can find
  them by heading scan: `## Goal Capsule`, `## Product Contract`,
  `## Planning Contract`, `## Implementation Units`, `## Verification Contract`,
  `## Definition of Done`, and optional `## Appendix`. Requirements-only
  artifacts omit the plan-only sections rather than emitting empty placeholders.
  These stable headings are the wayfinding contract: consumers scan them
  (markdown headings) instead of reading
  the whole document.
- **Goal Capsule is top-loaded.** It appears before Product Contract and long
  appendices for fast orientation — not a hidden machine copy.

## Format principles

These shape what "good" markdown looks like; the agent applies them per
artifact based on content shape.

### ID prefix format

Stable IDs (R, U, A, F, AE, KTD) appear as plain prefixes at the start of
the bullet or heading — do NOT bold the prefix. The prefix is visually
distinctive on its own; bolding it inflates visual noise.

```markdown
- R1. The plan returns paginated sessions.   ← right
- **R1.** The plan returns paginated sessions.   ← wrong (bolded prefix)
```

Same applies to unit headings: `### U1. Cloak detection in preflight contract`.

### Content shape: prose vs bullets vs tables

The same content can be rendered three ways; the agent picks per content
shape, not by template default.

- **Prose** when the content has narrative flow (motivation, decision
  rationale, problem framing). Bullets fragment narrative into
  disconnected pieces.
- **Bullets** when items share a parallel shape but each carries enough
  prose to not fit a table cell.
- **Tables** when 5+ items share uniform structure (`ID + body`,
  `name + value`, `decision + rationale`, `risk + mitigation`). Tables
  scan faster at that scale and unlock additional columns (status,
  traceability, severity) that bullets can't accommodate cleanly.

The test: which shape would a reader scan fastest for this content? If
items have parallel structure and 5+ instances, table. If items are 3-5
and each has a few lines of prose, bullets. If the content is a single
narrative thought, prose.

### Bold leader labels within bullets

When a bullet has substructure that benefits from named fields (Key Flows
with Trigger / Actors / Steps / Outcome, Acceptance Examples with Covers
/ Given / When / Then), use bold leader labels at the start of nested
bullets — not deeper heading levels.

```markdown
- F1. Anonymous capture
  - **Trigger:** Agent enters Step 2a with no session.
  - **Actors:** A1, A2
  - **Steps:** Preflight detects cloak; agent launches; capture proceeds.
  - **Covered by:** R1, R2, R5
```

This gives the bullet structure without needing H4/H5 headings that would
clutter the doc and break TOC generation.

### Section separators

For substantial artifacts, use horizontal rules (`---`) between top-level
H2 sections. Omit for short docs where separators would dominate.

### Tables for genuinely comparative info only

Use tables for the uniform-shape case in "Content shape" above. Don't use
tables to render content lists that are really bullets — markdown tables
are noisier in raw form and worse for diffs.

## Section anatomy

How section types commonly render in markdown. These are patterns, not
contracts — the agent picks the shape that fits the content.

- **Goal Capsule** — bullets or a small table for objective, authority,
  execution profile, stop conditions, and tail ownership.
- **Product Contract** — H2 section containing Summary, Problem Frame,
  Requirements, and product-scope subsections. Put Requirements under
  `### Requirements` so review tools can distinguish Product Requirements
  from implementation detail.
- **Planning Contract** — H2 section for KTDs, high-level technical design,
  assumptions, and sequencing.
- **Summary / Problem Frame** — prose paragraphs.
- **Requirements** — bullets with `R<N>.` prefix. When requirements span
  more than one concern, grouping under bold inline headers is the default
  shape, not optional polish (group by capability, not by discussion order);
  render a flat list only when every requirement is about the same thing.
  When requirements have status, traceability, or severity that warrant
  additional columns, escalate to a table.
- **Implementation Units** — H3 heading per unit with `U<N>.` prefix.
  Fields (Goal, Files, Patterns, Test Scenarios, Verification) render as
  bullets with bold leader labels, or as sub-headings if the field has
  multi-paragraph content.
- **Verification Contract / Definition of Done** — use tables when commands,
  applicability, unit IDs, and done signals share a uniform shape. Name
  concrete repo commands such as `bun test` rather than generic "run tests"
  when the repo has known commands.
- **Key Technical Decisions** — bullets with `KTD<N>.` plain prefix (same
  format as `R1.`/`U1.`) + bold decision name + prose rationale. Legacy
  plans with unnumbered KTDs stay readable by label; do not renumber
  existing numbered ones. A `session-settled:` annotation renders as part
  of the KTD bullet's visible text, stem preserved verbatim.
- **Key Flows / Acceptance Examples** — bullets with bold leader labels
  (Trigger / Actors / Steps / Outcome / Covers / Given-When-Then).
- **Scope Boundaries** — bullets, optionally split into "Deferred for
  later" / "Outside this product's identity" sub-headings when the
  positioning distinction matters.

The agent picks more elaborate or simpler shapes based on what each
specific artifact's content needs.

## Diagrams

When the section contract calls for a diagram (flow, state machine, swim
lane, data-flow, entity/relationship, layout), write it as D2 beside the
document, in a `diagrams/` subfolder (create it only when there is a
diagram to put in it). The pipeline draws every diagram in D2, so a fenced
mermaid block is a contract break, not a style choice.

```text
documentation/requirements/business-requirements/diagrams/<concept>.d2
documentation/requirements/business-requirements/diagrams/<concept>.svg
```

Render after writing the `.d2`:

```bash
D2="${D2:-$HOME/.local/bin/d2}"
if [ ! -x "$D2" ]; then D2="$(command -v d2 || true)"; fi
"$D2" "<file>.d2" "<file>.svg"
```

Embed it next to the Flow, Key Decision, or Requirements group it
illustrates: `![<concept>](diagrams/<concept>.svg)`, with the path relative to the
document. If `d2` is not installed, still write
the `.d2` and the image link, and say in the closing summary that the SVG
was not rendered. Do not invent an SVG.

Quantitative comparisons (bar charts, scatter plots) are a table with the
data; let prose or a caption carry the interpretation.

For a **UI/layout shape**, render the region composition as a D2 grid (or
describe it in prose) — never hand-draw a box-drawing/ASCII wireframe; it
violates the no-box-drawing-characters rule and reads poorly. Screens are
designed later, in `ui-design` (Figma) and `screen-spec`.

## Inline code and code blocks

- **Inline code** for identifiers (variable names, function names,
  flag names, file paths, IDs that aren't section anchors).
- **Fenced code blocks** with language tag for code, shell commands,
  API request/response samples. Always specify the language for syntax
  highlighting and accessibility.

```markdown
The flag `--cdp-url` accepts a URL.

` ``bash
browser-use --cdp-url http://localhost:9222
` ``
```

## No process exhaust

Engineering process metadata stays out of the artifact:

- No "captured at Phase X" notes
- No `## Next Steps` pointing to the next skill
- No italic provenance lines ("*Brainstorm completed 2026-05-13*")
- No engineering-flow shepherding ("Now read this file:", "Next, run that
  command:")

This information belongs in commit messages, tool output, and agent
transcripts — not in the artifact a reader returns to weeks later.

## Frontmatter shape

Per-skill frontmatter fields are defined in each skill's section contract
(`plan-sections.md` lists plan frontmatter; `brainstorm-sections.md` lists
brainstorm frontmatter). Common rules:

- YAML at the top of the file, delimited by `---` on its own line above
  and below.
- Field names in lowercase snake_case (`created_at`, `topic`, not
  `CreatedAt`, `Topic`).
- **No status / lifecycle field.** Artifacts are point-in-time records
  (decision or discovery), not tracked work items. Do not introduce a
  mutable `status` field or an `active → completed` lifecycle — whether
  the work shipped is derived from git, not stored in the doc.
- Stable across artifact revisions — never rename or repurpose a field.

## Post-write audit

Before declaring the markdown file written, scan it for these common
slips:

- All stable IDs are plain-prefix format, not bolded.
- No HTML elements mixed in.
- No fenced mermaid block; every diagram is a `.d2` beside the document with an image link.
- All file paths are repo-relative.
- Horizontal rule separators between H2s (for Standard / Deep artifacts).
- No process exhaust (Phase X notes, Next Steps pointers, provenance
  lines).
- Tables only where 5+ uniform-shape items justify them.
- Frontmatter has all the per-skill required fields with reasonable values.
