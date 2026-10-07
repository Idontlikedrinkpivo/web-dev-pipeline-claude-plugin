---
name: screen-spec
description: >-
  Writes the front-end spec for each screen (ТЗ на экран), one file per S-n,
  after the mockups exist: reads the frames register, the Figma frames via
  MCP and documentation/api/openapi.yaml, and maps every frame element to
  its behaviour per condition, operationId and fields, plus states,
  response errors and derived values, citing the SRS. Use after `ui-design` when asked for «ТЗ на фронт»,
  «ТЗ на экран», «опиши экран для фронта» or a screen spec. Not for drawing
  frames (`ui-design`) or screen code (`frontend`).
---

# Screen Spec

The frames show what a screen looks like; the API says what an operation
takes and returns; the SRS says who may do what. None of them says which
element calls which operation in which condition, which response field it
shows, and what the actor sees when that call answers `409`. A front-end
developer left with the three decides those links alone, and each screen
decides them differently. The screen spec is that missing layer: one file
per screen, written after the mockups, read side by side with the frame.

Because it is written after the design, it may point at the frames — by
`nodeId` and component variant — and quote their texts. It still never
describes the look in words: the frame is the look, and a sentence about a
green outline goes stale the day the designer changes it.

Write every file in Russian. Do not translate ids (`S-`, `M1`, `UC-`, `A-`,
`BR-`, `FR-`), `operationId`s, field paths, or `nodeId`s. Template headings
stay as `references/template.md` writes them.

## Not this skill's job

| Not here | Owner |
|---|---|
| Drawing or changing frames, naming screens `S-n`, the «Тексты» wording | `ui-design` — a frame that is wrong is a Разрыв with owner `design` |
| Adding or changing an operation or a response | `openapi-spec-generator` — a Разрыв with owner `API` |
| Deciding who may do what, or a business rule | the SRS (`srs-writer`) — a Разрыв with owner `SRS` |
| Screen code | `frontend`, through `plan` → `work` |
| Test cases | `ui-test-cases` (write), the stage after this one |
| Global interface behaviour (hover, focus ring, progress on a running request, Escape closes a dialog) | `ux-patterns` — it applies to every screen and is never restated here |

No human-facing surface means no frames register and no screens: the whole
design branch is skipped per `pipeline` → Skips. Do not invent a console.

## Inputs

| Input | Required | Use |
|---|---|---|
| Frames register `documentation/ui/frames-register.md` | always | header (fileKey, Тип продукта, Ширины, Доступность, «Слои по действиям»), `sources:` (the SRS pin); table «Экраны» — `S-n`, UC ids, actors, screen / state / nested-step `nodeId`s, status; table «Общие состояния» — the app-wide state frames (`Общее · …`). Missing → stop and name `ui-design` |
| The Figma file the register names, through the Figma MCP | always | layers named by action, variants, the `S-n · Аннотация` frame (Фокус line, numbered «Элементы», «Тексты»). MCP unavailable → stop: never invent a `nodeId` or a text. Tell the user to connect and authorise the Figma MCP once with `/mcp` |
| `documentation/api/openapi.yaml` | when the product has HTTP | every `operationId`, field path and declared status. Frames done but no API yet → stop and name `openapi-spec-generator` (`pipeline`: the screen specs wait for the contract) |
| The SRS `documentation/requirements/srs/srs.md` | always | actors (`A-n`) and what each role may do, UC ids, rule ids (`BR-`, `FR-`) to cite |
| `ux-patterns` | always | the completeness list of states, and what is global (not restated) |

The DB schema is not an input: a screen sees the API, never a column. The
architecture is not an input either. `ui-wishes.md` is never grounds for
anything here: a frame that departs from a wish is not a Разрыв.

## Artifact

One file per screen: `documentation/ui/screen-specs/S-<n>-<screen-slug>.md`,
in the folder beside the frames register (`S-1-schedule.md`,
`S-4-booking-form.md`). With several UI products each has its own
`documentation/ui/<product>/` holding its register and `screen-specs/`; one
product keeps everything straight in `documentation/ui/`.
`<screen-slug>` is the screen name in kebab-case Latin, chosen once; the
filename never changes afterwards, because plans, tests and code cite it.
Resolve the repo root with `git rev-parse --show-toplevel` (cwd if not a git
repo).

Read `references/template.md` before writing or checking a file: it holds
the exact template and a filled example (S-1 «Расписание» of a room-booking
product).

