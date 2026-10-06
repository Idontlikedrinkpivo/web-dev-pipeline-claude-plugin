---
name: frontend
description: >-
  Turns a screen spec (ТЗ на экран: elements, behaviour per condition,
  states, response outcomes, Figma nodeIds) and the OpenAPI contract into
  typed, accessible screens on the stack the architecture names, with React
  + Vite and Next.js profiles. Use whenever a plan unit or task writes
  frontend code from a screen spec, or the user asks to build or fix
  screens, pages, forms or components — «сверстай экран», «сделай
  страницу», a screen id like S-1. Not for drawing screens (`ui-design`),
  backend code, or Playwright test details (`playwright-cli`).
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
| Figma `S-n · Аннотация` «Тексты» table (the screen spec quotes it) | the exact wording of every label and message | Copy verbatim, with no rewording. The «» that mark a text in the table are not part of it; quotes, «…» and dashes inside the text stay as written (UX-78). A text with no row is a gap question, not text you write |
| `documentation/api/openapi.yaml` | every HTTP call, request and response shape, status codes | Only through a client or types generated from this file, so a contract change surfaces as a type error instead of a silent runtime mismatch. A hand-written `fetch`/axios URL, path string or DTO interface drifts from the contract unnoticed |
| Figma `fileKey` / `nodeId` cited in the spec | widgets, presentation of nested steps, layout at every width, spacing, tokens, visual hierarchy | Read with the Figma MCP (`get_design_context`, `get_screenshot`, `get_variable_defs`); if `figma-*` skills are installed, follow them instead. Map to the project's components and tokens — generated snippets are a reference, not code to paste |
| Existing code in the repo | patterns, shared components, the app-wide handler | Reuse before adding. A second button, modal or API client beside an existing one is a defect |

A spec input missing (no screen spec for the screen, no OpenAPI when the screen
calls HTTP) is a stop: name it. Do not build from the SRS or from a guess.

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
   — then the generated files are in its `Files`. Generated files are never
   hand-edited. One data function or hook per `operationId`, named after it,
   in `features/<feature>/`.
2. **Map every row.** Walk the screen spec's «Элементы» table row by row:
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
   use it and never copy it per screen). While a call runs, the triggering control shows progress and ignores
   repeat presses [UX-15]; a
   success without navigation is announced as a status message (`aria-live`).
5. **Fields** follow «Поля ввода»: the rule, when it is checked, the exact
   error text next to the field. Derive the form schema from the generated
   request type so a contract change breaks the build, not the user.
