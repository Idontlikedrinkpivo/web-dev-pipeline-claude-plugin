---
name: web-design-guidelines
description: >-
  Code-level rules for web interfaces — Vercel's Web Interface Guidelines,
  embedded and mapped onto `ux-patterns`: accessibility, focus, forms,
  motion, typography, long content, images, performance, navigation state,
  touch, theming, locale, Next.js hydration and copy, each rule with its
  UX-n. Use when writing or reviewing React / Next.js screen code: a screen
  unit in `code-review-unit`, `impl-ui`'s self-check before hand-off, or a
  request such as «проверь интерфейс», «ревью вёрстки», «аудит
  доступности кода». Reports `file:line — UX-n — суть`. Not mockups
  (`ui-design`), not the rules' rationale (`ux-patterns`).
---

# Web interface guidelines

The code-level form of `ux-patterns`: what each rule looks like in markup,
CSS and React. Every rule names the `ux-patterns` rule it belongs to (the
Next.js hydration rules belong to `frontend`'s profile), so a finding here
and a finding against the frames cite the same id. An
embedded copy of Vercel's Web Interface Guidelines (MIT,
`vercel-labs/web-interface-guidelines`, commit `434b7f9`); `LICENSE` is
the original licence and `VENDORED.md` lists what changed.

Who uses it:

- `frontend` and `impl-ui` write screen code by these rules and, before
  handing a screen unit over, review their own diff with them together with
  `ux-patterns` → «Проверка экрана перед сдачей».
- `code-review-unit` checks a screen unit's diff against them (its UI lens)
  and reports in the format below.
- Directly: the user names files or a folder to check. With no files named,
  ask which ones.

The rules are here in full; do not fetch them from the network. The
upstream file can hold rules that are not yet mapped to `ux-patterns`, and
one of them could contradict a decision this pipeline made (placeholders,
quotes, focus after a failed submit).

## How to review

1. Read the files in scope — for a unit, the files its diff touches.
2. Check every rule below that the code can break. A rule marked
   «только по требованиям» applies only when the SRS asks for that
   feature; a Next.js rule only in a Next.js project.
3. Report each breach once, at the line that causes it, with its `UX-n`.
   Say what to change when the fix is not obvious from the finding.

## Rules

### Accessibility

- Icon-only buttons have an accessible name (`aria-label`) → UX-8
- Form controls have a visible `<label>` → UX-17
- Custom interactive elements handle the keyboard (`onKeyDown` / `onKeyUp`); native `<button>` and `<a>` already do → UX-64
- `<button>` for actions, `<a>` / `<Link>` for navigation, never `<div onClick>` → UX-64
- Images have `alt`; a decorative image has `alt=""` → UX-66
- Decorative icons have `aria-hidden="true"` → UX-66
- Toasts and field messages are announced politely (`aria-live="polite"`); a field error is tied to its field with `aria-describedby`; `role="alert"` only for a failed operation → UX-28
- Semantic HTML (`<button>`, `<a>`, `<label>`, `<table>`) before ARIA → UX-64
- Headings in order `<h1>`–`<h6>` → UX-3; a skip link to the main content on pages with navigation → UX-64
- `scroll-margin-top` on heading anchors → UX-65
- Meaningful media has captions, a transcript or a description → UX-66
- Media controls work from the keyboard; decorative media is hidden from assistive technology → UX-61, UX-66

### Focus

- Every interactive element has a visible focus: `focus-visible:ring-*` or equivalent → UX-63
- Never `outline-none` / `outline: none` without a replacement → UX-63
- `:focus-visible` rather than `:focus` (no ring on click) → UX-63
- `:focus-within` for compound controls → UX-63
- Sticky headers, footers and overlays do not cover the focused element → UX-65

### Forms

