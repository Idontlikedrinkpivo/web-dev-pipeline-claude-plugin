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
  `✍️ пишутся` when you start a section's cases and `✅ написаны` with
  their count when they are done, then the bar and the line «Написано: N
  из M разделов · кейсов: K»; the «Без интерфейса» row likewise. Change nothing else
  there.
- One case per reachable AC (main, Alt, Exc), per state row and per
  user-causable response outcome not yet covered, per «Поля ввода» rule,
  per forbidden action per role.
- Steps name actions and data by the spec's names and screen ids — never a
  widget or a gesture («выполнить отмену брони», not «нажать кнопку»);
  expected results quote the exact text the screen spec takes from the
  frame's «Тексты» table and name the state row.
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
