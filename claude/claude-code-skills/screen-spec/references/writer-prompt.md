# Writer packet and report

`screen-spec` sends this to `screen-writer`, one dispatch per screen (or a
batch of up to three small ones). The subagent starts with a clean context:
what is not in the packet does not exist for it. It reads Figma and the API
itself and writes the files itself; there is no `doc-typist` on this stage.

## The packet

```
You write the front-end spec (ТЗ на экран) for the screens below, one file
per screen, from the Figma frames, the OpenAPI contract and the SRS. You do
not draw or edit frames, you do not edit the API, the SRS or the register,
and you decide no product behaviour: what the inputs do not settle is a
Разрывы row with its owner (design | API | SRS), never a guess. You cannot
ask the user.

SKILL           <path to screen-spec/SKILL.md> — follow "What each file
                holds", "The sync check" and the Writer half; skip the
                Orchestrator half. Read references/template.md before the
                first file and copy its shape exactly.
MODE            greenfield | increment
UI FOLDER       documentation/ui/ | documentation/ui/<product>/ (several UI
                products: the register and screen-specs/ paths below sit
                in that subfolder)

SCREENS
  <one block per screen:
   S-n · <Экран> → OUTPUT PATH documentation/ui/screen-specs/S-<n>-<slug>.md
   the register row as is: Сценарии, Акторы, Кадр, Состояния, Вложенные шаги
   Аннотация frame nodeId: <nodeId> | not found
   WHY (increment only): what changed — frame, operation, SRS rule, new screen>

INPUTS (read in full)
  Register:   documentation/ui/frames-register.md
              (header: fileKey, Тип продукта, Ширины, Слои по действиям;
               «Общие состояния» → Общее · … frames)
  Figma:      fileKey <key>
  OpenAPI:    documentation/api/openapi.yaml | none (no HTTP)
  SRS:        documentation/requirements/srs/srs.md@<version>
              (the register's sources: pin)
  Existing file (increment): <path> | none

GENERAL HANDLER
  <the `общий обработчик` rows from an existing screen file of this product,
   to copy word for word | derive — you are the first writer: build them
   from «Общие состояния» and their texts, and return them in the report>

RULES
- Figma reads: get_metadata on every screen, state, nested-step and
  Аннотация frame; one get_screenshot per screen, state and nested-step
  frame; get_design_context on the Аннотация frame to copy its «Элементы»
  and «Тексты» tables verbatim, and on another frame only when metadata and
  the screenshot cannot tell what an element is. Use the figma-* skills when
  installed, else the Figma MCP tools (mcp__figma__* or
  mcp__plugin_dev-pipeline_figma__*). Neither available → BLOCKED.
- № comes from the annotation's «Элементы» table, one numbering across the
  screen and its nested steps; never renumber. With «Слои по действиям: нет»
  number in reading order and add the Разрыв «нет аннотации — № назначены ТЗ».
- Every text in «» is copied from «Тексты». It is keyed by element and SRS
  flow, not by status: map flow → SRS named error → the status whose error
  code the operation declares, and write the flow id beside the code.
- Every branch of an interactive element ends in one outcome of the closed
  set; every non-success status of every called operation has a row in
  «Ошибки ответов»; every computed value is defined once in «Производные
  значения» with its rule id or «из API».
- Never in words: colours, sizes, icons, borders, positions, hover, cursor,
  focus ring, progress on a running request, backend services or SQL, a
  column name, the text of a business rule (cite its SRS id).
- Run the eight sync checks; each miss is one Разрывы row with one owner.
  Grep every operationId, field path, error code and status in
  documentation/api/openapi.yaml before writing it. Every placeholder in a
  text needs a source. Before writing «нет кадра / нет текста», search the
  annotation.
- No library or component names and no timings the frame does not state.
- «Загрузка и вызовы» is a numbered list in call order; a call whose input
  comes from an earlier response names that item and the field:
  «2. После ответа 1 → getCourseProgram (program_id из ответа 1)». No
  diagram file.
- Greenfield: frontmatter version: <the open iteration's version, e.g.
  0.1.0>, updated today, sources (SRS and API pinned as path@<version> —
  the version each was read at — register by path), figma: <fileKey> /
  <nodeId>; one «первый выпуск» journal row at that version. Increment:
  rewrite the file in place, keep its path, leave version, updated and the
  journal alone, drop resolved Разрывы rows.
- Russian prose; ids, operationIds, field paths and nodeIds untranslated.
- Write only the OUTPUT PATHs. Do not commit. Do not run doc-review or
  pipeline.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS          DONE | DONE_WITH_CONCERNS | BLOCKED
FILES WRITTEN   one line per screen:
  S-1  documentation/ui/screen-specs/S-1-<slug>.md · 9 элементов · 5 состояний · 12 строк ошибок · Разрывы: design 2, API 1, SRS 0
SYNC CHECK      per screen: the eight checks — ok | the count of misses
FIGMA READS     per screen: get_metadata N · get_screenshot N · get_design_context on <nodeIds>
GENERAL HANDLER the общий обработчик rows as written (only when derived here) | copied
CONCERNS        one line each, or none
BLOCKER         only for BLOCKED: what is missing (MCP, register row, operation)
```

A screen with no file, or a file that cites a `nodeId` the writer did not
read from Figma, is not done. The session checks the files on disk; the
report is the writer's claim.
