# Code audit — the project against the plugin's rules

Read when the user asks «проведи аудит кода», «проверь код на соответствие плагину», «нужно ли переписывать», or
after `upgrade-docs` wrote the document set as it is. The set says what the system is; the audit says where that
differs from how the plugin builds systems — in the code and in the technical decisions the documents record —
and what fixing it would take. The user decides every item; nothing is changed by the audit itself. The point is
that the user hears everything: each deviation, the rule, the fix, its cost and its risk.

Format is not audited — headings, tables, wording, file layout are `upgrade-docs`. The audit judges decisions:
layering, where a rule lives, ports, transactions, keys and constraints, exposed ids, migration safety, one
operation per use case, the error format, statuses, paging, the security model, what the stack skills forbid or
require. Security in depth stays `security-audit`'s.

## Before

- **The documents.** With the architecture written (by its stage or as it is), the audit knows the modules and can
  judge the documents too. Without it, say so: the audit can judge the code alone, but a fix or a rewrite is made
  by the documents — recommend `upgrade-docs` (the set as it is) first, one question.
- The working tree is clean; the audit reads and runs only read-only commands, so no branch is needed yet.

## Steps

1. **Tool results.** Run the project's own `lint`, `typecheck` and `test`, and the quality tools that are
   installed (knip, jscpd, dependency-cruiser, import-linter, ruff, mypy); save each output under
   `$(git rev-parse --git-dir)/pipeline-work/audit-<YYYY-MM-DD>/`. A tool that is not installed is named in the
   report, never installed by the audit.
2. **Scopes.** One per module — the areas of architecture §2 and their folders in §5; without an architecture, the
   top-level source folders (each backend module, the frontend, the shared code). A module over ~40 source files
   splits by its sub-folders. Plus one **documents** scope when the architecture, the schema or the API exist.
3. **Dispatch** `code-auditor` (`executor-catalog`) once per scope, in parallel, with the packet in
   `references/auditor-prompt.md`; write the row line first (`code-auditor | dev-pipeline:code-auditor`). The
   accepted deviations and risks of architecture §1 go into every packet, so nothing accepted comes back. Post one
   chat line as each scope returns («Аудит: 3 из 7 модулей»).
4. **Merge** the findings into decisions: the same rule broken in many places is one decision with every
   occurrence; ids `A1…An` by severity, then in the module order of step 2, then by the smallest `file:line` of
   its occurrences — the questions follow the ids. A decision several scopes found takes the highest severity they
   gave and sorts under the first of them in step 2's order. A decision that a pending `upgrade-code` change makes
   (the service endpoints are `devops-ready`, the gates `quality-gates`, the contract test `contract-test`) gets no
   A-id: it is listed under that change's name, and its question is the change's, asked in the queue, not twice. A
   finding that mixes a change's part with another rule is split: the change's part under the change, the rest a
   decision of its own. For each decision: the module(s), «сейчас», the rule, «как должно быть»,
   what it changes — documents, code, the API (a breaking change for its callers?), the data (a migration?) —,
   whether behaviour changes, and the cost in plan units with their grade (`plan` → the complexity cascade, as an
   estimate). For each module: its findings by severity, the auditor's verdict, and the share of its files they
   touch.
5. **The report** `documentation/plans/code-audit-<YYYY-MM-DD>.md` (out of git, like every working file of
   `plans/`), in Russian:
   - «Итог» — findings P0–P3, the modules with a suggested verdict, the total cost;
   - «Модули» — a table: модуль · P0 · P1 · P2 · P3 · вывод · цена · риск;
   - «Решения» — each `A<n>`: сейчас → как должно быть (правило), что затронет, поведение, цена, риск;
   - «Сделано намеренно» — decisions the documents record that differ from the rules;
   - «Не проверено» and «Инструменты» (what ran, what was missing).
6. **Tell the user everything**, in plain words, in one message: the totals, each module's verdict with its cost
   and risk, the P0 and P1 decisions by name, and the report's path. No item is left out because it looks small:
   the P2/P3 count is said too.
7. **Ask, one question per message** (`pipeline` → `references/question-format.md`):
   - each P0 and P1 decision: `A. Исправить — сначала документ, потом код`, `B. Оставить как принятое отклонение`
     (the user's reason is recorded), `C. Позже`;
   - each scope's P2/P3 together, the documents scope too: `A. Исправить вместе`, `B. Оставить`, `C. Позже`;
   - each module whose verdict is «переписать заново»: `A. Переписать заново`, `B. Поправить на месте`,
     `C. Оставить как есть` — with what a rewrite costs and what it risks (behaviour the tests do not pin).
   A non-answer counts as C: nothing is recorded. A recommendation comes from the evidence: a P0 is fixed; a rule the documents decided on
   purpose is offered as B.
8. **Make what was chosen**:
   - **Оставить** — a row of architecture §1 «Принятые отклонения» (rule, where, the user's reason, date), through
     `pipeline` → `references/decision-changes.md`, committed — on an open iteration's branch, with none on
     `chore/plugin-<installed version>` (`upgrade-code` → Steps 3). Later audits and reviews skip it. With no
     architecture yet, the row goes to the `accepted` list of `documentation/.dev-pipeline.json` (committed, so
     another machine sees it) as `{"id": "A<n>", "audit": "code-audit-<date>.md", "rule": "<skill → rule>",
     "where": ["<file or document>"], "reason": "<the user's words>", "date": "<YYYY-MM-DD>"}`, and the
     architecture's first writing — by its stage or as it is — moves it to §1. An open question of an as-is
     document that this answer settles is closed in the same commit: the row leaves `open-questions.md`, its
     answer lives in the accepted row.
   - **Исправить** — open the next iteration first (`pipeline` → Service version: the level from how each
     revision will be typed — a fix or «уточняет» is PATCH, a «добавляет» or a «ломает» for the API's callers is
     MINOR; `plan` re-checks it from the diff), so everything lands on its branch. A chosen fix that needs part of
     another decision the user left for later says so in that decision's question, and carries that part in its
     own documents and plan; the rest stays as answered. Then the documents: each decision a design document states changes there to «как должно
     быть», through `references/decision-changes.md` (a `doc-typist` `MODE revise`), with the stage's review
     offered, committed. Then the code: `plan` `MODE fix` over the chosen rows (`code-audit-<date>.md A<n>`), then
     `plan-review` and `work` as usual.
   - **Переписать заново** — the same, the module's documents revised first; the plan's units start with
     characterization tests that pin what the module does now, then rebuild it by the documents, and remove the old
     code last; behaviour changes only where the revised documents say. A rewrite of the whole project is its own
     iteration — say its scale before the plan.
   - **Позже** — nothing recorded; the report stays for the next run.
9. **Report**: what was decided per item, the commits, the iteration opened, the next step (`plan`).

## Rules

- Read-only until the answers: the audit changes no code and no document.
- Every item reaches the user with its cost and risk; nothing is fixed silently, nothing is hidden as minor.
- Code follows the documents: a fix that changes a design decision changes the document first.
- An accepted deviation is never raised again.
