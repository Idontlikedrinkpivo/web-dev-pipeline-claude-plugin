---
name: db-schema-design
description: >-
  Designs the relational schema from the SRS: DBMS, tables, keys, indexes, migrations, ER diagram. Use for «схема БД»,
  «спроектируй базу», «какие таблицы нужны», «Postgres или MySQL». Not API or entities.
---

# Database Schema Design

## Orchestrator (session)

The session writes no DBML, no migration file, and no ER `.d2`. The
dispatched writer settles them and nests `doc-typist` to print them. A
report whose `DELEGATED` is not `doc-typist` comes back until it is. The
session dispatches the typist only for a print defect (step 4).

1. Stop if the SRS is missing — no actors, no use cases, no rules. Name
   `srs-writer`. Do not wait for
   `clean-architecture-design`: it runs after this stage, so the writer
   reads invariants from the SRS and decides each constraint itself (§4).
   No `schema.md` but the repository already runs a database — another
   tool's migrations (`alembic/`, `prisma/migrations/`, `drizzle/`, SQL
   files outside `documentation/`) or ORM models: stop and ask whether to
   document that schema as it is, in the namespace it lives in (`public`
   included), or to design a new one beside it. The greenfield branch
   would otherwise lay a second schema over a live one. From `upgrade-docs`
   (`MODE as-is`) that is answered — as it is — and the code stands in for a
   missing SRS (`upgrade-docs/references/as-is.md`).
2. When a schema document already exists, read `doc-versioning`.
   The writer runs as a subagent and cannot ask the user. Before dispatch,
   settle what only the user can: the DBMS and its major version when no
   file states them (a manifest or compose in the repo, the SRS, an
   existing `schema.md`) — this stage owns that decision, and the
   architecture takes it from here — and the classification of a field
   that looks sensitive when the SRS does not say (§6). One question per
   message (`pipeline/references/question-format.md`); each answer goes
   into the packet's ANSWERS. On an increment, fill POPULATED for every
   existing table the slice changes: `rows: yes` when the migration that
   created it is in a released tag (`git ls-tree -r --name-only
   v<last version> documentation/db/migrations/`), `rows: no` when this
   unreleased iteration created it; with no tag and a live database, ask.
3. Read `executor-catalog` and
   `executor-catalog/references/design-complexity.md`. Dispatch
   exactly one writer with
   `executor-catalog/references/design-writer-prompt.md`. Before the
   `Agent` call, write `Grade | Executor | subagent_type` for the design
   row the grade picked, then dispatch it without asking which model.
   Follow the catalog dispatch contract: `subagent_type` is `dev-pipeline:<row>`
   and the call passes no `model` (the agent file holds it) unless the
   user named one. A missing agent or a rejected alias is a stop.
