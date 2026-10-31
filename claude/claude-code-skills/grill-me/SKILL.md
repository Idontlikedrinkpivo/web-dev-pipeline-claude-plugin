---
name: grill-me
description: >-
  Interview, one question at a time, that stress-tests a requirements draft, SRS, plan or design until no silent
  assumption is left. Use for «допроси меня», «выжги допущения», «проверь мои допущения». Critique: doc-review.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it. Ask every question in Russian. Do not translate cited tokens when you quote them.

Every question — each round and the close — is shown as "How a question is shown" says.

Prefer an existing artifact as the subject: a `brainstorm` Product Contract, a requirements draft, or a stated plan. Do not invent a new product to grill.

## When a pipeline stage invoked this file

`brainstorm` and `srs-writer` invoke this as their **exit gate**: the document is already written, and the grill runs before it is handed downstream. Three rules follow from that:

- **The subject is what that stage decided**, not the whole product again. Grilling an SRS means its NFRs, invariants, flows, and exception paths — the product decisions that arrived already grilled with the business requirements stay off the frontier unless this document contradicts them. An SRS made from a ticket, a note, or a chat paste had no business-requirements grill: its product decisions are on the frontier too.
- **An empty frontier on the first round is a pass — shown, not asserted.** A stage that settled nothing new — an increment touching one requirement — ends the session in one turn. A bare "nothing to ask" cannot be told apart from a lazy skip, so before declaring it, walk the document once against these branches, limited to this stage's subject, and mark each Clear / Partial / Missing: actors and roles; scope in/out; data and lifecycle (states, uniqueness, deletion); flows including error, empty, and concurrent cases; non-functional bounds (numbers, not adjectives); security and access; external dependencies and their failure modes; terminology; testability of acceptance criteria. A Partial or Missing branch that would change the document is a frontier question. The empty-frontier close lists each branch in one line (`Clear — <why>`). Do not manufacture questions for Clear branches; a fabricated frontier trains the user to skip the gate.
- **The reversals land in that document, in place, once — at the close.** This rule's home is here; `brainstorm` and `srs-writer` cite it. The invoking stage applies the whole ledger after the user confirms the close: one pass, not one per round. A decision this grill overturned replaces the line it contradicts; it never sits beside it. When the reversal contradicts an *upstream* document, name that instead of silently editing it. The contradiction is the user's call; when the user rules that the upstream document changes, that is a changed decision for it, landed and committed at once with no version change (`pipeline` → `references/decision-changes.md`). This grill does not stamp either document: both stay on the last committed version. A number moves only in the commit that contains that file.

The invoking stage then records `grilled: YYYY-MM-DD` on a business-requirements document. An SRS has no `grilled:` field; the gate on an SRS closes in the report and does not touch the header. Setting `grilled:` does not change `version` and does not add a changelog row.

## When the user invoked this directly

No stage is waiting to finish the job, so this file does it after the user confirms the close (the `Гриль закрыт?` question, "The close"). The session does not type a contract document: each one keeps its writer, who keeps the template's shape and the ids other documents cite.

1. **Subject is a file** — apply the reversals from the ledger to it, in place, with the same rules as above (replace the contradicted line, name an upstream contradiction instead of editing upstream, do not touch `version`, add no changelog row), through its writer:
   - an SRS — `srs-author`, `MODE grill-reversal`, the reversals in `REVERSALS` and the deferred questions in `DEFERRED` (`srs-writer` → Grill reversals);
   - another contract document or a plan — `doc-typist`, `MODE revise`, one `SETTLEMENT` line per reversal (`executor-catalog` → Nesting, `references/doc-typist-prompt.md`);
   - a business-requirements document — the session edits it, as `brainstorm` writes it.
   Resolve the row through `executor-catalog` and dispatch it by name; a missing agent is a stop (the user installs or updates the `dev-pipeline` plugin). Read the file back: every reversal landed, nothing else moved.
2. **The file is a business-requirements document** — set `grilled:` to today yourself. An SRS gets no `grilled:`, `reviewed:`, `status`, or `sources`. On any other document leave `grilled:` out, because there it would read as a gate that failed.
3. **Commit it** at once, as a changed decision is committed (`pipeline` → `references/decision-changes.md`, step 5): that document and its `open-questions.md` only, on the iteration's branch, opened first when none is (`pipeline` → Service version). A plan is out of git: nothing to commit. A contract document is not stamped here; its stage's next stamp types the change (`doc-versioning` → Commits that are not stamps).
4. **Subject lives only in the chat** — there is nothing to write; list the settled decisions from the ledger in the chat as the result.
5. **On a business-requirements document or an SRS** — read `pipeline` and ask about the next unrun transition in that stage's row, per "Asking before a transition". Otherwise end with the result: on any other document `grill-me` is not a gate in the chain, so there is no row to continue.

