---
name: grill-me
description: >-
  A round-by-round interview that stress-tests an existing requirements
  draft, SRS, plan or design until no silent assumption is left,
  then writes the agreed reversals into that document. Use when the user
  asks to grill, допросить требования, выжечь допущения or stress-test a
  draft, and when `brainstorm` or `srs-writer` offer it as their
  gate. Not for writing documents, persona review (`doc-review`), inventing
  a subject to grill, or implementation.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it. Ask every question in Russian. Do not translate cited tokens when you quote them.

**Do not touch `open-questions.md`.** At any path, that file holds open questions and nothing else. This skill does not create it, append to it, or edit a heading in it. A grill round, `Гриль закрыт?`, and `ответьте в чате` do not belong there. Replacing one such heading with another is still an edit: leave the file alone. Questions go in the chat. The ledger is only `${TMPDIR:-/tmp}/grill-<repo>-<doc-slug>.md` (see the ledger rule below). Reversals, after the user confirms the close, go into the subject document.

**One question per message, in the chat, including later rounds and the close.** The message is one `**Вопрос N.**` block: what is decided, what each option does, the recommendation. Then stop. The user answers by sending a message. Do not call `AskQuestion` or any other question card (`AskUserQuestion`, `request_user_input`, `ask_question`, `ask_user`). A card, «Asking questions», or a file edit is a failed question.

Prefer an existing artifact as the subject: a `brainstorm` Product Contract, a requirements draft, or a stated plan. Do not invent a new product to grill.

## When a pipeline stage invoked this file

`brainstorm` and `srs-writer` invoke this as their **exit gate**: the document is already written, and the grill runs before it is handed downstream. Three rules follow from that:

- **The subject is what that stage decided**, not the whole product again. Grilling an SRS means its NFRs, invariants, flows, and exception paths — the product decisions that arrived already grilled with the business requirements stay off the frontier unless this document contradicts them. An SRS made from a ticket, a note, or a chat paste had no business-requirements grill: its product decisions are on the frontier too.
- **An empty frontier on the first round is a pass — shown, not asserted.** A stage that settled nothing new — an increment touching one requirement — ends the session in one turn. A bare "nothing to ask" cannot be told apart from a lazy skip, so before declaring it, walk the document once against these branches, limited to this stage's subject, and mark each Clear / Partial / Missing: actors and roles; scope in/out; data and lifecycle (states, uniqueness, deletion); flows including error, empty, and concurrent cases; non-functional bounds (numbers, not adjectives); security and access; external dependencies and their failure modes; terminology; testability of acceptance criteria. A Partial or Missing branch that would change the document is a frontier question. The empty-frontier close lists each branch in one line (`Clear — <why>`). Do not manufacture questions for Clear branches; a fabricated frontier trains the user to skip the gate.
- **The reversals land in that document, in place.** A decision this grill overturned replaces the line it contradicts; it never sits beside it. When the reversal contradicts an *upstream* document, name that instead of silently editing it. The contradiction is the user's call; when the user rules that the upstream document changes, that is a changed decision for it, landed and committed at once with no version change (`pipeline` → `references/decision-changes.md`). This grill does not stamp either document: both stay on the last committed version. A number moves only in the commit that contains that file.

The invoking stage then records `grilled: YYYY-MM-DD` on a business-requirements document. An SRS has no `grilled:` field; the gate on an SRS closes in the report and does not touch the header. Setting `grilled:` does not change `version` and does not add a changelog row.

## When the user invoked this directly

No stage is waiting to finish the job, so this file does it after the user confirms the close (the `Гриль закрыт?` question, last section):

1. **Subject is a file** — apply the reversals from the ledger to it, in place, with the same rules as above: replace the contradicted line, name an upstream contradiction instead of editing upstream, do not touch `version`, add no changelog row.
2. **The file is a business-requirements document** — set `grilled:` to today yourself. An SRS gets no `grilled:`, `reviewed:`, `status`, or `sources`. On any other document leave `grilled:` out, because there it would read as a gate that failed.
3. **Subject lives only in the chat** — there is nothing to write; list the settled decisions from the ledger in the chat as the result.
4. **On one of those two documents** — read `pipeline` and ask about the next unrun transition in that stage's row, per "Asking before a transition". Otherwise end with the result: on any other document `grill-me` is not a gate in the chain, so there is no row to continue.

Work the tree one question at a time. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the first of them. Stop. The next frontier question waits for the user's message.

