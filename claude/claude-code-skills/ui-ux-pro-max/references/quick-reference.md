# Quick Reference — Full Rule Set (all 10 categories)

> dev-pipeline: every rule below ends with the `ux-patterns` rule it maps to
> (`→ UX-<n>`), or with the place it belongs (`ui-design`, «только по
> требованиям»). Rules that contradicted `ux-patterns` were rewritten to
> agree with it; native-platform (iOS, Android, visionOS) and WCAG AAA rules
> were removed — see `VENDORED.md`.

Load this file for a UI review pass or when you need every rule of a category. Most rules also appear, with their rationale and code, in `data/ux-guidelines.csv` (`--domain ux`); this file is a static index for scanning without a search.

## Quick Reference

### 1. Accessibility (CRITICAL)

- `color-contrast` - Minimum 4.5:1 ratio for normal text (large text 3:1); Material Design → UX-7
- `focus-states` - Visible focus rings on interactive elements (2–4px; Apple HIG, MD) → UX-63
- `alt-text` - Descriptive alt text for meaningful images → UX-66
- `aria-labels` - aria-label for icon-only buttons → UX-8
- `icon-context` - Semantics depend on use: decorative icons beside visible text are hidden from the accessibility tree; meaningful icons need a text alternative; icon controls need an accessible name and applicable state → UX-66
- `keyboard-nav` - Tab order matches visual order; full keyboard support (Apple HIG) → UX-64
- `form-labels` - Use label with for attribute → UX-17
- `skip-links` - Skip to main content for keyboard users → UX-64
- `heading-hierarchy` - Sequential h1→h6, no level skip → UX-3
- `color-not-only` - Don't convey info by color alone (add icon/text) → UX-6
- `reduced-motion` - Respect prefers-reduced-motion; reduce/disable animations when requested (Apple Reduced Motion API, MD) → UX-61
- `escape-routes` - Provide cancel/back in modals and multi-step flows (Apple HIG) → UX-34, UX-24
- `keyboard-shortcuts` - Preserve system and a11y shortcuts; offer keyboard alternatives for drag-and-drop (Apple HIG) → UX-67
- `focus-not-obscured` - Sticky UI, overlays, and banners must not hide the keyboard-focused control (WCAG 2.2 AA) → UX-65
- `dragging-alternative` - Every author-controlled drag action needs a single-pointer and keyboard alternative (WCAG 2.2 AA) → UX-67
- `web-target-size` - Web pointer targets need 24×24 CSS px or a documented exception; do not substitute native units (WCAG 2.2 AA) → UX-9
- `consistent-help` - Repeated help mechanisms stay in the same relative order across a page set (WCAG 2.2 A) → UX-68
- `redundant-entry` - Reuse information already supplied in the same process unless re-entry is essential (WCAG 2.2 A) → UX-23
- `accessible-authentication` - Allow password managers and paste; provide a non-cognitive authentication path (WCAG 2.2 Minimum, AA). The Enhanced AAA criterion is not represented in the dataset → UX-38
- `auto-rotation-controls` - Carousels and moving content need pause/stop controls and must stop on focus or reduced motion (WAI) → UX-61
- `contextual-live-badge-updates` - Announce a changed count/status as a complete contextual phrase without moving focus; use one appropriate live/status region and atomic updates only when needed → UX-70

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - Web targets at least 24×24 CSS px; 44×44 on touch widths and in B2C; extend the hit area beyond the visual bounds if needed → UX-9
- `touch-spacing` - At least 8 px between neighbouring targets on touch widths → UX-9
- `hover-vs-tap` - Use click/tap for primary interactions; don't rely on hover alone → UX-63
- `loading-buttons` - Keep the button enabled until the request starts; while it runs show progress and ignore repeat presses → UX-14, UX-15
- `error-feedback` - Clear error messages near problem → UX-21
- `cursor-pointer` - Add cursor-pointer to clickable elements (Web) → UX-63
- `gesture-conflicts` - Avoid horizontal swipe on main content; prefer vertical scroll → UX-67
- `tap-delay` - Use touch-action: manipulation to reduce 300ms delay (Web) → UX-76
- `press-feedback` - Visual feedback on press: an instant colour or background change → UX-63
- `gesture-alternative` - Don't rely on gesture-only interactions; always provide visible controls for critical actions → UX-67
- `safe-area-awareness` - Keep primary touch targets away from notch, Dynamic Island, gesture bar and screen edges → UX-74
- `no-precision-required` - Avoid requiring pixel-perfect taps on small icons or thin edges → UX-9
- `swipe-clarity` - Swipe actions must show clear affordance or hint (chevron, label, tutorial) → UX-67
- `drag-threshold` - Use a movement threshold before starting drag to avoid accidental drags → UX-76

