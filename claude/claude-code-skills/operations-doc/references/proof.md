# Proving the document

A query nobody ran is a guess, and an operator finds out at night. So every
query and command in the document runs on the test stand before the
document is committed, and a test keeps the queries true afterwards.

## The proof run

1. **Start the test stand** the project's way: the verify skill
   (`.claude/skills/verify/`) and its doctor first; without one,
   `deploy-topology`'s test compose. A doctor that is not READY is fixed
   first or reported — never proven on a broken stand.
2. **Make one record of each kind** through the API or the UI, the way a
   user would — never by inserting rows: a booking, its cancellation, a
   maintenance block that queues a letter. A record that needs an external
   failure (a letter that cannot be sent) uses the stand's fake of that
   system when the test compose has one; otherwise its rows are proven only
   by the query test and the report says so.
3. **Run every query** with the read-only role when the document names one,
   with the parameters of the records just made; every log filter over the
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

A test in the project's own suite, beside `deploy-topology`'s sync test,
that reads `documentation/operations/operations.md`, takes every ` ```sql `
block and asks the test database to prepare it without running it — for
PostgreSQL `PREPARE q AS <query>` followed by `DEALLOCATE q`, which checks
every table, column and type and infers `$n`. Each block is also checked to
start with `SELECT` or `WITH`. A failure names the query id (`З-2`) and the
database error. It runs with the integration tests, so a migration that
renames a column fails the build that renames it.

A write procedure (`П-<n>`) has its statement in a ` ```sql ` block too: the
test prepares it inside a transaction it rolls back, and the read-only check
skips blocks under a `П-` heading.
