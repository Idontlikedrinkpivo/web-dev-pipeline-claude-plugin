# NFR decisions in foundation §1

Read this when writing foundation §1 «Решения по безопасности» or
«Решения по NFR».
Both tables turn an SRS §4 requirement into a design decision. Neither
decides that a requirement exists — that is the SRS's job.

## Security decisions — mandatory, always

Turn each applicable sub-item of the input's Security NFR checklist (an
SRS's `NFR-*` Security sub-items, or an equivalent stated by the user)
into one concrete decision, not a restatement of the requirement.

The **NFR-ID** cell is copied from the SRS that `srs-writer` produced:
`documentation/requirements/srs/srs.md`, section 4, id `NFR-<n>`.
That file is listed in `sources`. Do not write `(to-be)`, `(as-is)`,
`—`, or an id this document made up. A `Not applicable` row keeps the
SRS id. Security rows are not a new sequence starting at 1: `NFR-<n>`
is continuous across the whole SRS section 4.

| NFR-ID | Sub-item | Decision |
|---|---|---|
| e.g. NFR-3 | Authentication & session policy | e.g. "Bearer JWT, 15-min access / 7-day rotating refresh" |
| e.g. NFR-4 | Authorization model | e.g. "ownership check per resource — step 1 of each scenario, «Доступ» row" |
| e.g. NFR-6 | Secrets & credential handling | e.g. "issued tokens stored hashed; no raw secret ever persisted" |
| e.g. NFR-7 | Rate limiting | e.g. "100 req/min per user on write endpoints" |
| e.g. NFR-5 | Third-party / webhook trust | e.g. "HMAC-SHA256 signature + timestamp, verified before Steps run" |
| e.g. NFR-8 | Encryption in transit / at rest | e.g. "TLS terminates at the ingress proxy; no column or bucket encryption — no payment data" |
| e.g. NFR-9 | Retention & deletion | e.g. "no retention window; delete = object store first, then the row" |
| e.g. NFR-10 | Audit trail | e.g. "append-only `audit_log` written by an `AuditLog` port on every admin mutation" |

The last three rows are decisions with a shape: encryption says where TLS
terminates and what is *not* encrypted; retention says how long data lives
and what "delete" means across stores in which order; audit says whether a
journal exists, which port writes it, and what never reaches a log. Each
forces structure — a port, a table, or an ordering inside a use case — so
none of them belongs in prose under another row.

Schema columns and the OpenAPI security scheme already exist. This table
records the code-side decision (which port, which order) and must not
contradict them. `code-review-full`'s security lens verifies the shipped
code against this table row by row. A missing row is a requirement
nothing downstream will check.

That is why the table has no "omit it" case. When the input carries **no**
Security NFR checklist, still write the table and walk the eleven
sub-items explicitly — authentication & session, authorization /
object-level access, data classification & PII, encryption in transit and
at rest, data retention & deletion, input trust boundaries, third-party /
integration trust, rate limiting & abuse resistance, secrets & credential
handling, audit trail of significant actions, LLM-specific threats. Each
gets either a decision or `Not applicable — <reason>`, where the reason
names why this system has no such surface ("no human actor: internal job
triggered by cron only"). `Not applicable` with no reason is a blank row
wearing a label.

A sub-item that clearly *does* apply but that no upstream document decided
is a row in `open-questions.md` **and** an upstream gap: name the missing NFR row so
`srs-writer` can be invoked on the existing SRS, rather than inventing a
security policy here. Deciding a mechanism is this document's job;
deciding that a requirement exists is not. This architecture file does not
bump the SRS.

## Other NFRs

Every SRS §4 row outside Security (performance, reliability /
availability, scalability, observability, and any other category the SRS
names) gets one row in foundation §1 «Решения по NFR». Without the row, a measure
like «p95 < 300 мс» or «RPO 1 ч» reaches no one: the plan and the reviews
read the architecture, not the SRS table.

| NFR-ID | Решение | Где в дизайне |
|---|---|---|
| e.g. NFR-1 | e.g. «список площадок — один запрос с индексом по `venue_id`, без N+1» | e.g. сценарии `venues`: `VenueQueries.list`; индекс в схеме |
| e.g. NFR-2 | e.g. «вне архитектуры — `deploy-topology`: две реплики, ежедневный бэкап» | — |

- **NFR-ID** follows the same rule as the security table: copied from
  the SRS, continuous numbering, never invented.
- **Где в дизайне** points at a section, a file, or a port. A decision
  with no place in the design is prose, not a decision.
- When the answer is not structural, write `Вне архитектуры — <stage>`
  and name the stage that owns it (`deploy-topology` for replicas and
  backups, `ci-pipeline` for a load test). This names an owner, not the
  next pipeline transition — that stays in `pipeline`.
- No quality tree and no scenarios table: the SRS already states the
  measure.
