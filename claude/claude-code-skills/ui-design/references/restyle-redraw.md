# Restyle and redraw on a new page

Read in `ui-design` when the user has chosen a new visual direction for
frames that already exist (`SKILL.md` → Visual direction): a **restyle**
changes the look of the same frames; a **redraw** draws every screen anew
on its own page. Both start after the visual-direction step
(`references/visual-direction.md`) has run and the user has chosen.

## Restyle

A new look for frames that already exist: the visual direction changes;
the screens, their structure, layer names, texts, annotation frames and
every `nodeId` stay. It is not a redesign — a screen whose structure must
change is `редизайн` and goes through `SKILL.md` → Drawing (mode draw).

1. The visual-direction step has run and the user has chosen. The register
   line names the new direction and `прежнее: «<имя>»`.
2. Read the file: `get_metadata` on every page, `get_variable_defs` on a
   screen frame. Local variables are restyled in place. A linked library
   belongs to its designer: say so and stop — its variables are not edited
   from here.
3. Dispatch `figma-sonnet` with `MODE restyle`: `SCREENS` lists every
   screen of the register with the mark `перекраска` and its frames, `APP-WIDE STATES` the app-wide
   frames, `VISUAL DIRECTION` the chosen direction.
4. Verify: every `nodeId` of the register still resolves under its name;
   one `get_screenshot` per screen shows the new look with no clipped text
   and no template tells (UX-60). A miss goes back with only the missing
   items, round after round while each round fixes at least one; what no
   round can fix is a row in `open-questions.md`.

The register's ids and statuses do not change; `updated:` moves on. When
the frontend is already built (the repository holds the screens' code),
the next stage is `plan`: its theme unit carries the `🎨 Tokens` variables
into the project's theme file. The screen specs stay valid, because only
the look changed.

## Redraw on a new page

The whole interface drawn anew in the chosen direction, on its own page.
The old frames stay exactly as they are on theirs — a designer's work is
neither restyled nor archived, and both versions can be compared side by
side.

1. The visual-direction step has run and the user has chosen.
2. Read the file: `get_metadata` on every page. Every product frame goes
   into `EXISTING FRAMES` and stays untouched.
3. Dispatch `figma-opus` with `MODE draw`, `PAGE` a new page `✅ Экраны ·
   «<имя направления>»`, every screen of the register in `SCREENS` marked
   `редизайн` with its old frames as the reference, every app-wide state
   `draw`, and `VISUAL DIRECTION`. The screens keep their S-ids and M-ids,
   and each element keeps the № and layer name of the old annotation
   wherever it stays, so the screen specs need new nodeIds rather than a
   rewrite.
4. Verify as in `SKILL.md` → Drawing (mode draw) → Verification. The register then points at the new frames: the
   frame, state and step cells take the new nodeIds; the header says
   **Кадры рисует:** `ui-design`, drops **Слои по действиям**, and adds
   **Прежние кадры:** the old page, who drew it, and that it is no longer
   used.

The next stage is `screen-spec` for every screen — the nodeIds changed,
and an element the builder added or reshaped needs its row — then
`ui-test-cases` (write) for the frame ids, then `plan`.
