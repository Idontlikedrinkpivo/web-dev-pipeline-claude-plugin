# Drizzle ORM — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **Docs ahead of the installed line.** Drizzle's documentation and Context7 may show the 1.0 line (relational
  queries v2, `defineRelations`, a new migrations folder) while the installed package is 0.x — check the version in
  the lockfile before copying an API.
- **Relations API.** Major lines ship different relation and relational-query APIs (declaration helper, `where` as
  operator vs object filter). Use the one the installed version supports and the repo already uses; code for the
  other line does not compile.
- **Driver error wrapping.** Whether a query error arrives wrapped by Drizzle and where the driver's SQLSTATE sits
  (`cause`, deeper). Probe it with a real duplicate insert.
- **Timestamp mode and precision.** Whether a timestamp column reads as `Date` or string, and the stored
  precision. A JS `Date` holds milliseconds; Postgres stores microseconds, so a cursor built from a `Date` skips or
  repeats rows that share a millisecond.
- **`returning()`, `onConflictDoNothing` / `onConflictDoUpdate`** availability and target syntax for the dialect
  and driver in use.
- **drizzle-kit / migrator folder format** — what `migrate()` expects in `migrationsFolder` in the installed line (a
  `meta/` journal, or one folder per migration), before pointing it anywhere.
- **Identity / generated columns, enum and CHECK helpers**, and how the inferred insert type treats columns with
  defaults.
- **Transaction API** on the driver in use (nested transactions / savepoints, isolation option).
