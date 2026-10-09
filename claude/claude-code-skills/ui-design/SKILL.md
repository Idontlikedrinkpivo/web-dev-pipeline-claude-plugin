---
name: ui-design
description: >-
  Design stage: picks the visual direction (two or three options from
  `ui-ux-pro-max`, drawn as style tiles, the user chooses), draws the Figma
  mockups straight from the SRS (no API needed), restyles existing mockups
  to a new direction, and keeps the frames register
  documentation/ui/frames-register.md — screen ids S-n, nodeIds, states,
  nested steps. Decides the screen set from use cases and roles, runs the
  completeness checklist, dispatches figma-opus / figma-sonnet, or indexes
  frames a designer already drew. Use for «нарисуй макеты», «дизайн
  экранов», «макеты в фигме», «перекрась макеты», «новый стиль
  интерфейса», «визуальное направление», mockups or screens. Not the
  screen spec (`screen-spec`), not code (`frontend`).
---

# UI Design

Turns settled use cases into **frames**: which screens the product has,
what each one lets each role do, and how every flow, state and error looks.
The design starts right after the SRS and does not wait for the API — a
screen is drawn from what the actor must do and see, not from the endpoints
that will serve it. `screen-spec` later reads these frames together with
the OpenAPI contract and writes the per-screen spec.

Before the first frame the look is chosen: the **visual direction** —
palette, type, shape, density and the one characteristic thing — offered as
two or three style tiles in Figma and picked by the user. A new look for
frames already drawn is a **restyle**: the look changes; structure, texts
and ids stay.

The only file this skill writes in the repo is the **frames register** — a
map from screen ids to Figma nodes, not a contract. Every widget,
presentation, layout and wording choice lives on the frames, picked by the
Figma builder by `ux-patterns`. Nothing here is fed back into the SRS —
except what the user changes while looking at the frames that is not the
look but the behaviour: a field, a step, a right, a rule («убери поле»,
«пусть отмена будет без подтверждения»). That is a changed decision for the
SRS, landed and committed before the frame is redrawn (`pipeline` →
`references/decision-changes.md`).

Write the register and every user-facing message in Russian. Do not
translate ids (`S-`, `M-`, `UC-`, `Alt-`, `Exc-`, `AC-`, `A-`, `BR-`).

## Scope

**USE when:**
- An SRS exists and a human faces a screen
- The user has a Figma file to fill (an empty one is enough), wants one
  created, or a designer already drew frames that need ids and a
  completeness check
- The SRS grew (an increment) and the frames must follow

**NOT for:**
- What each element does, which operation it calls, its error outcomes —
  `screen-spec`, after the frames and the OpenAPI contract exist
- Deciding what to build — the SRS (`srs-writer`)
- Production screen code — `frontend` through `plan` → `work`

If there is no human-facing surface (an API, a worker, a CLI), say so in
one line and stop. Do not invent a console. The whole design branch is
skipped; `pipeline` names what follows.

**Handed to another person?** In the session of a person who took
this stage (`pipeline` → `references/team.md`): the version comes from the
branch `iteration/<version>`, inputs arrive by `git pull --rebase`, only this
stage's folder is written and committed, with no version change, and the
stage ends with the «готов и запушен» line for the owner instead of a
pipeline offer.

## Inputs

| Input | When |
|---|---|
| SRS `documentation/requirements/srs/srs.md` | always: actors and roles (§ actors), use cases with Main / Alt / Exc flows and their AC, business rules, NFR (widths, accessibility, languages). No SRS: ask once for it; do not invent `UC-` ids |
| `ui-wishes.md` beside the SRS (`documentation/requirements/srs/`) | when it exists. An input, never a contract: the builder weighs each wish against `ux-patterns` and the use case and may decide otherwise. A frame that departs from a wish is not a gap and not a finding anywhere |
| `ux-patterns` | always: the product-type variants and the completeness checklist (Полнота макета) |
| `ui-ux-pro-max`, `frontend-design` | the visual-direction step and a restyle: the design data, and the way to turn it into options that fit this product |
| A brand book or brand colours | when the SRS or the user names them: they pin the direction |
| Figma file | always; asked once (Entry question) unless the register already holds it |
| The frames register | on every run after the first: it holds the file, the mode, the header lines and every S-id |

