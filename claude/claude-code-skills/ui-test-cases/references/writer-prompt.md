# Writer packet and report

```
You write the user test cases for one product from its documents. You do
not run anything, edit the documents, or decide behaviour the spec left
open — such a case goes to GAPS.

SKILL           <path to ui-test-cases/SKILL.md> — follow Mode write
OUTPUT PATH     documentation/ui/test-cases/ — README.md and one file per
                section (documentation/ui/<product>/test-cases/ with several
                UI products); an old single test-cases.md beside it is moved
                in first (ui-test-cases → Mode write → Artifact)
MODE            greenfield | increment (keep every TC- id; new cases take the next number)
PROGRESS FILE   documentation/plans/<version>/progress-test-cases.md

INPUTS (read in full)
  SRS:        documentation/requirements/srs/srs.md@<version> | none
              (frontend repo: cases from the screen specs alone)
  Screens:    documentation/ui/frames-register.md + one
              documentation/ui/screen-specs/S-<n>-<slug>.md per screen
  OpenAPI:    documentation/api/openapi.yaml | none
  Existing cases: <the test-cases/ folder | an old test-cases.md> | none

RULES
- Progress: with the Edit tool, set a section's row in PROGRESS FILE to
  `✍️ пишутся` when you start a section's cases and `✅ готово` with
  their count when they are done, then the bar and the line «Написано: N
  из M разделов · кейсов: K»; the «Без интерфейса» row likewise. Change nothing else
  there.
- One case per reachable AC (main, Alt, Exc), per state row and per
  user-causable response outcome not yet covered, per «Поля ввода» rule,
  per forbidden action per role.
- Two layers (ui-test-cases → What a case set must hold → Two readers):
  the body for a person — roles and screens by name, steps as actions by
  the label the user sees (never a widget, a gesture, or an element
  number), «Что должно быть» as the labelled texts a person sees, a
  server failure as a precondition in words; then the mandatory
  «Трассировка» line — source ids, frame nodeId, state row, `шаг N → эл. M`
  for every step that touches an element, operationId with status or mock,
  ARIA expectations. A «Проверяет» line with the requirement ids opens each
  case. Steps go through controls the spec names when another path exists;
  expected texts carry real values computed from the preconditions, never
  `{дата}` or «по кадру».
- Preconditions name the data, so a runner can seed it.
- README.md holds what every section shares, the «Разделы» table and,
  at its end, the coverage table: AC → TC ids, or «Без интерфейса» +
  reason. A section file holds only its cases. TC ids run across the set.
- Russian prose; ids, operationIds, paths untranslated.
- Write only under OUTPUT PATH (and delete the old single file after the
  move). Do not commit.
```

Report — last message, exactly:

```
STATUS        DONE | DONE_WITH_CONCERNS | BLOCKED
FILES WRITTEN README.md and each section file written or changed | none
COUNTS        N cases · M AC covered of K · L «Без интерфейса»
GAPS          one line per behaviour the spec did not decide, or none
```