## Working the tree

Work the tree one question at a time. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the first of them. Stop. The next frontier question waits for the user's message.

The user's message reshapes the tree: a settled decision pushes the frontier outward and unblocks the question that depended on it. Ask that next question the same way. A question whose answer depends on one still unanswered belongs later, not in this message. A reply that answers nothing is no decision (`pipeline` → `references/question-format.md` → Answers); «потом», «отложим» on a question is a **deferred** decision — logged as such, never settled for the user.

### How a question is shown

As `pipeline` → `references/question-format.md` says — read it before the first round: what a person will see, with an example, first; the terms after it, each explained; the options with fixed letters; «Рекомендую …: почему»; «Ответьте сообщением: буква или свой текст.»; one question per message; no question card. In a grill a question is one decision: several options that can stand together are still one question, and the reply may name more than one letter.

## The ledger

Answers held only in context are lost with a compaction or a cut-off session, so every round goes to a file outside the repo, kept by `scripts/ledger.py`, run from the project's root (`L` below is `python3 "${CLAUDE_SKILL_DIR}/../grill-me/scripts/ledger.py"` — the path holds when another stage loaded this file; the script's docstring holds the file's name and header):

- **Before round 1, and first thing in a resumed or compacted session:** `L open --kind grill --doc <document's main file>` — subject only in the chat: `--chat <topic-slug>`, slug fixed on round 1. `state: resumed` or `changed` prints the logged lines: read them before recomputing the frontier and never re-ask a logged decision. `changed` means the document moved under the grill (a decision changed elsewhere): keep the decisions and re-check the frontier against the new text. `restarted` means the old ledger was a past iteration's grill, now deleted: round 1.
- **After each round:** `L add <the same selector> "<line>"`, one line per decision: `Раунд N · qK · <decision> · reverses <id or —>`, or `Раунд N · qK · отложено · <the question in one line>`.
- **At the close,** apply reversals from `L show …`, not from memory, then `L close …` once they landed — a ledger left behind is read by the next grill of the same document as its own.

**Do not touch `open-questions.md` before the close.** At any path, that file holds open questions and nothing else, and a round in progress has none yet. Do not create it, append to it, or edit a heading in it during the rounds — not to show a question, not to "repair" a grill heading already there. A grill round, `Гриль закрыт?`, and `ответьте в чате` never belong there. **At the close**, each deferred decision in the ledger becomes one row in `open-questions.md` beside the document (`doc-versioning` → Открытые вопросы), class `Отложено`, with the source `(допрос, YYYY-MM-DD)` — written by whoever applies the reversals, in the same pass, so a deferred question is kept rather than lost with the ledger.

## Facts

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch `code-explorer` through `executor-catalog` (`subagent_type: "dev-pipeline:code-explorer"`, no `model` — the agent file holds it); don't ask the user for anything you could look up yourself. Follow the catalog dispatch contract: not `Explore` or `general-purpose`, and a missing agent is a stop — the user installs or updates the `dev-pipeline` plugin. Don't block on it: a running exploration is an unsettled prerequisite, so a question that does not depend on it is asked now, and the one that does waits. The _decisions_ are the user's: one per message, then wait.

## The close

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. That holds on the first round too — an empty first frontier is a pass, not a skip, so never invent questions to look thorough. Do not act on it until the user confirms you have reached a shared understanding.

The close is a question too, shown the same way: this block, then stop.

```
**Гриль закрыт?**

Нерешённых вопросов не осталось: всё, что меняет документ, решено с вами.
Подтверждение записывает согласованные правки в документ и закрывает
проверку; отложенные вопросы уходят в open-questions.md рядом с ним.
Отказ возвращает ещё один раунд вопросов, и те вопросы тоже будут в чате.

  A. Да — общее понимание. Правки вносятся, проверка закрыта. (рекомендую)
  B. Нет — ещё вопросы. Допрос продолжается.

Рекомендую A: развилки этого этапа закрыты.

Ответьте сообщением: буква или свой текст.
```

When a pipeline stage invoked this file, "act on it" means the stage applies the reversals and the deferred rows to its document and closes its gate; on a direct call, it means the steps in "When the user invoked this directly". Neither happens before the user's message.
