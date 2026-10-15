# Required records

Some records the system keeps because someone outside the code demands it:
a law, a regulation, the customer's security rules. They are not like a
queue of letters: they may not be switched off, purged early or shown to
anyone, and an inspection asks for them by name. A system that lacks one
has a gap no operations document can work around.

## Finding them

Read the SRS for every requirement that says a record must be kept —
security, audit, compliance, personal data, retention — and every law or
regulation it names. Typical ones:

- processing of personal data: what was collected, changed, handed over or
  deleted, by whom and when;
- consents: who agreed to what, when, and the withdrawal;
- data-subject requests: access, correction, deletion, and the answer with
  its date;
- access to personal data: who opened or exported whose data;
- security audit: sign-ins, role changes, actions the requirements name
  («кто отменил», «кто изменил баланс»).

Then find each in the inventory (step 1): its table or log event. A record
the SRS asks for that no table or event holds is **«не ведётся»**.

## What the row says

- **Основание** — the law or regulation by name, or «требования безопасности
  заказчика» when only the SRS asks; no requirement ids (the document's
  rule), the report traces each row to its SRS id.
- **Срок: требуется / в системе** — the retention the basis sets and the one
  the system has (the purge job, a partition drop, nothing). Shorter than
  required, or «хранится вечно» where the basis demands deletion, is a gap.
- **Кто может смотреть** — the roles the SRS allows. A record that itself
  holds personal data (who looked at whose data) is shown only to those
  roles; its queries show the fields the task needs and say why.
- The rest as in «Журналы»: what a record holds, how to see it, where it is.

## In the report

First, before every other line of the stage's report:

- a required record the system does not keep — «не ведётся», with the SRS
  id and the basis;
- a retention shorter than its basis, or no deletion where the basis
  demands one;
- a required record anyone can read, or one only SQL shows when the SRS
  gives a role the right to see it.

Each is a gap for the next plan, not something this stage fixes: the
document describes the system as it is.
