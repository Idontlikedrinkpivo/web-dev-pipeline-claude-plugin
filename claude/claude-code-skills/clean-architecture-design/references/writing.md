# Writing the architecture so people can read it

The general rules for every document are `doc-versioning` → `references/readable.md`; this file is how they apply
to the architecture. The foundation, the domain model and the scenarios are read by developers, reviewers and the
agents that build from them — and every one of them scans before reading. A table cell that holds a whole mechanism, a paragraph of
twelve clauses joined by semicolons, a decision date in the middle of a rule: each is correct and unreadable. The
rules below keep every fact and change only where it sits.

## Rules

1. **A table cell is one fact** — one or two short sentences, about 300 characters at most. A decision that needs
   more gets a short cell (the decision in a phrase, «подробно — ниже») and a `####` subsection under the table
   with a list: one fact per line, a bold lead word, the detail after a dash.
2. **A paragraph is at most four sentences.** A mechanism — an order of checks, a sequence of calls, what happens
   on a failure — is a numbered list; independent facts are a bulleted one.
3. **The plain word first, the code name after it**: «идентификатор сессии (`SessionIdSource`)», not a run of
   identifiers. Backticks only for what is literally in the code or the configuration.
4. **Each fact once, in its home.** A port's signature lives in §4, a file path in §5, a rule in the domain
   model's invariant table; §1 and the scenarios point there by name, they do not restate it.
5. **No history in the body.** Decision dates («решение 2026-10-06»), review and audit finding ids, «было: …» —
   go to the changelog row of the change, not into the rule. The body says what is true now.
6. **Numbers stay exact** — limits, sizes, timeouts are copied, never rounded into words.

## Example — a security decision (room booking)

Not this — a mechanism in a cell (the sample's foundation, as written):

```markdown
| NFR-3 | аутентификация | onRequest-хук `src/shared/providers/auth/sso-auth.ts` проверяет Bearer JWT библиотекой `jose` по JWKS издателя (`OIDC_ISSUER_URL`, discovery), проверяет `iss`, `aud` = `OIDC_AUDIENCE`, `exp`; claim `role=admin` → роль Admin, иначе Resident; сессий и refresh у нас нет — их держит SSO; все маршруты кроме `/healthz`; нет или недействителен токен → 401 |
```

This — the decision in the cell, the mechanism below, every fact kept:

```markdown
| NFR-3 | Аутентификация | Вход только через SSO коворкинга: портал проверяет его токен на каждом запросе и своей сессии не держит. Подробно — ниже |

#### Аутентификация (NFR-3)

- **Где проверяется** — хук на каждом запросе (`src/shared/providers/auth/sso-auth.ts`), на всех маршрутах, кроме `/healthz`.
- **Что проверяется** — Bearer JWT библиотекой `jose` по ключам издателя (`OIDC_ISSUER_URL`, discovery): подпись, `iss`, `aud` = `OIDC_AUDIENCE`, `exp`.
- **Роль** — claim `role=admin` → администратор, иначе резидент.
- **Сессии** — своих нет, и refresh тоже: их держит SSO.
- **Отказ** — нет токена или он недействителен → 401.
```

## Checking a rewrite

When an existing document is rewritten for readability, prove that nothing was lost:
`python3 <doc-versioning skill folder>/scripts/facts_check.py snapshot <file> <snapshot.json>` before,
`python3 <…>/facts_check.py verify <file> <snapshot.json>` after. It compares the requirement ids, the backticked
names and the numbers of the body (the changelog left out) as multisets and lists every difference; a lost fact
goes back, a duplicate that rule 4 removed is named in the report.
