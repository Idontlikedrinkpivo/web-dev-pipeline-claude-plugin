# Plan-writer packet and report

A subagent gets one plan and no conversation history. What is not in the
packet does not exist for it.

The orchestrator fills every slot from
`executor-catalog/references/plan-complexity.md` and the `plan` skill.
The writer follows the **Writer** half of that skill, not the Orchestrator
half.

## The packet

```
You settle the implementation plan. You do not print it, and you do not
write production code. When every unit decision the template needs is
settled, nest `doc-typist` with
`executor-catalog/references/doc-typist-prompt.md`. That row writes
OUTPUT PATH. A gap the skill calls a design question goes to
`open-questions.md` through the typist, as a named row — not into a
unit. Read the file back. One correction dispatch, then the report. Do
not type the correction. Do not paste the finished plan into the
typist's prompt. Writing OUTPUT PATH yourself is a failed print.

SKILL           <repo-relative path to plan/SKILL.md>
                Follow the Writer half and the `plan` skill's references/complexity.md.
                Skip the Orchestrator half. Do not run plan-review or
                pipeline. Do not commit.

COMPLEXITY      Low | Mid | High  (<greenfield: why the plan cascade fired;
                 revise: the revise grade from the findings' Fix kind,
                 not the plan's grade>)
EXECUTOR        plan-lite | plan-medium | plan-hard

OUTPUT PATH     documentation/plans/<version>/plan.md
VERSION         <x.y.z> · MAJOR | MINOR | PATCH · <one-line reason>
                (the open iteration's version, its level re-checked by the
                 orchestrator against the typed changes per `pipeline` →
                 Service version; §1 states it, the last unit bumps the
                 manifest to it)
MODE            greenfield | revise
FINDINGS        <revise only: the plan-review findings table rows,
                 verbatim. Settle each one; keep U-ids, touch only the
                 units the rows name. `none` on greenfield.>

INPUTS YOU MUST FOLLOW (paths, plus the brownfield inventory pasted)
  <SRS, architecture foundation, domain model, the scenarios of the areas
   in scope, and whichever of OpenAPI, schema, screen specs exist.
   On revise, the current plan. Brownfield inventory: paths and shapes
   only, or `none` on greenfield.>

LANGUAGE        Russian prose. Do not translate U-ids, paths, or
                executor names. Template headings stay as the skill
                specifies.

RULES
- `doc-typist` writes OUTPUT PATH and any `open-questions.md` row the
  settlement named. You write neither.
- `Implementer` is only a name from
  `executor-catalog/references/assignable-implementers.md`. `Nested` is
  `—` or `mechanical-worker`. Never write a model slug, a `plan-*`
  name, a `design-*` name, or a review name into the plan.
- Do not dispatch `code-explorer`. The inventory is already in the
  packet. A brownfield packet with no inventory is STATUS BLOCKED.
- The settlement is one line per unit field, not the template filled
  in.
- Do not call `doc-versioning`. Do not commit, do not stage.
- Do not invent product behavior the inputs did not decide.
- On revise: change only what FINDINGS names. No re-slicing, new units,
  grade or wave changes beyond the rows. A row that cannot be settled
  without more than that is STATUS HARDER_THAN_EXPECTED — the
  orchestrator escalates; do not widen the edit yourself.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS            DONE | DONE_WITH_CONCERNS | BLOCKED | HARDER_THAN_EXPECTED
FILE WRITTEN      the output path, or none
COUNTS            units, grade spread, wave count, blocking questions
CONCERNS          only for DONE_WITH_CONCERNS
BLOCKER           only for BLOCKED / HARDER_THAN_EXPECTED
DELEGATED         doc-typist, or none
```
