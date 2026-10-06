---
name: ux-patterns
description: >-
  Checkable UI/UX rules (ids `UX-1` … `UX-80`, B2B and B2C variants) for every
  screen: action hierarchy, forms and validation, feedback, navigation,
  dialogs, data screens, empty and error states, tokens, icons, typography
  and motion, accessibility, B2C conversion and consent, implementation
  rules for code, Russian copy — plus the completeness checklist a mockup
  must pass and the checklist a built screen passes before hand-over. Read
  by `ui-design`, the Figma builders, `screen-spec`, `frontend` and
  reviewers. Use whenever a screen, form, table, dialog or flow is
  designed, drawn, built or reviewed — «сделай удобно», «по лучшим
  практикам UX». Not the visual direction itself (palette, fonts): that is
  chosen in `ui-design`.
---

# UX Patterns

A component library can be assembled any way. These rules keep the result
usable. They are distilled from Nielsen Norman Group, Baymard, GOV.UK
Design System, Material 3, Apple HIG, IBM Carbon, Atlassian, Shopify
Polaris, GitHub Primer, AWS Cloudscape and W3C WCAG 2.2 / WAI-ARIA APG,
checked in October 2026, and reconciled with three rule sets this plugin
embeds: `web-design-guidelines` (Vercel Web Interface Guidelines — the
code-level detail behind Section 8), `ui-ux-pro-max` (style, palette and
font data for the visual direction, and a searchable mirror of these
rules) and `frontend-design` (taste rules for drawing). Every rule in
those three carries the `UX-<n>` it maps to, and none of them contradicts
this file. The source per rule is in `references/sources.md`; read it when
a rule is challenged.

Every rule is checkable on a screen-spec row, a frame screenshot, or a diff. A
rule nobody can check is not in this file.

## Product type

The frames register names it (`ui-design` → **Тип продукта**):

| Type | Who | Defaults |
|---|---|---|
| `B2B` | internal or business tool; trained, returning, mostly desktop users behind SSO | density, tables, sidebar, efficiency over persuasion |
| `B2C` | public consumer web; anonymous, impatient, often mobile users | conversion, trust, performance, consumer law |

A product with both faces (a public site plus an admin) names the type per
area; a screen follows the type of its area. When a rule below has no
type column, it holds for both.

Both types are **desktop first**: the main width is the desktop one, drawn
and built first, and the narrow width must work (UX-74).

## Who applies what

| Reader | Applies |
|---|---|
| `ui-design` | records the product type and the visual direction, decides the screen set, and runs Полнота макета against it before and after drawing; picks no widget itself — it hands the choices to the builders |
| `figma-opus` / `figma-sonnet` (or a designer) | pick every widget, presentation and behaviour pattern — button or menu item, dropdown or radio group, dialog or side panel or page, toast or banner, table or cards, undo or confirmation — compose frames that satisfy Sections 1–7 and 9 and Полнота макета by the taste rules of `frontend-design`, and write the copy by UX-12, UX-21, UX-78 and UX-79 into the «Тексты» table; a designer may choose differently without touching any document |
| `screen-spec` | records what the frames chose — the behaviour each element has, its texts verbatim from «Тексты», cited by frame — and the `UX-<n>` exception a frame notes; it never picks a widget or rewrites a text |
| `frontend` | implements Sections 1–9 — the look from the frames and the code rules of Section 1 (UX-59, UX-61, UX-62, UX-66), the behaviour (Sections 2–7), the implementation rules (Section 8, with the code-level detail in `web-design-guidelines`), the texts (Section 9) — and the accessibility baseline, and runs Проверка экрана перед сдачей before handing a screen over |
| `doc-review` (design lens), `code-review-unit` (UI lens) | cite the `UX-<n>` a finding breaks; the UI lens also checks Section 8 against `web-design-guidelines` and the screen checklist |
| `ui-test-cases` (run) | checks the screen-checklist items a screenshot shows when it compares a screen with its frame |

