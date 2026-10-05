---
name: typescript-drizzle-orm
description: >-
  Persistence with Drizzle ORM in TypeScript: repository adapters that map
  records to domain entities, queries and joins, keyset pagination,
  transactions, idempotent inserts, driver-error classification, applying
  the SQL migration files. Use when code imports drizzle-orm or drizzle-kit, or a task
  adds or changes a repository, query, transaction or migration. Tables
  follow the schema document; not for designing tables, HTTP routes
  (`typescript-fastify`), or validation (`zod-skill`).
---

# Drizzle ORM

## Which layout applies

- **An architecture document exists** (`clean-architecture-design`): follow its foundation §5 file tree.
  Table definitions and records live in `adapters/persistence/`; the repository adapter implements
  the port the use case owns and maps records to entities explicitly. The domain imports nothing
  from `drizzle-orm`, HTTP, or validation libraries.
- **No architecture document, existing repo:** follow the repo's layout (for example
  `src/db/schema.ts`, `src/<feature>/<feature>.repository.ts`), its return types (rows or
  entities), and its error classes for the change at hand. Do not restructure or introduce
  mappers unasked. A new business rule still goes into a module that imports no Drizzle, Fastify,
  or Zod, not into the repository or a route — say so in one line of the final answer.

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
   loading an old row does not re-run creation rules. One round-trip test per mapper: every field
   set to a non-default value, entity → record → entity equal.
4. **A repository answers in domain terms.** It returns entities or read models, never records or
   HTTP bodies. "Not found" is `null` or a named error, as the port signature says. A constraint
   violation it can expect (duplicate email, dangling reference) becomes a named domain or
   application error; the HTTP status is mapped later by the error handler. It never throws an
   HTTP error class. Brownfield: reuse the error class the repo already throws for that case, but
   keep the classification in the repository or a db-error helper it calls, not in a route.
5. **The database enforces what races.** A unique index, FK, or CHECK holds under concurrent writes;
   an app-side "check, then insert" does not. Keep the pre-check if it gives a nicer error, and
   also classify the constraint violation, because two instances can pass the check together.
6. **Classify driver errors by SQLSTATE read from the wrapped error** (walk the `cause` chain), not
   from the message: unique `23505`, FK `23503`, check `23514`, serialization `40001`, deadlock
   `40P01`. Never put the driver message into a client-facing detail; it carries SQL and parameters.
7. **One query per read.** Load a list with its related rows through one join or relational query,
   never one query per item in a loop.
8. **Keyset pagination**, when the contract pages a collection: `ORDER BY` the sort columns plus the
   id as tie-breaker, the compound predicate `(a < x) OR (a = x AND id < y)`, `limit + 1` rows to
   know whether a next page exists, never `.offset(`. The cursor carries the stored value at full
   precision. Encoding and validating the cursor is the HTTP layer's job (`typescript-fastify`).
9. **Transactions.** A single-aggregate save is one transaction inside `repository.save`; a write
   spanning aggregates goes through a `UnitOfWork` port only when the architecture names one.
   Idempotent create: a unique constraint on the key plus an insert that does nothing on conflict
   (or catches `23505`) and re-reads the winner. Never an in-process map as the source of truth.
10. **Migrations are the SQL files in `documentation/db/migrations/`**, written by `db-schema-design`;
    `schema.ts` follows them, not the other way round. Do not `drizzle-kit generate` them — that
    writes a second migration history from `schema.ts`. Apply them with the command `repo-scaffold`
    wired. Drizzle's `migrate()` reads only drizzle-kit's own folder format, which plain numbered
    files are not, so the default is a plain SQL runner; point `migrationsFolder` there only after
    checking the installed version reads such files. Never edit a committed file — a change is the
    next file.
11. **Options, not a checklist.** Relations, optimistic locking (a version column in every
    update's `WHERE`), and pool tuning only for a present need. The driver owns its pool: close it
    in the existing shutdown path, no second tracker.

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
  catch (e) { if (sqlState(e) === '23505') throw new EmailAlreadyTaken(user.email); throw e }
}
```

Error helper, pagination, idempotent insert, optimistic lock, tenant predicate, and the migration
cases: [references/repository-adapter.md](./references/repository-adapter.md).

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **Relations API.** Major lines ship different relation and relational-query APIs (declaration
  helper, `where` as operator vs object filter). Use the one the installed version supports and
  the repo already uses; code for the other line does not compile.
- **Driver error wrapping.** Whether a query error arrives wrapped by Drizzle and where the driver's
  SQLSTATE sits (`cause`, deeper). Probe it with a real duplicate insert.
- **Timestamp mode and precision.** Whether a timestamp column reads as `Date` or string, and the
  stored precision. A JS `Date` holds milliseconds; Postgres stores microseconds, so a cursor
  built from a `Date` skips or repeats rows that share a millisecond.
- **`returning()`, `onConflictDoNothing` / `onConflictDoUpdate`** availability and target syntax for
  the dialect and driver in use.
- **drizzle-kit / migrator folder format** — what `migrate()` expects in `migrationsFolder` in the
  installed line (a `meta/` journal, or one folder per migration), before pointing it anywhere.
- **Identity / generated columns, enum and CHECK helpers**, and how the inferred insert type treats
  columns with defaults.
- **Transaction API** on the driver in use (nested transactions / savepoints, isolation option).