Each file is a versioned document under `doc-versioning`: a new file is born
at the open iteration's service version (the `documentation/plans/<version>/`
folder; `0.1.0` on greenfield) with one «первый выпуск» row in
`## Журнал изменений` (the SRS's Russian columns). After that, writers edit
the body in place and never touch `version`, `updated`, or the journal; the
stamping commit (`doc-versioning`) writes the version and the rows. `doc-review` sets `reviewed:`
when its gate closes. Downstream of a screen spec: `ui-test-cases` and the
plan's screen units.

Questions the user defers during `doc-review` go to `open-questions.md`
beside the frames register, one file for all screens of the product, each
row starting with its `S-n`. Mismatches the writer finds are not questions:
they are Разрывы rows inside the screen's own file.

## What each file holds

The sections, in order (template in `references/template.md`):

1. **Экран** — actors with their conditions, UC ids, where the actor comes
   from, which `S-n` and `M<n>` it leads to, the narrow-width frame (the
   register's `375 → nodeId`), and the **Фокус** line from the annotation:
   where focus lands at entry, after a nested step closes, and after a
   failed submit, named by element number.
2. **Загрузка и вызовы** — an ordered list «условие → `operationId`
   (параметры)»: when the screen calls what, in the order the front makes
   the calls. When a call's input comes from an earlier call's response, its
   item names that earlier item and the field it takes: «2. После ответа 1 →
   `getCourseProgram` (`program_id` из ответа 1)». A reload after a mutation
   is not such a dependency. The list is Frontend ↔ API only: no services,
   databases or internal hops behind the API. A screen spec has no diagram;
   the numbered items carry the order.
3. **Элементы** — one row per row of the annotation's «Элементы» table
   (`№ | слой | поток`). `№` is that number: one numbering across the screen
   and its nested steps, append-only, so a removed element leaves a gap and
   this skill never renumbers. «Элемент» is the layer's name without its
   prefix (`действие: отмена брони` → «отмена брони»). «Поведение по
   условиям» gives, per condition (role, a flag or value from the API, a
   derived value), what the element shows and the outcome. «Метод и поля» names the `operationId` and the
   response or request field paths (`rooms[].bookings[].can_cancel`;
   `cancelBooking` ← `bookingId` = `rooms[].bookings[].booking_id`), or
   `текст кадра` for a static text. «Кадр» is the `nodeId` and the component
   variant (`16:760 · Слот=Своя`). A nested step `M<n>` (`M1`, as the
   register numbers it) is its own subsection under Элементы, with the rows
   of its elements.
4. **Поля ввода** — only when the screen has inputs: field, required, the
   rule (`operationId` → property and its constraint, or an SRS id), when it
   is checked (`при уходе с поля`, `при отправке`, `ответ <код>`), and the
   error text verbatim from «Тексты».
5. **Состояния экрана** — every state the register's «Состояния» cell lists,
   under the register's name (`Loading`, `Empty`, `Error`, `Forbidden`,
   `Занято (UC-4 Exc-1)`), and every other state from the `ux-patterns`
   completeness list that can happen on this screen: when it happens (the
   call and the response that lead there), what is visible and what the
   actor can do, its frame. App-wide states are one row pointing to the
   register's «Общие состояния». A state that cannot happen is one line
   saying why («Forbidden — не бывает: экран открыт обеим ролям, SRS §2»).
6. **Ошибки ответов** — every non-success status every called operation
   declares, with what happens and its frame. Statuses the app handles the
   same way everywhere (typically `401`, `429`, `5xx`, no network) are rows
   marked `общий обработчик`, each pointing to its `Общее · …` frame from the
   register's «Общие состояния»; their text is identical in every screen
   file of the product (Orchestrator step 4).
7. **Производные значения** — every value the front computes, defined once:
   name, how it is computed from which fields, the SRS rule it implements; or
   `из API: <field>` when the server already gives it. Element rows refer to
   the name and never repeat the formula.
8. **Разрывы** — what the sync check found: what does not match, where
   (element number, `nodeId`, `operationId` + status, SRS id), the owner
   (`design` | `API` | `SRS`), and what the spec says meanwhile.

### The outcome of an action is a closed set

Every branch of an interactive element ends in exactly one of these:

| Outcome | When |
|---|---|
| операция `<operationId>` | the action calls HTTP; the id is copied from `documentation/api/openapi.yaml`. Its success is described in the element row, its errors in «Ошибки ответов» |
| шаг `M<n>` | opens a nested step of this screen (the layer `шаг: M<n>`; its frame is in the register's «Вложенные шаги») |
| переход на `S-n` | navigates, with the parameters it carries (`room_id`, `starts_at`) |
| закрытие | leaves the nested step or the screen |
| значение формы | the value waits and leaves with another element's operation |
| нет действия | the element only shows data in this condition |

An action that needs an operation the API lacks is written as
`операция — нет в OpenAPI` plus a Разрыв with owner `API`. Do not invent an
`operationId`.

### What a file never contains

- **A description of the look.** No colours, sizes, borders, icons or
  positions in words. «Пройден: зелёная обводка, бейдж с галочкой» becomes
  «вариант `Урок=Пройден` (12:340)». The frame and the variant name carry it.
- **Wording that is not on the frame.** Every text in «» is copied verbatim
  from the «Тексты» table on the screen's `S-n · Аннотация` frame. A meaning
  with no row there is a Разрыв (`design`) with `текст — нет в «Тексты»`,
  never a sentence the writer composes. The table is keyed by place and
  SRS flow, not by HTTP status (`S-1 · Empty`, `M1 · заголовок`,
  `№4 отмена брони · UC-3 Exc-1`, `№2 длительность · ошибка`): to put a
  text on a status row, follow the flow to the SRS named error and to the
  status whose error code the operation declares for it (`UC-3 Exc-1` →
  `BOOKING_STARTED` → `cancelBooking` `409`). A flow that maps to no
  declared status, or a status no flow explains, is a Разрыв.
- **Backend internals.** No services behind the API, no SQL, no «бэкенд
  объединяет прогресс с подпиской». The API is the boundary the front sees.
- **An implementation choice.** No library or component name («Sonner»,
  «MUI Dialog») and no timing the frame does not state: the stack and
  `ux-patterns` decide those; the spec names the outcome («сообщение об
  успехе», UX-27).
- **Global behaviour.** No «курсор меняется на pointer», no hover, no focus
  ring, no «кнопка показывает загрузку» — `ux-patterns` holds those for every
  screen. Only a screen-specific departure is written, with its
  «Исключение UX-<n>» from the frame's annotation.
- **A restated business rule.** «Урок доступен, если пройден предыдущий» is
  the SRS's; the spec cites `BR-4` and, when the API computes it, the field
  (`is_available`). The front never recomputes a rule the API already
  returns; when the API does not return it and computing it on the front
  would duplicate a business rule, that is a Разрыв (`API`).
- **A column name.** A field path is from the API response, not the table.

### The sync check

The writer runs it while writing, not afterwards; each miss is a Разрывы row.

1. Every UC action of the screen's UC ids, as the SRS states it, has an element
   row (or a nested-step row). An action with no element → `design`.
2. Every interactive element on the frame (layers `действие: …`, `ввод: …`,
   `шаг: M<n>`) maps to an outcome from the closed set. An element with no action or operation
   → `design` or `SRS`, whichever has to decide.
3. Every status an operation declares has a row in «Ошибки ответов» with an
   outcome; a declared status with no frame or no text → `design`; a status
   the screen must handle that the API does not declare → `API`.
4. Every data field the frame shows exists in an API response (or is a
   derived value built from one). Missing → `API`, or `design` when the frame
   shows data the SRS never asked for.
5. Every state in the register's «Состояния» has a frame, and every state the
   screen can reach has a row. Missing frame → `design`. Which frame applies
   at which width comes from the register's «Ширины»; a width between two
   drawn frames with no stated switch point → `design`.
6. Every placeholder in a quoted text (`{interval}`, `{N}`) has a source: a
   response or error-body field, a value the screen already holds, or a
   derived value. A text that needs data no response returns → `API`.
7. Every input limit a frame shows (one date only, hours, length, a
   required mark) matches the request schema and the SRS. The frame stricter
   than both → `design` or `SRS`; the API looser than the SRS → `API`. Also
   check the cases the SRS forbids and the frame does not show (a time in
   the past, a range that ends before it starts).
8. Every identifier written — `operationId`, field path, error `code`,
   status — is copied from `documentation/api/openapi.yaml`, case and
   spelling included; grep each before writing it. A status or code the API
   does not declare is not written as declared; it is a Разрыв (`API`).

Before a Разрыв says something is missing («нет кадра», «нет текста»),
search the annotation's «Элементы» and «Тексты» and the register's states
for the element number and the SRS id. A Разрыв that the frame disproves
sends the frontend developer to the designer for nothing.

## Orchestrator (session)

The session writes no screen file. `screen-writer` reads Figma and the API
and writes the files itself; there is no `doc-typist` on this stage.

1. **Find the register.** Missing → stop and name `ui-design`. Read its
   header and both tables. Only screens with status `готово к разработке`
   in «Экраны» are specified; a `черновик`
   screen is left out and named in the close, because its frame may still
   move.
2. **Check the other inputs.** The product has HTTP and
   `documentation/api/openapi.yaml` is missing → stop and name
   `openapi-spec-generator`. Call `get_metadata` on one screen `nodeId` from
   the register to prove the Figma MCP answers; failure → stop with the
   `/mcp` instruction. The SRS path comes from the register's `sources:`; a
   pin behind the SRS's current `version` is said in the chat (`doc-versioning`
   → Staleness) — the frames may lag the SRS.
3. **Pick the screens.**
   - No screen file exists yet → every ready screen.
   - Screen files exist (an increment) → a screen is in scope when its frame
     changed, its operations changed, a rule it cites changed, or the
     register added it. Check each existing file against its frame:
     `get_metadata` on the screen, state and nested-step `nodeId`s, and
     compare element numbers, variants and node ids with the file's «Кадр»
     column; compare the operations in «Метод и поля» with
     `documentation/api/openapi.yaml`;
     read the SRS journal for the cited rule ids. A screen with no evidence
     of change is not dispatched and its file is not touched.
   - The user named screens → those, plus nothing else.
   Write the list in the chat with the reason per screen («S-3 — кадр 22:10:
   новый элемент 7»), then dispatch; this is not a question.
4. **Settle the general handler once.** The rows for `401`, `429` and `5xx`
   must read the same in every file. When a screen file exists, copy its
   `общий обработчик` rows. Otherwise the first writer derives them from the
   register's «Общие состояния» (Сессия истекла, Слишком много запросов,
   Ошибка сервера, Нет сети — each an `Общее · …` frame) and their texts;
   the session copies the returned rows into every later packet. A status
   the app must handle globally with no row there is a Разрыв (`design`).
