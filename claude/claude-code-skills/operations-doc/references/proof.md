# Proving the document

A query nobody ran is a guess, and an operator finds out at night. So every
query and command in the document runs on the test stand before the
document is committed, and a test keeps the queries true afterwards.

## The proof run

1. **Start the test stand** the project's way: the verify skill
   (`.claude/skills/verify/`) and its doctor first; without one,
   `deploy-topology`'s test compose. A doctor that is not READY is fixed
   first or reported — never proven on a broken stand.
2. **Have one record of each kind.** Records the stand already holds
   (earlier test runs leave plenty) count — list what is there first and
   make only the missing kinds, through the API or the UI, the way a
   user would — never by inserting rows: a booking, its cancellation, a
   maintenance block that queues a letter. A record that needs an external
   failure (a letter that cannot be sent) uses the stand's fake of that
   system when the test compose has one; otherwise its rows are proven only
   by the query test and the report says so.
3. **Run every query** with the read-only role when the document names one,
   with the parameters of real records — `PREPARE` the block as written and
   `EXECUTE` it with values, inside `BEGIN READ ONLY … ROLLBACK`; every log filter over the
   container's stdout (`docker compose logs --no-log-prefix backend`); every
   health and metrics call.
4. **Check the answer**, not just the exit code: the row the query should
   find is there, the columns are the ones its row describes, a personal
   field appears only where the row says. A wrong answer is a wrong
   document: fix it and rerun.
5. **Leave the stand as it was** — the verify skill's cleanup; the records
   made here are test data on the test stand only.
6. Write the date into the document's header line («Запросы проверены на
   тестовом стенде: …») and the counts into the report: queries run,
   filters run, rows proven only by the query test.

## The query test

Do not write it from this prose: copy the reference test and adapt only the
lines it marks `ADAPT` (the path to the repo root, the schema the document
names, the database connection) — `assets/test_operations_queries.py` for
a Python backend (pytest), `assets/operations-queries.test.ts` for a
TypeScript one (vitest and the `postgres` driver). Both do what follows,
and the shape checks run without a database too.

A test in the project's own suite, beside `deploy-topology`'s sync test,
that reads `documentation/operations/operations.md`, takes every ` ```sql `
block and asks the test database to prepare it without running it — for
PostgreSQL `PREPARE q AS <query>` followed by `DEALLOCATE q`, which checks
every table, column and type and infers `$n`. Each block is also checked to
start with `SELECT` or `WITH`. A failure names the query id (`З-2`) and the
database error. It runs with the integration tests, so a migration that
renames a column fails the build that renames it.

A procedure (`П-<n>`) has its statements in a ` ```sql ` block too: the
test runs them inside a transaction it always rolls back (DDL such as
`CREATE ROLE` included — PostgreSQL rolls it back), and the read-only check
skips blocks under a `П-` heading. A psql variable in a procedure
(`:'readonly_password'` — how the operator passes a secret) is replaced by a
literal in the test.

**Where it runs.** The project's integration database, never the stand's:
other integration suites reset their database, so pointing them at the
stand would wipe its data. To run the new test once during this stage, make
a throwaway database on the stand's server (`CREATE DATABASE …`), migrate it
the project's way, run only this test file there, then drop that database.
Prove the test can fail: rename one column a query uses in the throwaway
database and see exactly the queries that use it fail.