### 3. Performance (HIGH)

- `image-optimization` - Use WebP/AVIF, responsive images (srcset/sizes), lazy load non-critical assets → UX-75
- `image-dimension` - Declare width/height or use aspect-ratio to prevent layout shift (Core Web Vitals: CLS) → UX-75
- `font-loading` - Use font-display: swap/optional to avoid invisible text (FOIT); reserve space to reduce layout shift (MD) → UX-75
- `font-preload` - Preload only critical fonts; avoid overusing preload on every variant → UX-75
- `critical-css` - Prioritize above-the-fold CSS (inline critical CSS or early-loaded stylesheet) → UX-75
- `lazy-loading` - Lazy load non-hero components via dynamic import / route-level splitting → UX-75
- `bundle-splitting` - Split code by route/feature (React Suspense / Next.js dynamic) to reduce initial load and TTI → UX-75
- `third-party-scripts` - Load third-party scripts async/defer; audit and remove unnecessary ones (MD) → UX-75
- `reduce-reflows` - Avoid frequent layout reads/writes; batch DOM reads then writes → UX-75
- `content-jumping` - Reserve space for async content to avoid layout jumps (Core Web Vitals: CLS) → UX-75
- `lazy-load-below-fold` - Use loading="lazy" for below-the-fold images and heavy media → UX-75
- `virtualize-lists` - Virtualize lists with 50+ items to improve memory efficiency and scroll performance → UX-75
- `main-thread-budget` - Keep per-frame work under ~16ms for 60fps; move heavy tasks off main thread (HIG, MD) → UX-75
- `progressive-loading` - Use skeleton screens / shimmer instead of long blocking spinners for >1s operations (Apple HIG) → UX-25
- `input-latency` - Keep input latency under ~100ms for taps/scrolls (Material responsiveness standard) → UX-48, UX-63
- `tap-feedback-speed` - Visual feedback on tap, instant or within 150 ms → UX-63
- `debounce-throttle` - Use debounce/throttle for high-frequency events (scroll, resize, input) → UX-75
- `offline-support` - Provide offline state messaging and basic fallback (PWA / mobile) → «Полнота макета», пункт 4
- `network-fallback` - Offer degraded modes for slow networks (lower-res images, fewer animations) → только по требованиям

### 4. Style Selection (HIGH)

- `style-match` - Match style to product type (use `--design-system` for recommendations) → ui-design: визуальное направление
- `consistency` - Use same style across all pages → UX-2
- `no-emoji-icons` - Use SVG icons (Heroicons, Lucide), not emojis → UX-57
- `color-palette-from-product` - Choose palette from product/industry (search `--domain color`) → ui-design: визуальное направление
- `effects-match-style` - Shadows, blur, radius aligned with chosen style (glass / flat / clay etc.) → UX-58
- `state-clarity` - Make hover/pressed/disabled states visually distinct while staying on-style (Material state layers) → UX-63
- `elevation-consistent` - Use a consistent elevation/shadow scale for cards, sheets, modals; avoid random shadow values → UX-58
- `dark-mode-pairing` - Design light/dark variants together to keep brand, contrast, and style consistent → UX-62
- `icon-style-consistent` - Use one icon set/visual language (stroke width, corner radius) across the product → UX-57
- `system-controls` - Prefer the component library's controls over custom ones; customise only when the brand requires it → UX-2
- `blur-purpose` - Use blur to indicate background dismissal (modals, sheets), not as decoration (Apple HIG) → UX-58
- `primary-action` - Each screen should have only one primary CTA; secondary actions visually subordinate (Apple HIG) → UX-11