- Inputs have `autocomplete` and a meaningful `name` → UX-19
- The right `type` (`email`, `tel`, `url`) and `inputmode` (`numeric`, `decimal`); never `type="number"` → UX-19
- Paste is never blocked (`onPaste` + `preventDefault`) → UX-19
- A click on the label focuses the field (`htmlFor` or a wrapping label) → UX-69
- `spellCheck={false}` on emails, codes and usernames → UX-19
- A checkbox or radio and its label share one hit target, no dead zone → UX-69
- The submit button stays enabled until the request starts; during the request it shows a busy state and ignores repeat presses, without `disabled` (which drops focus) → UX-14, UX-15
- A field's error sits under that field → UX-21; after a failed submit focus goes to the error summary at the top, and a one-field form keeps focus on its field → UX-22
- No placeholder, except in a search field («Поиск по названию…»); a format example goes in the hint between the label and the field → UX-17, UX-19
- `autocomplete="off"` where browser autofill gets in the way (search, internal codes) → UX-19
- Leaving with unsaved changes asks first (`beforeunload` or a router guard) → UX-35

### Motion

- `prefers-reduced-motion` removes motion, smooth scrolling included; only loading indicators keep moving → UX-61
- Animate `transform` and `opacity` only → UX-61
- Never `transition: all`; list the properties → UX-61
- A correct `transform-origin`; in SVG, transforms on a `<g>` with `transform-box: fill-box; transform-origin: center` → UX-61
- Animations stop or reverse when the user acts; they never block input → UX-61
- Anything that moves on its own for more than 5 s has pause, stop or hide → UX-61
- Muted decorative loops stop under `prefers-reduced-motion` → UX-61

### Typography

- An ellipsis is one character, `…`, not `...` → UX-78
- Quotes «ёлочки», inner quotes „лапки“; no straight `"` in interface text → UX-78
- A non-breaking space between a number and its unit (`10&nbsp;МБ`, `5&nbsp;мин`), in `№&nbsp;5`, `т.&nbsp;е.`, in shortcuts (`⌘&nbsp;K`) → UX-78
- Waiting states end with `…`: «Загрузка…», «Сохранение…» → UX-78
- `font-variant-numeric: tabular-nums` for number columns, totals and timers → UX-59
- `text-wrap: balance` (or `pretty`) on short multi-line headings → UX-59
- Every font loads with its `cyrillic` subset (`next/font`: `subsets: ['latin', 'cyrillic']`; `@fontsource`: the cyrillic files) → UX-59

### Long content

- Text containers handle long content: `break-words` (`overflow-wrap: anywhere` for links and ids), or `truncate` / `line-clamp-*` for secondary text only — never for actions, errors, names or titles — with the full text reachable without hover → UX-71
- Flex children that hold text have `min-w-0` → UX-71
- Empty strings and arrays render the screen's empty state, not a broken layout → UX-44
- The screen holds short, average and very long values → UX-71

### Images

- `<img>` has explicit `width` and `height` → UX-75
- Images below the first screen: `loading="lazy"` → UX-75
- The critical image of the first screen: `priority` or `fetchpriority="high"` → UX-48

### Performance

- Lists over ~50 items are virtualized (`virtua`, `content-visibility: auto`) or paginated → UX-75, UX-43
- No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `offsetWidth`, `scrollTop`) → UX-75
- DOM reads and writes are batched, not interleaved → UX-75
- Prefer uncontrolled inputs; a controlled input is cheap per keystroke → UX-75
- `<link rel="preconnect">` for CDN and asset domains → UX-75
- Critical fonts: `<link rel="preload" as="font">` with `font-display: swap` → UX-75
- A muted looping `<video autoplay muted loop playsinline>` instead of an animated GIF, with a still alternative; for short loops, an H.264 MP4 source for Safari and a `prefers-reduced-motion` still → UX-75, UX-61

### Navigation and state

- The URL holds the state: filters, tabs, pagination, expanded panels → UX-32
- Links are `<a>` / `<Link>` (Cmd/Ctrl+click and middle click work) → UX-64
- Every stateful view can be linked to (state in the URL, e.g. with nuqs) → UX-32
- A destructive action has a confirmation or an undo window, never runs at once → UX-36