6. **Focus** follows the frame and `ux-patterns` (dialog focus, error
   summary). **Widths** go desktop first: the desktop width of the frames
   register is built first, then each narrower width follows the frame
   drawn at it, with no sideways page scroll at any width (UX-74).
   **Theme** comes from the Figma variables (`get_variable_defs`): each
   one maps to the project's theme variable for the same role — on
   shadcn/ui its theme variable of the same name; in a project with its
   own names (`--surface-card`, `--ink-900`) the one for that role — light
   and dark, in the project's one theme file; radius, shadows and fonts
   likewise. A restyle in Figma is a theme unit: the theme file changes,
   and the screens follow without edits unless one hardcodes a value — that
   value moves into the theme in the same unit.
   **Fonts** come from the frame: the family, weights and sizes its text
   styles or variables name. Load that family with its `cyrillic` subset
   (the framework's font loader or self-hosted files, UX-59) instead of
   letting the browser fall back to a system font, because a fallback changes every text width and weight on
   the screen.
7. **Behaviour follows `ux-patterns`** (load it; the variant from the
   frames register's **Тип продукта**) where the spec and the frame leave the
   mechanics open: validation on blur and again on submit, the error
   clears once fixed, the error summary takes focus after a failed submit
   and values are kept [UX-20, UX-22]; Save stays enabled and shows the
   errors [UX-14]; a running request shows progress on its control and
   ignores repeat presses [UX-15]; skeletons by the response thresholds,
   data stays visible on refresh [UX-25, UX-26]; toasts only for success,
   errors never auto-dismiss [UX-27]; URL holds filters, tab and page
   [UX-32]; unsaved changes are guarded [UX-35]; dialogs per WAI-ARIA
   [UX-34]. B2C adds Core Web Vitals budgets and the consent rules
   [UX-48, UX-53, UX-54]. Section 8 of `ux-patterns` holds for every
   screen: layout, performance, touch, `Intl` [UX-74 – UX-77]; Section 9
   for every text the code adds, such as an `aria-label` [UX-78, UX-79].
   A test that pins one of these names the rule id. Where the screen spec
   records an «Исключение UX-<n>», build what it says — it was reviewed.
8. **Texts** come from the frame's «Тексты» table (as quoted in the screen
   spec) and live where the project keeps UI strings (i18n catalog keyed by
   `S-n`, or a per-feature messages module); tests assert them verbatim. A
   designer's rewording changes the frame, the screen spec and this
   catalog — never the SRS.

9. **Code-level rules** are in `web-design-guidelines`: the code form of
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

## Accessibility baseline

Target from the frames register header (default WCAG 2.2 AA). Semantic elements first
(`button`, `a`, `form`, `label`, headings in order, `dialog` with a labelled
title); every input has a visible label; every action works from the keyboard
in a logical focus order; focus is visible and trapped inside an open modal
and restored on close; a control the frame shows as an icon only carries the
action's name from the spec as its accessible name; colours and contrast come from the design tokens, not ad-hoc values.
Tests query by role and accessible name, so the suite checks this too.
**Contrast is checked, not assumed.** Every colour pair the screen uses —
text on its background in each variant and state, and each control's
boundary (outline borders, input borders, focus ring) — meets 4.5:1 for text
and 3:1 for boundaries and large text. Kit defaults do not always: in stock
shadcn/ui the light destructive variant and neutral outline borders fall
below it. When the frame overrides a library style to pass (its annotation
or a value that differs from the kit), implement the frame's value in the
project's theme or variant, not as a one-off class; when the frame does not
and a pair fails, fix it the same way and name it in the report.

## Verification

Read the real commands from `package.json` (dev, build, lint, typecheck,
test); a missing one is reported, not invented.

1. Typecheck, lint, unit/component tests — all green. One component test per
   state row and per mapped response outcome, with the API mocked at the
   network boundary by fixtures typed from the generated types.
2. E2E for the screen's main path, written per `playwright-cli`.
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
(signatures, defaults, generated-artifact paths, "since version X"), because
they would go stale faster than the skill is edited. Before relying on one:
read the installed version from the lockfile or manifest, then check current
docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a
quick probe in the project.

Check per stack before relying on it:

- **Rendering and data fetching** — where data loads (server, client, both),
  what is cached, for how long, and how to invalidate after a mutation.
- **Router APIs** — file conventions, params, navigation calls, loading/error
  boundaries, redirects.
- **Forms and validation** — how the form library binds a schema, and whether
  the schema library's installed major is the one its resolver supports.
- **OpenAPI client generator** — config file name and keys, output path,
  client flavour, how errors and non-2xx statuses are typed.

## How it plugs into the pipeline

`work` forwards this skill and the one matching profile in the packet's
`STACK SKILLS` to every `impl-ui` unit (the plan cites a screen spec and a
Figma `nodeId`) and to any other unit whose files are browser UI code; the
executor follows it from there. Redesign and new screens are `ui-design`,
then `screen-spec`; e2e test mechanics are
`playwright-cli`; component-test conventions are `vitest` when the project
uses Vitest.

## Report

Name: profile used (or "no profile"), files by `S-n`, each state and response
outcome → where it is handled, commands run with results, the Figma
comparison result or why it was skipped, the «Проверка экрана перед сдачей»
items with their result (inside `work`, the report's SCREEN CHECK field), libraries added, and every gap sent back to
`screen-spec` or `ui-design`.
