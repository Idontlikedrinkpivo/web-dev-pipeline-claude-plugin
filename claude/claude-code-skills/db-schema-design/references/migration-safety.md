# Migration safety on a populated table

Read only in increment mode, when the target table already has rows. A
greenfield `0001_init.sql` needs none of this: an empty table locks for
microseconds, so the plain DDL in `SKILL.md` is the right call there.

Every step below that says "its own migration" or "the next migration" is
its own numbered file in `documentation/db/migrations/`
(`0004_add_bookings_room_fk.sql`, then `0005_validate_bookings_room_fk.sql`).
Each file starts with `SET search_path TO <db_schema>;`. A committed file is
never edited: a step that went wrong is undone by the next file.

On a table with rows and traffic, most one-step `ALTER TABLE` forms take an
`ACCESS EXCLUSIVE` lock, scan every row, or rewrite the table. Every query
behind that lock waits, so a "small" migration becomes an outage. Each row
below trades one blocking step for several short ones.

## Timeouts first

Every such migration file starts with, after its `SET search_path` line:

    SET lock_timeout = '5s';
    SET statement_timeout = '15min';

`lock_timeout` makes the migration fail fast instead of queueing behind a
long transaction and blocking everyone queued after it. A failed migration
is retried; a stalled one takes the application down.

## Safe sequences

| Change | Unsafe one step | Safe sequence | squawk rule |
|---|---|---|---|
| Add index | `CREATE INDEX` | `CREATE INDEX CONCURRENTLY`, in its own migration, outside a transaction | `require-concurrent-index-creation` |
| Add FK | `ADD CONSTRAINT … FOREIGN KEY` | `… NOT VALID`; `VALIDATE CONSTRAINT` in the next migration | `adding-foreign-key-constraint` |
| Add CHECK | `ADD CONSTRAINT … CHECK` | `… NOT VALID`; then `VALIDATE CONSTRAINT` | `constraint-missing-not-valid` |
| Add UNIQUE | `ADD CONSTRAINT … UNIQUE` | `CREATE UNIQUE INDEX CONCURRENTLY`; then `ADD CONSTRAINT … UNIQUE USING INDEX` | `disallowed-unique-constraint` |
| New NOT NULL column / set NOT NULL | `ADD COLUMN … NOT NULL`, `SET NOT NULL` | add nullable → backfill in batches → `CHECK (c IS NOT NULL) NOT VALID` → `VALIDATE` → `SET NOT NULL` (PG ≥ 12 skips the scan) → drop the CHECK | `adding-not-nullable-field` |
| Column with a volatile default | `ADD COLUMN … DEFAULT gen_random_uuid()` (rewrites the table) | add without default → backfill → `SET DEFAULT` | `adding-field-with-default` |
| Rename column / table | `RENAME` | expand/contract: add new → backfill and dual write → switch reads → drop old in a later release | `renaming-column`, `renaming-table` |
| Change column type | `ALTER COLUMN … TYPE` | new column + backfill + switch (a no-rewrite widening such as `varchar(n)` → `text` is fine) | `changing-column-type` |
| Drop column | `DROP COLUMN` while code reads it | stop reading it in code first; drop in a later migration | `ban-drop-column` |

`VALIDATE CONSTRAINT` scans existing rows under a lock that still allows
reads and writes, which is why it is split from the `ADD`. `CONCURRENTLY`
cannot run inside a transaction; when the migration tool wraps each file in
one, give the index its own file: the runner `repo-scaffold` wires applies
a file that contains `CONCURRENTLY` outside a transaction. Name that in the
report too, so the changelog row carries it.

## Record and lint

In the report, name which sequence this increment uses and whether each step
is reversible; the stamp writes it into the schema changelog row. Dropping or
renaming a column is `ломает` there, even when the sequence makes it safe for
the running code: other documents and the code cited the old name. A multi-step change spans several
migration files; list their file names in order. `schema.md` shows the
schema after the last of them.

When `squawk` is installed, run `squawk documentation/db/migrations/<NNNN>_<slug>.sql` on each new file and report its
findings in the stage close. Disable a rule only with the reason written in
the report (the changelog row carries it), so the next reader knows the lock was a decision and not an
oversight.
