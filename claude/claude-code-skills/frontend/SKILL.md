---
name: frontend
description: >-
  Builds screens from a screen spec and OpenAPI (React + Vite or Next.js); usually run by work. Directly: «сверстай
  экран S-3» once its ТЗ exists. No mockup: ui-design; a chat fix: work.
---

# Frontend

The design is already decided: the look and the texts by the Figma frames,
each screen's behaviour by its screen spec (`screen-spec`), calls by
OpenAPI, placement by the architecture. This skill is how to transcribe
them into code without inventing anything, on any stack. It teaches no
framework: the model already knows the frameworks, and facts that change
between releases are checked live (Version-sensitive behaviour).

## Inputs and their authority

| Input | Decides | Rule |
|---|---|---|
| Architecture foundation `documentation/architecture/architecture.md` §1 «Стек» / «Ключевые решения» | framework, language, profile | Read first. Pick the profile below |
| Architecture foundation §5 «Дерево файлов» | where each file goes | Wins over the profile layout. A file the tree does not place goes where the profile says, and the report names it |
| Screen spec `documentation/ui/screen-specs/S-<n>-*.md` (`documentation/ui/<product>/screen-specs/` with several UI products) | elements and their behaviour per condition, the operation and fields each uses, states, response outcomes, derived values | Behaviour comes from here. Its element № matches the frame annotation |
| Figma `S-n · Аннотация` «Тексты» table, or a text layer marked «текст слоя» in a designer's file without annotation (the screen spec quotes either) | the exact wording of every label and message | Copy verbatim, with no rewording. The «» that mark a text in the table are not part of it; quotes, «…» and dashes inside the text stay as written (UX-78). A text with no row is a gap question, not text you write |
| `documentation/api/openapi.yaml` | every HTTP call, request and response shape, status codes | Only through a client or types generated from this file, so a contract change surfaces as a type error instead of a silent runtime mismatch. A hand-written `fetch`/axios URL, path string or DTO interface drifts from the contract unnoticed |
| Figma `fileKey` / `nodeId` cited in the spec | widgets, presentation of nested steps, layout at every width, spacing, tokens, visual hierarchy | Read with the Figma MCP (`get_design_context`, `get_screenshot`, `get_variable_defs`); if `figma-*` skills are installed, follow them instead. Map to the project's components and tokens — generated snippets are a reference, not code to paste |
| Existing code in the repo | patterns, shared components, the app-wide handler | Reuse before adding. A second button, modal or API client beside an existing one is a defect |

A spec input missing (no screen spec for the screen, no OpenAPI when the screen
calls HTTP) is a stop: name it. Do not build from the SRS or from a guess.

**A small fix on a screen with no spec.** A project whose screens were built
before this pipeline has code but no screen specs, and stopping there would
block a one-line fix. A fix that changes no behaviour a document defines —
a wrong text the user dictates, a broken handler, a layout or contrast bug,
a missing loading or error branch the user describes — goes ahead without
a spec; the report says «без ТЗ на экран: <что поправлено>». A new element,
state, operation or rule still needs the spec (`screen-spec`) or the
frames (`ui-design`) first.

## Pick the stack profile

Read §1 «Стек» and load only the matching file — the other profiles carry
defaults that contradict it and only add noise:

| §1 names | Profile |
|---|---|
| Next.js | `references/nextjs.md` |
| React + Vite (SPA) | `references/react-vite.md` |
| anything else | no profile — follow this file only and say so in the report |

React + Vite and Next.js are the pipeline's two frontend stacks: together
they cover client apps behind a login and public, SEO-facing sites, and the
Figma frames are drawn in the shadcn/ui style both profiles build with. A
new project picks one of them; another framework appears only when an existing
repo already uses it, and then this file alone applies.

A profile's library choices are marked «по умолчанию, можно поменять»: a
library already in `package.json` or named in §1 wins over the default.
Adding a library the project does not have is a decision — name it in the
report.

**Selection criterion.** Every default in a profile, and every library this
skill adds, is widely used and has complete official documentation (guides
plus an API reference for the current major). Why: the code is written and
checked against current docs (Version-sensitive behaviour), and a niche or
thinly documented library leaves that check nothing to read. When a task
needs something no profile default covers, pick by this criterion and prefer
what the framework ships with over a third-party package. A library already in
the project is used as is, whether or not it meets the criterion.