Not inputs: `documentation/api/openapi.yaml` and the DB schema. A frame
never cites an `operationId` or a column; errors are drawn per SRS exception
flow (`UC-3 Exc-1`), and `screen-spec` maps them to status codes later.

## Order of a run

1. Entry question — only when there is no register yet.
2. Header lines — product type, widths, accessibility.
3. Visual direction — when the look is not chosen yet, or the user asks
   for a new one.
4. Mode **draw**: screen set and coverage plan → drawing → verification.
   Mode **index**: indexing → completeness questions to the designer.
   **Restyle**: the existing frames take the chosen direction →
   verification. **Redraw**: every screen drawn anew on a new page, the old
   frames untouched → verification.
5. Quality gate, then Closing and the next stage.

A later run (an SRS increment, a redesign request, «дорисуй состояние»,
«перекрась макеты») starts at step 2 with the register it finds, and
touches only what changed.

**Progress file.** Before the first Figma dispatch of a run — style tiles,
drawing, restyle, redraw, renaming — create
`documentation/plans/<version>/progress-design.md` per `pipeline` → `references/progress-files.md`: the
tiles and every screen of the run `⏳ ждёт`. Post its link in the chat
before the dispatch and pass it to the builder as `PROGRESS FILE`; the
builder marks each screen as it draws it, and the session marks `🔍
проверка` → `✅ проверен` as it verifies each one, writing the count with
the link in the chat after each verified screen and each returned dispatch
(`pipeline` → `references/progress-files.md` → After each item). Drawing a dozen screens
takes a long time, and the file is how the user tells progress from a
hang.

## Entry question

Ask once, when there is no register yet. One question in the chat, in
Russian, per `grill-me` → "How a question is shown". Do not open a question
card. A and B carry the file link, so this one message asks for it:

```text
**Вопрос 1. Есть ли уже макеты**

Макеты — это кадры экранов в Figma. От ответа зависит, рисую ли я их сам
или только описываю нарисованное дизайнером.

  A. Макеты уже нарисованы дизайнером — пришлите ссылку на файл. Я присвою
     экранам номера S-n, составлю реестр кадров и проверю, все ли сценарии
     и состояния нарисованы; пробелы станут вопросами дизайнеру.
  B. Макетов нет — пришлите ссылку на файл, где рисовать (пустой подойдёт).
     Я решу набор экранов по сценариям SRS и нарисую их. (Recommended)
  C. Макетов нет и файла нет — я создам пустой файл в вашем Figma сам и
     нарисую в нём. Можно добавить ссылку на проект Figma, куда его
     положить; без неё файл ляжет в черновики (Drafts).

Ответьте сообщением: буква и ссылка на figma.com (для C — не обязательна).
```

Recommend the option the user's earlier messages point to. A reply A or B
with no `figma.com` link writes nothing: ask for the link again, because
frames that cannot be opened cannot be drawn or indexed.

**C — creating the file.** Figma MCP `whoami` gives the user's plans (one
is used as is; several are one question), then `create_new_file`:
`editorType: "design"`, the plan's `key`, `fileName` «<продукт> — макеты»,
the `projectId` from a project link if given. Post the link, record it and
the `fileKey` in the register header, go on as B. Say in one line that a
Drafts file is visible only to its owner and can be moved to the team's
project (the link stays). No Figma MCP or a failed call: say why, ask for
a link (B).

Record the answer in the register header as **Кадры рисует:** `ui-design`
(B, mode **draw**) or `дизайнер` (A, mode **index**). A later run reads the
header and asks neither question again.

The answer and the file disagree — they chose A and the file has no product
frames, or chose B and the file already holds frames for these screens —
stop and say so. Do not pick a mode they did not pick.

The Figma MCP is required in both modes. If its tools are missing or
unauthorized, stop: do not invent node ids, and tell the user to connect and
authorize the Figma MCP once with `/mcp`. Use the `figma-*` skills when
installed; otherwise the MCP tools directly (`mcp__figma__*`, or
`mcp__plugin_dev-pipeline_figma__*` when the server comes from this plugin).

## Artifact — the frames register