### 5. Layout & Responsive (HIGH)

- `viewport-meta` - width=device-width initial-scale=1 (never disable zoom) → UX-55
- `desktop-first` - Design and build the desktop width first; the narrow width must work → UX-74
- `breakpoint-consistency` - Test at every width in the frames register, desktop first → UX-74
- `readable-font-size` - Minimum 16px body text on mobile (avoids iOS auto-zoom) → UX-59
- `line-length-control` - 50–75 characters per line for running text → UX-4
- `horizontal-scroll` - No sideways page scroll at any width; a table scrolls inside itself → UX-74
- `spacing-scale` - Use 4pt/8dp incremental spacing system (Material Design) → UX-1
- `touch-density` - Keep component spacing comfortable for touch: not cramped, not causing mis-taps → UX-10
- `container-width` - Consistent max-width on desktop (max-w-6xl / 7xl) → UX-4
- `z-index-management` - Define layered z-index scale (e.g. 0 / 10 / 20 / 40 / 100 / 1000) → UX-74
- `fixed-element-offset` - Fixed navbar/bottom bar must reserve safe padding for underlying content → UX-74
- `scroll-behavior` - Avoid nested scroll regions that interfere with the main scroll experience → UX-74
- `viewport-units` - Prefer min-h-dvh over 100vh on mobile → UX-74
- `orientation-support` - Keep layout readable and operable in landscape mode → UX-55
- `content-priority` - Show core content first on mobile; fold or hide secondary content → UX-5
- `visual-hierarchy` - Establish hierarchy via size, spacing, contrast — not color alone → UX-5
- `compact-label-overflow` - Choose badge, status tag, filter chip, or removable value from its semantics; keep essential labels available and disclose unavoidable truncation to pointer and keyboard users → UX-72
- `chip-collection-reflow` - Wrap the collection before shrinking labels; make a `+n` overflow summary an operable disclosure instead of hiding values → UX-72

### 6. Typography & Color (MEDIUM)

- `line-height` - Use 1.5-1.75 for body text → UX-59
- `line-length` - Limit to 50–75 characters per line → UX-4
- `font-pairing` - Match heading/body font personalities → ui-design: визуальное направление (шрифт с кириллицей)
- `font-scale` - Consistent type scale (e.g. 12 14 16 18 24 32) → UX-3
- `contrast-readability` - Darker text on light backgrounds (e.g. slate-900 on white) → UX-7
- `weight-hierarchy` - Use font-weight to reinforce hierarchy: Bold headings (600–700), Regular body (400), Medium labels (500) (MD) → UX-3
- `color-semantic` - Define semantic color tokens (primary, secondary, error, surface, on-surface) not raw hex in components (Material color system) → UX-1
- `color-dark-mode` - Dark mode uses desaturated / lighter tonal variants, not inverted colors; test contrast separately (HIG, MD) → UX-62
- `color-accessible-pairs` - Foreground/background pairs must meet 4.5:1 (AA) or 7:1 (AAA); use tools to verify (WCAG, MD) → UX-7
- `color-not-decorative-only` - Functional color (error red, success green) must include icon/text; avoid color-only meaning (HIG, MD) → UX-6
- `truncation-strategy` - Prefer wrapping over truncation; when truncating use ellipsis and provide full text via tooltip/expand (Apple HIG) → UX-71
- `letter-spacing` - Respect default letter-spacing per platform; avoid tight tracking on body text (HIG, MD) → UX-59
- `number-tabular` - Use tabular/monospaced figures for data columns, prices, and timers to prevent layout shift → UX-59
- `whitespace-balance` - Use whitespace intentionally to group related items and separate sections; avoid visual clutter (Apple HIG) → UX-5
- `heading-line-balance` - Use balanced wrapping on short headings as a progressive, user-agent-controlled heuristic; keep natural wrapping readable and never force final words together with blanket nonbreaking spaces → UX-59
- `long-token-wrapping` - Let URLs, IDs, and user content reflow with `overflow-wrap: anywhere` and a shrinkable flex/grid text child; do not apply `word-break: break-all` to normal prose → UX-71

