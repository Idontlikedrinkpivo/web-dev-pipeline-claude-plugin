# How a question is shown

Read before the first question of a stage — a grill round, a review
finding, a gate or a transition, a version, a format change, any choice
the user makes. Every stage asks the same way, so the user learns one
shape and never has to guess what a message wants from them. Older texts
point here as `grill-me` → "How a question is shown"; it is this file.

## The reader

A business or systems analyst, a junior one included. They must see what
the choice changes before they see a term. A question that opens with
`FR-2`, `UC-5`, «хранимые поля» or a skill's name is read as noise: in
one project the user answered «ничего не понял» four times running.

## The shape

1. **Title line** — `**Вопрос N. <что решаем, простыми словами>**`
   (a gate or a transition may drop the number).
2. **What a person will see, or what breaks — one sentence in plain
   words, with a concrete example**: an input and what comes out
   («файл «Отчёт.docx» скачается как «download»»), a screen and what is
   on it, an action and its result.
3. **Then the terms, in brackets or after a dash**, each with what it
   means for this choice: the id (`OQ-1` — открытый вопрос 1), the token
   (`Bearer` — вход по токену в заголовке), the skill (`doc-review` —
   несколько ревьюеров читают документ). Keep the real names; a term
   with no explanation is a failed question.
4. **Options**, each a letter and what it does to the product or the
   document: `A.`, `B.`, `C.` in the order the stage defines. The letters
   never move — the recommended option keeps its letter and gets
   «(рекомендую)» at the end of its line. Older texts write
   «(Recommended)»: same meaning, write the Russian one. When options can
   stand together, say the reply may name several letters.
5. **`Рекомендую X: <одно предложение почему>.`** Judged from what this
   stage just decided, not from habit. When nothing points either way,
   say so: any answer is fine.
6. **The last line, always:** `Ответьте сообщением: буква или свой текст.`

Then stop. The next question is a new message after the user answered.

```text
**Вопрос 1. Видит ли посетитель черновики в списке записей**

Сейчас посетитель видит и записи без статуса: черновик «Отчёт за май»
появится у него в списке, хотя автор его ещё не отправил. Правило на
будущее (`OQ-1` в `documentation/to-be/open-questions.md` — открытый
вопрос 1) предлагает такие записи скрыть.

  A. Оставить как сейчас — спецификация описывает сегодняшний код,
     черновики видны. (рекомендую)
  B. Записать правило на будущее — спецификация требует скрывать записи
     без статуса, код придётся поменять.

Рекомендую A: эта спецификация фиксирует текущий код, а правило на
будущее остаётся отдельным списком.

Ответьте сообщением: буква или свой текст.
```

## One question, one message, no card

- One question per message. Several open questions in one message dilute
  every answer; a question that depends on an unanswered one waits.
- No question card: `AskUserQuestion`, `AskQuestion`, `request_user_input`,
  `ask_question`, `ask_user` and any other picker are not used. A turn
  that opens one is a failed question, even with the chat block in the
  same turn. A picker the user closed without choosing chose nothing.
- A promise is not the question. «Выведу вопросы», «Формирую сообщение»,
  or a line written into a document, `open-questions.md` or a ledger does
  not show it.
- Never skip a question silently, and never paste the same block twice.

## Answers

- **No answer is not an answer.** A message about something else, a
  reply that fits none of the options, silence — nothing is decided.
  Never take the first option, the recommended one, or «what the user
  would probably pick»: say in one line that the question is still open,
  or, where the stage defines it, record the item as «позже» and change
  nothing (`upgrade-docs`).
- **An answer that fits no open question is not guessed.** A lone letter
  after its question was closed, or a letter two open questions both
  offer, gets one line back: which question it answers. Two branches run
  in one session put the branch into the letter («Б-A», «Д-A» —
  `references/branch-order.md`).
- The user's own text instead of a letter is an answer: restate in one
  line how you understood it before acting on it when it could be read
  two ways.