5. **Progress file, then dispatch.** Before the first dispatch, create
   `documentation/plans/<version>/progress-screen-specs.md` per
   `pipeline` → `references/progress-files.md` with every screen in scope `⏳ ждёт`, and post its
   link in the chat. A screen goes `✍️ пишется` when its writer is
   dispatched, `🔍 проверка` when its file lands, and `✅ готово` with its
   element and Разрывы counts after step 6 (or `🔁 возвращено: …`).
   Read `executor-catalog`. Resolve `screen-writer`, write the
   resolved row (`screen-writer | dev-pipeline:screen-writer`) and dispatch it
   with `references/writer-prompt.md`, without asking which model and with no
   `model` on the call. One dispatch per screen; a batch of up to three only
   when each is small (about eight elements or fewer, no nested step).
   Dispatch one at a time, not in parallel: a parallel dispatch would need a
   worktree, which starts from HEAD and misses the uncommitted register and
   API, and the Figma MCP serves one reader at a time better. A missing agent
   or a rejected alias is a stop per the catalog.
6. **Inspect each file on disk** against the Quality gate below. Mechanical
   checks first: every `operationId` in the file exists in the contract
   (searched over `documentation/api/`); every non-success status those
   operations declare has a row in «Ошибки ответов»; every «Кадр» `nodeId`
   resolves (`get_metadata` on a sample of three, and on every one the
   writer flagged); no look words (`цвет`, `зелён`, `серым`, `обводк`, `px`,
   `курсор`, `ховер`). A miss sends that screen back with the list, round
   after round while each round closes something; when progress stops it
   is a stop with the report (`pipeline` → `references/convergence.md`). Do not edit the file
   yourself.
   `BLOCKED` from the writer is reported as is; there is no escalation row.
