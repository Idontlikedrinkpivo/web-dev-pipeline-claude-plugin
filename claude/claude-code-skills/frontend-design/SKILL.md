---
name: frontend-design
description: >-
  Internal: taste rules for frames and a visual direction, read by ui-design and the Figma builders; not for direct
  requests.
---

# Frontend Design

> Modified for dev-pipeline from Anthropic's `frontend-design` skill
> (`anthropics/skills`, commit `683bc88`, Apache License 2.0 — see
> `LICENSE.txt`). Changed: the design happens in Figma frames and the
> visual direction, not in page code; boldness is bounded by the product
> type; motion, line length, the first screen and copy follow
> `ux-patterns`; fonts must have Cyrillic. Every change is listed in
> `VENDORED.md`.

Approach this as the design lead at a studio known for giving every client a
distinct visual identity. This client has already rejected proposals that
felt cliché or templated: make deliberate choices about palette, typography
and layout that are specific to this brief. In this pipeline that judgment
goes into the visual direction (`ui-design`) and the frames the Figma
builders draw; `frontend` then builds the frames as they are.

**Loaded straight from a request?** This skill is read by `ui-design` and
the Figma builders; it changes no frame itself. When it came from the
user's words alone («перерисуй стильнее», «сделай менее шаблонно», «нужен
характер») and not from one of them, hand the work to `ui-design` and
follow it: there a new look runs as style tiles the user picks, the old
look is kept in `🗄 Архив`, and the choice lands in the frames register —
none of which happens from here, so a restyle started here leaves the
register and the screen specs describing a look that is gone.

## Ground the design in the subject matter

The SRS names the product, its actors and their jobs; `ui-wishes.md` and
the user's earlier choices are hints about taste. The subject's industry,
materials and vernacular are where distinctive choices come from — a tool
for booking meeting rooms looks different from a children's reading app.
Build with the brief's real content throughout: real names, plausible
numbers, the texts the actor will read — never «Lorem ipsum» or «Название
1».

## Design principles

The product type sets how far to go (`ux-patterns` → Product type). B2B
is restrained and dense: the boldness goes into one place — the accent
colour, the typeface, one characteristic element — and the work screens
stay quiet. B2C and a public page may be more expressive. No rule of
`ux-patterns` is broken for expressiveness.

On a B2C home page or a public page, the first screen is the first thing
viewers see (UX-49). Open with the most characteristic thing in the
subject's world, in the most fitting form: a headline, an image, a live
example. A big number with a small label, supporting stats and a gradient
accent is the default treatment; use it only if it is truly the best option.
A B2B work screen opens with the work itself.

Typography carries the personality. One family or two; if two, clearly
distinct. Choose them deliberately, not the defaults you would reach for on
any project, and only among families with the Cyrillic alphabet (the
`cyrillic` subset; `ui-ux-pro-max` checks it). Set a clear type scale with
intentional weights (UX-3). When type is a headline or a visual element, let
the treatment itself be an active part of the design.

Running text stays within 50–75 characters per line (UX-4). Serif body text
gets slightly more line height than sans.

Avoid the commonest tells of a generated page (UX-60): accenting a single
word of a headline by italic, bold or colour; all-caps labels; labels that
add nothing above the content.

Visual structure is information. Outlines, borders, numbering, dividers and
labels encode something about the content rather than decorate it.
Numbered markers (01 / 02 / 03) only for content that really is a sequence —
a stepped process or a timeline.

Motion answers an action or shows what changed — opening, expanding,
confirming (UX-61). Fade-and-slide entrances on each section and hover
effects on every card are the generic default and read as generated. A B2C
first screen may have one orchestrated moment; a B2B product has none.

Copy can make a design feel as templated as the layout; see «Writing»
below.

## Process: plan, check against the brief, build, critique

For calibration, generated design currently clusters around these six traits:

1. a warm cream background (near #F4F1EA) with a high-contrast serif and a
   terracotta or clay accent (near #D97757 — Anthropic's own accent, so on
   a client's brief it reads as a tell);
2. a near-black background with one acid-green or vermilion accent;
3. a broadsheet layout with hairline rules, zero radius and dense
   newspaper columns;
4. the SaaS card kit: content chopped into identical rounded cards, one
   radius on everything, the same soft grey shadow (rgba(0,0,0,.1)) under
   each, gradient washes as decoration;
5. template chrome whatever the subject: a tracked-out ALL-CAPS label above
   every heading; meta strings joined with middle dots («A · B · C»);
   labels built as «СЛОВО — фрагмент»; tinted near-black (#0B0B0B, #111)
   instead of the foreground token; a monospace face for small data labels
   (numbers use the body face's `tabular-nums`, UX-59); «→» in link and
   button text;
6. the assistant's own palette and props: purple-to-indigo as the accent,
   gradient-filled headline text; cards nested in cards; a coloured stripe
   thicker than 1 px down the left of a card, an alert or a list row; a
   card with a border and a wide soft shadow at once (pick one); a «Новое»
   or «Бета» pill above the main heading, a pulsing «live» dot as
   decoration; a product shot faked from grey bars instead of the real
   screen.

Each trait is legitimate for some brief, but they are defaults rather than
choices. Where the brief pins a look down — the SRS, a brand book, the
direction the user chose — follow it exactly, including when it asks for
one of these. Where an axis is free, do not spend it on one of these
defaults.

Work in two passes. First a short plan:

- Colour: the base palette as 4–6 named hex values — the tokens
  (`ui-ux-pro-max` → palette roles).
- Type: the families and their roles.
- Layout: one-sentence descriptions and ASCII wireframes to compare ideas;
  how content aligns.
- Principles: what makes this product's screens its own, and where the one
  bold thing sits.

Then check the plan against the brief before drawing: if a part reads like
the default you would produce for any similar product (ask: would this
plan fit any booking or CRM product unchanged? If yes, it is a default),
revise it and say what changed and why. Draw only after that, by the revised plan.

## Restraint and self-critique

Spend boldness in one place; keep everything around it quiet and
disciplined; cut decoration that does not serve the brief. Build to the
quality floor without announcing it: `ux-patterns` → «Полнота макета»,
plus the items of «Проверка экрана перед сдачей» a frame can show —
every width in the register, desktop first; contrast in every theme;
long values; icons from one set; texts (its items on widths, contrast,
value lengths, icons and texts). Screenshot each frame as you go and
critique it; before handing over, remove one decorative element.

The directions the user turned down are kept in the frames register's
«Визуальное направление» line (`ui-design` writes it), so the next run does
not offer them again; name in your report what you tried and dropped.

## Writing

Words are design content, not decoration. Before writing anything, ask what
the screen needs to say and how it helps the person get through it:
describe what a thing is or does, do not sell it, and give each text one
job. The rules for the words themselves — names, buttons, errors, empty
states, typography — are `ux-patterns` Section 9 «Texts in Russian» with
UX-12, UX-21, UX-44, UX-45, UX-78 and UX-79 it cites.
