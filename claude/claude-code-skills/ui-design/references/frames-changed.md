# Frames changed by hand

Read in `ui-design` when the user says the frames were edited outside this skill — «макеты поменялись», «я
поправил кадры», «дизайнер изменил макеты», «обнови реестр под макеты» — in a project that has a frames
register. The frames are the truth here: the register, the screen specs and the test cases follow them.

**Why.** A frame edited by hand drifts from the documents silently: `screen-spec` sees it only when it is run
again, and otherwise the mismatch surfaces weeks later in the acceptance run as «🖼 расхождение с макетом»
(`ui-test-cases`), when the code is already built on the old spec.

**What it is not.**

- A restyle — a new look the user picks from new options: `references/restyle-redraw.md`.
- A redesign of a screen's structure — a screen split, merged or given another job: that changes the SRS and
  needs a new screen spec (`pipeline` → `references/decision-changes.md` → Frames), and the screen is
  `редизайн` in mode draw.
- A request to draw something — «дорисуй состояние» is mode draw with the mark `правка`.

When the comparison shows such a change, say so in one line and stop this mode for that screen; the rest goes on.

## Step 1 — read what changed

1. Read the register: header, «Экраны», «Общие состояния».
2. List the page's children once (`get_metadata` on each page that holds product frames) — this finds frames
   the register does not know.
3. For every register row: `get_metadata` on the screen frame, each state frame, each nested-step frame and
   the `S-n · Аннотация` frame — one frame per call, as everywhere in this skill (a whole page in one call
   is cut off on a real file). Then the app-wide state frames.
4. Compare with the register: frame names, the states and nested steps, the nodeIds. When screen specs exist,
   also compare the annotation's «Элементы» numbers and «Тексты» with each spec's «Кадр» column — the
   register holds no elements, the spec does. One `get_screenshot` of an annotation frame only when metadata
   cannot tell whether a text changed.
5. Show the result in the chat as one table, information, not a question:

| Экран | Итог | Что именно |
|---|---|---|
| S-1 Вход | без изменений | — |
| S-2 Расписание переговорных | изменён | новое состояние «Занято целиком»; эл. 4 переименован; текст эл. 7 |
| S-4 Переговорные | кадр удалён | нет кадра 16:7 (Error) |
| — | новый кадр | «Экспорт расписания» 18:3 на странице `✅ Экраны` |

Marks: `без изменений`, `изменён` (with what: a new or removed state, a renamed frame, elements added or
renumbered, texts), `кадр удалён` (a frame the register cites that the file no longer has), `новый кадр` (a
frame on the page that is in no row).

## Step 2 — update the register in place

- A new state or nested-step frame → its line in the row's cell (`M<n>` takes the next free number); a new
  narrow size → `<Ш×В> → nodeId`.
- A renamed frame → the register keeps the S-id and takes the new nodeId or name where it changed.
- A removed frame → a row in `open-questions.md` («S-4: кадр Error 16:7 удалён из файла — состояние больше не
  нужно или кадр перенесён?»), classed `Блокирует старт` when a use-case flow or a role is left with no frame,
  otherwise `Отложено`; the register line stays until the answer. Never a silent deletion: the spec and the
  cases cite that frame.
- A new frame that is a new screen → the next free `S-n` only when it serves an SRS use case; otherwise it is
  a behaviour the SRS lacks — a changed decision for the SRS first (`pipeline` →
  `references/decision-changes.md`), and the row waits for it.
- **Ids keep their meaning.** S-ids, M-ids and element № are never renumbered or reused: the specs, the cases
  and the code cite them. A new element takes the next free №. A renumbering found in the annotation is not
  taken over: when **Кадры рисует** is `ui-design`, the old № are put back in the annotation only
  (`figma-sonnet`, `MODE edit`, the annotation frame alone), said in one line; when a designer draws, it is a
  row in `open-questions.md` addressed to them.
- Rerun `ux-patterns` → Полнота макета on the changed screens only: a removed state may leave a flow without
  a frame. A miss is an `open-questions.md` row, and the screen's Статус follows the usual rule.
- Move `updated:` to today; `sources:` stays — the SRS did not change.

Commit the register (and `open-questions.md`) at once: `docs: реестр кадров — правки макетов`.

## Step 3 — the cascade

- **No screen specs yet** → the register is all; go to the close.
- **Screen specs exist** → run `screen-spec`'s increment for exactly the screens marked `изменён` (and a
  new screen once it has its S-id), handing it that list: it is the scope, `screen-spec` does not detect it
  again. Then `ui-test-cases` mode write, `MODE increment`, for the cases of those screens (traces, texts,
  frame ids).
- Each document lands as a changed decision (`pipeline` → `references/decision-changes.md`): no version bump,
  committed at once. When a change alters behaviour another document defines — an SRS rule, an error, a
  right («теперь отмена без подтверждения») — that is a changed decision for the SRS first, landed before the
  spec.
- Code already built on the old spec is named in the close as a fix for the next plan (decision-changes →
  Work already built on the old decision).

## Close

Run `python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/push_branch.py"`, then one line in Russian — what was
updated, for example «Обновлено по правкам макетов: реестр кадров (S-2, S-4), ТЗ на экран S-2, тест-кейсы
TC-12, TC-14; открытый вопрос по S-4.» Then back to where the iteration stood: `pipeline` names that stage.