7. **Close** (below), then ask the gate and the next stage.

## Writer (dispatched)

You write the screen files the packet names, following this skill and
`references/template.md`. You cannot ask the user: what the inputs do not
decide is a Разрыв, not a guess.

**Read the frames.** For each screen: `get_metadata` on the screen frame,
each state frame, each nested-step frame, and the `S-n · Аннотация` frame —
layer names (`действие: …`, `ввод: …`, `шаг: M<n>`, `данные: …`), component
variants, `nodeId`s. The annotation's «Элементы» table gives each layer its
`№` and flow; its Фокус line goes into Экран. When the register says
**Слои по действиям: нет** (a designer's file left as drawn), read the
layers as they are, number elements in the user's reading order, and add
one Разрыв (`design`): «нет аннотации — № назначены ТЗ». One
`get_screenshot` per screen, state and nested-step frame, to see what the
metadata cannot tell. The «Элементы» and «Тексты» tables must be copied verbatim: read them
with `get_design_context` on the annotation frame only, because a screenshot
read risks a typo. Call `get_design_context` on another frame only when
metadata and the screenshot cannot tell what an element is or which variant
it uses; it is a code-generation read and pulls assets this step does not
need. When the `figma-*` skills are installed, follow them for these calls;
otherwise use the Figma MCP tools directly (`mcp__figma__*`, or
`mcp__plugin_dev-pipeline_figma__*` from the plugin). Never write a
`nodeId` you did not read from the file.

**Read the contract.** In `documentation/api/openapi.yaml`, each operation
the screen calls: parameters, request body, response schema with its field
paths, every declared status with its error code. From the SRS: the actors
on this screen and what each may do, the UC flows (main, Alt, Exc) with
their named errors, and the rule ids behind each condition. Build the map
flow → named error → status before copying texts (What a file never contains
→ wording).

**Write.** Fill the template section by section, run the sync check, and
put every miss in Разрывы. On an increment, rewrite the screen file in
place: re-read its frames and operations, keep the file's path, keep `№` as
the annotation now gives it, remove Разрывы rows that are resolved, and
leave `version`, `updated` and the journal alone. Write only the files in
the packet. Do not commit, and do not run `doc-review` or `pipeline`.

## Quality gate

1. Every section of the template is present in order; Поля ввода is omitted
   only on a screen with no inputs; «Загрузка и вызовы» is a numbered list,
   each dependent call naming the earlier item and the field it takes, and
   no diagram anywhere.
2. Every element of the annotation has a row with `№`, behaviour per
   condition, method and fields (or `текст кадра`), and `nodeId` · variant.
3. Every interactive branch ends in one outcome from the closed set; every
   `операция` id exists in the contract (`documentation/api/`).
4. Every non-success status of every called operation has a row in «Ошибки
   ответов»; `общий обработчик` rows match the other screen files of the
   product word for word.
5. Every text in «» is in the frame's «Тексты» table; a missing one is a
   Разрыв, not prose.
6. Every computed value is in «Производные значения» once, with its rule id
   or `из API`; no element row repeats a formula; no business rule the API
   returns is recomputed.
7. No look in words, no backend internals, no global `ux-patterns` behaviour,
   no column names, no restated rule text.
8. The eight sync checks ran; each miss is a Разрывы row with one owner, and
   no «нет кадра / нет текста» row is disproved by the annotation.
9. Frontmatter has `version`, `updated`, `sources` (SRS and API pinned as
   `path@<version>`, the register by path) and `figma: <fileKey> / <nodeId>`.

## Closing

Report in the chat:

- each file written or rewritten, with its element and Разрывы counts;
- screens left out: `черновик` in the register, or untouched on an increment;
- Разрывы grouped by owner, with the stage that fixes them — `design` →
  `ui-design`, `API` → `openapi-spec-generator`, `SRS` → `srs-writer`. This
  skill fixes none of them; a fix there re-runs this stage for the affected
  screens;
- the executor rows dispatched (`screen-writer` × N) and any re-dispatch.

Then read `pipeline` and ask per "Asking before a transition": first the
gate `doc-review` on the files just written (one review over the set — its
verdict goes on the progress file's «Ревью ТЗ» line), then
the next stage its table names — `ui-test-cases` in mode write. A skipped
gate is named in the report and blocks nothing; a declined offer stops the
sitting.

## References

- `references/template.md` — the file template and a filled example. Read
  before writing or checking a file.
- `references/writer-prompt.md` — the packet and report for `screen-writer`.
- `executor-catalog` — the Dispatch contract.
- `doc-versioning` — versioning of each screen file, `open-questions.md`.
- `ux-patterns` — the completeness list of states and the global behaviour
  this spec does not restate.
- `pipeline` — the gate and the next stage.