## Per screen or component

1. **API layer first.** Screens are built one at a time (`work`). The first
   screen unit of a run generates the client/types from
   `documentation/api/openapi.yaml` with the project's generator and adds a
   `package.json` script so the next person regenerates the same way; a
   later screen reuses them and regenerates only when the spec changed since
   — then the generated files are in its `Файлы`. Generated files are never
   hand-edited. One data function or hook per `operationId`, named after it,
   in `features/<feature>/`.
2. **Map every row.** Walk the screen spec's «Элементы» table row by row — a unit for part of a screen
   (`S-<n> эл. <from>–<to>`) walks its own rows and builds on what the earlier parts set up, reading the rest of the
   spec only where its elements point:
   the row says what the element does in each condition and which operation
   and fields it uses; the frame (its nodeId / variant) says what it looks
   like. «Загрузка и вызовы» says which call loads the screen in which
   condition and in which order: an item that takes a field from an earlier
   response («из ответа 1») runs after that response. Links to other `S-n` →
   the router. An element not in the table is not built; a derived value is
   computed only as «Производные значения» defines it, or taken from the API
   field it names.
3. **Implement every row of «Состояния экрана»** — Loading, Empty, Error,
   Forbidden and the rest, each nested step — as a reachable branch, not a
   TODO, showing the frame for that state and the next action the row names.
4. **Implement every row of «Ошибки ответов»**: branch on the typed status
   from the generated client, never on a message string. `общий обработчик`
   goes to the one app-wide handler drawn on the register's «Общие
   состояния» frames (the first screen unit builds it in shared code; later screens
   use it and never copy it per screen). A
   success without navigation is announced as a status message (`aria-live`).
5. **Fields** follow «Поля ввода»: the rule, when it is checked, the exact
   error text next to the field. The form's schema, a format rule the server also checks, and which
   actions the user may take come from the contract and the response, never retyped (`react` → «A form is
   one library (React Hook Form) and one schema», «What the user may do comes from the response»).
6. **Shape the code to stay changeable** by the `react` skill: server data through the one data layer, a
   page as a data hook plus its view, shared Loading / Error / Empty, no second copy of a component. The
   quality gates hold it (`repo-scaffold/references/quality-gates.md`).
