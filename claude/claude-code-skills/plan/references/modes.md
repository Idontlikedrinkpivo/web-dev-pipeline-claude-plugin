# Plan modes

The writer reads the section of its MODE before Step 1. The session reads
the table in `SKILL.md` → Modes to pick one. Steps 1–7 of `SKILL.md` hold
in every mode; this file says what each mode changes.

## Contents

- greenfield
- increment — what is in scope, the inventory, a path this version retired, brownfield without documents
- fix — after `DEFECTS` or `FIX`
- revise — after `plan-review`

## greenfield

The first plan of a product: the repository holds only what `repo-scaffold`
made. Every use case, operation, screen, NFR decision and configuration
variable of the documents is in scope, because the first version added all
of them. No inventory: the design documents and the scaffold say
everything the digest needs. The scaffold already wrote VERSION into the
manifest, so there is no bump unit.

## increment

A version over code that already runs. In scope is only what this version
added or changed: the ids named in the documents' changelog rows whose
«Версия» is this version (OpenAPI: `info.x-changelog`), plus the changes
not stamped yet, typed from the diff since the last tag `v<version>`. An
id an earlier version built is not planned again — `plan-review` checks
coverage against the same list.

**The inventory is in the packet.** `code-explorer` mapped the code these
changes reach: the files that implement each changed id, the patterns a
new unit mirrors, storage access, the test conventions, and every use of
each symbol a change removes or renames. Take `Образец` paths and
`Файлы` from it. For each unit that removes or changes a field, a
constant, an environment variable, a response shape or a public symbol,
search the repository for the symbol (`grep` — code, tests, e2e, CI,
documents) and put every hit in `Файлы` or in «Не затрагивается» with the
reason. That search, and no wider reading: a plan written by reading the
repository unit by unit costs more than the inventory saved. An executor
that meets an unlisted caller mid-run sends the unit round again — the
most common rework in real runs.

The last unit bumps the manifest's `version` to VERSION when MANIFEST in
the packet differs from it.

### A path this version retired

List every id this iteration marked `[deprecated in <version>]` or
removed (a «ломает» row of this version, `удалён:`). Marks from older
versions are not this plan's job. For each id whose code is still in the
repository, add one unit. `Документы` cites the retired id and what
replaced it. `Файлы` names the old path. The goal says that path is gone
and the replacement covers it. A test says the old call is absent and the
replacement scenario passes. The unit does not delete the specification
row.

Three exceptions, each one sentence in that unit:

- A client still calls the HTTP operation. Remove this product's callers
  and the screen. Leave the operation `deprecated: true`.
- The code still serves a live requirement. Name that requirement.
- The code cannot be found. Put «где живёт <id>» in `open-questions.md`,
  class `Блокирует старт`. The plan is not done while that row is open.

A repository with no such code skips this.

### Brownfield without documents

The code *is* the design: the user wants work planned against it and
there are no design documents. Every `Документы` cell reads
`code:<path>` — the file whose current behaviour the unit keeps or
changes — so execution and `plan-review` know the citation is inferred,
not specified. Scope is the user's request, item by item; each item
needs a unit. The architecture level is read from the code (one layer or
several) and named in §1 as inferred.

## fix

After a UI acceptance run with the verdict `DEFECTS`
(`documentation/plans/<version>/test-run.md`) or a security audit with
`FIX` (`security-audit.md`), for the rows the user chose to fix — REPORT
ROWS in the packet, `TC-n` or `F<n>`. The plan of this version already
ran; fix units join it.

From a code audit (`documentation/plans/code-audit-<date>.md`, rows
`A<n>` the user chose to fix or to rewrite — `upgrade-code` →
`references/audit.md`) the iteration was opened for these fixes and has no
plan yet: the fix units are the plan — `plan.md` is born with them from U1,
and, as in any new plan, the last unit bumps the manifest when it differs
from VERSION (the «no bump unit» below is for fixes appended to a plan that
already ran). The documents the
rows change were revised first; each unit cites the revised document and
the row. A row that does not change behaviour starts with a
characterization test that pins what the code does now and stays green; a
rewrite of a module starts with those tests over the whole module, builds
it anew by the documents, and removes the old code in its last unit.

- **Append, touch nothing.** New units take the next unused U-ids after
  the plan's highest. No existing unit is edited, renumbered or
  re-graded, and no bump unit is added — the version is set (a fix plan
  born in its own iteration, from a code audit, is the exception above). A fix unit
  may name a done unit in `Зависит от`; it is already committed.
- **One unit per row, or per shared cause.** Rows with one root cause
  (one missing check behind three cases) are one unit naming all of
  them.
- **`Документы` cite the row.** `test-run.md TC-12`, `security-audit.md
  F2` — plus the design id the row says was broken (the AC, BR,
  operation, screen) when the report names one; that id is what the fix
  must satisfy. A row with no design id takes its expected behaviour from
  the row itself («ожидалось»; the finding's «Что»).
- **The first scenario reproduces the row.** The case's steps, or the
  finding's exploit request, as a test that fails now for the reason the
  row gives — then passes after the fix. A unit that only patches code
  without that test has not proven the defect gone.
- **A row that is not a defect is not a unit.** A spec gap, a case the
  user rules «так и должно быть», a finding whose fix reverses a settled
  decision: those go to `open-questions.md` and to the user
  (`pipeline` → `references/decision-changes.md`).
- **§1 gets one line** — «Исправления по test-run.md: TC-3, TC-12», «по
  security-audit.md: F2, F5» or «по code-audit-<date>.md: A1, A4». §2 gets the new rows, §4 their wave.
- Grade each unit by the unit cascade as usual; a finding about access,
  auth or data leaks keeps the risk floor.

`plan-review` then reviews the appended units only, and its coverage
ledger is the report rows.

## revise

After `plan-review` returned `FIX_THEN_PROCEED` or `RETURN_TO_PLAN`.
FINDINGS in the packet names the blocking rows of `plan-review.md`.
Change only what those rows name — a row may ask to split a unit or add
one; nothing beyond the rows is re-sliced, added, re-graded or moved.
Keep U-ids. A row that cannot be settled without more is
`HARDER_THAN_EXPECTED`.