A screen spec, frame or diff that must break a rule (a product constraint, a
legal text) says so next to the place, with the rule id. Silence is a
finding.

## 1. Visual system — using the library

- **UX-1 Tokens only.** Spacing from the scale (4-px base, multiples of 8
  for layout gaps and padding); colours from semantic tokens (`primary`,
  `secondary`, `muted`, `destructive`, `border`, `ring`, …); no raw hex,
  no `mt-[13px]`. A new colour is a new token in light and dark.
- **UX-2 One component per purpose.** The same thing looks and behaves the
  same on every screen. A missing variant is added once to the component
  (its variants definition), never as per-screen overrides.
- **UX-3 Type scale.** At most three text sizes and three weights per
  screen; headings in order (`h1` once, no skipped levels — a smaller look
  is a style, not a lower tag). Emphasis by weight before colour.
- **UX-4 Line length** 50–75 characters for running text (`max-width`
  ≈ 70ch); page content has a max width.
- **UX-5 Hierarchy reads top to bottom:** title → content → actions. Related
  items grouped by spacing, unrelated separated; the most important
  content gets the most space and contrast, top-left.
- **UX-6 Colour never carries meaning alone** (WCAG 1.4.1): an error, a
  status, a required mark also has text or an icon.
- **UX-7 Contrast:** text 4.5:1, large text 3:1, control boundaries,
  icons and focus ring 3:1 (WCAG 1.4.3, 1.4.11). Kit defaults are checked,
  not assumed.
- **UX-8 Icons have visible labels.** Icon-only only in a dense toolbar,
  then with a tooltip and an accessible name.
- **UX-9 Targets:** at least 24×24 px (WCAG 2.5.8). B2C and every touch
  width: 44×44 px, with at least 8 px between neighbouring targets.
- **UX-10 Density:** B2B — compact rows 32–40 px; B2C — 48 px and more.
- **UX-57 Icons:** one set, SVG, one style per hierarchy level (outline or
  filled, one stroke width), sizes from tokens. An emoji is never an icon.
- **UX-58 Depth and shape:** one shadow (elevation) scale and one radius
  scale for the whole product; blur only behind a modal or a panel, never
  as decoration.
- **UX-59 Text:** body line height 1.5–1.75, default letter spacing; on
  narrow widths body text and inputs at least 16 px; numbers in columns,
  totals and timers use the font's tabular figures (`tabular-nums`), not a
  monospace face; short multi-line headings `text-wrap: balance`. Every
  family has the `cyrillic` subset and loads with it (Next.js `next/font`:
  `subsets: ['latin', 'cyrillic']`), or Russian text falls back to a
  system face.
- **UX-60 No template tells** — the defaults that make a screen look
  generated: no ALL-CAPS labels above content; no single accented word in a
  heading; «01 / 02 / 03» markers only when the content is a sequence; no
  «→» appended to button or link text; no «A · B · C» meta strings as
  decoration; content is not chopped into identical cards with one shadow;
  a gradient only when it carries meaning; a big number with a small label
  and a gradient on the first screen only when it is truly the best option.
  The five generated-look clusters are in `frontend-design`.
- **UX-61 Motion** only answers an action or shows what changed (opened,
  saved, moved): no decorative entrances, staggered reveals or animated
  hover on non-interactive cards, no spring curves, no scale on press, no
  animated transitions between screens; a B2C first screen may have one
  orchestrated moment (parallax only there). Animate `transform` and `opacity` only, never
  `transition: all`; durations and easing from shared tokens; an animation
  is interruptible and never blocks input; endless motion only in loading
  indicators; anything that moves on its own for more than 5 s (carousel,
  video) has a pause. `prefers-reduced-motion` removes motion, smooth
  scrolling included; smooth scrolling is only for anchors on long pages.
- **UX-62 Dark theme** (when the SRS has one) is designed together with the
  light one, and contrast is checked in each separately; `color-scheme`,
  `theme-color` and the native `<select>` colours are set.
