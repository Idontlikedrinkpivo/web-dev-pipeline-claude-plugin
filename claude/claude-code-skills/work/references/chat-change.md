# A change asked in chat outside a run

Read when the user asks in the chat for a change to code the pipeline built — «сделай поле необязательным»,
«убери предупреждение», «поправь текст на кнопке» — and no run of `work` is in progress, or the run has closed.

Such a change is still code on the iteration's branch, and the user will ship it with the rest. Without this
procedure it went from the executor straight into a commit and a push, with no review and no tests, four times in
one evening (ai-initiatives, 2026-10-06), until the user dictated the order themselves: review, then the tests on
the branch, then the merge. A unit of a plan gets that order from `work`; a change asked in chat gets the same
order, sized down.

## Size it first

| The change | Route |
|---|---|
| Small and settled: one screen element, a text, a validation rule, a field made optional, a log line — the documents already say it, or the user's words settle it and no document says otherwise | this procedure |
| It contradicts a document (SRS, OpenAPI, schema, architecture, screen spec) | `pipeline` → `references/decision-changes.md` first — the document fixed and committed — then this procedure |
| Larger: a new screen or operation, a change across areas, a migration over live rows, a new dependency | not a chat change: a plan change (`plan`, then `work`). Say so in one line and ask |

A small screen change needs no screen spec: in a project whose screens predate screen specs, the current screen
and the user's words are the spec for a change this size. A new screen still needs one.

## Steps

1. **Branch.** The open iteration's `iteration/<version>`. With no open iteration (the last one is merged), a
   branch `fix/<short-name>` from `main`; the user merges it, as an iteration.
2. **Executor.** Write a unit spec from the user's words — a goal sentence, the files, the scenario that proves
   it («поле «Отчество» пустое → форма сохраняется, в карточке прочерк») — grade it by
   `plan/references/complexity.md`, and dispatch the row `executor-catalog` names for that grade (`impl-ui` for a
   screen) with the worker packet. The session writes no code itself, as in a run.
3. **Review.** `code-review-unit` with that spec. At least one `review-medium` pass, whatever the grade: no plan
   graded this change and no batch is coming to catch it. Its verdict is honored as in a run (`work` → Step 5.4).
4. **Tests on the branch, before the commit.** The unit's own tests, then every test the change can break: the
   module's suite, and the e2e specs or UI test cases that cover the changed screen or operation (search the
   spec files and `documentation/ui/test-cases/` for the screen id, the operation, the old text). A red goes
   back to the executor, never into the commit. A suite that needs the test stand runs on it per the project's
   verify skill.
5. **Commit** the change alone with the trailer `Plan-Unit: <version>/chat-<n>` (`n` counts the iteration's chat
   changes from 1; `plan_state.py` lists the ones already made under `other`), so `code-review-full` maps it
   when it falls inside a run's range. On a `fix/` branch, stop here: the merge is the user's.

## The report

One line in the chat, always with both checks named:

```text
Готово: поле «Отчество» необязательное · коммит `4c2d8e1` · Ревью: COMMIT (review-medium) · тесты: модуль 14 ✓, e2e S-4 3 ✓
```

A check that did not run is named in that line with the reason — «тесты: e2e не запускались — стенд не поднят» —
never left out. The push stays the user's step, after the line.