Write `<repo-root>/documentation/ui/frames-register.md`. Resolve
`<repo-root>` via `git rev-parse --show-toplevel` (cwd if not a git repo).
`documentation/ui/` is shared with the screen specs `screen-spec` writes
(`screen-specs/`) and the test cases; create it when missing. Several UI
products (a client app and an admin) get one subfolder each,
`documentation/ui/<product>/`, holding the same files; one product keeps
everything straight in `documentation/ui/`. Read
`references/frames-register.md` before writing the register the first time —
it has the template and a filled example.

The register is an unversioned row of the `doc-versioning` Registry: no
`version`, no changelog, edited in place by every run, `updated:` moves on
every write; `screen-spec` cites it by path with no `@<version>`. Its
frontmatter `sources:` pins the SRS version the frames were drawn from
(`srs.md@<version>`), so a stale sweep sees frames that lag the SRS. The
visual-binding rule does not apply to it: it names frames.

What it holds:

- **Frontmatter:** `title`, `updated`, `sources:` (the SRS `@<version>`).
- **Header:** Figma URL and `fileKey`, **Кадры рисует**, **Тип продукта**,
  **Ширины**, **Доступность**, **Визуальное направление**, and in index
  mode **Слои по действиям**.
- **Экраны:** `S-n | Экран | Сценарии | Акторы | Кадр | Состояния | Вложенные
  шаги | Статус`. State and step cells list `имя → nodeId`. Статус is
  `черновик` or `готово к разработке`.
- **Общие состояния:** the app-wide states (session expired, too many
  requests, server error, offline) with their frames — not a screen, so not
  an `S-` id. `screen-spec` points its общий обработчик here.

Ids are append-only. `S-1…` is assigned here, by design; a screen dropped by
a redesign keeps its id with Статус `черновик` and a note, and its number is
never reused. `M-n` is numbered per screen (`S-2 · M1`).

Questions go in `documentation/ui/open-questions.md`, in the
`doc-versioning` → Открытые вопросы format — never into the register.

## Header lines

Fill them from the SRS before any drawing; the builder and `frontend`
otherwise guess them per screen.

| Line | From | When the SRS cannot tell |
|---|---|---|
| **Тип продукта** | the SRS actors: `B2B` (internal or business tool), `B2C` (public consumer web), or per area (`публичный сайт — B2C, админка — B2B`). It picks the variant of every `ux-patterns` rule that has one | row classed `Блокирует старт`, asked in the chat |
| **Ширины** | the NFR on devices and platforms (`1440, 375`); the desktop width always first (UX-74) | row classed `Блокирует старт`, asked in the chat with a proposal: B2B `1440, 375`; B2C `1440, 768, 375` |
| **Доступность** | the accessibility NFR | default `WCAG 2.2 AA`; say so in one line, no question |

Ask each missing line as its own question, per `grill-me` → "How a question
is shown", with a recommended option. Drawing waits for the answers; once
answered, write the line and remove the row. A deferred answer leaves the
row and nothing is drawn. **Визуальное направление** comes from the next
step, not from the SRS.

## Visual direction

The look every frame shares: palette, type, radius and shadow, density, and
the one characteristic thing. It is chosen once, before the first frame,
written into the register header as **Визуальное направление**, and reused
by every later run.

| Situation | What happens |
|---|---|
| Mode draw on a file with no product frames and no linked library | the step runs before the screen set is drawn |
| Product frames exist, the register has no direction (they were drawn before this step existed), and nobody asks for a new look | no step: new screens follow the existing frames; the line says `по кадрам файла` |
| The user asks for a new look of existing frames («перекрась», «новый стиль», «переработать интерфейс», «нарисуй заново») — a designer's frames too | the step runs, then Restyle or Redraw. When the request does not say which, ask once: **перекрасить** — the same frames, only the look changes; or **нарисовать заново на отдельной странице** — every screen drawn anew in the new direction, the old frames left untouched on their page. On a restyle of a designer's file, say once that their look changes and the old one is kept in `🗄 Архив` |
| A linked library, or a designer's frames (mode index), with no request for a new look | no step: the look is theirs; the line says `по библиотеке <имя>` or `по макетам дизайнера` |
| The SRS or the user pins the look (a brand book, brand colours) | the options stay inside that; with everything pinned, one option and no question |

Read `references/visual-direction.md` and follow it: a three-line brief
from the SRS; two or three options from `ui-ux-pro-max`, planned by
`frontend-design`, filtered for template tells (UX-60), Cyrillic and
contrast; style tiles drawn by `figma-opus` (`MODE direction`); one
question with the options; the answer written into the register. Drawing
and a restyle wait for the answer.

