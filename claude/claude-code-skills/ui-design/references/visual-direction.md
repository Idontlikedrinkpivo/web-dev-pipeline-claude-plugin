# Visual direction — the step

Read in `ui-design`'s «Visual direction» step and before a restyle. The step
ends with one choice by the user and one line in the register header; the
tokens themselves are created by the next builder run.

## 1. Brief

Three lines, from the SRS and `ui-wishes.md`, before any search:

- **Предмет:** what the product is about, in its own words («бронирование
  переговорных в офисе»).
- **Аудитория:** who uses it, how often, in what situation (the actors and
  the NFR).
- **Тип и ширины:** from the register header.

Add what pins the look: brand colours or a brand book named in the SRS or
by the user; on a restyle, the current look (one `get_screenshot` of two or
three key screens) and what the user dislikes in it; the directions the
register lists as rejected.

## 2. Options

Invoke the `dev-pipeline:ui-ux-pro-max` skill and search with its commands
— its script path resolves only once the skill is loaded; the token mapping
is there too:

- `--design-system` with the subject and audience in English terms,
  `--product-type` and `--density` by the register's **Тип продукта** (the
  font pair is then picked for it), two or three runs that differ on a real
  axis: `--variance` (calm or bolder), style keywords (flat or soft), light
  or dark;
- `--domain color`, `--domain typography`, and `--domain google-fonts` with
  `cyrillic` in the query, when an option needs another palette or face.

Load `dev-pipeline:frontend-design` and shape each option as its «Process»
plans it:

- **Имя:** two or three Russian words that say the character («Хвойный
  тихий», «Тёплый графит»). The examples in this file show the shape, not a
  look to reuse: Tailwind's blue `#2563EB`, Inter, purple-to-indigo are the
  defaults every generated screen reaches for (`frontend-design`).
- **Палитра:** 4–6 named hex values, then the full token list the Figma
  packet's VISUAL DIRECTION needs: every token of the mapping table
  (`ui-ux-pro-max` → palette roles), with `chart-1` … `chart-5` taken from
  Primary, Secondary, Accent and two more hues of the palette, each at 3:1
  against the background; a dark set too when the SRS needs a dark theme
  (UX-62).
- **Шрифт:** one or two families with their roles, each with the
  `cyrillic` subset.
- **Форма и плотность:** the radius and shadow scales (UX-58); compact rows
  for B2B (UX-10), comfortable for B2C.
- **Смелость:** the one bold thing, and what stays quiet.
- **Не делаем:** the data's Avoid list and the template tells of
  `frontend-design`.

## 3. Filter

Fix or drop an option that:

- falls into one of the six clusters of `frontend-design` or another tell
  of UX-60, unless the brief asks for it;
- has a family without the `cyrillic` subset;
- has a text pair below 4.5:1 or a control boundary below 3:1 in any of its
  themes (UX-7) — compute the ratio, do not judge it by eye;
- is bolder than the product type allows (B2B restraint: `frontend-design`
  → «Design principles»);
- repeats a rejected direction;
- differs from another option only in hue — merge them.

Two strong options are better than three with a filler.

## 4. Style tiles

Dispatch `figma-opus` with `MODE direction` (`executor-catalog` → the Figma
packet): `OPTIONS` holding the plans, `EXISTING FRAMES` from
`get_metadata` (they stay untouched), an `SRS EXCERPT` with the actors and
one or two main use cases (the tiles' real data), `SCREENS` none. It draws one tile per option on the
page `🎨 Направления`: the palette with token names, the type scale on
Russian text, the button set, a field with its hint and error, a table row
and a card with this product's real data, a toast and a badge. Check each
tile's `nodeId` with `get_metadata`; read the report for the changes the
builder made to an option and carry them into the question.

## 5. The question

One question, per `grill-me` → "How a question is shown". Link each tile:
`https://www.figma.com/design/<fileKey>/?node-id=<nodeId with - for :>`.

```text
**Вопрос 2. Какое визуальное направление взять**

Направление — общий вид всех экранов: цвета, шрифт, скругления и
плотность. Его увидят на каждом макете, а потом в коде. Образцы — на
странице «🎨 Направления» в Figma.

  A. «Хвойный тихий» — тёплый светлый фон, хвойно-зелёный акцент #1F6F5C,
     шрифт Onest, компактные строки таблиц; смелость только в акценте.
     Образец: <ссылка>. (рекомендую)
  B. «Тёплый графит» — графитовый акцент #334155 на тёплом сером, шрифт
     IBM Plex Sans, скругления крупнее. Образец: <ссылка>.
  C. Своё — опишите словами или пришлите пример.
  D. Без направления — нейтральная серая палитра и один акцент; выбрать
     направление можно позже.

Рекомендую A: это инструмент на весь рабочий день — ничего не отвлекает
от расписания.

Ответьте сообщением: буква или своё описание.
```

Recommend the option that fits the product type and the brief best, with
one sentence why. An answer «своё», or «A, но …», becomes a new option:
shape it, filter it, draw its tile, ask again. D, or «не надо», is a
decline: record it (step 6) and go on to the screen set with the neutral
set; the tiles stay on their page.

When the SRS has a public page, ask one more question: two or three landing
patterns from `--domain landing`, each with its section order and where the
main action sits.

Then offer the chosen option's suggested effects (`ui-ux-pro-max` →
Suggested Effects) as a list, not a question that blocks. Leave out first
what `ux-patterns` rules out — UX-61 (decorative entrances, staggers,
springs, animated screen transitions, parallax outside a
B2C first screen), UX-63 (hover slower than 150 ms, hover on
non-interactive cards), UX-47 (gauges, pies) — so the user is never
offered what the builder would then refuse. Each one the user picks becomes a line
in `ui-wishes.md` («Подсветка строки при наведении —
предложено при выборе направления»).

## 6. Record

Write the register header line:

```markdown
- **Визуальное направление:** «Хвойный тихий» — primary #1F6F5C, Onest,
  плотность компактная, тема светлая; токены — страница `🎨 Tokens`;
  выбрано 2026-10-06; отклонены: «Тёплый графит»
```

A decline is recorded too, so a later run does not take it for «not
chosen yet» and ask again:

```markdown
- **Визуальное направление:** отказ — нейтральная палитра, 2026-10-06
```

On a restyle or a redraw add `прежнее: «<имя>»`. Later runs read the tokens from
`🎨 Tokens` (`get_variable_defs`), not from this session's notes. The packet's `VISUAL DIRECTION` is the
chosen plan from step 2 with the user's adjustments: the next `figma-opus`
run in mode draw creates the tokens from it; `figma-sonnet` in `MODE
restyle` rewrites the existing ones. After a decline it is `declined`: the
builder makes a neutral grey scale plus one accent.
