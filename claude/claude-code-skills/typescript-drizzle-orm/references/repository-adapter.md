# Repository adapter patterns (PostgreSQL)

Each pattern is for a present need; reuse what the repo already has first. Names (`User`,
`EmailAlreadyTaken`, `PageAfter`) stand for the entity, named errors, and port types the
architecture document defines; in a repo without one, use its existing types and error classes.
Check every Drizzle call below against the installed version (`version-checks.md`).

## Reading the SQLSTATE

```typescript
// adapters/persistence/pg-error.ts — the driver error may be wrapped one or more levels deep
export function sqlState(e: unknown): string | undefined {
  let cur: unknown = e
  for (let depth = 0; typeof cur === 'object' && cur !== null && depth < 5; depth++) {
    if ('code' in cur && typeof cur.code === 'string' && /^[0-9A-Z]{5}$/.test(cur.code)) return cur.code
    cur = 'cause' in cur ? cur.cause : undefined
  }
  return undefined
}
```

| SQLSTATE | Meaning | Repository throws |
|---|---|---|
| `23505` | unique violation | the named error for that key (`EmailAlreadyTaken`), or re-reads the winner for an idempotency key |
| `23503` | FK violation | the named error for the missing reference (`AuthorNotFound`) |
| `23514` | check violation | usually a bug: the entity should have refused first; rethrow |
| `40001`, `40P01` | serialization failure, deadlock | rethrow unchanged — the use case reruns its whole transaction a bounded number of times (below); what is left is the contract's 503 with `Retry-After` |
| anything else | | rethrow unchanged; the global handler logs it with its SQLSTATE and answers the contract's 500 |

A uniqueness clash reaches the client only as its named error, never as a bare 409 (`typescript-fastify` → Errors,
`openapi-spec-generator` → Step 6).

A rerun wraps load → decide → save, not one statement — the decision was made on the rows the lost transaction
read. One shared helper does it, wired in `bootstrap/` around each use case whose transaction can lose to a
concurrent one, so the use case itself knows no driver codes:

```typescript
// adapters/persistence/rerun.ts — the only loop; the repository never retries
// bootstrap: const cancelBooking = (input: CancelInput) => rerunOnConflict(() => cancelBookingUseCase.execute(input))
export async function rerunOnConflict<T>(run: () => Promise<T>, attempts = 3): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try { return await run() }
    catch (e) {
      const state = sqlState(e)
      if (attempt >= attempts || (state !== '40001' && state !== '40P01')) throw e
      await new Promise((r) => setTimeout(r, 20 * attempt + Math.random() * 30))
    }
  }
}
```

Match on the constraint name when one table has several unique constraints, so a duplicate
slug is not reported as a duplicate email.

## Keyset page

The repository returns entities plus the raw values the next cursor needs; the HTTP adapter
encodes the cursor (opaque base64url, not signed) and validates it before the query (`typescript-fastify`).

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
  // the conflict proves the first call's row exists; a missing one is a bug, not a result
  if (!winner) throw new Error(`no row for idempotency key ${key.value} after a conflict`)
  return toEntity(winner) // same key → the first call's result
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
  available, write those tests as they would run and report the run as owed (`vitest` → no database
  here); the classification itself can be shown meanwhile by throwing an error shaped like the
  wrapped one (code on `cause`, not top level) from a stubbed insert.
- Use-case tests use an in-memory fake of the port, never a mocked Drizzle client.
