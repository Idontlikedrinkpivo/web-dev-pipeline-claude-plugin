# Who runs the design

Read when an iteration opens on a product people use through screens, and
at the fork after the SRS. Who draws the mockups decides the rest of the
iteration's shape: whether the design branch runs in this session, in
someone else's, or waits for frames drawn by hand. So it is asked once, at
the start, and every later stage builds on the answer instead of guessing.

## When to ask

At the iteration's first stage, right after its version is fixed (`pipeline`
→ Service version), when the product faces a human on a screen: the frames
register exists, or the request, the business requirements or the SRS speak
of screens, pages or an interface. A product with no screens (an API, a
worker, a CLI) gets no question. When the opening stage cannot tell yet,
ask at the fork after the SRS, before the branch-order question — the
answer shapes its recommendation.

The frames register already says **Дизайн ведёт** — no question: one line
in the chat («Дизайн ведёт дизайнер в своей сессии плагина, как в реестре
кадров; поменялось — скажите») and go on.

## The question

One question per `grill-me` → "How a question is shown":

```text
**Вопрос. Кто ведёт дизайн в этой итерации**

От ответа зависит порядок работ: кто рисует макеты и пишет тест-кейсы и
ждёт ли бэкенд дизайн.

  A. Всё делаем сами — макеты рисует плагин в Figma, тест-кейсы тоже здесь.
  B. Отдельный дизайнер работает с плагином на своём компьютере — макеты (и
     тест-кейсы, если договоритесь) он ведёт сам в той же ветке итерации.
  C. Отдельный дизайнер рисует в Figma руками, без плагина — когда макеты
     будут готовы, плагин разметит их и проверит, всё ли нарисовано.

Ответьте сообщением: буква или свой текст.
```

Recommend what the user's earlier messages point to; with nothing to go on,
recommend none and say that any answer is fine. The answer holds for the
iteration and can change at any message («дизайнер ушёл, рисуем сами»).

## What follows from each answer

| | A. Сами | B. Дизайнер с плагином | C. Дизайнер без плагина |
|---|---|---|---|
| Fork after the SRS (`references/branch-order.md`) | the usual options and recommendation | recommend «только бэкенд»; the hand-over (`references/team.md`) follows at once | recommend «сначала бэкенд»; the design branch here starts when the user says the frames are ready |
| `ui-design` | in this session; its entry question offers only B and C (draw) | in the designer's session; it asks its own entry question | in this session, index mode: the entry question asks only for the link to the designer's file; completeness gaps are written as questions to the designer, ready to forward |
| Screen specs and test cases | in this session | one question per stage — the designer, an analyst, or this session (`references/team.md` → Handing over) | in this session, or handed over the same way |
| Meeting point (`docs-consistency`) | both branches done here | waits for each person's «готово и запушено» | both branches done here |

## Where the answer is kept

In the frames register header, **Дизайн ведёт:** `мы` | `дизайнер с
плагином` | `дизайнер без плагина`, written by the first session that has
both the answer and the register, and committed with it. Before the
register exists the answer lives in this session; a later session that
finds neither the field nor a register asks again. It is separate from
**Кадры рисует**, which says who draws the frames inside the design stage.