- **UX-66 Text alternatives:** a meaningful image has `alt`, a decorative
  one `alt=""`; a decorative icon next to text is hidden from screen
  readers (`aria-hidden`); video and audio have captions or a transcript.

## 2. Actions

- **UX-11 One primary action** per screen and per modal (a temporary
  side panel may have its own). Others are secondary, outline or ghost.
  Two filled buttons side by side is a finding.
- **UX-12 Labels are verb + object** in sentence case: «Сохранить
  изменения», «Удалить инициативу». Never «ОК»/«Да» answering a question.
- **UX-13 Order is consistent across the product:** on a page or form the
  primary comes first (left), secondary after it; in a dialog the primary
  is last (right). The same order on every page and in every dialog of
  the product.
- **UX-14 Do not disable Save/Submit.** Keep it enabled and show the errors
  on press. A control disabled for another reason says why next to it; an
  action the user can never have (permissions) is hidden.
- **UX-15 While a request runs** the triggering control shows progress and
  ignores repeated presses — a busy state, not the `disabled` attribute,
  so focus stays on it; the server is idempotent anyway.
- **UX-16 Groups:** 2–3 actions in a row; more go into a menu.
- **UX-63 Control states:** every interactive element has hover, pressed,
  focus and disabled states; focus is always visible (`:focus-visible`),
  and removing the outline without a replacement is a finding; hover and
  focus raise contrast; the reaction is instant or within 150 ms, with a
  pointer cursor; non-interactive cards do not react to hover; an input
  looks like an input; read-only looks and is marked differently from
  disabled.
- **UX-67 Drag and gestures have an alternative:** every drag has a
  single-tap and keyboard way (buttons «Выше» / «Ниже», a «Переместить»
  menu); every swipe has a visible control (WCAG 2.5.7).

## 3. Forms

- **UX-17 One column, label above the field.** A placeholder is never the
  label and is used only in a search field («Поиск по названию…»); a format
  example lives in the hint (UX-19).
- **UX-18 Marking:** B2B — «(необязательно)» on optional fields only.
  B2C — `*` on required **and** «(необязательно)» on optional (Baymard:
  marking only optional fields makes 32% skip required ones). Keep
  optional fields few; in B2C cut every field the flow can live without.
- **UX-19 Field fit:** width matches the expected length; mobile keyboard
  and autofill via `type` / `inputmode` / `autocomplete` (WCAG 1.3.5),
  `autocomplete="off"` only where browser autofill misleads (search,
  internal codes); `spellcheck` off in emails, codes and logins;
  `inputmode="numeric|decimal"` instead of `type=number`; paste is never
  blocked; formats are accepted loosely (spaces, dashes) and explained
  beforehand in a hint between the label and the field; a password field
  has «Показать пароль».
- **UX-20 Validation timing:** on blur, never while typing; the error
  clears as soon as the value is fixed; everything is checked again on
  submit and on the server. B2C: a positive check mark on complex fields
  (password, email).
- **UX-21 Error copy** is an instruction in the question's words
  («Введите email в формате name@example.com»), placed directly under the
  field and tied to it with `aria-describedby`. Never «Неверное значение»,
  «Упс».
- **UX-22 After a failed submit:** an error summary at the top that takes
  focus and links to the fields, the same messages at the fields, the page
  title prefixed «Ошибка:». Entered values are kept — card data included.
  A one-field form (search, an SMS code) has no summary: focus returns to
  the field.
- **UX-23 Do not ask twice** for what the flow already has (WCAG 3.3.7):
  billing = shipping by default, no «repeat password/email».
- **UX-24 Long forms:** steps with clear names, Back/Next with descriptive
  labels, save and continue. Autosave only for toggles; text fields have
  an explicit Save; do not mix the two in one form. A long form keeps a
  draft in the browser and offers «Восстановить черновик» on return; it
  reaches the server only through the explicit Save.
