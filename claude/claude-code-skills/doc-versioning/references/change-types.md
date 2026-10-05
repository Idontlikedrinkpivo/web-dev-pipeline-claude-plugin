# Change types by document

Read when typing a change at the stamp (`SKILL.md` → What a version is), and
when `doc-review` or `docs-consistency` checks a row's `Тип`. The criterion
is in `SKILL.md`; this file holds the examples per document.

## No row — not a change of the contract

Explaining an existing cited token is not a version. The token is the same
token. This is the same rule on architecture, OpenAPI, and DB schema:

| Document | no row (same token, new explanation) |
|---|---|
| Architecture | prose, rationale, or comment on an existing entity, port, invariant row, assumption `A-n`, or file-tree entry |
| OpenAPI | `description`, `summary`, `title`, or `example` on an existing operation, parameter, or schema property |
| DB schema | `Note`, `note:`, or `COMMENT ON` on an existing table or column |

Also no row everywhere: formatting, heading polish, whitespace; a typo that
does not change the meaning of a cited rule; restating a decision already
in this document or its pinned source.

## «уточняет» — recorded wording, same contract

- Rephrasing an FR / NFR / UC so it reads clearer, Given/When/Then unchanged
- Expanding a Why or a non-normative example next to a rule that already bound

## «ломает» and «добавляет» — the contract moved

| Document | ломает (not exhaustive) | добавляет (not exhaustive) |
|---|---|---|
| SRS | an FR, NFR, BR, UC or AC removed or changed in meaning; an actor's rights narrowed; a security decision changed | a new FR, NFR, BR, UC or AC; a new actor |
| Architecture foundation | a module, port signature, store, external system, stack choice or assumption `A-n` changed or removed | a new module, port, adapter, external system or assumption |
| Domain model | an entity's states, an invariant row or a named error changed or removed | a new entity, value object, state, invariant row or named error |
| Scenarios | a use case removed; a port or operation it calls, its outcome or its errors changed | a new use case |
| Screen spec | an element removed; an operation or field it cites, a state or a response outcome changed | a new element, state or response outcome |
| OpenAPI | an `operationId`, path, method, schema name or property type changed or removed; a property made required; a status's meaning changed | a new operation, schema, optional property or response status |
| DB schema | a table, column, type, FK, CHECK / UNIQUE changed or removed; a column made NOT NULL | a new table, a nullable or defaulted column, an index |

A comment on one of those is no row. A removal is always «ломает».
