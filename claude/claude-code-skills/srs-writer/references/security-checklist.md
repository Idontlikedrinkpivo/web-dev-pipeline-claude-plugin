# Security sub-checklist — SRS §4

Read when writing or checking §4 of an SRS. One row per sub-item, each with its own `NFR-ID`. The rules for «Не применимо» and for sub-items the source is silent on are in SKILL.md → Security sub-checklist. In the SRS file write «Не применимо», not "Not applicable". The English names in this table are the topics; the requirement cell is Russian.

| Sub-item | What to state as the requirement |
|---|---|
| **Authentication & session policy** | Who/what must be authenticated before reaching this capability; session lifetime, rotation, or token expiry if the source material specifies one |
| **Authorization / object-level access control** | Which resources require an ownership or role check before read/write (this is what an IDOR gap looks like when it's missing) — every such resource should also have a matching `NotAuthorized`/`Forbidden` Exception Flow in its Use Case |
| **Data classification & PII handling** | What data is sensitive (PII, credentials, payment data) and what must never be logged, exported, or shown to an unauthorized actor |
| **Encryption in transit & at rest** | Which traffic must be encrypted and where TLS is expected to terminate; which stored data must be encrypted on disk (columns, buckets, backups) |
| **Retention & deletion** | How long each class of data may live, what "delete" must mean for the user (including files and derived copies), and anything that must be purged on a schedule |
| **Input trust boundaries** | Which inputs cross from an untrusted actor (user upload, webhook, third-party API response) and therefore need validation before use |
| **Third-party / integration trust** | For each inbound callback (webhook) or outbound call to a user-supplied destination: how authenticity/trust is established |
| **Rate limiting / abuse resistance** | Which capabilities need throttling and why (cost exhaustion, brute force, scraping) |
| **Secrets & credential handling** | Only if this FR issues, stores, or rotates credentials, tokens, or API keys — state the handling requirement |
| **Audit trail of significant actions** | Which actions must stay attributable after the fact (who did what, when) and how long that record is kept — state «Не применимо» with a reason when no actor is distinguishable (a single shared service account, cron-only trigger) |
| **LLM-specific threats** | Only if the product has an LLM-facing capability: prompt injection, cross-user data leakage, output-as-trust. Otherwise mark this sub-item «Не применимо» explicitly rather than omitting it |