- **UX-69 Label and field are one:** clicking the label focuses the field;
  a checkbox or radio label is part of its hit area; related fields are
  grouped under a heading (`fieldset` / `legend`); rarely used settings sit
  behind «Дополнительно».

## 4. Feedback, loading, notifications

- **UX-25 Response thresholds:** under 1 s — no indicator; 1–10 s — a
  skeleton in the content's shape for a page or table, a spinner only for
  a small module; over 10 s — progress with a percentage or «3 из 50» and
  what is happening.
- **UX-26 Refresh keeps data visible** and shows when it was updated; a
  skeleton never replaces data the user is reading.
- **UX-27 Toast is for success only,** short, one at a time, 4–10 s,
  announced with `role="status"`. Errors and messages that ask for an
  action never disappear on their own: inline at the place, or a banner.
  B2C: a reversible action's toast carries «Отменить» and stays 10 s,
  paused while hovered or focused.
- **UX-28 Status messages** are announced without moving focus
  (`role="status"`, WCAG 4.1.3). A field error is tied to its field
  (`aria-describedby`) and announced politely when it appears;
  `role="alert"` only for a failed operation (the request did not go
  through); after a failed submit focus moves to the summary (UX-22).
- **UX-29 Optimistic update** only for operations that almost always
  succeed (toggle, like): snapshot, update, roll back with an inline error.
  Never for payments or destructive actions.
- **UX-70 A count change is announced as a phrase** — «В корзине 3
  товара», not a bare number — without moving focus; not every badge is
  its own live region.
- **UX-80 AI-generated content is labelled:** an answer or text produced by
  AI is marked as such next to it, and the user knows they are talking to
  AI (the EU AI Act, Art. 50, requires it). Streaming the answer and rating
  it are features — only when the SRS has them.

## 5. Navigation, dialogs, destructive actions

- **UX-30 Navigation stays visible on desktop** (no hamburger there).
  B2B — left sidebar when there are many sections. B2C — top navigation;
  on mobile a bottom bar for 3–5 equal sections, otherwise Priority+
  («Ещё»).
- **UX-31 Where am I:** the active item has `aria-current="page"`; every
  page has a unique `<title>` starting with its `h1`; breadcrumbs only
  for hierarchies three levels deep and more.
- **UX-64 Semantics and keyboard:** an action is a `<button>`, a navigation
  is a link (Ctrl/Cmd-click opens a new tab), never a clickable `<div>`;
  everything works from the keyboard in reading order; pages with
  navigation have «Перейти к содержимому»; after a route change in a
  single-page app focus moves to the main content and the tab title
  updates (UX-31).
- **UX-65 Focus not obscured:** sticky headers, panels, banners and chat
  widgets never cover the focused element (WCAG 2.4.11); anchored headings
  have `scroll-margin-top`.
- **UX-68 Help in one place:** help, contacts and the support chat sit in
  the same place on every page (WCAG 3.2.6).
- **UX-32 Shareable state lives in the URL** — filters, tab, page, the
  open item; Back closes an overlay that looks like a page and returns a
  list to the same position.
- **UX-33 Modal only for** a critical warning, data the task cannot
  continue without, or a short rare task. Frequent tasks stay on the page;
  editing that needs the context beside it goes to a non-modal side panel.
  B2C on mobile: a bottom sheet with a visible Close for short tasks, a
  full-screen page for long ones. Never a modal on a modal.
- **UX-34 Dialog behaviour** (WAI-ARIA APG): `role="dialog"`,
  `aria-modal`, a visible title as its name; Tab cycles inside, Esc
  closes, focus returns to the trigger; first focus is the first control,
  or the least destructive one when the action is irreversible.
- **UX-35 Unsaved changes** are guarded: leaving inside the app asks
  «Уйти без сохранения?»; closing the tab uses `beforeunload`.
