---
name: ui-ux-pro-max
description: >-
  Searchable design data behind the pipeline's visual direction: product
  types with their styles, palettes in shadcn-style roles, font pairings
  checked for Cyrillic, landing-page patterns, chart types, icons, and
  React / Next.js / shadcn / Tailwind notes; every UX row names its
  `ux-patterns` rule. Used by `ui-design` in the «Визуальное направление»
  step (a new product, or a restyle of existing mockups), by the Figma
  builders and by `frontend`. Use it whenever a palette, typeface, style,
  density or landing layout is being chosen or compared for a web
  product — «подбери палитру», «какой шрифт», «стиль интерфейса» — even
  when the user does not name it. A change of the product's look itself
  starts in `ui-design`, whose visual-direction step uses this data. Not
  the UX rules (`ux-patterns`) and not drawing (`ui-design`).
---

# UI UX Pro Max — design data

An embedded copy of UI UX Pro Max (MIT, `nextlevelbuilder/ui-ux-pro-max-skill`
v2.13.0, commit `477bcb2`), fitted to this pipeline. `LICENSE` is the
original licence; `VENDORED.md` lists every change against the original.

## Place in the pipeline

| Who | Uses | For |
|---|---|---|
| `ui-design`, step «Визуальное направление» | `--design-system`; `--domain color`, `typography`, `google-fonts`, `style`, `landing` | two or three directions (palette, fonts, style, density) for the user to choose from; landing patterns when the SRS has a public page; suggested effects as proposals |
| `figma-opus` (`MODE direction`, `MODE draw`), `figma-sonnet` (`MODE restyle`) | the chosen direction as the packet states it | style tiles; the token set; rebinding existing frames |

Used directly, it also gives implementation notes for a stack (`--stack
react`, `nextjs`, `shadcn`, `html-tailwind`; `--domain react`) and the short
form of every rule with its `UX-n` (`references/quick-reference.md`).

The UX data here is the same rule set as `ux-patterns`. Every row of
`data/ux-guidelines.csv` names its rule in the «UX Rule» column, and every
line of `references/quick-reference.md` ends with `→ UX-n`; cite that id in
annotations, specs and findings. A row marked «только по требованиям» is a
feature, not a rule: it reaches a screen only when the SRS asks for it.

## Running the search

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/search.py" "<query>" --domain <domain>
```

If `python3` is missing, try `python`, then `py -3`. Python 3 only, no
packages. The script reads only this skill's `data/` folder and writes
nothing.

Choose the smallest mode that fits:

1. **A product-wide visual direction** → `--design-system`.
2. **One concern** (a palette, a font, a chart, a UX question) → one
   explicit `--domain`.
3. **Implementation in a known stack** → `--stack`; a design question in
   the same task is a separate `--domain` search.

Build each query around one intent, in 2–5 meaningful English terms (the
data is in English, so Russian words match nothing) with one useful
constraint (product, audience, interaction): `"meeting room
booking corporate"`, not a whole brief. Check that the domain, the top
result and its fit for this product are right before using it. Retry once
with a narrower query or an explicit domain when the result is empty or off
topic; if that fails too, say that no match was found and label any general
advice as a fallback, not as data. Never present an empty search as a
result.

| Need | Domain | Example |
|---|---|---|
| Product type → style, palette, landing | `product` | `"booking appointment" --domain product` |
| More styles | `style` | `"minimal flat accessible" --domain style` |
| Palettes | `color` | `"corporate trust blue" --domain color` |
| Font pairings | `typography` | `"professional clean" --domain typography` |
| One Google font | `google-fonts` | `"cyrillic geometric sans" --domain google-fonts` |
| Charts | `chart` | `"occupancy over time" --domain chart` |
| UX question | `ux` | `"error summary validation" --domain ux` |
| Landing structure | `landing` | `"pricing social proof" --domain landing` |
| Icons | `icons` | `"calendar outline" --domain icons` |
| React / Next.js performance | `react` | `"rerender memo list" --domain react` |

Stacks: `react` (React + Vite), `nextjs`, `shadcn`, `html-tailwind` — the
pipeline's two front-end stacks and their component and styling layer.

