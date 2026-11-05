---
name: typescript-drizzle-orm
description: >-
  Internal: Drizzle ORM rules (repositories, transactions, keyset pages, migrations); read by work's executors before
  Drizzle code.
---

# Drizzle ORM

## Essentials

Read first, in full; the sections below hold the detail — the packet names the ones this unit needs.

- Tables transcribe `documentation/db/schema.md`; a missing table is a question, not an invention → Rules 1.
- Migrations are the SQL files from `db-schema-design`: no `drizzle-kit generate`, never edit a committed file
  → Rules 10.
- The database enforces what races (unique, FK, CHECK), and a race test proves it; a pre-check alone fails
  → Rules 5.
- Classify driver errors by `sqlState(e)` through the `cause` chain, never `e.code` or the message
  → Rules 6, The reviewer checks 4.
- `40001` / `40P01` is rethrown; only the `bootstrap/` helper reruns the whole use case → Rules 9,
  The reviewer checks 8.
- Idempotent create: unique key plus `onConflictDoNothing()` and a re-read of the winner → Rules 9.
- A repository returns entities through the mapper (restore factory), never records → Rules 3, 4.
- One query per read, and keyset pages (`limit + 1`, never `.offset(`) → Rules 7, 8.
- `sql.raw` never takes a value from a request or a record; a dynamic identifier goes through an allow-list
  → Rules 13.
- A business rule in a query uses its owner's constant, never a literal → Rules 11.

## Which layout applies

The cases (architecture document, Framework-first, existing repo) are in
`typescript/references/which-layout-governs.md`, shared by the backend and test skills of both stacks — read it
first. Drizzle's placement in them:

- **An architecture document exists**: table definitions and records live in `adapters/persistence/`; the
  repository adapter implements the port the use case owns and maps records to entities explicitly. The domain
  imports nothing from `drizzle-orm`, HTTP, or validation libraries.
- **Framework-first**: a route or a small service queries the tables directly.
- **Existing repo**: its layout (for example `src/db/schema.ts`, `src/<feature>/<feature>.repository.ts`), its
  return types (rows or entities) and its error classes; no mappers introduced unasked.

## Rules

1. **Tables follow the schema document.** `db-schema-design` owns tables, columns, and constraints
   (`documentation/db/schema.md` and the migration files in `documentation/db/migrations/`);
   transcribe them: `timestamptz` instants (a timestamp column
   with time zone), the CHECK / UNIQUE / FK constraints it declares, an enum or CHECK for a closed
   set of values. A table the task needs but the document lacks is a question, not an invention.
   Brownfield: extend `schema.ts` the way it is already written.
2. **Records are inferred, not retyped.** `typeof table.$inferSelect` / `$inferInsert` (or the
   `InferSelectModel` helpers) next to the table definition. A hand-written interface mirroring
   columns drifts at the first rename.
3. **Mapping lives in the repository adapter.** A mapper module beside the repository has
   `toEntity(record)` and `toRecord(entity)`; the entity has no `fromRow` / `toRow` and never sees a
   record type. Reconstitute through the entity's restore factory, not its create factory, so
   loading an old row does not re-run creation rules. One round-trip test per mapper
   (`typescript/references/shared-test-rules.md` → 1).
4. **A repository answers in domain terms.** It returns entities or read models, never records or
   HTTP bodies. "Not found" is `null` or a named error, as the port signature says. A constraint
   violation it can expect (duplicate email, dangling reference) becomes a named domain or
   application error; the HTTP status is mapped later by the error handler. It never throws an
   HTTP error class. Brownfield: reuse the error class the repo already throws for that case, but
   keep the classification in the repository or a db-error helper it calls, not in a route.
5. **The database enforces what races, and a race test proves it** (`typescript/references/shared-test-rules.md`
   → 2, written by `vitest`). A unique index, FK, or CHECK holds under concurrent writes; an app-side "check,
   then insert" does not. Keep the pre-check if it gives a nicer error, and also classify the violation, because
   two instances can pass the check together (`typescript/references/conflicts-and-retries.md` → rules 1, 5).
6. **Classify driver errors by SQLSTATE read through the `cause` chain** (`sqlState(e)`,
   `references/repository-adapter.md` → Reading the SQLSTATE), never the message: Drizzle wraps the driver error,
   so `e.code` on the outer one is not the SQLSTATE. What `23505`, `23503`, `23514`, `40001` and `40P01` each
   become is `conflicts-and-retries.md` → rules 1–3. The driver message never goes into a client-facing detail;
   it carries SQL and parameters.
7. **One query per read.** Load a list with its related rows through one join or relational query,
   never one query per item in a loop.