- **UX-36 Reversible → undo, irreversible → confirm.** A confirmation names
  the object in bold and its consequence («Удалить инициативу **X**?
  Документы удалятся. Отменить нельзя.»), its button repeats the verb
  («Удалить инициативу»), and it is not the default focus. Confirmations
  for everything are a finding — users stop reading them.
- **UX-37 Danger styling at every step:** a destructive action is red
  wherever it appears — on a page or in a menu as a danger control of
  secondary weight (red text or outline, never the filled primary), set
  apart from the primary action (its own group, a divider, or an «Опасная
  зона» section at the end); in the confirmation the confirming button is
  the filled red one. «Выйти» and «Удалить аккаунт» stand apart from the
  ordinary menu items; only the second is red. Type-to-confirm (the
  object's name) only for high risk: cannot be recreated, or breaks other
  objects.
- **UX-38 Sessions:** warn before expiry (≥2 min, extend with one action,
  WCAG 2.2.1), say whether work is kept, and keep it across re-login
  (2.2.5). Login allows paste and password managers, no cognitive test
  without an alternative (3.3.8).

## 6. Data screens and states

- **UX-39 Table or cards:** comparing items by attributes → a table whose
  first column is a human-readable name; B2C browsing visual items → grid
  of cards (5 essentials: price, title, image, rating with count,
  variants).
- **UX-40 Columns:** numbers right-aligned, text left; long headers wrap to
  two lines then truncate with the full text in a tooltip; sticky header on
  long tables; a visible cue for horizontal scroll; a sortable column shows
  its direction (`aria-sort`).
- **UX-41 Row and bulk actions:** checkboxes plus a bulk bar above the table
  (≤5 actions, rest in a menu); per row a menu, or up to two inline
  icon buttons.
- **UX-42 Filters:** applied filters visible as removable chips with
  «Сбросить всё»; B2B and desktop — apply instantly; B2C mobile — a filter
  sheet with «Применить». No scroll-to-top on every change.
- **UX-43 Paging:** search, compare and return tasks → pagination (hidden
  when one page; first, last, neighbours, «…»; page number in the title).
  B2C catalog → «Показать ещё» with lazy loading and Back to the same
  position. Infinite scroll only for feeds, and never where a footer
  matters.
- **UX-44 Three different empty states:** first use — what this is for and
  one primary «Создать …»; no results — «Ничего не найдено» and
  «Сбросить фильтры», the count still visible; never «Нет записей» that is
  replaced by data a moment later. The empty state replaces the table, not
  a blank grid under its header.
- **UX-45 Error state** says what happened and what to do («Повторить»), in
  plain words, next to the failed part; the rest of the screen keeps
  working.
- **UX-46 Forbidden:** permanently unavailable → hidden; available later →
  disabled with «Доступно, когда …»; data the user cannot see → an
  explanatory state with a way forward (ask for access).
- **UX-47 Dashboards:** few metrics, the key one largest and first; bars and
  lines, not pies, donuts, gauges or 3D — parts of a whole are a 100 %
  stacked bar or horizontal bars with values; the same series keeps its
  colour everywhere; a KPI shows its comparison window.
- **UX-71 Long content:** long words, links and ids wrap
  (`overflow-wrap: anywhere`, `min-w-0` on flex children) instead of
  breaking the layout; what matters — actions, errors, names, headings — is
  never clamped; clamped secondary text is reachable in full, not by hover
  only; nothing is lost at 200 % text zoom or at the narrow width (WCAG
  1.4.4, 1.4.10, 1.4.12); a screen is checked with short, average and very
  long values.
- **UX-72 Badges and chips:** a badge is a status — not clickable, never
  colour alone; a chip is a value or an action — a button with a selected
  state; a badge or chip label stays whole on one line; a chip set wraps,
  and what does not fit sits behind an expandable «+N».
- **UX-73 Charts:** the legend sits next to the chart; axes have labels and
  units; exact values on hover and from the keyboard; series differ by more
  than colour; a text summary or a table for screen readers; their own
  Loading, Empty and Error states (UX-25, UX-44, UX-45); thousands of points
  are aggregated; numbers and dates through `Intl` (UX-77).

## 7. B2C additions

- **UX-48 Performance is UX** (Core Web Vitals at p75): LCP ≤2.5 s,
  INP ≤200 ms, CLS ≤0.1. Every image and video has its size or
  `aspect-ratio`; the hero image is `fetchpriority="high"` and never lazy;
  lazy loading below the first screen only.
- **UX-49 First screen:** the value proposition and one primary CTA; the
  rest in scannable sections below — people scroll when the top promises
  something. Social proof is concrete (name, role), never small numbers.
- **UX-50 Price and trust:** the total, delivery and returns are visible as
  early as the product page; no fee appears for the first time at the last
  step.
- **UX-51 Account later:** guest path first, account creation after the
  goal (purchase, booking). Password rules shown before typing (the
  show-password toggle is UX-19); passkeys and social sign-in say what
  happens to the account.
- **UX-52 Onboarding** is contextual help at the moment of need, not a
  carousel tour; if a tour exists, «Пропустить» is visible on every card.
- **UX-53 No deceptive patterns:** no confirmshaming, pre-checked consent,
  items added without asking, fake urgency or scarcity, cancellation
  harder than sign-up, hidden or drip fees. Legally binding in the EU (DSA
  Art. 25, GDPR/Planet49) and partly in the US (ROSCA, state
  auto-renewal laws, FTC Junk Fees Rule).
- **UX-54 Cookie consent:** the first layer has «Принять все», «Отклонить
  все» and «Настроить» with equal weight; withdrawing is as easy as
  giving; nothing pre-selected.
- **UX-55 Mobile web:** never disable zoom, never lock orientation; primary
  actions within thumb reach at the bottom of tall screens. Motion is
  UX-61.
- **UX-56 Localisation-ready:** room for text growth (short strings up to
  +200%), CSS logical properties, `lang` and `dir` set; no text inside
  images. Dates, numbers and money are UX-77.

## 8. Implementation — for code

Checked in the code by `frontend` and the `code-review-unit` UI lens. The
code-level detail of each rule — the attributes, CSS properties and
anti-patterns to flag — is in `web-design-guidelines`, marked with these ids.

- **UX-74 Layout:** desktop first — the main width is the desktop one (the
  first in the register's **Ширины**), drawn and built first, and the
  narrow width must work; the page never scrolls sideways (a table scrolls
  inside itself, UX-40); `dvh` instead of `100vh`; full-bleed layouts keep
  `env(safe-area-inset-*)`; fixed bars never cover content; one `z-index`
  scale; `overscroll-behavior: contain` in modals and drawers; images never
  wider than their container; layout by flex and grid, not by measuring in
  JS.
- **UX-75 Performance in code** (both types; the Core Web Vitals budgets for
  B2C are UX-48): lists longer than ~50 rows are virtualised or paginated
  (UX-43); search-as-you-type is debounced; no layout reads during render;
  code split by route; third-party scripts `async` / `defer`; every image
  has its size, and below the first screen `loading="lazy"`; fonts
  `font-display: swap`, only the critical ones preloaded; video instead of
  GIF; space reserved for content that loads later.
- **UX-76 Touch on narrow widths:** `touch-action: manipulation`; the tap
  highlight colour set on purpose; `autoFocus` only on desktop and only for
  a single main field; text selection off while dragging.
- **UX-77 Dates, numbers and money through `Intl`** in every product; brand
  names, codes and ids carry `translate="no"`.

## 9. Texts in Russian

- **UX-78 Typography:** «ёлочки» quotes, „лапки“ inside them; the ellipsis
  is one character «…»; waiting states read «Загрузка…», «Сохранение…»; a
  spaced em dash «—» in text; a no-break space between a number and its
  unit («10 МБ», «5 мин»), in «№ 5» and «т. е.»; counts in digits
  («8 проектов»); a capital only on the first word (UX-12).
- **UX-79 One action, one name:** the button «Опубликовать» produces
  «Опубликовано»; things are named in the user's words, not the system's
  («уведомления», not «вебхуки»); active voice; errors do not apologise and
  are never vague (UX-21, UX-45); an empty screen invites the next action
  (UX-44); the user is «вы» in lower case; sections are named without
  pronouns («Проекты», not «Мои проекты»), «мои» only next to someone
  else's.

## Полнота макета

The completeness checklist. `ui-design` runs it twice: on the screen set
before drawing (it becomes the per-screen plan in the Figma packet), and on
the file after drawing or indexing (each miss is a redraw or a question to
the designer). Every item is checkable from the frames: their names, the
layer names by action, the annotation, the screenshot. An item that cannot
apply to a screen is skipped, not drawn for show.

1. **Every flow is reachable.** Each use case's Main flow, every `Alt-n`
   and every `Exc-n` with a human actor has a frame, a state, or a nested
   step on some screen where the actor meets it; the annotation cites the
   flow id.
2. **Every role sees its actions.** For each role on a screen, the actions
   it has are drawn; the ones it must not have are hidden, or disabled with
   the reason when available later (UX-46). A screen two roles share shows
   the difference on a frame or on the annotation.
3. **Every data screen has its states:** Loading (UX-25), Empty — each kind
   the screen can have (UX-44), Error with a way to retry (UX-45), and
   Forbidden when an SRS exception says the actor may not see the data
   (UX-46).
4. **App-wide states exist once:** session expired (UX-38), too many
   requests, server error, offline — each a frame the whole product shares.
5. **Every destructive action is guarded:** undo when it is reversible, a
   confirmation naming the object and the consequence when it is not
   (UX-36, UX-37).
6. **Every field has its validation error** — one per rule the SRS gives
   it (required, format, limit), under the field (UX-21), and the failed
   submit has its summary (UX-22).
7. **Every result without navigation has success feedback** — saved,
   cancelled, N found — as a status message (UX-27, UX-28).
8. **Every action that waits shows progress** and ignores a repeat press
   (UX-15), on the frame or on the annotation.
9. **Every text is on the «Тексты» table** of the screen's annotation: each
   action, state message, error, success message and step title above.
10. **Every screen that collects personal data shows the notice.** When the
   SRS marks a field as personal data (phone, email, name, address), the
   screen that first collects it says what it is used for and links the
   processing policy, with an unticked consent where the SRS or the law
   asks for one (UX-53); the text is on «Тексты». A sign-in by phone code
   is such a screen.

## Проверка экрана перед сдачей

The checklist a built screen passes. `impl-ui` runs it before handing a
screen unit over and reports each item; the `code-review-unit` UI lens
checks it; `ui-test-cases` covers the items a screenshot shows when it
compares a screen with its frame. An item that cannot apply is skipped.

1. **Every width** in the register's **Ширины**, the desktop one first:
   nothing clipped, no sideways page scroll (UX-74).
2. **Keyboard only:** the whole screen works without a pointer; focus is
   always visible and never covered (UX-63, UX-64, UX-65).
3. **Contrast** of text and controls in every theme the product has (UX-7,
   UX-62).
4. **Reduced motion:** with `prefers-reduced-motion` nothing moves but
   loading indicators (UX-61).
5. **Zoom:** at 200 % and at the narrow width nothing is lost (UX-71).
6. **Value lengths:** short, average and very long values keep the layout
   (UX-71).
7. **Icons** from one set, no emoji; icon-only buttons have a name (UX-57,
   UX-8).
8. **Texts** follow Russian typography and one name per action (UX-78,
   UX-79).

## How to cite

A spec row, a frame annotation, a test name or a review finding cites the
rule as `UX-<n>`. A deliberate exception is written next to the place:
«Исключение UX-14: кнопка заблокирована, пока идёт загрузка файла —
требование SRS FR-…».
