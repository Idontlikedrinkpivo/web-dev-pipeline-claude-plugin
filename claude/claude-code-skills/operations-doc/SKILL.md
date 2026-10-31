---
name: operations-doc
description: >-
  Writes the operations document for a built system: logs, jobs, alarms, troubleshooting. Use for «эксплуатационная
  документация», «где посмотреть журналы», «инструкция для поддержки». Deployment: deploy-topology.
---

# Operations document

The deploy document says how to start the system. Nobody has said how to
live with it afterwards: where to see who cancelled a booking, whether the
night job ran, why a letter never left, what to do when the queue grows.
Without it the first incident is solved by reading code — by whoever can.
This stage writes that down once, from what the documents and the code
already decide, and proves every query on the test stand.

Write the document in Russian. Do not translate table and column names,
operationIds, event names, paths or ids.

## Inputs

| Source | What it gives |
|---|---|
| SRS | NFRs on audit, retention, reliability, observability, personal data; roles that should see records |
| DB schema (`documentation/db/schema.md`, «Закрытые наборы значений») | the tables that record what happened, their status values |
| Architecture foundation and scenarios | jobs and their schedule, external systems and their failure handling, log events, alarms, config |
| OpenAPI | operations that show records, and who may call them |
| Frames register and screen specs | screens that show records, per role |
| `documentation/deploy/deploy.md` | containers, health checks, how logs leave a container |
| The code | the event names the logger really writes, job schedules, metrics endpoints — the code wins over a document; a difference goes to the report |
| `.claude/skills/verify/` | how to start the test stand for the proof |

Missing SRS or schema: stop and name the stage that writes it. No storage:
the journals section says so and the rest still applies.

## Steps

The stage keeps no progress file; it writes one document. Each step's
result goes into the chat in a line.

1. **Inventory.** List what the system records, each with its source
   (schema table, architecture section, `file:line`):
   - **records** — tables whose rows are a record of what happened: audit
     marks (`cancelled_by`, `created_by`), event and history tables,
     outgoing queues (outbox), received events, idempotency keys;
   - **required records** — every record a law, a regulation or the SRS
     says must be kept: processing of personal data, consents, data-subject
     requests, access to personal data, security audit. For each: the
     basis, the retention the basis sets against the retention the system
     has, and who may read it. A required record the system does not keep
     at all is the worst gap this stage can find (`references/required-records.md`);
   - **jobs** — every scheduled or looping process: schedule, what it
     changes, how a run leaves a trace;
   - **log events** — every named event the code writes
     (`grep` the logger calls), with its fields; which ones are alarms. An
     alarm is a symptom the user feels — requests failing, answers slow, a
     job late, a message not sent — never a bare cause (CPU, memory), and its
     «Что делать» cell points to the operation or troubleshooting row
     (П-n, Т-n) that handles it;
   - **health and metrics** — endpoints, metric names, what a dashboard
     counts;
   - **external systems** — each failure mode and what the system does
     (the architecture's error table);
   - **retention** — how long each record lives and what deletes it.
   An item a document names and the code does not have (or the reverse) is
   a difference: the code wins in the document, and the difference goes to
   the report.
2. **How to see each one** — in this order of preference, all that exist:
   a screen (S-n and the role), an API operation (operationId and the
   role), a read-only SQL query, a log filter. A record that an SRS role is
   meant to see (support, administrator) but only SQL can show is a **gap**:
   write the query, mark the row «только SQL — экрана нет», and list it in
   the report. Never invent a screen or an operation.
3. **Write `documentation/operations/operations.md`** per
   `references/template.md`: sections, row shapes, the rules for queries
   (read-only, schema-qualified, bounded, numbered parameters, personal data
   only where the task needs it) and for log filters (JSON lines on the
   container's stdout, whatever collects them). Each row names what is
   behind it (table, `file`, operationId) in its own column — the duty
   developer's way in; the operator reads the rest. No requirement ids
   (FR, NFR, BR, UC, actors, frames) — the facts themselves, screens by title.
4. **Prove it on the test stand** per `references/proof.md`: start the stand
   (the verify skill's doctor first), make one record of each kind through
   the API or the UI, run every query and every command of the document,
   and check each returns what its row says. A query that fails or returns
   the wrong thing is fixed in the document, then rerun.
5. **Keep it true with a test** — `references/proof.md` → The query test: a
   test in the project's suite that prepares every SQL block of the
   document against the test database, so a renamed column fails the build,
   not the operator at night. Copy it from `assets/` (pytest or vitest) and
   adapt the lines marked `ADAPT`; do not rebuild it from the prose.
6. **Hand it over.** When `release/<version>/` exists, copy the document
   there as `OPERATIONS.md`; `scripts/build-images.sh` copies it on every
   rebuild (`deploy-topology` → Step 8). When the folder does not exist
   yet, say that the next build carries it.
7. **Commit** the document and the test (`docs: эксплуатация`), then close
   per `pipeline` → "Asking before a transition": the report first —
   the document as a link, a required record the system does not keep or
   keeps shorter than its basis first, how many records, jobs, events and alarms it
   covers, the queries proven, every gap from step 2 and every difference
   from step 1 — then the next stage the `pipeline` table names. Report the
   differences in three groups, because each is fixed differently: **the code
   contradicts a document** (a defect — a fix in code; prove it on the stand
   when you can), **a document is behind the code** (the document's owner
   stage fixes the text), **the documents are silent** (nobody decided — a
   question for the user before any code). An item that looks like a
   difference but a document states it on purpose is not one.

## On an increment

The document exists: edit it in place. Read the iteration's changes
(`git diff v<previous>..HEAD` over the schema, architecture and code), add
or change only the rows they reach, and rerun the proof for those rows; the
query test reruns all of them anyway. A record removed from the system
leaves the document in the same commit.

## Guardrails

- **Nothing invented.** A record, job, event or alarm comes from a source
  in the inventory; an operation the system lacks («переотправить письмо
  вручную») is not described as if it existed — the row says how it is done
  today (a SQL update the operator must not run, an admin action, nothing)
  and the gap goes to the report.
- **Read-only.** The document's queries never change data. A routine fix
  that needs a write (requeue a stuck letter) is a numbered procedure with
  its precondition, the exact statement, how to check it worked and how to
  undo it — and the report names it, because a write by hand is a missing
  feature.
- **Personal data.** A query shows a personal field only when the task
  needs it, and the row says so; a log filter never prints one. The
  document holds no secrets — variable names only, as in `deploy.md`.
- **Not the deploy document.** Starting, updating and configuring the
  system stay in `deploy.md`; this document links to it.

## References

- `references/required-records.md` — records a law, a regulation or the
  SRS requires: how to find them, what their section holds, the gaps.
- `references/template.md` — the document's sections and row shapes, with
  the room-booking example.
- `references/proof.md` — the proof run on the test stand and the query
  test.
- `deploy-topology` (skill) — the stand, `deploy.md`, the release folder.
- `pipeline` (skill) — the stage table and the transition question.
