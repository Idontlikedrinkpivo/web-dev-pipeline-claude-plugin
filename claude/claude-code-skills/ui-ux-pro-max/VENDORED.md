# Embedded copy: what changed against the original

- **Original:** UI UX Pro Max, https://github.com/nextlevelbuilder/ui-ux-pro-max-skill,
  folder `.claude/skills/ui-ux-pro-max`, version 2.13.0, commit `477bcb2`
  (3 October 2026).
- **Licence:** MIT, `LICENSE` in this folder (copied from the repository
  root). The changes below are distributed under the same licence.
- **Why the changes:** the copy is one part of a single rule set with
  `ux-patterns`. A rule that disagreed with it was rewritten to agree, by
  the decisions in the reconciliation (Р1–Р22); what does not apply to the
  pipeline's web products was removed. The mapping of every rule is in the
  plugin repository, `claude/ux-sources/сверка.md`, appendices А and Г.

## Removed

| What | Why |
|---|---|
| `data/app-interface.csv`, `references/pro-rules.md` | native iOS / Android / React Native rules |
| `data/motion.csv` (GSAP presets), the `gsap` domain, the `--motion` dial | motion only answers an action or shows a change (UX-61, Р1) |
| the `web` domain | it searched `app-interface.csv` |
| stacks other than `react`, `nextjs`, `shadcn`, `html-tailwind` (SwiftUI, React Native, Flutter, Jetpack Compose, JavaFX, WPF, WinUI, Avalonia, Uno, UWP, Vue, Svelte, Astro, Nuxt, Nuxt UI, Angular, Laravel, three.js) | the pipeline builds with React + Vite and Next.js on shadcn/ui and Tailwind |
| `scripts/tests/`, `scripts/validate_data.py` | maintenance of the original data, not used at run time |
| `data/ux-guidelines.csv` rows 22 Touch Target Size (native units; the web rule is row 104), 26 Pull to Refresh, 27 Haptic Feedback, 94 Gaze Hover, 95 Depth Layering, 97 Asset Weight, 101 Focus Not Obscured (Enhanced), 102 Focus Appearance | native platforms, 3D, WCAG AAA |

## Changed

- `SKILL.md` — rewritten for the pipeline: its place among the skills, the
  search contract, how the design-system output maps onto the tokens, no
  `--persist`.
- `data/ux-guidelines.csv` — a «UX Rule» column naming the `ux-patterns`
  rule of every row. Rows rewritten to agree with `ux-patterns`: 1 Smooth
  Scroll (only for anchors, off under reduced motion), 7 Excessive Motion,
  21 Container Width, 29 Hover States (within 150 ms, no hover on
  non-interactive cards), 32 Loading Buttons (busy state, not `disabled`),
  35 Confirmation Dialogs (undo for reversible actions), 44 Error Messages
  (polite field errors, `role="alert"` only for a failed operation), 56
  Inline Validation (on blur), 54 Input Labels (above the field), 57 Input
  Types (`inputmode` instead of `type=number`), 59 Required Indicators (by
  product type),
  64 Mobile First → Desktop First, 65 Breakpoint Testing (the widths of the
  frames register), 73 Line Length (50–75 characters), 82 Toast
  Notifications (success only, 4–10 s), 109 Focusable Error Summary
  (one-field form exception).
- `data/charts.csv` — to agree with UX-47: part-to-whole is a 100 %
  stacked bar or horizontal bars with values (was pie or donut);
  performance against a target is a bullet chart or a progress bar (was a
  gauge); sunburst, nested donut and gauge removed from the secondary
  options; row 22, 3D spatial data, removed; the streaming chart's
  acid-green-on-dark guidance replaced by the theme's tokens.
- `data/products.csv` rows 37, 65 and `data/landing.csv` row 4 — «Mobile-
  first» → desktop first (UX-74); `data/products.csv` row 91 — category
  shares as 100 % stacked bars instead of pie and donut charts;
  `data/styles.csv` row 37 — gauges replaced by progress and bullet charts.
- `data/ux-guidelines.csv` row 49 (Caching) — marked «не применяем»: the
  nginx configuration of `deploy-topology` follows the user's reference.
- `references/quick-reference.md` — every rule ends with `→ UX-n`; rules
  rewritten as in the CSV (also `tap-feedback-speed` within 150 ms and
  `input-type-keyboard` without `type=number`), `mobile-first` renamed
  `desktop-first`; native,
  AAA and decorative-motion rules removed.
- `scripts/core.py` — the `gsap` and `web` domains and the removed stacks
  dropped from the configuration; the `ux` output shows «UX Rule».
- `scripts/design_system.py` — the motion dial is off (`motion_info =
  None`; the GSAP code paths remain but never run); a font pairing is
  chosen only when every family has the `cyrillic` subset in
  `google-fonts.csv`; headings say that a landing pattern is only for a
  public page and that suggested effects are proposals; the checklist items
  and the decorative-motion warning cite `UX-n`.
- `scripts/search.py` — the `--motion` dial and the removed stacks dropped
  from the arguments and the usage text.

## Updating from the original

Diff the new upstream folder against commit `477bcb2`, apply what changed
in the data and scripts, and repeat the steps above for new rows: give each
a `UX-n` (a new rule goes into `ux-patterns` first), rewrite a disagreeing
row, drop what is native or AAA. Then update the version and commit at the
top of this file.