When the SRS has a public page, the same step offers its landing pattern
(the section order and the place of the main action). The effects the data
suggests are offered as proposals; each one the user picks becomes a line
in `ui-wishes.md`.

## Screen set — information architecture

In mode **draw**, and for new use cases on any later run, the session
decides which screens exist. This is a design decision; it lives only in the
register and the frames, never in the SRS.

1. List every use case with a human actor. A system-only actor (cron,
   webhook, another service) gets no screen.
2. Group by actor area first (a public face and an admin are separate areas
   and may differ in product type), then by the object the actor works on.
3. **One job per screen.** A screen serves the use cases that act on the
   same object in the same context (`Мои брони`: view, cancel, extend). Two
   unrelated jobs in one `S-` id are a question, not a merge.
4. A short task that belongs to a screen (confirm a destructive action, fill
   a small form) is a **nested step** `M-n` of that screen, not a new
   `S-` id. How it is shown — dialog, side panel, own page — is the
   builder's choice (UX-33); the `M` says nothing about presentation.
5. Every human use case lands on at least one screen; every screen serves at
   least one use case. Name each screen by its object or job (`Расписание
   переговорных`), never by its widget.
6. Name the entry for each screen (from where the actor arrives) and its
   neighbours — this is what the builder draws as navigation.

Then build the **coverage plan**: run `ux-patterns` → Полнота макета against
the screen set and write, per screen, what the frames must show — the flows
by id (`UC-3`, `UC-3 Alt-1`, `UC-3 Exc-2`), which actions each role sees or
does not see, the states the screen needs, the destructive actions and the
fields. That plan is the packet's `SCREENS`; the builder decides how.

Write the screen set into the register now — rows with empty frame cells
and Статус `черновик` — so a failed dispatch does not lose the ids. Show it
in the chat as a short table (`S-n | Экран | Сценарии | Акторы`) before the
dispatch. It is information, not a question: the
dispatch does not wait, and the user may redirect it at any time.

## Drawing (mode draw)

Read `executor-catalog` and `executor-catalog/references/figma-packet.md`.

