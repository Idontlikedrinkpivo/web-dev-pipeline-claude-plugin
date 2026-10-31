# Entry question

Read when `ui-design` starts with no frames register yet. It holds who is
asked what by the design owner, the question text, creating the file for
option C, and how the answer is recorded.

Ask once, per `grill-me` → "How a question is shown", in the chat, no
question card. The iteration's design owner (`pipeline` →
`references/design-owner.md`) decides which options are shown and which
mode follows:

| Design owner | Options shown | Mode |
|---|---|---|
| recorded nowhere (an iteration picked up from another session) | ask `pipeline` → `references/design-owner.md`'s question first, then go by its answer below | — |
| «мы» | B and C | **draw** |
| «дизайнер с плагином» | A, B and C — asked in the designer's session | by the answer |
| «дизайнер без плагина» | only A, in this session: the question is just the file link, because the designer draws in Figma on their own | **index**, once the frames are there |

A and B carry the file link, so this one message asks for it:

```text
**Вопрос 1. Есть ли уже макеты**

Макеты — это кадры экранов в Figma. От ответа зависит, рисую ли я их сам
или только описываю нарисованное дизайнером.

  A. Макеты уже нарисованы дизайнером — пришлите ссылку на файл. Я присвою
     экранам номера S-n, составлю реестр кадров и проверю, все ли сценарии
     и состояния нарисованы; пробелы станут вопросами дизайнеру.
  B. Макетов нет — пришлите ссылку на файл, где рисовать (пустой подойдёт).
     Я решу набор экранов по сценариям SRS и нарисую их. (рекомендую)
  C. Макетов нет и файла нет — я создам пустой файл в вашем Figma сам и
     нарисую в нём. Можно добавить ссылку на проект Figma, куда его
     положить; без неё файл ляжет в черновики (Drafts).

Рекомендую B: о готовых макетах в разговоре речи не было, а сценарии SRS
уже есть.

Ответьте сообщением: буква и ссылка на figma.com (для C — не обязательна).
```

Recommend the option the user's earlier messages point to. A reply A or B
with no `figma.com` link writes nothing: ask for the link again, because
frames that cannot be opened cannot be drawn or indexed.

**C — creating the file.** Figma MCP `whoami` gives the user's plans (one
is used as is; several are one question), then `create_new_file`:
`editorType: "design"`, the plan's `key`, `fileName` «<продукт> — макеты»,
the `projectId` from a project link if given. Post the link, record it and
the `fileKey` in the register header, go on as B. Say in one line that a
Drafts file is visible only to its owner and can be moved to the team's
project (the link stays). No Figma MCP or a failed call: say why, ask for
a link (B).

Record the answer as **Кадры рисует:** `ui-design` (B, **draw**) or
`дизайнер` (A, **index**), with **Дизайн ведёт** when known, in the register
header; a later run reads it and asks neither question again.

The answer and the file disagree — they chose A and the file has no product
frames, or chose B and the file already holds frames for these screens —
stop and say so. Do not pick a mode they did not pick.
