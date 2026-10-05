# Per-document exceptions

Read when the document being written or checked is a business-requirements
draft, the project map, a diagram, an implementation plan, or a DB schema
and its migrations. The shared rule for the unversioned rows — no `version`, no
changelog, no typed rows, cited without `@<version>` — is stated once in `SKILL.md` →
Registry; this file holds only what each document adds to it.

## Business requirements (unversioned)

`brainstorm` writes a working draft, not a published contract. It can
change many times in a day.

- `grilled:` still records that the grill gate closed; a later rewrite that
  changes grilled decisions clears the field and the gate runs again.
- Keep one file per product and edit it in place — a second business-requirements
  file beside `requirements/business-requirements/business-requirements.md` is still a failure.
- Frontmatter cites `stated-directly` or an unpinned path. Downstream
  `sources:` cite the BRD path with no `@<version>`.
- A rewrite is not a version and does not cascade. Offer `srs-writer` when the
  user wants the contract updated.

## Project map (unversioned)

`repo-scaffold` writes `documentation/project-map/project-map.md` — an index of paths
and how to run, not a contract. `sources:` cites the architecture path with
no `@<version>`. One file per repo; an increment that changes the tree or how to
run updates this file in place. Do not copy the foundation's §5 tree or §2 modules table into it.

## Diagrams (unversioned)

`clean-architecture-design` writes the foundation's D2 views to
`documentation/architecture/diagrams/` (`context`, `containers`, `layers`,
`stores`, `modules` — `.d2` plus the rendered `.svg`), each embedded in the
foundation section it illustrates; there is no separate diagram index. Key
scenarios get a PlantUML diagram in `scenarios/<area>/diagrams/`
(`<use-case-kebab>.puml` / `.svg`). They are projections, not second contracts: no
`version`, no changelog. A human edit of a `.d2` or `.puml` does not change the
architecture until the user asks to apply it; applying a renamed or removed
cited token is then typed on the architecture document, not on the
diagram. See `clean-architecture-design/references/architecture-diagram.md`.

The ER diagram (`documentation/db/diagrams/er.d2` / `.svg`) is the same kind
of projection of the DB schema, rebuilt in the same write. Screen specs have
no diagram.

## Implementation plan (never versioned)

A plan is a work order, not a contract. Each service version gets its own
folder, `documentation/plans/<version>/`, with one `plan.md` whose U-id
namespace starts at U1, pinned (`path@<version>`) to the spec versions it was built from; a
version that holds several changes groups them inside that one plan. The
folder name is the service version (`pipeline` → Service version), not a
document version: the plan has no `version` field and no changelog, and
**omits `grilled:`** — plans are not grill-gated. While the version is open
(no `summary.md`) its plan is revised in place; a closed version's plan stays
executable and is never edited to describe new work. Its registry downstream
is the `work` skill: name `work`. Do not treat `plan-review` as this skill's
successor.

## DB schema (document in place, database by migration)

The schema *document* is one of the contracts: edited in place, and its
`version` moves only in the commit that stamps this file. It shows the
whole current schema (DBML and notes) and no SQL. The database changes only
by appending a migration file,
`documentation/db/migrations/NNNN_<snake_slug>.sql` — unversioned, never
edited after it is committed; the schema document carries the version.

**`migration:`** in the schema's frontmatter names the last migration file
the DBML already shows (`migration: 0007` for `0007_bookings_cancel.sql`).
`db-schema-design` sets it in the same write that appends the file: it
describes the body, like the DBML, and is not a version, so a writer may
set it. The stamp checks it names the newest file in `db/migrations/`; a
schema whose `migration:` lags the folder shows tables the database will not
have, or the reverse.

A `Note` / `COMMENT ON` on a table or column that already existed is neither
a migration nor a row. A new table, a nullable or defaulted column, or an
index is a new migration now and a «добавляет» row when it is committed; a
changed or dropped column, a type, tightened nullability, an FK or a CHECK
is a new migration and a «ломает» row. The row says what the migration does. It does not add a row to the
SRS, the API, or the architecture.