**Read the file first, always** — also on the first run and when the
pipeline reached this step on its own. `get_metadata` on every page lists
the product frames already there; they go into the packet's `EXISTING
FRAMES`, and each in-scope screen gets its mark against them:

| Mark | When |
|---|---|
| `новый экран` | an `S-` id with no frame in the file |
| `правка` | the frame exists; this run adds or changes a flow, an action, a state, a field or a role on it |
| `редизайн` | the screen's structure changes, or the user called it a redesign. A new action on the old structure is `правка` |
| `без изменений` | the frame exists and nothing in this run touches it |
| `перекраска` | Restyle: the frame takes the chosen direction; nothing else on it changes |

A screen whose frame exists is never `новый экран`, whatever an earlier
plan said. An increment never redraws existing screens (a redraw of the
whole interface is the user's own request — Redraw on a new page): it touches only
the screens its new or changed use cases reach (the SRS changelog since the
register's `sources:` pin names them), and every other screen is `без изменений`,
keeps its ids, and stays out of `SCREENS`. A frame the register cites but
the file no longer has is a row in `open-questions.md`, not a silent
redraw.

**Design system.** Fill the packet's `DESIGN SYSTEM` from the file: the
libraries enabled in it (`get_libraries`), else its local variables
(`get_variable_defs` on a frame), else `none`. With `none` the builder
creates the token set from the chosen direction (the packet's `VISUAL
DIRECTION`) and draws the components itself in the shadcn/ui style; say so
in one line and that a shadcn/ui kit linked as a library (for example the
free Obra one) would bring the frames closer to the code. This is
information; the dispatch does not wait.

**Routing:**

| Situation | Executor |
|---|---|
| The file has no product frames, or any screen is `новый экран` or `редизайн`, or an app-wide state frame is missing | `figma-opus`, `MODE draw` |
| Every touched screen is `правка` | `figma-sonnet`, `MODE edit` |
| Style tiles of the visual direction | `figma-opus`, `MODE direction` |
| The existing frames take a new direction; nothing else changes | `figma-sonnet`, `MODE restyle` |
| Every in-scope screen is `без изменений` and the completeness check passes | nobody |

One subagent for the whole set; do not parallelize edits to one file.
Before the `Agent` call, write `Name | subagent_type` for the row and
dispatch that agent (`subagent_type: "figma-opus"` or `"figma-sonnet"`)
without asking which model, with no `model` unless the user named one. A
dispatch on `general-purpose` or any other agent is a failed dispatch:
discard its result. A missing agent or a rejected alias is a stop per the
catalog's Dispatch contract and Slug hygiene.

**Verification.** The report is the builder's claim. Before writing any id,
call `get_metadata` on each returned `nodeId`. An id that does not resolve,
or whose frame name does not start with its `S-` id (or `Общее ·` for an
app-wide state), is not written; that screen is not done. Then rerun the
completeness check on what is really in the file — the layer names
(`действие: …`, `ввод: …`, `шаг: M…`) and the state frames make it
checkable from metadata; one `get_screenshot` of a screen's `S-n · Аннотация`
frame shows its «Элементы» and «Тексты» tables. A miss goes back to
`figma-sonnet` with only the missing items, round after round while each
round places at least one (`pipeline` → `references/convergence.md`); an item no round can
place is a row in `open-questions.md` and the screen stays `черновик`.

Write the verified ids into the register and set a screen to `готово к
разработке` when its frames resolve, its completeness items pass, and its
Figma section is named `… · готово к разработке`. Move the `sources:` pin to
the SRS version the run drew from and `updated:` to today.

On failure (`BLOCKED`, unresolved ids), leave the ids empty and the screens
`черновик`, report what blocked, and do not offer the next stage.

## Restyle

A new look for frames that already exist: the visual direction changes;
the screens, their structure, layer names, texts, annotation frames and
every `nodeId` stay. It is not a redesign — a screen whose structure must
change is `редизайн` and goes through Drawing.

1. The visual-direction step has run and the user has chosen. The register
   line names the new direction and `прежнее: «<имя>»`.
2. Read the file: `get_metadata` on every page, `get_variable_defs` on a
   screen frame. Local variables are restyled in place. A linked library
   belongs to its designer: say so and stop — its variables are not edited
   from here.
3. Dispatch `figma-sonnet` with `MODE restyle`: `SCREENS` lists every
   screen of the register with the mark `перекраска` and its frames, `APP-WIDE STATES` the app-wide
   frames, `VISUAL DIRECTION` the chosen direction.
4. Verify: every `nodeId` of the register still resolves under its name;
   one `get_screenshot` per screen shows the new look with no clipped text
   and no template tells (UX-60). A miss goes back with only the missing
   items, round after round while each round fixes at least one; what no
   round can fix is a row in `open-questions.md`.

The register's ids and statuses do not change; `updated:` moves on. When
the frontend is already built (the repository holds the screens' code),
the next stage is `plan`: its theme unit carries the `🎨 Tokens` variables
into the project's theme file. The screen specs stay valid, because only
the look changed.

## Redraw on a new page

The whole interface drawn anew in the chosen direction, on its own page.
The old frames stay exactly as they are on theirs — a designer's work is
neither restyled nor archived, and both versions can be compared side by
side.

1. The visual-direction step has run and the user has chosen.
2. Read the file: `get_metadata` on every page. Every product frame goes
   into `EXISTING FRAMES` and stays untouched.
3. Dispatch `figma-opus` with `MODE draw`, `PAGE` a new page `✅ Экраны ·
   «<имя направления>»`, every screen of the register in `SCREENS` marked
   `редизайн` with its old frames as the reference, every app-wide state
   `draw`, and `VISUAL DIRECTION`. The screens keep their S-ids and M-ids,
   and each element keeps the № and layer name of the old annotation
   wherever it stays, so the screen specs need new nodeIds rather than a
   rewrite.
4. Verify as in Drawing. The register then points at the new frames: the
   frame, state and step cells take the new nodeIds; the header says
   **Кадры рисует:** `ui-design`, drops **Слои по действиям**, and adds
   **Прежние кадры:** the old page, who drew it, and that it is no longer
   used.

The next stage is `screen-spec` for every screen — the nodeIds changed,
and an element the builder added or reshaped needs its row — then
`ui-test-cases` (write) for the frame ids, then `plan`.

## Indexing (mode index)

A designer drew the frames; this skill describes them and finds what is
missing. It does not draw over a designer's work.

1. Read the file: `get_metadata` on every page (frame names, layer names,
   ids), one `get_screenshot` per screen frame. Use `get_design_context`
   only when metadata and the screenshot cannot tell what an element is,
   and load `figma-design-to-code` before that call — it is a code read and
   pulls assets this step does not need.
2. Recognise screens, their state frames and nested-step frames. Assign
   `S-n` in the order of the user's path; map each frame to the use cases
   and actors it serves. A frame whose role is unclear (is this a state of
   S-2 or its own screen?) is a question to the user, one per message.
3. Fill the register with the designer's frames as they are. Do not rename
   frames to `S-n · …`: the register is the map, and a designer's file
   keeps its names.
4. Run `ux-patterns` → Полнота макета against what is drawn. Every miss is a
   question to the designer: a row in `open-questions.md` («Дизайнеру: нет
   кадра для UC-3 Exc-2 — бронь уже отменена»), classed `Блокирует старт`
   when a use-case flow or a role has no frame, otherwise `Отложено`. List
   them in the chat too, grouped by screen.
5. Layers named by action (`действие: отмена брони`) and an `S-n · Аннотация`
   frame with numbered «Элементы» and the «Тексты» table let `screen-spec`
   map the frames reliably. When the file lacks them, ask once, in one
   message, whether to add them: renaming layers and adding annotation
   frames beside the screens, without changing anything the actor sees. A
   yes dispatches `figma-sonnet` with `MODE rename` (see the packet); a no
   is recorded in the register header (**Слои по действиям:** нет) and
   `screen-spec` reads the frames as they are.

A screen in index mode becomes `готово к разработке` when its frames are
in the register and no `Блокирует старт` row names it. When the user asks to
fill a gap rather than wait for the designer, that screen is drawn as in
mode draw — `figma-opus` matches the designer's look from `EXISTING FRAMES`.

## Quality gate

Check before closing; a failure is fixed or becomes an `open-questions.md`
row named in Closing.

1. Every human use case is on at least one screen, and every screen serves
   at least one use case — Screen set.
2. Every `ux-patterns` → Полнота макета item holds for every in-scope
   screen, or has its row in `open-questions.md` — Verification / Indexing.
3. Every id in the register resolves in the file (`get_metadata`); none was
   copied from a report unchecked.
4. No `без изменений` screen was redrawn, moved, or renamed; no frame in
   `EXISTING FRAMES` changed outside the run's `SCREENS`; after a redraw on
   a new page, no old frame changed at all.
5. The header has **Тип продукта**, **Ширины** and **Доступность**, or the
   run stopped on their `Блокирует старт` rows.
6. The register cites no `operationId`, column, or HTTP status — those
   belong to `screen-spec`.
7. Ids were only appended: no `S-` or `M-` id was renumbered or reused.
8. The header has **Визуальное направление**, or says whose look the
   frames follow (a library, a designer).
9. The screenshots show realistic content in Russian — no «Lorem ipsum»,
   «Название 1» or empty tables standing in for data.

## Gate and next stage

The frames are not a document, so this stage has no `grill-me` or
`doc-review` gate of its own; the completeness check above is its check.
`ui-wishes.md` is never grounds for a finding here.

## Closing

Report, in Russian: the register path, the mode, `S-1–S-n` with each
screen's mark for this run (`новый экран`, `правка`, `редизайн`, `без
изменений`), which executor drew (or that none did), and the open rows by
class.

When frames were drawn, list the Figma sections whose name now ends in
`готово к разработке` and ask the user to mark them **Ready for dev** in Dev
Mode — the pipeline cannot set that status itself. One line, not a
question; the stage does not wait for it.

After a restyle, name the direction and the screens restyled; after a
redraw, the new page and the screens drawn on it.

Then read `pipeline` and ask about the stage its table names after this one
(normally `screen-spec`, which needs these frames and the OpenAPI contract;
`pipeline` says what runs first when the contract is missing; after a
restyle of screens already built, `plan`; after a redraw, `screen-spec`
for every screen), per "Asking before a transition". A no stops the sitting. While frames are still
missing (a failed dispatch, a blocking header row), the last message is the
blocker, not the next stage.