8. **Keyset pagination**, when the contract pages a collection: `ORDER BY` the sort columns plus the
   id as tie-breaker, the compound predicate `(a < x) OR (a = x AND id < y)`, `limit + 1` rows to
   know whether a next page exists, never `.offset(`. The cursor carries the stored value at full
   precision. Encoding and validating the cursor is the HTTP layer's job (`typescript-fastify`).
9. **Transactions.** A single-aggregate save is one transaction inside `repository.save`; a write
   spanning aggregates goes through a `UnitOfWork` port only when the architecture names one.
   Idempotent create: a unique constraint on the key plus `.onConflictDoNothing()` (or a caught `23505`)
   and a re-read of the winner, never an in-process map (`conflicts-and-retries.md` → rule 4). A
   serialization failure or deadlock is rethrown, and `rerunOnConflict`, the one helper `bootstrap/` wires,
   reruns the use case's whole run (`repository-adapter.md` → Reading the SQLSTATE; rule 2).
10. **Migrations are the SQL files in `documentation/db/migrations/`**, written by `db-schema-design`;
    `schema.ts` follows them, not the other way round. Do not `drizzle-kit generate` them — that
    writes a second migration history from `schema.ts`. Apply them with the command `repo-scaffold`
    wired. Drizzle's `migrate()` reads only drizzle-kit's own folder format, which plain numbered
    files are not, so the default is a plain SQL runner; point `migrationsFolder` there only after
    checking the installed version reads such files. Never edit a committed file — a change is the
    next file.
11. **A query applies a business rule only by its owner's constant.** A filter by status or role
    imports the list from the domain module (the domain model's «Кто ещё применяет»), never a
    literal in SQL; an adapter writes what the domain decided and never re-derives the rule, an
    upsert's conflict branch included.
12. **Options, not a checklist.** Relations, optimistic locking (a version column in every
    update's `WHERE`), and pool tuning only for a present need. The driver owns its pool: close it
    in the existing shutdown path, no second tracker.
13. **Raw SQL binds every value.** The `sql` template tag sends each `${…}` as a bound parameter, so a value goes
    there and only there. `sql.raw(...)` never takes a value from a request or a stored record — only a literal
    the code owns: it is pasted into the statement as text, and a value in it is injection even when the app
    produces it today, because the next caller passes a request field through the same function. A dynamic column
    or table name (a sort field, a report's table) goes through an allow-list map from the request's word to the
    column or table object (or `sql.identifier` of a literal from that map), never `sql.raw` of the input.

## Shape of a repository adapter

```typescript
// adapters/persistence/user.mapper.ts — the only place that knows both shapes
export const toEntity = (r: UserRecord): User =>
  User.restore({ id: UserId.from(r.id), email: Email.from(r.email), createdAt: r.createdAt })
export const toRecord = (u: User): NewUserRecord =>
  ({ id: u.id.value, email: u.email.value, createdAt: u.createdAt })

// adapters/persistence/user.repository.ts — implements application's UserRepository port
async save(user: User): Promise<void> {
  try { await this.db.insert(users).values(toRecord(user)) }
  catch (e) { if (sqlState(e) === '23505') throw new EmailAlreadyTaken(user.email, { cause: e }); throw e }
}
```

Error helper, pagination, idempotent insert, optimistic lock, tenant predicate, and the migration
cases: [references/repository-adapter.md](./references/repository-adapter.md).

**Version-sensitive points** — [references/version-checks.md](./references/version-checks.md). In a `work` packet
their answers come in `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead
of fetching docs. Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **No `drizzle-kit generate`, no `meta/` journal, no edited committed migration file**; a schema change arrives as
   the next SQL file from `db-schema-design`, and `schema.ts` follows it.
2. **A paged read is keyset**: sort columns plus the id, the compound predicate, `limit + 1`, never `.offset(`.
3. **One query per read** — no query per item in a loop.
4. **An expected constraint violation is classified by SQLSTATE read through the `cause` chain** (and the
   constraint name when a table has several) into a named error; the driver message never reaches a client.
5. **A guard against a double action has a race test against the real database** (`vitest`), not only a
   pre-check.
6. **A repository returns entities or read models through the mapper**, which has a round-trip test; a business
   rule in a query uses its owner's constant, never a literal.
7. **No `sql.raw(...)` of a value from a request or a record**: values go through the `sql` tag's `${…}`, a dynamic
   identifier through an allow-list map to the column or table object.
8. **`40001`/`40P01` is rethrown unchanged by the repository and rerun only by the `bootstrap/` helper**, around the
   use case's whole run; an idempotent create re-reads the winner (`typescript/references/conflicts-and-retries.md`).
