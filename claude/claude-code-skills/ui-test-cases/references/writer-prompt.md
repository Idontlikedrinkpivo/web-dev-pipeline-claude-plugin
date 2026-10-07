# Writer packet and report

```
You write the user test cases for one product from its documents. You do
not run anything, edit the documents, or decide behaviour the spec left
open — such a case goes to GAPS.

SKILL           <path to ui-test-cases/SKILL.md> — follow Mode write
OUTPUT PATH     documentation/ui/test-cases.md
                (documentation/ui/<product>/test-cases.md with several UI products)
MODE            greenfield | increment (keep every TC- id; new cases take the next number)
PROGRESS FILE   documentation/plans/<version>/progress-test-cases.md

INPUTS (read in full)
  SRS:        documentation/requirements/srs/srs.md@<version> | none
              (frontend repo: cases from the screen specs alone)
  Screens:    documentation/ui/frames-register.md + one
              documentation/ui/screen-specs/S-<n>-<slug>.md per screen
  OpenAPI:    documentation/api/openapi.yaml | none
  Existing cases: <path> | none

RULES
- Progress: with the Edit tool, set a screen's row in PROGRESS FILE to
  `✍️ пишутся` when you start its cases and `✅ написаны` with their count
  when they are done, then the bar and the line «Написано: N из M экранов
  · кейсов: K»; the «Без интерфейса» row likewise. Change nothing else
  there.
- One case per reachable AC (main, Alt, Exc), per state row and per
  user-causable response outcome not yet covered, per «Поля ввода» rule,
  per forbidden action per role.
- Steps name actions and data by the spec's names and screen ids — never a
  widget or a gesture («выполнить отмену брони», not «нажать кнопку»);
  expected results quote the exact text the screen spec takes from the
  frame's «Тексты» table and name the state row.
- Preconditions name the data, so a runner can seed it.
- End with the coverage table: AC → TC ids, or «Без интерфейса» + reason.
- Russian prose; ids, operationIds, paths untranslated.
- Write only OUTPUT PATH. Do not commit.
```

Report — last message, exactly:

```
STATUS        DONE | DONE_WITH_CONCERNS | BLOCKED
FILE WRITTEN  <path> | none
COUNTS        N cases · M AC covered of K · L «Без интерфейса»
GAPS          one line per behaviour the spec did not decide, or none
```
