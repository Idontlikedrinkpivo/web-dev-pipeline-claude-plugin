# Repository adapter patterns (PostgreSQL)

Each pattern is for a present need; reuse what the repo already has first. Names (`User`,
`EmailAlreadyTaken`, `PageAfter`) stand for the entity, named errors, and port types the
architecture document defines; in a repo without one, use its existing types and error classes.
Check every Drizzle call below against the installed version (SKILL.md checklist).

## Reading the SQLSTATE

```typescript
// adapters/persistence/pg-error.ts — the driver error may be wrapped one or more levels deep
export function sqlState(e: unknown): string | undefined {
  for (let cur: unknown = e, depth = 0; cur && depth < 5; depth++) {
    const code = (cur as { code?: unknown }).code
    if (typeof code === 'string' && /^[0-9A-Z]{5}$/.test(code)) return code
    cur = (cur as { cause?: unknown }).cause
  }
  return undefined
}
```

| SQLSTATE | Meaning | Repository throws |
|---|---|---|
| `23505` | unique violation | the named error for that key (`EmailAlreadyTaken`), or re-reads the winner for an idempotency key |
| `23503` | FK violation | the named error for the missing reference (`AuthorNotFound`) |
| `23514` | check violation | usually a bug: the entity should have refused first; rethrow |
| `40001`, `40P01` | serialization failure, deadlock | a transient error the use case may retry; the HTTP layer answers it as the spec says (often 503 with `Retry-After`) |
| anything else | | rethrow unchanged; the global handler logs it and answers 500 |

Match on the constraint name when one table has several unique constraints, so a duplicate
slug is not reported as a duplicate email.

## Keyset page

The repository returns entities plus the raw values the next cursor needs; the HTTP adapter
encodes, signs, and validates the cursor.

```typescript
async listNewestFirst(limit: number, after?: { createdAt: string; id: string }) {
  const rows = await this.db.select().from(users)
    .where(after ? or(lt(users.createdAt, after.createdAt),
                      and(eq(users.createdAt, after.createdAt), lt(users.id, after.id))) : undefined)
    .orderBy(desc(users.createdAt), desc(users.id))
    .limit(limit + 1)
  const page = rows.slice(0, limit)
  const last = page.at(-1)
  return {
    items: page.map(toEntity),
    next: rows.length > limit && last ? { createdAt: last.createdAt, id: last.id } : null,
  }
}
```

`createdAt` here is read as the stored string (or the column precision matches what JS keeps),
so the boundary row compares equal. Sort by another column: that column plus `id`, in both the
`ORDER BY` and the predicate, ascending and descending mirrored.

## Idempotent create

```typescript
async createOnce(user: User, key: IdempotencyKey): Promise<User> {
  const [row] = await this.db.insert(users).values({ ...toRecord(user), idempotencyKey: key.value })
    .onConflictDoNothing({ target: users.idempotencyKey }).returning()
  if (row) return toEntity(row)
  const [winner] = await this.db.select().from(users).where(eq(users.idempotencyKey, key.value))
  return toEntity(winner!) // same key → the first call's result
}
```

The unique index on the key is the guard; two concurrent retries both miss a pre-read, and only
the constraint stops the second insert. A repeat with the same key but a different body is a
named error decided by the entity (architecture invariant table), not silently the first result.

## Optimistic lock

```typescript
const updated = await this.db.update(orders)
  .set({ ...toRecord(order), version: sql`${orders.version} + 1` })
  .where(and(eq(orders.id, order.id.value), eq(orders.version, order.version)))
  .returning({ id: orders.id })
if (updated.length === 0) throw new OrderChangedConcurrently(order.id)
```

Zero rows means "gone or changed"; read once to tell which if the contract distinguishes them.
The use case decides whether to retry; the repository never loops.

## Tenant predicate

Every method over tenant-owned rows takes the tenant id first and puts it in the `WHERE` of
every select, update, and delete, including the existence check after a zero-row update.
Row-level security, if present, is the second line, not the only one. One adapter test proves
tenant A's read and write never touch tenant B's rows.

## Transactions

`db.transaction(async (tx) => { ... })` inside the repository method that saves one aggregate
(the aggregate row, its child rows, an outbox row). Pass `tx`, not `db`, to every statement inside.
Across aggregates only through the `UnitOfWork` port the architecture names.

## Migrations

1. A schema change starts in `db-schema-design`: the next file
   `documentation/db/migrations/<NNNN>_<slug>.sql` and the updated `documentation/db/schema.md`.
   Then change the table definition in `schema.ts` to match the schema after that file.
2. Apply with the project's migration command (a plain runner: files in name order, each applied
   once and recorded in a version table in the project schema). No `drizzle-kit generate`, no
   `meta/` snapshot or journal in that folder.
3. Never edit a committed migration file; a mistake is fixed by the next file.
4. Required column on a populated table: the steps (nullable → backfill → `SET NOT NULL`) are
   separate files per `db-schema-design/references/migration-safety.md`; code written between them
   tolerates the null.
5. The adapter tests run on a database migrated by the same command, so a `schema.ts` that
   disagrees with the files fails there.
6. Query-only work adds no migration file.

## Tests

- Mapper round-trip without a database.
- Repository against a real Postgres (container or the project's PGlite setup), one test per
  classified SQLSTATE, produced by a real duplicate insert or FK violation. With no database
  available, throw an error shaped like the wrapped one (code on `cause`, not top level) from a
  stubbed insert, and say the real-database test is still owed.
- Use-case tests use an in-memory fake of the port, never a mocked Drizzle client.
