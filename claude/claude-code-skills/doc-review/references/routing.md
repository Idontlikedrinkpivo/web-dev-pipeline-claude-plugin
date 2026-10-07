# Routing (interactive only)

After the report, if any actionable finding remains (`gated_auto` or
`manual` at anchor `75` or `100`), follow `grill-me` → "How a question is
shown".

In the chat, in Russian, say how many findings remain and what each option
does. A finding is one review comment. `gated_auto` means the reviewer
suggested a fix that still needs a yes. The reviewed document is not
changed. `open-questions.md` receives a finding only after the user
defers it. It is not where the question is shown.

- **A. Разобрать по одному.** Каждое замечание отдельно: применить, отложить или пропустить.
- **B. Применить рекомендованное.** Для каждого замечания берётся действие, которое ревьюер уже предложил.
- **C. Отложить все.** Замечания уходят в `open-questions.md` рядом с документом, сам документ не меняется.
- **D. Только отчёт.** Никаких правок.

Recommend one in a sentence — by default **A**: the user sees every
finding and decides each; recommend B only when every finding is a small,
one-right-answer fix. One question, then stop. The user answers by sending a message. Do not open a question card. Options:

- **A. Разобрать по одному.**
- **B. Применить рекомендованное.**
- **C. Отложить все.**
- **D. Только отчёт.**

Never skip the question silently.

If the only leftovers are FYI, skip this question.

## A — One by one

Severity order P0 → P3. One finding per message. The finding text is
the message. Then stop. The user answers by sending a message. Do not
open a question card. A file edit is not the text. «Запишу в файл,
чтобы текст был виден» is a failed turn. Do not put the current finding
into `open-questions.md` in order to show it. That file is updated only
after the user chooses Отложить.

```
**Замечание N из M. {title}**

Что не так: …полный текст замечания, не заголовок…
Что изменится, если применить: …
Что останется, если отложить: …

Рекомендация: A. Применить — одно предложение, почему.
```

M is the number of findings to route in this round, so the user sees how many are left. Terms in the finding stay; say what they mean for this fix. End the message with «Ответьте сообщением: буква или свой текст.» Options:

- `A. Применить` — when that is the recommended action, append ` (Recommended)`
- `B. Отложить`
- `C. Пропустить`

- **Apply** — edit the document with that finding's `suggested_fix`. No
  `suggested_fix` → treat as Defer. Leave `version`, `updated`, and the
  changelog untouched. An applied finding is not a new version.
- **Defer** — append to `open-questions.md` in the reviewed document's
  folder (below). Do not edit the reviewed document.
- **Skip** — record, do not edit.

After the last finding, print a one-line completion (applied / deferred /
skipped counts). Then see "Re-review" below.

## B — Best judgment

Preview the planned action per finding (`Apply` / `Defer` / `Skip` from
`recommended_action`). Ask Proceed / Cancel. On Cancel, return to A–D.
On Proceed, execute the preview. Then see "Re-review" below.

## Re-review

When at least one fix was applied in this round, ask once more, one
question in the chat: `A. Проверить ещё раз` / `B. Закончить` — A
`(Recommended)`, because a fix can open a new gap. There is no limit on
rounds: they go on until one brings no finding the user has not decided —
the report then says «Новых замечаний нет — ревью пройдено» — or progress
stops (`pipeline` → `references/convergence.md`): a decided finding comes
back past synthesis, or a round raises only what earlier rounds raised;
then say so — a document that keeps producing new findings usually has its
problem upstream — and recommend B. A re-dispatches the same personas with
the accumulated decision primer. A round where every finding went to C or D
applied nothing and ends the review. The rounds are inside the gate,
not a pipeline transition; each opens with one line in the chat («Ревью,
круг 3: новых замечаний 2»).

## C — All to the parking lot

Preview the list. On Proceed, Defer every remaining actionable finding
into `open-questions.md` beside the reviewed document. No other edits. Do not touch
the reviewed document.

## D — Report only

No edits. Done.

## Defer — append to `open-questions.md`

This is the only destination when the user parks a finding. The file
sits in the reviewed document's folder. The same path runs when they
say `отложи`, `потом`, or `в open questions` in chat after the report —
not only when they pick A–D. There is no shared
`documentation/open-questions.md`.

1. Read `doc-versioning` → **Открытые вопросы** if the file shape is not
   already in this session. Create `<document-folder>/open-questions.md`
   when this is the first question, with that section's stub. Two
   exceptions: a scenarios document parks into
   `documentation/architecture/open-questions.md`, shared by the three
   architecture documents, and a screen spec into
   `documentation/ui/open-questions.md`, beside the frames register.
2. Do **not** add a question to the reviewed document. It has no
   open-questions section. If an older heading is already in the body
   (`## Deferred / Open Questions`, `## Открытые вопросы`, SRS `## 9`,
   a plan `## 6`), leave it for the convention check;
   new items go only to the sibling file.
3. Under `## From YYYY-MM-DD review of <reviewed-path>`, append:

```
- **{title}** — {section} ({severity}, {reviewer}, confidence {confidence})

  {why_it_matters}
```

Do not append `suggested_fix` or the evidence array. `{why_it_matters}`
says what goes wrong if the question stays open. It does not say how to
close it. Parking means nobody has decided yet, and a recommendation written
into the parking lot reads later as if it had been agreed. If the same
`normalize(section) + normalize(title)` already exists under today's
heading for that path, skip the duplicate.
4. Tell the user the parking-lot path and that the reviewed document
   was not changed.
