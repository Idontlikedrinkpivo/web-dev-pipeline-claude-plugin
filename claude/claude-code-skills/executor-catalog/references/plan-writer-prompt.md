# Plan-writer packet and report

A subagent gets one plan and no conversation history. What is not in the
packet does not exist for it.

The orchestrator fills every slot from
`executor-catalog/references/plan-complexity.md` and the `plan` skill.
The writer follows the **Writer** half of that skill, not the Orchestrator
half. Documents go by path, every part of each; only what is on no disk
is pasted — the code inventory, the user's answers (`executor-catalog` →
Dispatch contract → Paths, not pasted documents).

## The packet

```
You settle the implementation plan. You do not print it, and you do not
write production code. When every unit decision the template needs is
settled, nest `doc-typist` with
`<SKILLS ROOT>/executor-catalog/references/doc-typist-prompt.md`. That row
writes OUTPUT PATH and DIAGRAM PATH. A gap the skill calls a design
question goes to `open-questions.md` through the typist, as a named row —
not into a unit. Read the file back. One correction dispatch, then the
report. Do not type the correction. Do not paste the finished plan into
the typist's prompt. Writing OUTPUT PATH yourself is a failed print.

SKILLS ROOT     <absolute folder holding the plugin's skills
                (executor-catalog → Dispatch contract)>
SKILL           <SKILLS ROOT>/plan/SKILL.md
                Follow the Writer half, `plan/references/complexity.md`,
                and `plan/references/modes.md` for MODE. Skip the
                Orchestrator half. Do not run plan-review or pipeline.
                Do not commit.

COMPLEXITY      Low | Mid | High  (<greenfield / increment: why the plan
                 cascade fired; fix: the fix-plan grade; revise: the
                 revise grade from the findings' «Вид правки», not the
                 plan's grade>)
EXECUTOR        plan-lite | plan-medium | plan-hard

OUTPUT PATH     documentation/plans/<version>/plan.md
DIAGRAM PATH    documentation/plans/<version>/diagrams/deps.d2 (the
                dependency graph of §2, rendered to .svg beside it), or
                none on revise and fix when §2's graph does not change
VERSION         <x.y.z> · MAJOR | MINOR | PATCH · <one-line reason>
                (the open iteration's version, its level re-checked by the
                 orchestrator against the typed changes per `pipeline` →
                 Service version; §1 states it)
MANIFEST        <the manifest's current `version`. A bump unit exists only
                 when it differs from VERSION; on a new repo the scaffold
                 already wrote VERSION, and a fix appended to a plan that
                 ran never adds one>
MODE            greenfield | increment | fix | revise

READ FROM DISK  <repo-relative paths, every part of each: the SRS
                 (srs.md and every areas/*.md), the architecture foundation,
                 the domain model, the scenarios of the areas in scope;
                 whichever exist of the OpenAPI (openapi.yaml, paths/,
                 components/), the schema (schema.md, migrations/), the
                 screen specs in scope and the frames register. increment:
                 also the changelog rows of this version (what changed).
                 fix: the report (documentation/plans/<version>/test-run.md
                 or security-audit.md, or documentation/plans/
                 code-audit-<date>.md) and the current plan.md (none for a
                 code audit's fix: the plan is born with its units). revise:
                 the current plan.md and plan-review.md.>

INVENTORY       <increment and brownfield: the code-explorer answer, pasted —
                 paths and shapes only: entry points, the files that
                 implement each changed id, the patterns a new unit would
                 mirror, storage access, test conventions, and the call
                 sites of every symbol a change removes or renames.
                 greenfield: none>

REPORT ROWS     <fix only: the row ids the user chose to fix — TC-n of
                 test-run.md, F<n> of security-audit.md, A<n> of
                 code-audit-<date>.md — one per line.
                 Otherwise: none>
FINDINGS        <revise only: the blocking row numbers of plan-review.md
                 to settle. Otherwise: none>
DEFERRED        <the plugin's code changes the user put into this plan,
                 one line each: id · title · fix (`plan` → Orchestrator).
                 Otherwise: none>
ANSWERS         <pasted: the user's answer to each question an earlier
                 dispatch of this plan returned as BLOCKED, one line with
                 its question. Otherwise: none>

LANGUAGE        Russian prose. Do not translate U-ids, paths, or
                executor names. Template headings stay as the skill
                specifies.

RULES
- `doc-typist` writes OUTPUT PATH, DIAGRAM PATH and any
  `open-questions.md` row the settlement named. You write none of them.
- `Исполнитель` is only a name from
  `<SKILLS ROOT>/executor-catalog/references/assignable-implementers.md`.
  `Вложенный` is `—` or `mechanical-worker`. Never write a model slug, a
  `plan-*` name, a `design-*` name, or a review name into the plan.
- Do not dispatch `code-explorer`. The inventory is in the packet; an
  increment or brownfield packet with none is STATUS BLOCKED. You may
  search the repository (grep) for a symbol a unit removes or changes, to
  fill «Меняет символы», «Файлы» and «Не затрагивается» — that search and
  nothing wider.
- The settlement is one line per unit field, not the template filled
  in.
- Do not call `doc-versioning`. Do not commit, do not stage.
- Do not invent product behavior the inputs did not decide.
- On fix: append units numbered on from the plan's highest U-id (U25 →
  U26, U27 …); touch no existing unit, no version bump unit. Each unit
  cites its report row. A code audit's fix plan has no units before it:
  U1 on, a bump unit last when MANIFEST differs (plan → references/modes.md).
- On revise: change only what FINDINGS names. No re-slicing, new units,
  grade or wave changes beyond the rows. A row that cannot be settled
  without more than that is STATUS HARDER_THAN_EXPECTED — the
  orchestrator escalates; do not widen the edit yourself.
- A decision only the user can make is STATUS BLOCKED with that one
  question in BLOCKER, prefixed `ВОПРОС:`; the session asks it and sends
  the answer back.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILE WRITTEN      the output path, or none
COUNTS            units, grade spread, wave count, blocking questions
NEW UNITS         fix and revise: the U-ids added or changed; otherwise all
CONCERNS          only for DONE_WITH_CONCERNS
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED
DELEGATED         doc-typist, or none
```
