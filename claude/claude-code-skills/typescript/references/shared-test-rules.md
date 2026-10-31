# Test rules both stacks share

`pytest-patterns` and `vitest`, and the persistence skills for the mapper and race rules, point here; each keeps only
its own tool. One text, because the same rules worded differently in three skills drift apart.

| Rule | Python (`pytest-patterns`) | TypeScript (`vitest`) |
|---|---|---|
| 2. Race test | `asyncio.gather`, one `AsyncSession` per task | `Promise.all`, one connection from the pool per call |
| 3. Property test | `hypothesis` | `fast-check` |

1. **Mapper round-trip.** Each mapper gets one round-trip test: every field set to a non-default value, entity →
   record → entity equal, so a field added without its mapper line fails the build. Pure, no connection.
2. **Race test.** A guard against a double action (a row lock, a conditional update, a unique key, an idempotency
   key) gets a race test against the real database: two concurrent calls, each with its own session or connection
   (never one transaction shared), then count the effect — exactly one refund, one row — and assert what the second
   caller got. Without it nothing shows that the lock is taken, or taken before the read it protects. That data is
   committed outside the per-test rollback, so clean it up explicitly.
3. **Property test.** An invariant over many values (a format, a range, a round trip, «whoever edits can see») gets
   a property test beside its examples.
4. **Group by behaviour.** Group tests (files, classes, `describe` blocks) by behaviour, never by plan unit (`U17:`);
   setup a second file needs goes to the shared fixtures or test helpers (`conftest.py`, the shared helpers folder),
   never copied.
5. **Mutants.** A surviving mutant named in a review finding points to the missing assertion: add one that fails on
   that mutant; never change the mutated code or weaken a test to kill it. Mutation runs are `work`'s, at the run's
   close (`work/references/health.md` → Mutation runs), never a unit's.
6. **No database reachable here** (a sandbox without Docker): write the database tests — repository, race and HTTP —
   as they would run, run the rest, and report the database run as owed — in a `work` packet a line in `CONCERNS`
   with the command to run. Never swap the database for SQLite, a mocked session or a mocked client to get a green
   run: that run proves nothing about the queries.