7. **Focus** follows the frame and `ux-patterns` (dialog focus, error
   summary). **Widths** go desktop first: the desktop width of the frames
   register is built first, then each narrower width follows the frame
   drawn at it, with no sideways page scroll at any width (UX-74).
   **Theme** comes from the Figma variables (`get_variable_defs`): each
   one maps to the project's theme variable for the same role — on
   shadcn/ui its theme variable of the same name; in a project with its
   own names (`--color-surface`, `--text-strong`) the one for that role — light
   and dark, in the project's one theme file; radius, shadows and fonts
   likewise. A restyle in Figma is a theme unit: the theme file changes,
   and the screens follow without edits unless one hardcodes a value — that
   value moves into the theme in the same unit.
   **Fonts** come from the frame: the family, weights and sizes its text
   styles or variables name. Load that family with its `cyrillic` subset
   (the framework's font loader or self-hosted files, UX-59) instead of
   letting the browser fall back to a system font, because a fallback changes every text width and weight on
   the screen.
8. **Behaviour follows `ux-patterns`** (load it; the variant from the
   frames register's **Тип продукта**) wherever the spec and the frame
   leave the mechanics open: sections 2–6 for actions, forms, feedback,
   navigation, dialogs and data states, section 7 on B2C, section 8 for
   every screen, section 9 for every text the code adds, such as an
   `aria-label`. The rules are not restated here, because a copy drifts
   when `ux-patterns` renumbers or rewrites one. A test that pins one of
   them names the rule id. Where the screen spec records an «Исключение
   UX-<n>», build what it says — it was reviewed.
9. **Texts** come from the frame's «Тексты» table (as quoted in the screen
   spec) and live where the project keeps UI strings (i18n catalog keyed by
   `S-n`, or a per-feature messages module); tests assert them verbatim. A
   designer's rewording changes the frame, the screen spec and this
   catalog — never the SRS.

10. **Code-level rules** are in `web-design-guidelines`: the code form of
   every `ux-patterns` rule — semantics and keyboard, focus, forms, motion
   under reduced motion, long content, images, performance, touch,
   theming, `Intl`, Next.js hydration. Keep CSS specificity flat: styles
   come from the theme tokens and utility classes on the element; a
   section-level selector and an element class that both set padding
   cancel each other out, so the spacing between sections is set in one
   place.

**A gap is a question, not code.** A state, text, element, response outcome
or field rule the screen spec does not give goes back to `screen-spec`; a
request to change the screen («переделай», «добавь кнопку», «редизайн»)
goes to `ui-design` first. The spec and the frames were reviewed and the
API and tests are tied to them, so a guess in code silently forks the
design. Inside `work`: report `BLOCKED` with the gap. Outside `work`: name
the gap and the stage, write no code for it.

**Called directly, outside `work`.** In a project the pipeline built (it
has `documentation/`), a change asked in the chat goes through `work` → A
change asked in chat outside a run (`work/references/chat-change.md`).
Outside a pipeline project (no `documentation/`), the change still gets
what a plan unit gets: a review of the diff (`/code-review`) and the tests
it touches run on the branch — the component tests and its screen's user
test cases (`ui-test-cases`) when the suite exists — and the report ends with one line «Ревью: …
· тесты: …», a skipped one named with why — chat fixes once reached commit
and push with neither, four times in one evening.

## Accessibility baseline

The target comes from the frames register header (default WCAG 2.2 AA); the
semantics, keyboard and focus rules are `web-design-guidelines`, contrast is
`ux-patterns` UX-7. Contrast is checked, not assumed: a colour pair that
fails — a kit default (`references/version-checks.md` → UI kit defaults) or a
frame's override of one — is fixed in the project's theme or variant, never
as a one-off class, and named in the report.

## Verification

Read the real commands from `package.json` (dev, build, lint, typecheck,
test); a missing one is reported, not invented.

1. Typecheck, lint, unit/component tests — all green. One component test per
   state row and per mapped response outcome, with the API mocked at the
   network boundary by fixtures typed from the generated types. Test helpers
   (render with router and session, the network mock, typed fixtures) live in
   one shared test folder, never copied into a test file; tests are grouped by
   behaviour, not by plan unit, and never read a stylesheet or a source file.
2. Walk the screen's main path in the running app with `playwright-cli`
   (open, act, check the result in the snapshot) — a check, not a committed
   spec. The E2E folder (`e2e/`) and its config belong to the user test
   suite of `ui-test-cases`, built from the test cases one spec per
   section; a per-screen spec beside it would test the same path twice and
   drift from the cases.
3. When the spec cites a `nodeId`: run the app, `playwright-cli resize` to
   each width in the frames register, `screenshot` the page and each state, get
   the frame with `get_screenshot`, and list the visible differences (layout,
   spacing, colour, missing element). If Figma or the running app is not
   reachable, say the comparison was not done. Never report "matches the
   mockup" without that comparison: a reviewer cannot tell an unchecked
   screen from a checked one.
4. Before hand-off, go through `ux-patterns` → «Проверка экрана перед
   сдачей» and review the diff with `web-design-guidelines`; fix what they
   find. An item that could not be checked (no browser, no Figma) is named,
   not passed.

## Version-sensitive behaviour

This skill does not pin library facts that change between releases
(signatures, defaults, generated-artifact paths, "since version X"): they
would go stale faster than the skill is edited. The points to check are in
[references/version-checks.md](./references/version-checks.md). In a `work`
packet their answers come in `CURRENT LIB DOCS`; where it says `none`, probe
the installed version in the project instead of fetching docs. Outside
`work`, read the file and check each point you rely on against the
installed version (context7 MCP — `resolve-library-id`, then `query-docs` —
or a quick probe).

## Report

Name: profile used (or "no profile"), files by `S-n`, each state and response
outcome → where it is handled, commands run with results, the Figma
comparison result or why it was skipped, the «Проверка экрана перед сдачей»
items with their result (inside `work`, the report's SCREEN CHECK field), libraries added, and every gap sent back to
`screen-spec` or `ui-design`.