### 7. Animation (MEDIUM)

- `duration-timing` - Choose shared motion tokens by distance, complexity, platform, and user context; test that feedback remains responsive instead of treating one duration range as universal → UX-61
- `transform-performance` - Use transform/opacity only; avoid animating width/height/top/left → UX-61
- `loading-states` - Match feedback to the expected wait and platform/component guidance; avoid both flashing indicators for near-instant work and unexplained long waits → UX-25
- `excessive-motion` - Motion only answers an action or shows what changed; no decorative entrances or staggers → UX-61
- `easing` - Use deceleration when arriving, acceleration when leaving, and linear motion for genuinely constant-rate progress or rotation → UX-61
- `motion-meaning` - Every animation must express a cause-effect relationship, not just be decorative (Apple HIG) → UX-61
- `parallax-subtle` - Parallax only as the one orchestrated moment of a B2C first screen, never under reduced motion → UX-61
- `exit-faster-than-enter` - Exit animations shorter than enter (~60–70% of enter duration) to feel responsive (MD motion) → UX-61
- `interruptible` - Animations must be interruptible; user tap/gesture cancels in-progress animation immediately (Apple HIG) → UX-61
- `no-blocking-animation` - Never block user input during an animation; UI must stay interactive (Apple HIG) → UX-61
- `fade-crossfade` - Use crossfade for content replacement within the same container (MD) → UX-61
- `gesture-feedback` - Drag, swipe, and pinch must provide real-time visual response tracking the finger (MD Motion) → UX-67
- `motion-consistency` - Unify duration/easing tokens globally; all animations share the same rhythm and feel → UX-61
- `opacity-threshold` - Fading elements should not linger below opacity 0.2; either fade fully or remain visible → UX-61
- `layout-shift-avoid` - Animations must not cause layout reflow or CLS; use transform for position changes → UX-61
- `cancellable-state-transitions` - Rapid state changes must cancel/replace prior micro-interactions safely, set the new final state explicitly, and never depend on an animation-end event for correctness → UX-61

### 8. Forms & Feedback (MEDIUM)

