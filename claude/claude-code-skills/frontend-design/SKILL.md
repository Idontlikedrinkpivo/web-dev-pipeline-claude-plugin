---
name: frontend-design
description: >-
  How to make frames and a visual direction read as made for this product,
  not as a template — Anthropic's frontend-design fitted to the pipeline:
  ground the look in the product's subject and audience, plan tokens, type
  and layout before drawing, check the plan for template tells (UX-60),
  spend boldness in one place (restrained in B2B), critique by screenshot,
  write copy by UX-79. Used by `ui-design`'s «Визуальное направление» step
  and by `figma-opus` / `figma-sonnet` when they draw or restyle frames.
  Use it whenever frames or a visual direction are being made, and when
  the user wants a less generic look («сделай менее шаблонно», «нужен
  характер», «перерисуй стильнее»), even without naming it. A change of
  the product's look starts in `ui-design`. Not screen code (`frontend`),
  not the UX rules (`ux-patterns`).
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

For calibration, generated design currently clusters around these traits:

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
   button text.

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
the default you would produce for any similar product (try a similar
prompt and see whether you land in the same place), revise it and say what
changed and why. Draw only after that, by the revised plan.

## Restraint and self-critique

Spend boldness in one place; keep everything around it quiet and
disciplined; cut decoration that does not serve the brief. Build to the
quality floor without announcing it: `ux-patterns` → «Проверка экрана
перед сдачей» (every width, desktop first; visible focus; reduced motion;
contrast in every theme; long values). Critique your own work as you go
with screenshots — a picture is worth a thousand tokens. Before handing
over, look in the mirror and remove one accessory.

The directions the user turned down are kept in the frames register's
«Визуальное направление» line (`ui-design` writes it), so the next run does
not offer them again; name in your report what you tried and dropped.

## Writing

Words are design content, not decoration. Before writing anything, ask what
the screen needs to say and how it helps the person get through it. The
interface language is Russian, by `ux-patterns` Section 9.

- Name things in the user's words, not the system's: «уведомления», not
  «вебхуки». Describe what something is or does; do not sell it (UX-79).
- Active voice. A button says exactly what happens: «Сохранить изменения»,
  not «Отправить» (UX-12). One action keeps one name along the whole path:
  «Опубликовать» → «Опубликовано» (UX-79).
- Failure and emptiness give direction, not mood: say what went wrong and
  how to fix it, in the interface's voice; errors do not apologise and are
  never vague (UX-21, UX-45). An empty screen invites the next action
  (UX-44).
- Plain verbs, a capital only on the first word, «вы» in lower case, no
  filler; each text does one job (UX-12, UX-78, UX-79).
