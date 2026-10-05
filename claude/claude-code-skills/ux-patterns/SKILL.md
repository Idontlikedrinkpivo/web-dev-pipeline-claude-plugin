---
name: ux-patterns
description: >-
  Checkable UI/UX rules (ids `UX-<n>`, B2B and B2C variants) for every
  screen: action hierarchy, forms and validation, feedback, navigation,
  dialogs, data screens, empty and error states, tokens and spacing,
  accessibility, B2C conversion and consent — plus the completeness
  checklist a mockup must pass. Read by `ui-design`, the Figma builders,
  `screen-spec`, `frontend` and reviewers. Use whenever a screen, form, table,
  dialog or flow is designed, drawn, built or reviewed — «сделай удобно»,
  «по лучшим практикам UX». Not the look: brand comes from Figma tokens.
---

# UX Patterns

A component library can be assembled any way. These rules keep the result
usable. They are distilled from Nielsen Norman Group, Baymard, GOV.UK
Design System, Material 3, Apple HIG, IBM Carbon, Atlassian, Shopify
Polaris, GitHub Primer, AWS Cloudscape and W3C WCAG 2.2 / WAI-ARIA APG,
checked in October 2026. The source per rule is in
`references/sources.md`; read it when a rule is challenged.

Every rule is checkable on a screen-spec row, a frame screenshot, or a diff. A
rule nobody can check is not in this file.

## Product type

The frames register names it (`ui-design` → **Тип продукта**):

| Type | Who | Defaults |
|---|---|---|
| `B2B` | internal or business tool; trained, returning, mostly desktop users behind SSO | density, tables, sidebar, efficiency over persuasion |
| `B2C` | public consumer web; anonymous, impatient, mostly mobile users | conversion, mobile-first, trust, performance, consumer law |

A product with both faces (a public site plus an admin) names the type per
area; a screen follows the type of its area. When a rule below has no
type column, it holds for both.

## Who applies what

| Reader | Applies |
|---|---|
| `ui-design` | records the product type, decides the screen set, and runs Полнота макета against it before and after drawing; picks no widget itself — it hands the choices to the builders |
| `figma-opus` / `figma-sonnet` (or a designer) | pick every widget, presentation and behaviour pattern — button or menu item, dropdown or radio group, dialog or side panel or page, toast or banner, table or cards, undo or confirmation — compose frames that satisfy Sections 1–6 and Полнота макета, and write the copy by UX-12 and UX-21 into the «Тексты» table; a designer may choose differently without touching any document |
| `screen-spec` | records what the frames chose — the behaviour each element has, its texts verbatim from «Тексты», cited by frame — and the `UX-<n>` exception a frame notes; it never picks a widget or rewrites a text |
| `frontend` | implements the behaviour (Sections 2–7) and the accessibility baseline |
| `doc-review` (design lens), `code-review-unit` (UI lens) | cite the `UX-<n>` a finding breaks |

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
  width: 44×44 px.
- **UX-10 Density:** B2B — compact rows 32–40 px; B2C — 48 px and more.

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
  ignores repeated presses; the server is idempotent anyway.
- **UX-16 Groups:** 2–3 actions in a row; more go into a menu.

## 3. Forms

- **UX-17 One column, label above the field.** A placeholder is never the
  label.
- **UX-18 Marking:** B2B — «(необязательно)» on optional fields only.
  B2C — `*` on required **and** «(необязательно)» on optional (Baymard:
  marking only optional fields makes 32% skip required ones). Keep
  optional fields few; in B2C cut every field the flow can live without.
- **UX-19 Field fit:** width matches the expected length; mobile keyboard
  and autofill via `type` / `inputmode` / `autocomplete` (WCAG 1.3.5);
  `inputmode="numeric|decimal"` instead of `type=number`; formats
  accepted loosely (spaces, dashes) and explained beforehand in a hint.
- **UX-20 Validation timing:** on blur, never while typing; the error
  clears as soon as the value is fixed; everything is checked again on
  submit and on the server. B2C: a positive check mark on complex fields
  (password, email).
- **UX-21 Error copy** is an instruction in the question's words
  («Введите email в формате name@example.com»), placed directly under the
  field. Never «Неверное значение», «Упс».
- **UX-22 After a failed submit:** an error summary at the top that takes
  focus and links to the fields, the same messages at the fields, the page
  title prefixed «Ошибка:». Entered values are kept — card data included.
- **UX-23 Do not ask twice** for what the flow already has (WCAG 3.3.7):
  billing = shipping by default, no «repeat password/email».
- **UX-24 Long forms:** steps with clear names, Back/Next with descriptive
  labels, save and continue. Autosave only for toggles; text fields have
  an explicit Save; do not mix the two in one form.

## 4. Feedback, loading, notifications

- **UX-25 Response thresholds:** under 1 s — no indicator; 1–10 s — a
  skeleton in the content's shape for a page or table, a spinner only for
  a small module; over 10 s — progress with a percentage or «3 из 50» and
  what is happening.
- **UX-26 Refresh keeps data visible** and shows when it was updated; a
  skeleton never replaces data the user is reading.
- **UX-27 Toast is for success only,** short, one at a time, 4–10 s,
  announced with `role="status"`. Errors and messages with an action never
  disappear on their own: inline at the place, or a banner. B2C: a
  reversible action's toast carries «Отменить».
- **UX-28 Status messages** are announced without moving focus
  (`role="status"`, errors `role="alert"`, WCAG 4.1.3).
- **UX-29 Optimistic update** only for operations that almost always
  succeed (toggle, like): snapshot, update, roll back with an inline error.
  Never for payments or destructive actions.

## 5. Navigation, dialogs, destructive actions

- **UX-30 Navigation stays visible on desktop** (no hamburger there).
  B2B — left sidebar when there are many sections. B2C — top navigation;
  on mobile a bottom bar for 3–5 equal sections, otherwise Priority+
  («Ещё»).
- **UX-31 Where am I:** the active item has `aria-current="page"`; every
  page has a unique `<title>` starting with its `h1`; breadcrumbs only
  for hierarchies three levels deep and more.
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
- **UX-37 Danger styling** only in the second step (the confirmation), never
  on the first button. Type-to-confirm (the object's name) only for high
  risk: cannot be recreated, or breaks other objects.
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
  long tables; a visible cue for horizontal scroll.
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
  lines, not pies, donuts, gauges or 3D; the same series keeps its colour
  everywhere; a KPI shows its comparison window.

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
  goal (purchase, booking). Password rules shown before typing; show-
  password toggle; passkeys and social sign-in say what happens to the
  account.
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
- **UX-55 Mobile web:** never disable zoom, never lock orientation, honour
  `prefers-reduced-motion`; primary actions within thumb reach at the
  bottom of tall screens.
- **UX-56 Localisation-ready:** room for text growth (short strings up to
  +200%), CSS logical properties, `lang` and `dir` set, dates, numbers and
  money through `Intl`; no text inside images.

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

## How to cite

A spec row, a frame annotation, a test name or a review finding cites the
rule as `UX-<n>`. A deliberate exception is written next to the place:
«Исключение UX-14: кнопка заблокирована, пока идёт загрузка файла —
требование SRS FR-…».