### Touch and interaction

- `touch-action: manipulation` → UX-76
- `-webkit-tap-highlight-color` set on purpose → UX-76
- `overscroll-behavior: contain` in modals, drawers and sheets → UX-74
- Page rubber-band only with a fine pointer: `overscroll-behavior: none` on `<html>` inside `@media (pointer: fine)`; coarse pointers keep the page default; check hybrid touch devices → UX-74
- While dragging: no text selection, `inert` on the dragged elements → UX-76
- Drag, swipe, pinch and path gestures have a tap or click and a keyboard alternative → UX-67
- `autoFocus` only on desktop and only for the single main field → UX-76

### Layout

- Full-bleed layouts respect `env(safe-area-inset-*)` → UX-74
- No unwanted scrollbars: fix the overflow; the page never scrolls sideways (a table scrolls inside itself) → UX-74
- Layout with flex and grid, not JS measurement → UX-74

### Theming

- `color-scheme: dark` on `<html>` in a dark theme → UX-62
- `<meta name="theme-color">` matches the page background → UX-62
- Native `<select>` has an explicit `background-color` and `color` → UX-62

### Locale

- Dates and times through `Intl.DateTimeFormat`, not hand-made formats → UX-77
- Numbers and money through `Intl.NumberFormat` → UX-77
- The interface language from `Accept-Language` / `navigator.languages`, never from the IP → только по требованиям (a multilingual product)
- Brand names, code tokens and identifiers carry `translate="no"` → UX-77

### Next.js hydration

Only in a Next.js project; the details are in `frontend` →
`references/nextjs.md`.

- An input with `value` has `onChange`, or uses `defaultValue`
- Dates and times rendered on the server and the client do not mismatch
- `suppressHydrationWarning` only where it is truly needed

### Hover and states

- Buttons and links have a hover state → UX-63
- Hover, pressed and focus raise contrast over the rest state; non-interactive cards do not react to hover → UX-63

### Copy

- Active voice: «Установите CLI», not «CLI будет установлен» → UX-79
- A capital letter only on the first word of a heading or button → UX-12, UX-78
- Counts in digits: «8 развёртываний» → UX-78
- Specific button labels: «Сохранить ключ», not «Продолжить» → UX-12
- An error message says how to fix it, not only what went wrong → UX-21
- The user is «вы», in lower case; sections are named without pronouns («Проекты», not «Мои проекты»), «мои» only where others' items are shown too → UX-79

### Anti-patterns — flag on sight

- `user-scalable=no` or `maximum-scale=1` → UX-71
- `onPaste` with `preventDefault` → UX-19
- `type="number"` → UX-19
- `transition: all` → UX-61
- `outline-none` without a `focus-visible` replacement → UX-63
- Navigation by `onClick` without `<a>` → UX-64
- `<div>` or `<span>` with a click handler instead of `<button>` → UX-64
- Images without dimensions → UX-75
- A large array `.map()` without virtualization → UX-75
- Form inputs without a label → UX-17
- Icon buttons without an accessible name → UX-8
- Hand-made date or number formats instead of `Intl.*` → UX-77
- `autoFocus` without a clear reason → UX-76
- An animated GIF where a compressed video fits → UX-75
- A gesture-only action without a tap or click and a keyboard alternative → UX-67

## Report format

Group by file, one line per finding, `file:line — UX-n — суть`, in Russian,
no preamble. A file with nothing to report gets `✓ замечаний нет`.

```text
## src/features/bookings/BookingForm.tsx

src/features/bookings/BookingForm.tsx:42 — UX-8 — у кнопки-иконки «Удалить» нет aria-label
src/features/bookings/BookingForm.tsx:67 — UX-61 — transition: all → перечислить свойства
src/features/bookings/BookingForm.tsx:88 — UX-78 — "..." → «…»

## src/components/RoomCard.tsx

✓ замечаний нет
```

Inside `code-review-unit` the same lines become that skill's findings, with
its own severity and verdict.
