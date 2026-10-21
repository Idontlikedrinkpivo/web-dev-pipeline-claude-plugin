# Readable documents

Every document the pipeline writes — requirements, schema, contract descriptions, architecture, screen specs, test
cases, the frames register, the deploy and operations documents — is read by people who scan before they read: an
analyst, a developer, a tester, an operator. The walls this file exists to prevent all look the same: one table
cell or one bullet holding five to fifteen facts joined by semicolons, a decision date in the middle of a rule, a
requirement that grew into a page. The rules keep every fact and change only where it sits.

## Rules

1. **A table cell is one fact** — one or two short sentences, about 300 characters at most. More than that is a
   short cell («подробно — ниже») and a subsection under the table with a list.
2. **A paragraph is at most four sentences.** A bullet is one fact.
3. **A run joined by «;» is a list.** A run of «for this case — that» (per actor, per state, per moment, per
   status, per error) is a table with one row per case.
4. **A sequence is a numbered list** — an order of checks, a procedure, steps an operator runs.
5. **The plain word first, the code name after it**: «идентификатор сессии (`SessionIdSource`)». Backticks only for
   what is literally in code, configuration or the interface.
6. **Each fact once, in its home**, pointed to by name from elsewhere — not restated.
7. **No history in the body.** Decision dates, review and audit finding ids, «было: …» go to the changelog row of
   the change. The body says what is true now. A changelog row is one or two sentences.
8. **Numbers and ids stay exact** — limits, sizes, ids are copied, never rounded into words.

The stage that owns a document may add its own shape on top (`openapi-spec-generator` → descriptions,
`clean-architecture-design` → writing); these rules hold under it.

## Example — a screen spec's «Экран» (room booking)

Not this — two bullets, each a run of cases:

```markdown
- **Акторы:** A-1 Резидент — смотрит расписание, открывает бронирование, отменяет свою бронь; A-2 Администратор — то же и видит, чья бронь, и отменяет любую (BR-3).
- **Фокус:** при входе — эл. 1; после закрытия M1 — эл. 5, из которого он открыт, а если бронь отменена — эл. 4 на её месте; после ошибки в M1 — текст ошибки в M1.
```

This — a row per case:

```markdown
**Акторы**

| Актор | Что может на этом экране |
|---|---|
| A-1 Резидент | смотрит расписание, открывает бронирование, отменяет свою бронь |
| A-2 Администратор | то же; видит, чья бронь, и отменяет любую (BR-3) |

**Фокус**

| Когда | Где фокус |
|---|---|
| при входе | эл. 1 |
| после закрытия M1 | эл. 5, из которого он открыт; если бронь отменена — эл. 4 на её месте |
| после ошибки в M1 | текст ошибки в M1 |
```

## Rewriting an existing document

Prove that nothing was lost: `python3 <this skill's folder>/scripts/facts_check.py snapshot <file> <snap.json>`
before, `… verify <file> <snap.json>` after. It compares the ids, the backticked names and the numbers of the body
(frontmatter and changelog left out) as multisets and lists every difference. A lost fact goes back; a duplicate
removed by rule 6 is named in the report. One document, one commit; meaning, numbers and ids do not change, so
the document's version does not either (SKILL.md → «(no row)»). A requirement that must be split to be readable
(an FR of a page) is a change of meaning — ask before splitting it.
