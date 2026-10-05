# Figma packet and report

`ui-design` sends this when at least one screen is `новый экран`,
`правка`, or `редизайн`, when an app-wide state frame is missing, when the
file has no product frames, or — in index mode, with the user's consent —
to name a designer's layers by action (`MODE rename`). The subagent starts
with a clean context. What is not in the packet does not exist for it.

The input is the SRS, not a UI spec: the packet says which flows, roles,
states and rules each screen must cover, by id; the builder decides every
widget, presentation, layout and text. The session writes the frames
register and verifies every `nodeId`. The subagent does not edit the
repository.

## The packet

```
You create or edit Figma frames. You do not edit the repository.
You do not invent a use case, a flow, a role, a rule, or a field that the
SRS excerpt does not contain.

SKILL           Follow the Figma skills for building and editing frames
                (figma-use, and figma-generate-design when a frame is new
                or redesigned). If those skills aren't installed, use the
                Figma MCP tools directly (`mcp__figma__*`, or
                `mcp__plugin_dev-pipeline_figma__*` from the plugin); if
                neither is available, return BLOCKED. Load `ux-patterns`
                too: Sections 1–6 for every frame, Section 7 when PRODUCT
                TYPE is B2C, and «Полнота макета» for what every screen
                must show. The SRS is the behaviour; you are the design.
                You choose every widget, presentation and layout: an
                action becomes a button, link or menu item; a choice a
                dropdown, radio group or segmented control; a nested step
                a dialog, side panel or page; a status message a toast,
                banner or inline line; a collection a table, cards or a
                list — each by `ux-patterns` for PRODUCT TYPE and the
                data's size. You also write every text the actor reads.

EXECUTOR        figma-opus | figma-sonnet
FILE            <figma.com URL>
MODE            draw | edit | rename
SRS             documentation/requirements/srs/srs.md@v<N>
PRODUCT TYPE    <B2B | B2C | per area: …>
VIEWPORTS       <the Ширины line: main width first, then the narrow one>
ACCESSIBILITY   <the Доступность line, e.g. WCAG 2.2 AA>
DESIGN SYSTEM   <linked library name | local variables in this file | none | not checked>

SRS EXCERPT     <pasted verbatim for the use cases in SCREENS: the actors
                and roles; each UC with its Main, Alt-n and Exc-n flows and
                every AC; the BR and FR rules those flows cite (limits,
                formats, required data); any text the SRS requires
                verbatim, with its BR>
UI WISHES       <the lines of documentation/requirements/srs/ui-wishes.md
                that relate to these use cases, or none. An input, not a
                contract: weigh each against `ux-patterns` and the use
                case and decide; follow it or not, and say why on the
                annotation when you do not>

SCREENS
  <for each screen this run touches:
   S-id · name — mark: новый экран | правка | редизайн
   Акторы: A-ids; for each role, the actions it has and the ones it must
     not see (hidden) or sees disabled with a reason
   Вход: where the actor arrives from; Соседи: the S-ids it leads to
   Потоки: the flow ids this screen must make reachable
     (UC-3, UC-3 Alt-1, UC-3 Exc-1, …)
   Состояния: the states it needs (Loading, Empty, Error, Forbidden, named
     flow states), from the session's completeness plan
   Вложенные шаги: planned M-ids with their purpose, when the plan needs
     one (a confirmation of a destructive action); you may add more
   Поля: the data the actor provides, with the SRS rule id for each
   Деструктивные действия: each with undo or confirmation, per UX-36
   Existing frames: fileKey and the nodeIds of the screen, state and
     nested-step frames, when the screen already has frames>
APP-WIDE STATES <Сессия истекла, Слишком много запросов, Ошибка сервера,
                Нет сети — each with its nodeId when it exists, or `draw`>
EXISTING FRAMES <every product frame already in the file,
                `name — nodeId`, from the session's `get_metadata`;
                `none` for an empty file>

RULES
- One file. Do not split the work across parallel agents.
- Draw only the screens in SCREENS and the APP-WIDE STATES marked `draw`.
  Every frame in EXISTING FRAMES that is not in SCREENS stays exactly as it
  is: do not redraw, restyle, move, or rename it. Before drawing anything,
  open the file and confirm the EXISTING FRAMES are there; when the file
  holds product frames the packet does not list, stop and return BLOCKED
  with their names instead of drawing over them.
- Completeness. Every flow in a screen's Потоки is reachable on its frames,
  every listed state has a frame, every role's hidden or disabled actions
  are shown by a frame or the annotation, every field has its error, every
  destructive action has its confirmation or undo, every result that
  appears without navigation has its success feedback — `ux-patterns` →
  Полнота макета. A flow you cannot place is reported, not dropped.
- A new screen in a file that already has frames reuses their look: the
  same components, variables, spacing, and naming as its neighbours, not a
  fresh style — also when the neighbours were drawn by a designer.
- A `правка` screen keeps its structure. Add or change what the packet
  lists; do not restyle the rest. Edit the state and nested-step frames
  that exist; draw one only when this run adds that state or step.
- A `новый экран` or `редизайн` screen may be built anew.
- Name interactive and data layers by what they do, not how they look, so
  `screen-spec` can map them: `действие: отмена брони`, `ввод:
  длительность`, `шаг: M2` (the control that opens a nested step),
  `данные: вместимость`. Never `Button 3` or `Frame 12`. Keep names that a
  frame already has in this form.
- Annotation. Beside each screen, an `S-1 · Аннотация` frame with:
  use cases and actors; the Фокус line (where focus lands at entry, after
  a nested step closes, after a failed submit — by action, not widget);
  the «Элементы» table `№ | слой | поток` numbering every named layer of
  the screen and its nested steps, append-only (an element keeps its №
  across runs; a removed one leaves a gap) — `screen-spec` uses these
  numbers for its «Элементы» rows; the «Тексты» table; the non-obvious
  widget choices, any «Исключение UX-<n>» and any departed wish with its
  reason.
- Write the copy. The SRS gives meaning, not wording: for every action,
  state message, success message, field error, step title and step
  question, write the text the actor reads, in the product's language, by
  `ux-patterns` (UX-12 verb + object, UX-21 error copy says how to fix).
  Keep the wording frames already have. Every text goes into the «Тексты»
  table: place → text, the place keyed by element № or state and by flow
  id (`S-1 · Empty`, `M1 · заголовок`, `№4 отмена брони · UC-3 Exc-1`,
  `№2 длительность · ошибка`). A text the SRS quotes with a BR is copied
  as is. `frontend`, `screen-spec` and the UI tests read this table.
- **File standard.** In an empty file (or one the user asks to reorganise),
  create these pages, in this order: `📄 Обложка`, `✅ Экраны`,
  `🧩 Компоненты` (local components, only when no library is linked),
  `🎨 Tokens`, `🗄 Архив`. In a file that already has its own pages, keep
  them: put new frames on the page that holds the existing screens and do
  not rename, move, or regroup what is there.
  - `📄 Обложка`: one 1920×1080 frame with the product name, the SRS path
    and version, and today's date (ISO, `2026-10-04`); set it as the file
    thumbnail (`figma.setFileThumbnailNodeAsync`). Update the date and
    version on every run that draws.
  - `✅ Экраны`: one Section per area or flow (`Брони`, `Профиль`), its
    name followed by the status: `Брони · черновик` while the run draws,
    `Брони · готово к разработке` once every screen in it is drawn and
    checked. Dev Mode statuses cannot be set from here; the user marks the
    section Ready for dev. A Section `Общие состояния` holds the app-wide
    state frames.
  - Inside a section, one row per screen, left to right: the screen frame,
    its state frames, its nested-step frames, the narrow-width frame, then
    `S-1 · Аннотация`. Rows follow the user's path, top to bottom.
  - `🗄 Архив`: a `редизайн` moves the old frames here, renamed with the
    date first (`2026-10-04 · S-3 · Профиль`), before the new ones are
    drawn. Nothing is deleted.
  - A new screen goes into its section below the existing rows; existing
    frames do not move.
- Name each screen frame `S-1 · <ScreenName>`, each state frame
  `S-1 · Empty`, each nested step `S-1 · M1 · <StepName>`, the narrow-width
  frame `S-1 · 375` (the width from VIEWPORTS), and each app-wide state
  `Общее · Сессия истекла`. The session finds frames by these names.
- Draw each screen at the first width in VIEWPORTS. Draw a second frame at
  the narrow width for every screen whose layout changes there (table →
  cards, a side panel → its own screen); that decision is yours.
- When the file or a linked library has components and variables, build
  from them (figma-generate-design, Step 2). Do not hardcode a colour or
  spacing a variable already holds. A component the library lacks (for
  example a skeleton) is drawn from the library's own variables in its
  style, and the report names it.
- When there is none, build in the **shadcn/ui style** (the look the
  pipeline's React + Vite and Next.js stacks build with), so a frame maps
  to code one to one. First create one local set on the `🎨 Tokens` page and
  bind every screen to it; do not restyle per screen:
  - colour variables named like shadcn/ui theme tokens: `background`,
    `foreground`, `card`, `muted`, `muted-foreground`, `primary`,
    `primary-foreground`, `secondary`, `destructive`, `border`, `input`,
    `ring` — a neutral grey scale plus one accent;
  - spacing on Tailwind's 4 px scale, multiples of 8 for layout gaps and
    padding; one radius for controls and cards;
  - type on Tailwind's sizes (12/14/16/18/20/24/30 px), one family, at
    most three weights;
  - components shaped as shadcn/ui ones: Button (default, secondary,
    outline, ghost, destructive), Input with a label above, Table, Card,
    Dialog, Toast (Sonner), Skeleton for loading. Reuse one component
    everywhere the same thing appears.
- Every frame uses Auto Layout, so it stretches with the width.
- Usability, each checkable on the screenshot (`ux-patterns` ids in
  brackets; the PRODUCT TYPE variant where a rule has one):
  - one primary action per screen and per nested step; secondary actions
    look secondary; a destructive action uses `destructive` only in its
    confirmation and is never the default focus [UX-11, UX-36, UX-37];
  - hierarchy reads top to bottom: title, content, actions; related items
    grouped by spacing [UX-5];
  - Empty and Error frames say what happened and give the next step;
    Loading uses skeletons in the content's shape [UX-25, UX-44, UX-45];
  - a field's error sits directly under that field [UX-21];
  - spacing, colour and type only from the variables; at most three text
    sizes per screen; numbers right-aligned in tables; nothing carries
    meaning by colour alone [UX-1, UX-3, UX-6, UX-40];
  - labels above fields, one column, optional fields marked for the
    product type [UX-17, UX-18];
  - on the narrow width, targets at least 44×44 px and body text at least
    16 px; no horizontal scroll.
- ACCESSIBILITY holds on every frame: interactive targets at least
  24×24 px, text contrast at least 4.5:1, large text and control
  boundaries at least 3:1, focus visible on every control. Show where focus
  lands on the annotation, not as a ring baked into the screen.
- After each screen, screenshot it and check: no placeholder text, no
  clipped text, every text of the «Тексты» table present, every layer
  named by action, every completeness item and usability point above.

MODE rename (index mode, with the user's consent): change nothing the actor
sees. Rename the interactive and data layers of the listed screens by
action, add the `S-n · Аннотация` frame beside each with the «Элементы»
table and a «Тексты» table read off the existing text layers. Do not touch
styles, positions, components, or wording.

REPORT (last message, exactly these fields)
```

## The report

```
STATUS            DONE | BLOCKED
FILE KEY          the fileKey
TOKENS            library | local (created) | none
SCREENS           one line per frame drawn or touched, for example:
  S-1               <nodeId>
  S-1.375           <nodeId>
  S-1.Empty         <nodeId>
  S-1.M1            <nodeId>   Отмена брони
  S-1.Аннотация     <nodeId>
  Общее.Сессия истекла  <nodeId>
COMPLETENESS      per S-id: ok | the flows, states or items not placed, and why
CHECKED           per S-id: ok | the defect left (labels, clipping, usability)
WISHES            per wish: the wish — followed | not followed: the reason
                  (or none when there is no ui-wishes.md)
SECTIONS          one line per section touched: name — готово к разработке | черновик
BLOCKER           only for BLOCKED
```

A screen, or a state, nested-step or annotation frame the rules require,
with no `nodeId` is not done. The session does not fill one in; it checks
every reported id with `get_metadata` before writing it to the register.
