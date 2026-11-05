# Database conflicts and retries both stacks share

`fastapi`, `fastapi-sqlalchemy`, `typescript-fastify` and `typescript-drizzle-orm` point here; each keeps only its
own tool. One text, because the same rule was written in five places across the four skills, and copies of a rule
drift at the next change. The contract's side — problem+json, never a bare 409, 503 with `Retry-After`
after the server's reruns — is `openapi-spec-generator` → Step 6; this file is how the code keeps it.

| Rule | Python (`fastapi-sqlalchemy`, `fastapi`) | TypeScript (`typescript-drizzle-orm`, `typescript-fastify`) |
|---|---|---|
| SQLSTATE source | `e.orig.sqlstate` on SQLAlchemy's `DBAPIError`; where the constraint name sits is a version check | the `cause` chain walked by `sqlState(e)` (`typescript-drizzle-orm/references/repository-adapter.md` → Reading the SQLSTATE); the constraint name from the same driver error |
| 1. Named error | `raise BookingOverlap(room_id=…) from e` — a domain exception with fields | `throw new EmailAlreadyTaken(email, { cause: e })` — a class with a literal `kind` |
| 2. Rerun helper | one async helper wired in `bootstrap/` around the use case, a fresh `AsyncSession` per attempt | `rerunOnConflict(run)` (`repository-adapter.md`), wired in `bootstrap/`, a fresh transaction per attempt |
| 3. The 500 | the exception handler for unnamed errors in `bootstrap/` (`fastapi` → Errors as problem+json) | the global error handler's third case (`typescript-fastify` → Errors) |
| 4. Idempotent insert | `insert(...).on_conflict_do_nothing(...)` from `sqlalchemy.dialects.postgresql`, or catch `23505`, then re-select | `.onConflictDoNothing()`, or catch `23505`, then re-read (`repository-adapter.md`) |
| 5. Race test | `pytest-patterns`, `asyncio.gather` | `vitest`, `Promise.all` |

1. **An expected violation becomes a named error.** A unique (`23505`), foreign-key (`23503`) or check (`23514`)
   violation the repository can expect — a duplicate email, a dangling reference, an overlap the database refuses —
   is classified by its SQLSTATE and, when the table has several constraints, its constraint name, never by the
   message: the message changes with the driver version and the server's locale, and a duplicate slug must not be
   reported as a duplicate email. The repository (or the db-error helper it calls, never a route) raises a named
   error with fields and the driver error as its cause; the answer is the status the contract gives that named
   error — never a bare 409 from a SQLSTATE, which the contract does not declare and no client can tell apart. A
   check violation is usually a bug — the entity should have refused first — so rethrow it unless the schema names
   it as an expected refusal. Keep an app-side pre-check if it gives a nicer error, and classify the violation as
   well: two instances can pass the check together.
2. **A serialization failure or deadlock is rerun, whole, a bounded number of times.** `40001` and `40P01`
   propagate unchanged from the repository: the repository never loops, and the use case knows no driver codes.
   One shared helper, wired in `bootstrap/` around each use case whose transaction can lose to a concurrent one,
   reruns the use case's whole run — load → decide → save, with a fresh session or connection — three times with a
   short random wait. Never one statement: the decision was made on rows the lost transaction read, so replaying
   only the write keeps the stale decision. What is left after the attempts is the contract's 503 with
   `Retry-After`, written by the error handler, never by the helper.
3. **Anything else propagates unchanged** and ends as the contract's 500: logged with its SQLSTATE and cause, the
   client gets the generic `detail`. The driver message never reaches a client answer — it carries SQL and
   parameter values. An unexpected constraint violation is this case, not a 409. Never swallow a driver error
   (`except Exception: pass`, an empty `catch`) and never re-raise it as the answer.
4. **A double action is settled by a unique constraint.** An idempotency key (a create with `Idempotency-Key`) or
   any «only once» action is stored under a unique index; the insert does nothing on conflict (or catches `23505`)
   and re-reads the winner, so a replay returns the first call's status and resource instead of a conflict. Never
   an in-process map — a second instance or a restart does not see it — and never a read-then-insert alone: two
   requests read «absent» together.
5. **The race test proves it** — `shared-test-rules.md` → 2: two concurrent calls, each with its own session or
   connection, then count the effect.