### How a question is shown

The reader is a business or systems analyst, including a junior one. They
must be able to see what the choice changes. Use the real terms (`OQ-1`,
`Bearer`, `to-be`, a file name, an id). In the same place, say what that
term means for this choice.

One question. One message. No card. `AskQuestion` and the other harness
pickers (`AskUserQuestion`, `request_user_input`, `ask_question`,
`ask_user`) are not used. The user answers by sending a message: a
letter, or their own text. A turn that opens a question card is a failed
question, even when the chat block is in the same turn.

A promise is not the question. «Выведу вопросы», «Формирую полное
сообщение», «Asking questions», or a note that `q6` is already in the
ledger does not show it. Writing it into the document,
`open-questions.md`, or the ledger does not show it either.

Russian. State what is being decided, what each option does to the
product or the document, and which option you recommend, with one
sentence why. A term without that explanation is a failed question.
Several options that can stand together are still one question: say the
reply may name more than one letter. Then stop.

```
**Вопрос 1. Какое поведение записывать в спецификацию**

Спецификация сейчас описывает, как программа работает сегодня.
В `documentation/to-be/open-questions.md` лежат уже принятые правила
на будущее. `OQ-1` — открытый вопрос 1: посетителю видны записи без
статуса. `Bearer` — способ входа по токену в заголовке запроса.

- **A. Оставить текущее поведение.** В спецификацию попадает то, что
  код делает сейчас. Правила из to-be в требования не входят.
- **B. Записать принятые правила.** Спецификация описывает to-be, а не
  сегодняшний код.

Рекомендую A: эта спецификация фиксирует текущий код, а to-be остаётся
отдельным списком.

Ответьте сообщением: буква или свой текст.
```

Never skip the question silently. Do not paste the same block twice.
The next question is a new message after the user has answered.

The user's message reshapes the tree: a settled decision pushes the frontier outward and unblocks the question that depended on it. Ask that next question the same way. A question whose answer depends on one still unanswered belongs later, not in this message.

After each round, append the settled answers to `${TMPDIR:-/tmp}/grill-<repo>-<doc-slug>.md` — `<repo>` is the repo folder name, `<doc-slug>` the document's path under `documentation/` without the extension, slashes as dashes (`requirements-srs-srs`, `plans-1.1.0-plan`); file names alone (`srs.md`, `plan.md`) repeat across projects and versions, and a stale ledger would silently skip questions (subject only in the chat: `grill-chat-<topic-slug>.md`, slug fixed on round 1), one line per decision: `Раунд N · qK · <decision> · reverses <id or —>`. A long session can be compacted or cut off before the close, and answers held only in context are lost with it. At the close, apply reversals from this ledger, not from memory. A resumed or compacted session reads the ledger before recomputing the frontier and never re-asks a logged decision.

The open-questions ban at the top of this file still holds on later rounds. Do not "repair" a grill heading already in `open-questions.md`. Leave that file untouched.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch `code-explorer` through `executor-catalog` (`subagent_type: "code-explorer"`, no `model` — the agent file holds it); don't ask the user for anything you could look up yourself. Follow the catalog dispatch contract: not `Explore` or `general-purpose`, and a missing agent is a stop with `install.sh`. Don't block on it: a running exploration is an unsettled prerequisite, so a question that does not depend on it is asked now, and the one that does waits. The _decisions_ are the user's: one per message, then wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. That holds on the first round too — an empty first frontier is a pass, not a skip, so never invent questions to look thorough. Do not act on it until the user confirms you have reached a shared understanding.

The close is a question too. One message, this block, then stop. A file edit is not the question. Do not write it into the subject document or the ledger, and do not touch `open-questions.md`. Do not open a card.

```
**Гриль закрыт?**

Фронтир пуст: нерешённых веток не осталось. Подтверждение записывает
согласованные правки в документ и закрывает гейт. Отказ возвращает
ещё один раунд вопросов, и те вопросы тоже будут в чате.

- **A. Да — общее понимание.** Правки вносятся, гейт закрывается.
- **B. Нет — ещё вопросы.** Гриль продолжается.

Рекомендую A: развилки этого этапа закрыты.

Ответьте сообщением: буква или свой текст.
```

A close that is only a card is a failed close. When a pipeline stage invoked this file, "act on it" means apply the reversals to that stage's document and close its gate; on a direct call, it means the steps in "When the user invoked this directly". Neither happens before the user's message.
