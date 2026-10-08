# A decision changed after its document

Read whenever a decision changes after the stage that wrote it down has
closed — in `work`, in a later stage, or in the chat between stages. The
document is updated in the same step, without the user asking, and the
change is committed before the work that depends on it goes on. A decision
that lives only in code or in the chat leaves every later stage, reviewer
and plan reading the old one, and nothing says which is true.

## What counts

- **The user answers a stop** — `BLOCKED` on a missing design decision, a
  review's `STOP`, a gap a writer or reviewer named.
- **The user changes a decision mid-stage** — «давай по-другому», «убери
  это поле», «пусть отмена будет без подтверждения».
- **A fact overrules the document** — the library cannot do what the
  design says, the installed major differs, a port or a name is taken —
  and the replacement is settled: by the user, or by the stage when that
  choice is the stage's own (an unverified version assumption checked by
  `repo-scaffold`).
- **A run shows the spec, not the code, is wrong** — the user rules so on a
  test-run defect or a review finding.

Not a changed decision: a worker's local choice inside what the documents
fix (the run report's `Decisions` hold it), an implementation detail no
document names, and an edit inside the stage that owns the document — a
grill reversal or an applied review finding on the document the stage is
still writing is that stage's own work.

## The owner

| What changed | Owner document | Writer that edits it |
|---|---|---|
| product behaviour, a business rule, a limit, an actor's right, an acceptance criterion | SRS — `srs.md` and the area file | `srs-author`, `MODE grill-reversal`, the decision in `REVERSALS` |
| a table, a column, an index | DB schema, plus a new migration file | `doc-typist`, `MODE revise` |
| an operation, a field, a status or error code | OpenAPI | `doc-typist`, `MODE revise` |
| a module, a layer, a port, an adapter, a configuration variable, a stack version | architecture foundation | `doc-typist`, `MODE revise` |
| an entity, an invariant, a named error | domain model | `doc-typist`, `MODE revise` |
| a step of a flow, a transaction boundary | the scenarios of the area | `doc-typist`, `MODE revise` |
| an element, a text or a state of a screen | the screen spec, and the frame when the look changes (`ui-design`, `figma-sonnet`) | `screen-writer`, as an increment of that screen (`screen-spec` → its packet) |
| an expected result of a case | the test cases (unversioned) | `ui-test-writer`, as an increment of that section |

The session does not edit a contract document by hand: the writer keeps
the template's shape and the ids that other documents cite.

## The steps

1. **Write it down first.** One line in the stage's report under
   «Изменённые решения» — `<было> → <стало> · решил <кто> · документы ·
   код по старому решению` — so a compaction or a stop mid-way cannot lose
   the decision.
2. **Find every document that states the old decision.** The owner, plus
   the documents downstream of it that repeat it: search `documentation/`
   for the changed token (an id, a column, an `operationId`, a variable)
   and read the hits, using `pipeline` → Increments («Changed → Names») for
   where to look.
3. **Edit them**, owner first, each through its writer with one
   `SETTLEMENT` line per change and nothing else. A downstream document
   whose change needs design judgment rather than a line edit — a scenario
   whose flow changes shape — is its stage's increment: stop and ask, with
   that stage named.
4. **Check it landed**: the new wording is in each file, the old one is
   gone, the ids that other documents cite still resolve.
5. **Commit at once**: one commit per decision, staging only those
   documents (and a new migration file or re-rendered diagram that belongs
   to them), message `docs: решение изменено — <кратко>`. Leave `version`,
   `updated`, `info.version`, the changelog and the pins as they are: like a
   move, this commit needs no request from the user, and the next stamp
   (`doc-versioning`) types these changes, because it compares each
   document with its last stamped state, not with `HEAD`. Edits of this
   iteration still uncommitted in the same file go into this commit too;
   the stamp types them all the same way.
6. **Then go on.** What runs next reads the new text.

## Work already built on the old decision

- **Code.** In `work`, a committed unit that implements the old decision
  gets a follow-up commit through its own executor, like a fix after a
  commit, carrying that unit's `Plan-Unit:` trailer, and listed in the run
  report. Outside `work`, the stage report names it as a fix for the next
  plan.
- **The plan.** `work` never edits the plan. A unit whose text contradicts
  the changed decision gets, in its packet, the decision as
  `CHANGED DECISIONS` — the document is already fixed and wins over the
  unit's text. A change that makes a unit pointless or needs a new one is a
  plan change: stop and ask.
- **Frames.** A change that alters what a screen shows goes to `ui-design`
  for the frame and to `screen-spec` for the spec, in that order.

## A finding against a settled decision

A review, an audit or a check may find something that a document already
decided on purpose — a limit the SRS rules out, a risk the architecture
accepted, a behaviour a decisions log fixed («предела по адресу нет»). Such
a finding is not a fix: fixing it silently reverses a decision the user
made. Every check that fixes on its own — `security-audit`, `doc-review`,
`code-review-unit`, `code-review-full`, `plan-review`, `docs-consistency` —
does this, whatever the finding's severity:

1. **Look before routing.** Search the SRS (NFR, BR), the architecture's
   decisions and accepted risks, and the project's decisions log for what
   the finding touches.
2. **When a decision covers it, ask — never fix by default.** One question
   with the decision quoted and its id, what the finding says, and two
   options: keep the decision (the finding becomes an accepted risk with
   that id as the reason) or change it (then this file, before any fix).
   Recommend from evidence — a concrete way to break the application that
   the decision did not consider — not from the finding's own advice.
3. **Nothing is fixed, planned or committed for it before the answer.**

## Where it applies

| Stage | The moment |
|---|---|
| `work` | the user's answer to `BLOCKED` or `STOP`, a change of mind mid-run, the final review's `STOP` |
| `code-review-full` | checks that every line of «Изменённые решения» landed in its documents, and that the code does not silently depart from a contract document |
| `ui-test-cases` run | a `❓ пробел в ТЗ`, or a defect the user rules is the spec's, not the app's |
| `screen-spec` | a Разрыв with owner `API` or `SRS` that the user settles |
| `ui-design` | the user changes behaviour while looking at the frames («убери поле», «другой порядок шагов») |
| `plan`, `plan-review` | a `STOP` on a documents gap: the decision goes into the document before the plan is written or revised |
| `repo-scaffold`, `deploy-topology`, `ci-pipeline` | a stack version, a port, a variable, a service name or a command that differs from the architecture |
| `grill-me`, `doc-review`, `docs-consistency` | an upstream contradiction the user rules on: the upstream document follows this file |
| between stages | «давай поменяем …» in the chat |
