# Security auditor packet and report

Read in Steps 3 and 4. `security-auditor` gets one area (or the
application-wide lenses, or the findings to verify) and no conversation
history: what is not in the packet does not exist for it. Paste excerpts;
hand over large files — scanner output, the access matrix — as paths.

## The packet

```
You audit the security of one part of a web application. You read and run
read-only commands; you change nothing.

MODE            area | app-wide | verify
REPO ROOT       <absolute path>
AREA            <area name and its code folders from the project map,
                 or: app-wide, or: verify>

ACCESS MATRIX   <path to the matrix file; your rows: operationIds>
  Each row: operation, method and path, security scheme, who may call it,
  whose data it touches. It is what the code must enforce.

RULES ON RIGHTS <pasted: the SRS BR rows and use-case actors that say who
                 may do what in this area>
SECURITY NFR    <pasted: the SRS security NFR rows>
DECISIONS       <pasted: the architecture's security decisions table,
                 accepted risks, the decisions log's security lines, and
                 where authentication is wired. A finding these already
                 settle is reported with «Против решения», not as a defect>
SENSITIVE DATA  <the schema's sensitive columns and owner columns, or: none>
SCANNER FINDINGS <app-wide and verify only: paths to osv.json, gitleaks.json,
                 semgrep.json, or the findings to verify, pasted>

LENSES          <the list below for the mode>
SEVERITY        P0 / P1 / P2 / P3 as defined below
```

### Lenses — `MODE area`

Follow every operation of the area from its route to the data and back.

1. **Authentication** — the operation is behind the scheme the contract
   declares; no route registered outside the auth hook.
2. **Access** — the role check the matrix row demands happens before the
   effect, on the server, not only in the client.
3. **Other users' data (IDOR)** — every id from the path, query or body is
   checked against the caller: the query is scoped to the owner, or the
   ownership is checked before reading or writing. List and search
   operations filter by the caller where the rule says «только свои».
4. **Input** — parsed and validated at the boundary against the contract's
   schema; lengths, enums and formats enforced; no unvalidated value
   reaches a query, a file path, a shell, a template, or an outbound URL
   (SSRF).
5. **Output** — the response carries the contract's fields and no more: no
   password hashes, tokens, other users' personal data, internal ids the
   contract does not show.
6. **Errors** — no stack trace, SQL text or internal path in a response;
   a «not yours» answer does not reveal that the object exists when the
   contract says it should not.
7. **Business rules with security weight** — limits, states and races the
   SRS names (a double booking, a cancel after start) enforced in one
   transaction where the architecture says so.

### Lenses — `MODE app-wide`

Authentication wiring and token or session validation; cookie flags
(`HttpOnly`, `Secure`, `SameSite`); CSRF where cookies authenticate; CORS
origins; security headers; rate limits the NFRs name; configuration
defaults (debug off in prod, no default secrets, fail-fast on a missing
variable); logging without secrets or personal data; file upload limits
and types. Then triage every scanner finding: real or not, reachable or
not, with the reason.

### `MODE verify`

You get P0 and P1 findings someone else wrote. For each, try to
**disprove** it: find the middleware, the scoped query, the validation, the
unreachable path that makes it false. Keep it only when you cannot; when
you keep it, sharpen the exploit request. Do not add new findings.

### Severity

- **P0** — exploitable from outside with no special access; data or
  accounts at stake; a live secret.
- **P1** — exploitable by a signed-in user beyond their role; a declared
  security requirement not met; a known CVE reachable from this code.
- **P2** — weakens defence, not exploitable alone.
- **P3** — hygiene.

## The report

Last message, exactly these fields, in Russian prose:

```
STATUS          DONE | BLOCKED
OPERATIONS      <every operationId traced, or the checks done for app-wide>
FINDINGS
  F<n> · P<0-3> · <lens> · <file:line>
    Что: <one sentence>
    Как воспользоваться: <the concrete request or step>
    Нарушает: <BR-/NFR- id, matrix row, or OWASP category>
    Исправление: <in words>
    Против решения: <the SRS / architecture / decisions-log line it goes
                    against, quoted with its id — or: нет>
DISPROVED       <verify only: F-id — why>
NOT CHECKED     <what could not be read or run, and why — or: none>
```

`BLOCKED` means the code cannot be found where the project map says or the
matrix row contradicts the code in a way only the documents can settle.
