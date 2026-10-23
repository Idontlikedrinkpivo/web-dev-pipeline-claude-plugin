# Existing schema: increment, do not redesign

Read this when a schema document already exists for the system (MODE
increment), before editing anything. The Writer half of `SKILL.md` still
holds; this is what changes when the schema is already live.

When a schema document already exists for this system, read the
`doc-versioning` skill and follow it. Edit the document in place. This
invocation is not a version event: do not touch `version` and do not add a
changelog row. The stamping commit (`doc-versioning`) writes the version
and one typed row per changed table or column. Set `migration:` to the
number of the last file in `documentation/db/migrations/` that the DBML
now reflects: it describes the body, like the DBML, so the writer keeps it
current. Two asymmetric rules govern here:

- The schema **document** grows in place — new tables and columns appended,
  existing definitions changed only when the feature changes them. The
  report's DOWNSTREAM line names each change with the type it implies, so
  the stamp can type its rows. A dropped or renamed column or table, a
  changed type, a new `NOT NULL` column without a default on an existing
  table, or a tightened constraint the code may violate is `ломает`; a new
  table or a new nullable column is `добавляет`; a reworded note with the
  same meaning is `уточняет`.
- The **database** changes only by appending a migration: the next numbered
  file in `documentation/db/migrations/` (`0002_add_room_capacity.sql`), and
  the same write updates `schema.md` so it still shows the whole current
  schema. A committed migration file is never edited — the database that
  already ran it would never see the change. A file this iteration wrote
  and nobody committed yet may still be rewritten. Name in the report
  which file the increment adds, what it does, and whether it is
  reversible; the stamp's changelog row carries it.

A greenfield schema needs no zero-downtime sequence. Once rows exist —
the packet's POPULATED says `rows: yes` for the table — read
`references/migration-safety.md` and use its safe sequence for every DDL on a
populated table, because a one-step `ALTER` there can lock or rewrite the table
under live traffic. Name the sequence and its reversibility in the report (the
stamp's changelog row carries it); do not present a destructive or locking
one-step DDL as routine.