## The design system for a visual direction

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/search.py" "<product> <audience> <keywords>" \
  --design-system -p "<Product>" -f markdown --density <1-10> [--variance <1-10>]
```

- `--density` sets the spacing scale: B2B 7–8 (compact rows, UX-10), B2C
  3–5.
- `--variance` moves the style from calm and centred (1–3) to bold and
  asymmetric (8–10): B2B 2–4; B2C and a public page up to 7. Two runs with
  different `--variance` or style keywords give two genuinely different
  directions — options that differ only in hue are one option.
- Do not use `--persist`. The chosen direction lives as variables in the
  Figma file (`🎨 Tokens`), in the frames register's «Визуальное
  направление» line, and later as CSS variables in code; a
  `design-system/MASTER.md` would be a second source that goes stale.

How the output maps onto the pipeline:

| Output section | Use |
|---|---|
| Style | the direction's character and its name in the option |
| Colors | tokens, by the table below; check every text pair for 4.5:1 and control boundaries for 3:1 (UX-7) before offering it |
| Typography | the pairing is already checked for Cyrillic (every family has the `cyrillic` subset); a font outside the pairings comes from `--domain google-fonts` with `cyrillic` in the query, and is kept only when its Subsets list `cyrillic` — `cyrillic-ext` alone has no Russian alphabet |
| Landing Pattern | only when the SRS has a public page: offered to the user as the section order and the place of the main action |
| Suggested Effects | proposals for the user, not rules. First drop what `ux-patterns` rules out — UX-61 (decorative entrances, staggers, springs, scale on press, animated screen transitions, parallax outside a B2C first screen), UX-63 (hover slower than 150 ms), UX-47 (gauges, pies); an accepted one becomes a line in `ui-wishes.md` |
| Avoid | added to the direction's «не делаем» line |
| Pre-Delivery Checklist | short form; the full one is `ux-patterns` → «Проверка экрана перед сдачей» |

Palette roles → the pipeline's tokens (the shadcn/ui names the Figma
variables and the code share):

| Output role | Token | Note |
|---|---|---|
| Primary, On Primary | `primary`, `primary-foreground` | the one accent: the main button, links, selection, the active menu item |
| Background, Foreground | `background`, `foreground` | |
| Card, Card Foreground | `card`, `card-foreground` | |
| Muted, Muted Foreground | `muted`, `muted-foreground` | also shadcn's `secondary` and `accent` (the secondary-button and hover surfaces), with `foreground` on them |
| Border | `border`, `input` | |
| Destructive, On Destructive | `destructive`, `destructive-foreground` | UX-37 |
| Ring | `ring` | the focus ring (UX-63) |
| Secondary, Accent/CTA | `chart-1` … `chart-5` | colours for data; in B2C or on a public page Accent may instead become a second accent for the key action of a screen, only when the user picks it (a new token, UX-1) |

The output gives one theme. When the SRS needs a dark theme, the dark set is
designed with the light one — lighter, desaturated tones rather than
inverted ones — and its contrast is checked separately (UX-62).

## If a search returns nothing

1. Retry once with a narrower query or an explicit domain or stack.
2. Still empty: use `ux-patterns` and say plainly that the suggestion comes
   from general defaults, not from this data («палитры под этот продукт в
   базе нет, предлагаю нейтральную»).
3. Never present an empty search as a match.

## Where to look

| Problem | Where |
|---|---|
| Can't choose a style or palette | `--design-system` again with other style keywords or another `--variance` |
| Contrast in a dark theme | `references/quick-reference.md` §6: `color-dark-mode`, `color-accessible-pairs` |
| Motion feels wrong | §7: `motion-meaning`, `easing`, `exit-faster-than-enter` (UX-61) |
| Form problems | §8: `inline-validation`, `error-clarity`, `focus-management` |
| Navigation is confusing | §9: `nav-hierarchy`, `adaptive-navigation`, `back-behavior` |
| Layout breaks at a width | §5: `desktop-first`, `breakpoint-consistency` (UX-74) |
| Performance | §3: `virtualize-lists`, `main-thread-budget`, `debounce-throttle` (UX-75) |
