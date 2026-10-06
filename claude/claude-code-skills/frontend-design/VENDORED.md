# Embedded copy: what changed against the original

- **Original:** Anthropic `frontend-design` skill,
  https://github.com/anthropics/skills, folder `skills/frontend-design`,
  commit `683bc88` (5 October 2026).
- **Licence:** Apache License 2.0, `LICENSE.txt` in this folder. `SKILL.md`
  is a modified file and says so at its top, as section 4(b) of the licence
  requires.
- **Why the changes:** the skill joins one rule set with `ux-patterns` and
  works where this pipeline decides the look — the visual direction in
  `ui-design` and the Figma frames — instead of in page code. The mapping of
  each point is in the plugin repository, `claude/ux-sources/сверка.md`,
  appendix В.

## Changed in `SKILL.md`

- Description and opening: the design goes into the visual direction and
  the frames; `frontend` builds the frames as they are.
- «Ground the design»: the brief is the SRS, `ui-wishes.md` and the user's
  earlier choices; real content instead of placeholders.
- «Take aesthetic risk» → boldness in one place, bounded by the product
  type: restrained and dense in B2B, more expressive in B2C and on a public
  page; no `ux-patterns` rule is broken for it (Р3).
- The hero: only for a B2C home page or a public page (UX-49); a B2B work
  screen opens with the work.
- Typefaces: only families with the Cyrillic alphabet.
- Line length under 80 characters → 50–75 (Р17, UX-4).
- Motion: one orchestrated moment only on a B2C first screen, none in B2B
  (Р1, UX-61).
- The template tells and the five clusters cite UX-60; numbers use
  `tabular-nums` of the body face rather than a monospace face (UX-59).
- The quality floor points to `ux-patterns` → «Проверка экрана перед
  сдачей».
- «Jot down notes» → rejected directions are kept in the frames register
  by `ui-design`; the builder names what it tried and dropped in its
  report.
- «More on writing» → «Writing», in Russian, with the `ux-patterns` ids
  (UX-12, UX-21, UX-44, UX-45, UX-78, UX-79); sentence case → a capital
  only on the first word.

## Moved

- The note on CSS selector specificity → `frontend`, where screen code is
  written.

## Updating from the original

Diff the new `skills/frontend-design/SKILL.md` against commit `683bc88`,
bring each change in with the adjustments above, and update the commit here
and in the notice at the top of `SKILL.md`.
