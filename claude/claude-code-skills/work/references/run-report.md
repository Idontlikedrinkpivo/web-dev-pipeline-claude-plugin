# Run report

Read at Step 7, before writing the run report: its shape, filled for one run.

```markdown
## Run report — <plan path>

**Base** — `BASE` recorded at Step 1; the start of every `BASE..HEAD` range.
**Прогресс** — `<сделано> из <всего>`, the same numbers as the chat line.

| U | Status | Executor used | Escalated | Commit |
|---|---|---|---|---|

**Decisions** — per unit, the worker's `DECISIONS` lines; the source for
`FROM DEPENDENCIES` in every dependent unit's packet.
**Verification** — what was run plan-wide and what it returned.
**Evidence** — per unit: the strategy used, and whether the red was witnessed
by the orchestrator (two-phase) or taken from the worker's report. A unit
committed on a reported red is a weaker claim than one committed on a witnessed
one, and the report should not blur them.
**Grade corrections** — units whose real difficulty did not match the plan's
grade, with the signal the cascade missed. This is the feedback that keeps
`complexity.md` calibrated for this project.
**Out of scope** — problems workers reported and nobody fixed.
**Cross-unit watch** — `OPEN` suspicions carried up from per-unit reviews, for
`code-review-full` to resolve at Step 7.
**Open** — units not attempted, and why.
**Отложено** — every parked unit and open final-review finding: what blocks
it, what was tried, the units waiting on it; the one place the user is
asked to decide, after the run.
**Lib docs** — which libraries Step 2b fetched (id + pinned version), or why
it wrote `none`.
**Full-plan review** — `code-review-full`'s verdict and findings from Step 7.
```

A filled excerpt, for calibration — match its density, not its domain:

```markdown
**Base** — `a41c9e2`
**Прогресс** — `3 из 12`

| U | Status | Executor used | Escalated | Commit |
|---|---|---|---|---|
| U3 | committed | mechanical-worker | — | `5b0d7f1` |
| U4 | committed | impl-lite | — | `c81e3a9` |
| U6 | committed | impl-critical | from impl-hard: `HARDER_THAN_EXPECTED` — два вебхука на одну оплату гоняются, нужна блокировка строки | `9e22c40` |

**Decisions** — U6: ключ идемпотентности `payment_intent_id`, unique в `payments.idempotency_key`; повтор возвращает сохранённый результат.
**Evidence** — U4: test-first, red из отчёта worker (2 падения в `order.test.ts`). U6: test-first, red witnessed в `PHASE tests-only` (4 падения в `pay-webhook.test.ts`).
**Grade corrections** — U6: каскад не учёл конкурентный внешний ретрай провайдера (signal 6); High верно, но без `impl-critical` не хватило.
**Cross-unit watch** — U4: `OrderStatus` в U4 — строковый union, в U2 — enum; сверить в Step 7.
```
