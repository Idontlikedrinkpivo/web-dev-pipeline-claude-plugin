# ER diagram — projection of the DBML

`db-schema-design` draws the tables it just wrote. The DBML stays the
contract. The diagram adds no table, column, or key the DBML does not
have.

## Path

The `diagrams/` subfolder next to the schema document:

```
documentation/db/schema.md
documentation/db/diagrams/er.d2
documentation/db/diagrams/er.svg
```

The schema document embeds the picture under `## ER`, after the DBML.
No `version` and no changelog on the `.d2`. Every write of the schema
document — a new migration file included — rebuilds the diagram, so it
always shows the current whole schema, like the DBML.

## Render

Layout is declared in the file. Run this from `documentation/db/diagrams/`
after writing the `.d2`:

```bash
D2="${D2:-$HOME/.local/bin/d2}"
if [ ! -x "$D2" ]; then D2="$(command -v d2 || true)"; fi
"$D2" "er.d2" "er.svg"
```

If `d2` is not installed, still write the `.d2` and the `## ER` image
link. Say in the stage close that the SVG was not rendered and name
`~/.local/bin/d2`. Do not invent an SVG. The orchestrator runs this
same command once when the `.svg` is missing. It does not edit the
`.d2`.

## What to draw

- One `sql_table` per DBML table, inside a container named after the
  schema (namespace).
- Every column: name and SQL type. Mark `primary_key`, `foreign_key`,
  and `unique` from the DBML. A column that is both PK and FK uses
  `{constraint: [primary_key; foreign_key]}`.
- One edge per `Ref`. Label it with the delete rule (`CASCADE`,
  `RESTRICT`). Crow's foot: many → one. A nullable FK uses the optional
  end (`cf-one`); a `NOT NULL` FK uses `cf-one-required`.
- A match the document states has no FK (email equality, no constraint)
  is a dashed edge with no arrowhead and a label that says there is no
  FK. Do not draw a relationship the DBML and the prose do not state.
- No `page` notes, callout boxes, or dashed comment edges. A `CHECK`
  stays in the DBML and the migration SQL; it is not a shape on the diagram.
- Every column's type cell carries a short Russian caption of what the
  attribute is, taken from that column's DBML `note:`, written as
  `type — подпись`. A caption that only repeats the column name does
  not count. Do not paste the full `CHECK` predicate into the picture.

More than 15 tables: `er.d2` shows keys only (PK, FK, unique).
Add `er-<group>.d2` per group the schema document already
named, with full columns, in the same `diagrams/` folder. Do not invent a group.

## Shape

```
vars: {
  d2-config: {
    layout-engine: elk
  }
}
direction: right

classes: {
  fk_many: {
    source-arrowhead.shape: cf-many
    target-arrowhead.shape: cf-one-required
  }
  fk_many_optional: {
    source-arrowhead.shape: cf-many
    target-arrowhead.shape: cf-one
  }
}

orders_service: "schema orders_service" {
  books: {
    shape: sql_table
    id: "bigint — внутренний ключ" {constraint: primary_key}
  }
  holds: {
    shape: sql_table
    id: "bigint — внутренний ключ" {constraint: primary_key}
    book_id: "bigint — книга этой брони" {constraint: foreign_key}
  }
  holds.book_id -> books.id: "CASCADE" {class: fk_many}
}
```

## In the schema document

```
## ER

![ER](diagrams/er.svg)
```

The picture is rebuilt from the DBML whenever this skill writes the
schema. A human edits the DBML (or asks for a column change); the
`.d2` is regenerated. Do not treat a hand-edited `.d2` as a second
schema.