- `input-labels` - Visible label per input (not placeholder-only) → UX-17
- `error-placement` - Show a specific error below the related field and connect it with aria-describedby → UX-21
- `submit-feedback` - Loading then success/error state on submit → UX-15, UX-27
- `required-indicators` - B2B: «(необязательно)» on optional fields only; B2C: * on required and «(необязательно)» on optional → UX-18
- `empty-states` - Helpful message and action when no content → UX-44
- `toast-dismiss` - Toasts for success only, 4–10 s; errors never auto-dismiss → UX-27
- `confirmation-dialogs` - Undo for reversible actions, confirmation for irreversible ones; never confirm everything → UX-36
- `input-helper-text` - A persistent hint between the label and the field, not a placeholder → UX-19
- `disabled-states` - Disabled elements use reduced opacity (0.38–0.5) + cursor change + semantic attribute (MD) → UX-63
- `progressive-disclosure` - Reveal complex options progressively; don't overwhelm users upfront (Apple HIG) → UX-69
- `inline-validation` - Validate on blur (not keystroke); show error only after user finishes input (MD) → UX-20
- `input-type-keyboard` - Semantic input types (email, tel, url) and inputmode (numeric, decimal) for the right mobile keyboard; never type="number" → UX-19
- `password-toggle` - Provide show/hide toggle for password fields (MD) → UX-19
- `autofill-support` - Use autocomplete / textContentType attributes so the system can autofill (HIG, MD) → UX-19
- `undo-support` - Allow undo for destructive or bulk actions (e.g. "Undo delete" toast) (Apple HIG) → UX-36
- `success-feedback` - Confirm completed actions with brief visual feedback (checkmark, toast, color flash) (MD) → UX-27
- `error-recovery` - Error messages must include a clear recovery path (retry, edit, help link) (HIG, MD) → UX-45
- `multi-step-progress` - Multi-step flows show step indicator or progress bar; allow back navigation (MD) → UX-24
- `form-autosave` - Long forms keep a browser draft and offer «Восстановить черновик»; data reaches the server only through Save → UX-24
- `sheet-dismiss-confirm` - Confirm before dismissing a sheet/modal with unsaved changes (Apple HIG) → UX-35
- `error-clarity` - Error messages must state cause + how to fix (not just "Invalid input") (HIG, MD) → UX-21
- `field-grouping` - Group related fields logically (fieldset/legend or visual grouping) (MD) → UX-69
- `read-only-distinction` - Read-only state should be visually and semantically different from disabled (MD) → UX-63
- `focus-management` - After a failed submit focus the error summary; a one-field form keeps focus on the field → UX-22
- `error-summary` - Put a focusable summary at the top after failed submit, link each item to its invalid field, and retain inline field errors → UX-22
- `touch-friendly-input` - Mobile input height ≥44px to meet touch target requirements (Apple HIG) → UX-9, UX-59
- `destructive-emphasis` - Destructive actions are red at every step: a secondary-weight danger control set apart from the primary action, the filled red button in the confirmation → UX-37
- `toast-accessibility` - Toasts must not steal focus; use aria-live="polite" for screen reader announcement (WCAG) → UX-28
- `aria-live-errors` - Field errors tied by aria-describedby and announced politely; role="alert" only for a failed operation → UX-28
- `contrast-feedback` - Error and success state colors must meet 4.5:1 contrast ratio (WCAG, MD) → UX-7
- `timeout-feedback` - Request timeout must show clear feedback with retry option (MD) → UX-45

### 9. Navigation Patterns (HIGH)

- `bottom-nav-limit` - Bottom navigation max 5 items; use labels with icons (Material Design) → UX-30
- `drawer-usage` - Use drawer/sidebar for secondary navigation, not primary actions (Material Design) → UX-30
- `back-behavior` - Back navigation must be predictable and consistent; preserve scroll/state (Apple HIG, MD) → UX-32
- `deep-linking` - All key screens must be reachable via deep link / URL for sharing and notifications (Apple HIG, MD) → UX-32
- `nav-label-icon` - Navigation items must have both icon and text label; icon-only nav harms discoverability (MD) → UX-8
- `nav-state-active` - Current location must be visually highlighted (color, weight, indicator) in navigation (HIG, MD) → UX-31
- `nav-hierarchy` - Primary nav (tabs/bottom bar) vs secondary nav (drawer/settings) must be clearly separated (MD) → UX-30
- `modal-escape` - Modals and sheets have a visible Close; Esc closes them → UX-34
- `search-accessible` - Search must be easily reachable (top bar or tab); provide recent/suggested queries (MD) → только по требованиям
- `breadcrumb-web` - Web: use breadcrumbs for 3+ level deep hierarchies to aid orientation (MD) → UX-31
- `state-preservation` - Navigating back must restore previous scroll position, filter state, and input (HIG, MD) → UX-32
- `tab-badge` - Use badges on nav items sparingly to indicate unread/pending; clear after user visits (HIG, MD) → UX-70
- `overflow-menu` - When actions exceed available space, use overflow/more menu instead of cramming (MD) → UX-16
- `bottom-nav-top-level` - Bottom nav is for top-level screens only; never nest sub-navigation inside it (MD) → UX-30
- `adaptive-navigation` - B2B: a left sidebar when there are many sections; B2C: top navigation; a bottom bar only on narrow widths for 3–5 sections → UX-30
- `back-stack-integrity` - Never silently reset the navigation stack or unexpectedly jump to home (HIG, MD) → UX-32
- `navigation-consistency` - Navigation placement must stay the same across all pages; don't change by page type → UX-30
- `avoid-mixed-patterns` - Don't mix Tab + Sidebar + Bottom Nav at the same hierarchy level → UX-30
- `modal-vs-navigation` - Modals must not be used for primary navigation flows; they break the user's path (HIG) → UX-33
- `focus-on-route-change` - After page transition, move focus to main content region for screen reader users (WCAG) → UX-64
- `persistent-nav` - Core navigation must remain reachable from deep pages; don't hide it entirely in sub-flows (HIG, MD) → UX-30
- `destructive-nav-separation` - Dangerous actions (delete account, logout) must be visually and spatially separated from normal nav items (HIG, MD) → UX-37
- `empty-nav-state` - Unavailable for good → hidden; available later → disabled with «Доступно, когда …» → UX-46

