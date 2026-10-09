# When a version is born

Read when deciding whether this run creates a document's first version or
stamps a new one (Which mode am I in).

**The same rule for every contract** — SRS, OpenAPI, the DB schema, the
three architecture documents and the screen specs. Writers (`srs-writer`,
`openapi-spec-generator`, `db-schema-design`, `clean-architecture-design`,
`screen-spec`), `grill-me`, `doc-review`, `plan` and `work` edit bodies and
never touch `version`, `updated`, `info.version`, or the changelog. A
correction pass, a reversal, and an applied finding stay on the last
stamped number — and so do the two commits that need no request: a move
into the split layout, and a decision changed after the document was
finished (`pipeline` → `references/decision-changes.md`). Opening an iteration fixes the service version (`pipeline`
→ Service version), not a document's: a document takes that number only
when a commit stamps a change in it.

**Stamps happen at two moments, by these steps only:** when a document
stage closes (its gates run or skipped — `pipeline` → Asking before a
transition), and when the user asks to version or publish. A writer, a
gate or a review mid-stage never stamps.

**At a stage's close** the steps below run over that stage's documents
only — the SRS, the schema (with its new migration files), the API, the
three architecture documents, or the screen specs — with no question, and
the commit message names them: `docs: <документ> <version>` («docs: SRS
2.1.1», «docs: схема БД и миграция 0007 2.1.1»). A later change in the same
iteration (a decision changed, a gate re-run) stamps again at its own close
under the same version: rows of this version are amended, not doubled.

1. Compare each contract file with its **last stamped state** — the
   commit that last moved its `version` line (`info.version` for
   OpenAPI; for a split set, the index file's): `git log -1 --format=%H
   -G '^version:' -- <index>` (`-G '^  version:'` for `openapi.yaml`),
   then `git diff <that commit> -- <the document's files>`. Not `HEAD`:
   decision-change and move commits since then are in that diff, and
   they are what the stamp types. The contract files only, under
   `documentation/`:
   `requirements/srs/srs.md`, `api/openapi.yaml`, `db/schema.md`,
   `architecture/architecture.md`, `architecture/domain.md`,
   `architecture/scenarios/*/*.md`, and `ui/screen-specs/S-*.md` (or
   `ui/<product>/screen-specs/`).
   Ignore code, plans, migrations, the frames register, and unversioned drafts.
2. None of them differ from its last stamped state — stop. Report that
   nothing was stamped. Do not commit.
3. Read the iteration's version: the name of the open
   `documentation/plans/<version>/` (no `summary.md`). The stage that
   changed the document should have opened it; when none is open, open it
   now per `pipeline` → Service version (the number with its level and
   reason, asked as a question; the folder is created on the answer). Two
   open folders — stop and ask which one is current.
4. For each file that differs, run `references/guardrails.md`. List the
   cited tokens its diff against the last stamped state touches — the file
   about to be committed, not the previous chat turn, so several
   correction passes and decision-change commits are one set of rows (a
   move changes no token and gets none) — and type each change once
   (What a version is). When no change gets a row, `version`, `updated`,
   and the changelog stay as HEAD had them. Otherwise set `version` to the
   iteration's version, `updated` to today, and add one row per changed
   cited token (or a tight group) at the top of the changelog, with
   `Кого затрагивает` taken from the writer's downstream verdict. A commit
   with three changes writes three rows. A clean sibling gets no row: a
   commit of the API does not add a row to the architecture journal, the
   schema journal, or the SRS journal.
5. In the same files, refresh each pin whose source rows after the pin are
   all «уточняет» (Staleness and cascade). Move no other pin.
6. One commit — at a stage's close `docs: <документ> <version>`, on the
   user's request `docs: publish document versions`. Stage
   only the files just stamped, plus a new file in `db/migrations/` or a
   rebuilt unversioned diagram that belongs to a dirty schema or
   architecture. Do not stage a plan folder's file.
7. Report each file with its `version` and the rows it got, by type, or
   «версия не менялась».

**Several commits in one iteration** add rows under the same version. A
token that already has a row of this version gets that row amended, not a
second one: the type is measured against the last release, so a token born
in this iteration stays «добавляет» however often it changed since.

**A file git has never had.** The writer creates it at
`version: <iteration version>` with one «первый выпуск» row typed «—». The
first commit sets that row's date and keeps it the only row; while it is
the «первый выпуск» of the open iteration, later commits of that iteration
add no rows either — everything in the file is still its first release.

`brainstorm` is not versioned. There is no visual-contract document: the look
is the Figma file; the frames register lists its screens and `nodeId`s, and
each screen spec cites them. OpenAPI has no markdown table: its number is
`info.version` and its rows are `info.x-changelog`, both stamped by the same
commit (`references/changelog.md`).