4. Inspect the files on disk. Run
   `python3 "${CLAUDE_SKILL_DIR}/scripts/table_docs.py" . --check`: a
   missing or name-echoing table `Note` or column `note:` is a print
   defect — dispatch `doc-typist` `MODE revise` with one `SETTLEMENT` line
   per line it prints, the text taken from the SRS (`executor-catalog` →
   Nesting), until none is left. Its migration lines (§0's schema header)
   send the writer back for a file this slice wrote; on an older, committed
   file they go into the report only, since that file is frozen. Then run
   `python3 "${CLAUDE_SKILL_DIR}/../doc-versioning/scripts/doc_check.py" . --only documentation/db/`:
   each `migrations` line (a file the main branch has, changed or deleted;
   `migration:` behind the newest file) sends the writer back — that change
   is a new file. A missing `documentation/db/diagrams/er.d2`, or a slice
   whose tables have no new file in `documentation/db/migrations/` (not in
   `MODE as-is`: no migration is written there), sends the writer back.
   When that `.d2` exists and the `.svg` does not, run the render command
   in `references/er-diagram.md` once. Do not edit the `.d2`. Then
   regenerate the table documents (Output, item 3):
   `python3 "${CLAUDE_SKILL_DIR}/scripts/table_docs.py"`. A
   `BLOCKED` with a question for the user is asked and sent back to the
   same row; any other `BLOCKED` / `HARDER_THAN_EXPECTED` escalates one
   design row (`executor-catalog` → Escalation); every round goes on while
   it makes progress (`pipeline` → `references/convergence.md`).
5. Close the stage by asking, per `pipeline` → "Asking before a
   transition". First ask about `doc-review`. Run: run it; it returns
   without asking the next stage. Skip: name it in the report. Stop:
   stop. After a run or a skip, ask the one next stage the table names. The writer does not run
   those. `doc-review` edits the body and does not bump. See
   `doc-versioning`.

## Writer (dispatched)

You settle the schema. You do not print it. When every decision this
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. That
row writes the schema document, the migration file(s), and the ER `.d2` / `.svg`. A gap this skill calls
BLOCKED returns before that dispatch. Read the files back. One
correction dispatch, then the report. Do not type the correction, and
do not paste the finished schema into the typist's prompt.

Translate the SRS into a concrete relational schema, one slice at a
time (Context Required). ORM-agnostic, PostgreSQL-flavored SQL (principles apply to
MySQL/MariaDB). Table and column `Note` / `COMMENT ON` text is Russian.
Do not translate identifiers.

If the SRS you were handed has no actors, use cases, or rules for this
slice, write nothing: return `STATUS BLOCKED` with the blocker "SRS
missing — run srs-writer".
A table guessed from a feature name becomes a contract the API and the
code then have to honour.

## Scope

**Not for:** a multi-tenant isolation strategy (`tenant_id` + RLS only
when the SRS calls for multi-tenancy); table partitioning (past ~100M
rows, not a day-one decision); diagnosing slow queries on a live database
(`EXPLAIN ANALYZE`, a production-debugging task).

## Context Required

| Required | Source |
|---|---|
| Entities, stored state, and the rules that must survive a restart | SRS actors, use cases, business rules |
| What a use case accepts and returns, and whether a value may be absent, when that data is stored | SRS, that use case |
| Which reads the use cases name | SRS |
| DBMS and its major version (PostgreSQL 18, MySQL 8.4) | A file the packet names, or the answer in ANSWERS. Recorded once, in «Решения по базе» (Output) |
| PII / credential / secret classification, if any (§6) | SRS Security NFR rows, or the answer in ANSWERS |
| Whether an existing table already holds rows | POPULATED — it picks the safe migration sequence |

You cannot ask the user. If one of these is still unresolved, return
`STATUS BLOCKED` with that one question; the session asks it and sends
the answer back.

Do not invent a layer, a port, or a file tree — those are architecture's
decisions, made after this schema.

Design the schema for **one vertical slice's use cases**, not every table
implied by the whole SRS. Repeat this skill per slice.

**This skill runs before `openapi-spec-generator`.** The names and types chosen
here are what the HTTP contract has to agree with, so the order is not
cosmetic: a spec published first forces either a rename here or a translation
layer between the two. When an OpenAPI spec already exists for this slice,
treat its property names as given and flag a mismatch instead of silently
picking a different column name.

## Existing schema: increment, do not redesign

When a schema document already exists, read `references/increment.md`
before editing: the document grows in place and is never re-versioned
here, the database changes only by a new numbered migration, a committed
migration is never edited, and a populated table (POPULATED) takes the
safe sequence of `references/migration-safety.md`. A greenfield schema
needs none of it.

---

## 0. Schema (namespace), not `public`

Every table lands in a schema named after the project or service
(`orders_service`, `hr_analyzer` — `snake_case`), never in PostgreSQL's
default `public`: `public` names no owner, is writable by every role on
older servers, and collides as soon as a second service shares the
instance. Decide it before the first `CREATE TABLE` ships — moving tables
out of `public` later is a coordinated multi-step change across every
table, connection string, and migration config.

```sql
-- documentation/db/migrations/0001_init.sql opens with these two lines:
CREATE SCHEMA IF NOT EXISTS <project_name>;
SET search_path TO <project_name>;
```

Every later file (`0002_…`) opens with the `SET search_path` line. The
statements after it stay unqualified for readability, and each file is
still correct on its own: the application's migration tool runs these
files as they are, straight from `documentation/db/migrations/`, and
without the `SET` line every unqualified table would land in `public` —
the exact mistake this section exists to prevent. The DBML names the
schema explicitly. Point the application at it both ways:

- **Connection**: `search_path=<project_name>` on the connection string or
  session (`?options=-csearch_path%3D<project_name>` for `postgresql://`),
  so unqualified names in code resolve here, not in `public`.
- **Migration tool**: its version table in this schema too (Alembic
  `version_table_schema`, Flyway `schemas`) — otherwise its history lives
  in `public` and two services collide on that bookkeeping table.

`deploy-topology` carries the same schema name into every environment's
connection string; only the server changes per environment.

A database that already lives in `public`, documented as it is (the
user's answer in ANSWERS), stays there: moving it is a planned change of
its own, not a side effect of documenting it. Its tables are described,
not created — no `CREATE TABLE` for a table that exists.

## 1. From the SRS to tables

Map, don't invent.

| SRS | Schema |
|---|---|
| An entity whose state must survive a restart | One table, `snake_case`, plural (`orders`, not `Order`) — one per entity, not one per class |
| A value that belongs to that entity | Columns on that entity's table (not a separate table, unless it repeats) |
| A one-to-many the use cases store | FK column on the "many" side + index on that FK |
| A named error a use case returns | Usually **not** a table — it's a response shape, not stored state (unless the SRS says a rejected attempt is stored) |
| A read the use cases need as its own stored shape | Its own table or a view, named from that read |
| A rule this skill classifies as `CHECK` / `UNIQUE` / `FK` | That constraint — see §4. The later entity method copies it; the constraint is a defense, not a second owner |
| A rule this skill leaves unconstrained | **No** DB constraint — the later entity method is the only enforcement |

```sql
-- ✅ snake_case, plural
CREATE TABLE orders (...);
CREATE TABLE order_items (...);

-- ❌ singular, mixed case, abbreviations
CREATE TABLE Order (...);
CREATE TABLE tbl_usr_prof (...);
```

### Primary Keys

| Column | On which tables |
|---|---|
| `id bigint GENERATED ALWAYS AS IDENTITY` — the primary key and every FK's target | Every table, always |
| `public_id uuid NOT NULL UNIQUE` (v7 by default; v4 when the SRS says creation time must not leak) — the id the API shows | Added to every table whose rows appear in the API contract |

```sql
CREATE TABLE orders (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- internal FK target
    public_id   uuid NOT NULL DEFAULT uuidv7() UNIQUE,           -- PG 18+; see the note below for older versions
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()                -- the repository's UPDATE sets it; DEFAULT fires on insert only
);
```

`uuidv7()` exists from PostgreSQL 18 — read the major from ANSWERS or the
file that states it. On an older version `gen_random_uuid()`
gives v4, which is not time-ordered: either the application generates the v7
id and the column has no default, or v4 is a decision written in the column's
note with the reason — never a silent swap.

**How the API names keys.** The contract never shows the internal `bigint`
key or a `bigint` reference. A table's `public_id` is the resource's `id`
in the API; a reference column `<thing>_id` (the referenced table in the
singular: `room_id` → `rooms`) keeps its name in the API and carries the
referenced row's `public_id`; a path parameter is `<resource>_id`
(`/bookings/{booking_id}`). `openapi-spec-generator` maps by this rule and
`docs-consistency` checks it; name every reference column so the rule
gives the API name.

### Columns and types

- `NOT NULL` by default; nullable only when the SRS says the value may
  be absent — an unasked-for `NULL` is a third state every reader must
  handle.
- `created_at` on every table. `updated_at` only on a table this slice
  updates, and its note names who maintains it — a `BEFORE UPDATE`
  trigger emitted in the migration, or the repository's `UPDATE`
  (`DEFAULT now()` alone fires only on insert).
- Amounts: `numeric(p,s)` (or integer minor units), currency in its own
  column — not `money`, `float` / `real`.
- Text: `text`; a length the SRS names is `CHECK (char_length(col) <= n)`
  — not `varchar(n)` / `char(n)` by default.
- Instants: `timestamptz`; `date` for a calendar day with no time — not
  `timestamp` without time zone.
- Ids and counters that can grow: `bigint` (identity for keys) — not
  `int` / `serial` / `bigserial`.

### Relationships and ON DELETE

Every reference is a real `FOREIGN KEY` with an explicit `ON DELETE`
(table below) and an index on the FK column — an unenforced reference
is an orphan waiting to happen. In DBML it is a standalone `Ref: … [delete:
…]` line: an inline `ref:` cannot carry the action.

`references/schema-patterns.md` → Foreign keys in SQL holds a one-to-many and a junction-table example;
read it when the slice has a many-to-many.

| `ON DELETE` | When |
|---|---|
| `CASCADE` | Child is meaningless without the parent |
| `RESTRICT` | Deleting the parent while children reference it should be an error |
| `SET NULL` | The reference is optional and should just clear |

---

## 2. Normalization

Start at 3NF. Denormalize **only** with a measured reason (a real read:write
ratio problem you've profiled) — not by default, and not because a join felt
inconvenient.

If a read model needs a joined/aggregated shape, denormalize only when
the SRS names that read shape and a reason to store it (a list screen too
slow to join, a report over history). Give it its own table or
materialized view and say in its `Note` which SRS id asked for it; a
denormalization nobody asked for is two copies to keep in sync.

---

## 3. Indexing

Index only what this slice's declared queries need — not every column: the
WHERE, JOIN, and ORDER BY … LIMIT columns of those queries, composite in the
query's column order, partial when the hot query filters a small subset.

```sql
-- Composite: matches "WHERE user_id = ? AND status = ? ORDER BY created_at DESC"
CREATE INDEX idx_orders_user_status_created
ON orders(user_id, status, created_at DESC);

-- Partial: most rows are not 'pending', but that's the hot query
CREATE INDEX idx_orders_pending ON orders(created_at DESC) WHERE status = 'pending';
```

---

## 4. Turning SRS rules into constraints

You decide the constraint. A rule that is a predicate SQL can check, a
uniqueness, or a reference becomes a real `CHECK`, `UNIQUE`, or `FK` —
not a comment. A rule that is a workflow, a permission, or a clock stays
out of the schema. The column note names which of the two it is, so
architecture can copy `none` or the constraint you wrote. Architecture's
invariant table copies your constraint; you decide it here.

```sql
-- A numeric bound
ALTER TABLE lots ADD CONSTRAINT lots_weight_positive CHECK (weight_kg > 0);

-- A named, closed set of states (see §5 for the enum-vs-text tradeoff)
ALTER TABLE orders ADD CONSTRAINT orders_status_valid
  CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'));

-- Uniqueness across a combination of columns
ALTER TABLE order_items ADD CONSTRAINT order_items_unique_line
  UNIQUE (order_id, product_id);
```

Do **not** encode a procedural rule as SQL. That rule belongs to the
entity architecture will write later. A constraint and an entity method
for the same check will drift.

---

## 5. Status columns and other patterns

### Enum-like status columns

```sql
-- Text + CHECK — easiest to migrate later. Default choice.
ALTER TABLE orders ADD COLUMN status text NOT NULL DEFAULT 'pending'
  CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'));
```

Use a native `ENUM` type only if the set of values is genuinely frozen —
`ALTER TYPE` on a live enum is painful.

The closed list of codes is owned **here**, not in the architecture
composition table. For every status (or other enum-like) column, emit a
reader table `## Закрытые наборы значений` with the columns
«Таблица.поле · Код · Подпись»: one row per allowed code. «Подпись» is the
human name of the code when a read shows one. Architecture and OpenAPI copy this column; they do
not keep a second list. Do not add a «нет» row for entities without a
status. Who may set which code is a later entity rule, not a CHECK,
unless the SRS states a predicate SQL can enforce.

### Situational patterns

Read `references/schema-patterns.md` when the SRS asks for soft delete,
a row that may belong to one of several parent kinds, or free-form
attributes. Every field the SRS names (email, status, price) is a column,
never a JSONB key, because only a column can carry a type and a constraint.

---

## 6. Sensitive Data (PII, Secrets)

Only when the SRS flags a column as PII, a credential, or a secret — do
not invent classification the SRS never stated. A credential, token, or
API key is never stored raw: a leaked table must not leak the secret, so
store a hash (and a non-secret lookup prefix when one is needed).

Read `references/sensitive-data.md` when any column is flagged: it holds
the pattern per data kind, the hashed `api_keys` example, and the limits
on encryption and audit tables.

---

## Output

Emit all four, and make sure they agree. The DBML and the ER live in
`documentation/db/schema.md` and `documentation/db/diagrams/`; the SQL
lives only in migration files — the document has no SQL block:

1. **DBML** — table definitions with relationships, each table and column with its note, because the table documents
   and every later stage read the meaning from these notes:
   - **Every table has a table-level `Note`** that opens with one or two plain sentences on what a row is — the entity
     or use-case state it stores — before any detail.
   - **Every column has a `note:`** whose first sentence is its description for readers — plain, whole on its own, ids
     at its end — because the table documents show only that sentence; details (which trigger sets it, why there is no
     index) come after it.
   - **No note that echoes the name** (`orders` → "orders", `id` → "id") — it tells the reader nothing and counts as
     missing.
   - **Notes come from the SRS** — do not invent a purpose the inputs did not decide.
   - **No UI data** — a note says what the data means, never how a screen shows it, and no column exists only to drive
     a widget or a layout (a menu order, a colour, an icon) unless the SRS requires it as data (`doc-versioning` →
     `references/writing-rules.md` → What, not how it looks).

```dbml
Table holds {
  id bigint [pk, increment, note: 'Внутренний ключ соединения; в API не попадает']
  public_id uuid [unique, not null, note: 'Идентификатор брони, который отдаёт контракт PlaceHold']
  book_id bigint [not null, ref: > books.id, note: 'Книга, которую резервирует эта бронь']
  starts_at timestamptz [not null, note: 'Начало брони']
  ends_at timestamptz [not null, note: 'Срок брони; не позже starts_at + 7 дней — CHECK holds_period_max_7d']

  Note: 'Одна бронь, созданная сценарием PlaceHold'
}
```

`Table holds [note: '...']` is the same contract as a `Note:` block inside
the table — pick one, not both.

2. **Migration SQL** — files in `documentation/db/migrations/`, named
   `NNNN_<snake_slug>.sql`, each opening with §0's header. Greenfield:
   `0001_init.sql`, then the actual `CREATE TABLE` statements (with
   constraints and indexes from §3–4) for one vertical slice. Increment:
   the next number, holding only this slice's DDL (`references/migration-safety.md`
   on a populated table). Carry the same note text as `COMMENT ON TABLE` /
   `COMMENT ON COLUMN` so the files and the DBML agree, and give every named
   `CHECK` a `COMMENT ON CONSTRAINT <name> ON <table> IS '<one plain sentence>'`
   — what the rule guarantees, in a reader's words, not the expression
   («Тип файла совпадает с его расширением: pdf, png, jpg, docx, xlsx, pptx»).
   DBML has no place for it; the table documents show that sentence instead
   of the SQL. No version and no
   changelog in a migration file; `schema.md`'s changelog row names it.

3. **Table documents** — one `documentation/db/tables/<table>.md` per table, generated from the DBML and
   `## Закрытые наборы значений` by this skill's `scripts/table_docs.py` (columns: Поле, Тип данных,
   Свойства, Значение по умолчанию, Связь, Допустимые значения, Описание; then the incoming references with
   what deleting a row does). The orchestrator runs it after the files land (step 4), and the plugin's hook
   reruns it after any edit under `documentation/db/`; the writer and the typist do not. Never edit those
   files — edit the DBML; they go into the same commit.

4. **ER** — `documentation/db/diagrams/er.d2` and `er.svg`, embedded under `## ER`. Follow `references/er-diagram.md`. The picture is a projection of this DBML: same tables, columns, and keys, nothing added. Render the SVG in the same write. Questions go in `documentation/db/open-questions.md`, not in a section of the schema.

The wrapping `documentation/db/schema.md` opens with
frontmatter per `doc-versioning` → Frontmatter (`version:` the open
iteration's service version on a new document — `0.1.0` on greenfield;
`migration: 0001`, the last migration file the document covers;
`updated:`; and `sources:` pinning the SRS by the version it was built
from — `documentation/requirements/srs/srs.md@0.1.0`), then H1, then the
`## Журнал изменений` table from `doc-versioning` (newest row first;
a new document has the one row `| <версия> | <дата> | первый выпуск | — | — |`), then
**`## Закрытые наборы значений`** when any table has a status (or other
closed-set) column, then `## Решения по базе`, then the DBML and the ER —
and no other section. It always shows the whole
current schema — after an increment, the DBML reads as if every migration
so far had run.

**`## Решения по базе`** — what holds for the whole schema, a short list, one
line each with its reason. The first line is the DBMS and its major version
(«СУБД: PostgreSQL 18 — …»): decided at this stage, the one home of that
decision; the architecture's §1 «Стек» and `repo-scaffold` take it from
here. Then the namespace (§0) and who creates it;
how migrations run (the files in number order, each once, what sets
`search_path` — the runner itself is the stack's, named by the
architecture); what makes keys (`uuidv7()` on PostgreSQL 18+, else what the
note under Primary Keys decided); collation or extensions the schema relies on. Not here: which SRS
requirements the tables serve (the column notes and the table documents
carry them), what each migration changed (its changelog row and the header
of its file), and how a release cuts over or rolls back (the deploy
document, `deploy-topology`). Do not put the changelog at the end.
Headings and columns are Russian; `DBML` and `ER` stay — terms of the trade.

Field names in the DBML and the migration SQL must match the SRS use-case inputs
and outputs — the API-contract step reads directly off these names.

## Before you finish

- [ ] Project schema, not `public`: migration headers, connection `search_path`, and version table as §0 sets them — §0
- [ ] This slice's DDL is a new numbered file in `documentation/db/migrations/` (as-is: none — `migrations:` names the project's folder); no committed file edited; `schema.md` has no SQL block, shows the whole current schema, and its `migration:` names the last file — Output
- [ ] One table per stored entity; PKs, FKs with `ON DELETE`, `NOT NULL`, timestamps, and types as §1 says; reference columns named `<thing>_id` so the API names follow — §1
- [ ] «Решения по базе» opens with the DBMS and its major version — Output
- [ ] 3NF; any denormalization names its SRS id — §2
- [ ] An index for every filter, join, and sort this slice declares, and nothing more — §3
- [ ] Every SQL-expressible rule is a constraint; every other rule has none — §4
- [ ] `## Закрытые наборы значений` for every closed-set column — §5
- [ ] No raw secret column — §6
- [ ] Every table and column has a note that says more than its name (`table_docs.py --check` prints no line); DBML, migration SQL, and ER agree; names match the SRS — Output
- [ ] Every named `CHECK` has a `COMMENT ON CONSTRAINT` sentence in its migration — Output
- [ ] Each column note opens with a plain sentence a reader understands alone; `documentation/db/tables/` regenerated (`table_docs.py`) and matches the DBML — Output

## Closing

The report has exactly the packet's fields: FILE WRITTEN names the
schema document and each migration file written, DIAGRAM WRITTEN the ER `.d2` (with `svg: missing` when
it did not render). A slice table left out, or a migration not written,
goes to CONCERNS. Do not run `doc-review` or `pipeline` — the orchestrator
closes the stage.