### 10. Charts & Data (LOW)

- `chart-type` - Trend → line, comparison → bar, parts of a whole → 100 % stacked bar; no pies, donuts or gauges → UX-47
- `color-guidance` - Use accessible color palettes; avoid red/green only pairs for colorblind users (WCAG, MD) → UX-73
- `data-table` - Provide table alternative for accessibility; charts alone are not screen-reader friendly (WCAG) → UX-73
- `pattern-texture` - Supplement color with patterns, textures, or shapes so data is distinguishable without color (WCAG, MD) → UX-73
- `legend-visible` - Always show legend; position near the chart, not detached below a scroll fold (MD) → UX-73
- `tooltip-on-interact` - Provide tooltips/data labels on hover (Web) or tap (mobile) showing exact values (HIG, MD) → UX-73
- `axis-labels` - Label axes with units and readable scale; avoid truncated or rotated labels on mobile → UX-73
- `responsive-chart` - Charts must reflow or simplify on small screens (e.g. horizontal bar instead of vertical, fewer ticks) → UX-73
- `empty-data-state` - Show meaningful empty state when no data exists ("No data yet" + guidance), not a blank chart (MD) → UX-73
- `loading-chart` - Use skeleton or shimmer placeholder while chart data loads; don't show an empty axis frame → UX-73
- `animation-optional` - Chart entrance animations must respect prefers-reduced-motion; data should be readable immediately (HIG) → UX-61
- `large-dataset` - For 1000+ data points, aggregate or sample; provide drill-down for detail instead of rendering all (MD) → UX-73
- `number-formatting` - Use locale-aware formatting for numbers, dates, currencies on axes and labels (HIG, MD) → UX-77
- `touch-target-chart` - Interactive chart elements meet the target size: 24 px, 44 px on touch widths → UX-9
- `contrast-data` - Data lines/bars vs background ≥3:1; data text labels ≥4.5:1 (WCAG) → UX-7
- `legend-interactive` - Legends should be clickable to toggle series visibility (MD) → только по требованиям
- `direct-labeling` - For small datasets, label values directly on the chart to reduce eye travel → UX-73
- `tooltip-keyboard` - Tooltip content must be keyboard-reachable and not rely on hover alone (WCAG) → UX-73
- `sortable-table` - Data tables must support sorting with aria-sort indicating current sort state (WCAG) → UX-40
- `axis-readability` - Axis ticks must not be cramped; maintain readable spacing, auto-skip on small screens → UX-73
- `data-density` - Limit information density per chart to avoid cognitive overload; split into multiple charts if needed → UX-47
- `trend-emphasis` - Emphasize data trends over decoration; avoid heavy gradients/shadows that obscure the data → UX-47
- `gridline-subtle` - Grid lines should be low-contrast (e.g. gray-200) so they don't compete with data → UX-73
- `focusable-elements` - Interactive chart elements (points, bars, slices) must be keyboard-navigable (WCAG) → UX-73
- `screen-reader-summary` - Provide a text summary or aria-label describing the chart's key insight for screen readers (WCAG) → UX-73
- `error-state-chart` - Data load failure must show error message with retry action, not a broken/empty chart → UX-73
- `export-option` - For data-heavy products, offer CSV/image export of chart data → только по требованиям
- `drill-down-consistency` - Drill-down interactions must maintain a clear back-path and hierarchy breadcrumb → только по требованиям
- `time-scale-clarity` - Time series charts must clearly label time granularity (day/week/month) and allow switching → UX-73
