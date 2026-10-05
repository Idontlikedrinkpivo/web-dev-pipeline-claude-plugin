# Rich Entities

## Entity is not an ORM model

If you have used Hibernate, Entity Framework, or Active Record, park that
meaning of "Entity". A class with `@Entity`, `@Table`, `@Column`, and
generated getters and setters is a **storage model**: it describes how to put
data into a database. A Clean Architecture entity is a **business object that
knows its own rules** — behavior, not a bag of fields.

### Bank account, two ways

ORM style:

- fields: `id`, `balance`, `number`;
- methods: `getBalance`, `setBalance`;
- no logic — it lives "somewhere in the services".

Clean Architecture style:

- same fields;
- methods: `deposit`, `withdraw`, `calculateInterest`;
- all the logic inside.

`withdraw` does not just decrement a number. It checks that funds are
sufficient, that the daily limit is not exceeded, that the account is not
frozen, whether a fee applies. These rules existed before computers — a
19th-century clerk checked the same things on paper. That is why they are the
most stable code in the system: "you cannot withdraw more than you have" does
not change when you move from PostgreSQL to Mongo or to a blockchain.

### Both kinds live in a real project

- In the center: rich domain entities with behavior.
- At the edge: anemic storage models for the ORM.
- Between them: an explicit mapping in the repository.

More code, yes. But when accounts move to a separate service two years later,
the repository implementation changes and the business logic does not move by
a line.

## Rich vs anemic

The debate is a holy war of "tabs vs spaces" caliber; in practice, projects
where the rule lives inside the entity are easier to maintain. When a rule
changes, you change one place. A newcomer opens the `Order` entity and sees
everything an order can do. No surprises.

The team still chooses. For simple CRUD, a rich model may be over-engineering.
When logic is complex, rules live for years and will change, rich models pay
back.

### Why this matters more when an LLM writes the code

When the model reads a rich entity, it sees how the concept works in one
file. In an anemic design the logic is smeared over ten services; the model
has to gather it piece by piece, and the context window is spent on
navigation instead of on the rule. With a clear prompt and a repository map,
rich models produce more predictable generation because the rule sits where it
is expected. Less context, more understanding. This stops being a debate about
"clean code" and becomes a way not to make the model reassemble the domain on
every task.

## Designing an entity

For each entity, write down:

1. **Identity** — what makes two instances the same thing (`AccountId`).
2. **State** — fields and the set of legal states (`Active`, `Frozen`,
   `Closed`). Prefer an explicit state type over boolean flags.
3. **Behavior** — methods named after the verbs in the requirements, taking
   whatever the rule needs to decide (the current instant, the actor, a typed
   fact the use case loaded). A requirement phrased as "X does Y, unless Z"
   produces one method named after Y — never a setter for the status field,
   which moves the "unless" to whoever remembers to check it.
4. **Invariants** — conditions that must hold after construction and after
   every transition. The constructor (or a factory) refuses to build an
   invalid entity; a transition refuses to move into an invalid state.
5. **Named errors** — one domain error per violated rule
   (`InsufficientFunds`, `CancellationTooLate`). Named errors are how the
   use case and the controller learn what happened without parsing strings.
6. **What it depends on** — only the language and other domain types.

### What an entity must not contain

- A framework base class (`models.Model`, `ActiveRecord::Base`,
  `@Entity`). That is the storage model's job.
- Serialization or persistence annotations. If the entity crosses the
  boundary to a client, the adapter layer produces the representation.
- Presentation methods (`toJson`, `toViewModel`, `displayName` for the
  screen). Otherwise the entity changes for two reasons — a business rule and
  a screen requirement — and two clients asking for different field names
  produce a conflict inside the domain.
- `save()` / `delete()` — no Active Record. `repository.save(entity)`.
- Knowledge of "who called me" — HTTP, queues, users' sessions.

## Value objects and named types

Concepts that appear in several places or carry their own small rules become
value objects: `Money` (currency, rounding), `Email` (format), a date range
(start < end, minimum length), a limit that knows its own period.

Named types compress meaning. `UserId`, `OrderId`, `SignedWebhookPayload`
tell the model what a value is and where it may go without opening the
definition; `string`, `T`, or `data: any` force it to guess from context, and
guessing is where inconsistent generations come from. A type name does for a
boundary what a file path does for a module: it makes the meaning visible
before the implementation is read.

In statically typed languages, encode states and transitions in the type
system where practical; the compiler then reviews the boundary for free while
the agent is still typing.

## The invariant table

The single most useful artifact for an agent implementing the domain. One row
per rule quoted from the requirements:

One row per rule, filled from the requirement's own words. The shape of a row
by the shape of the rule:

| Shape of the rule | Owner | Enforced in | Outcome |
|---|---|---|---|
| a single value must be well-formed or within bounds | the value object for that value | its constructor, so an invalid instance cannot exist | a named error |
| a cap on how many of something one party may have | the party's aggregate, holding the count, or a policy value object it calls | a method the use case asks *before* acting | a named error |
| a deadline that changes what the action means | the aggregate whose state changes | one method taking the current instant and returning which outcome happened | a resulting state, no error; a second aggregate may then record its own consequence |
| a named transition only a certain kind of actor may complete | the aggregate that changes state | the method taking that actor as a typed value | a named error if the actor's kind is wrong; otherwise the resulting state |
| repeated events crossing a threshold | a score or history value object on the aggregate | the method that records the event | a resulting state carrying its own boundary (until when, what is now required) |
| money or quantity computed from rules with tiers and exclusions | a policy value object | the totals method the aggregate calls | a derived value, no error |
| a calendar boundary ("day", "quarter", "in N days") | the value object that computes it, given an instant and a zone | its method — never `Clock` | a derived date or instant |
| a recorded fact never changes; a mistake is fixed by a new fact (ledger entries, receipts, audit rows) | the entity that records it | the type has no mutating method; the correcting entity's factory takes the fact it corrects | the correcting fact, no error; schema `none` unless a trigger exists |
| an external event or a client request takes effect at most once (a provider event id, an idempotency key) | the entity the first occurrence creates, holding the key and what the first call produced | its factory takes the key; a method compares a repeat with the stored one (same body → replay, different body → named error). The use case looks the key up through a port *before* acting | the stored outcome of the first call on a replay, or a named error; schema `UNIQUE` on the key as the last line |
| a rule you had to guess | as above | as above | as above, tagged `(A-n)` in the table and listed in `open-questions.md` |

The document table also has **Ограничение в схеме**: `none` | `CHECK` |
`UNIQUE` | `FK`. That cell is for `db-schema-design`. It is never a cell
that says the database enforces the rule — «Где проверяется» stays the
entity or value-object method.

Publish the table with headers `Правило | Владелец | Где проверяется |
Ограничение в схеме | Исход` and nothing above it. Do not copy this
section's explanations, a column gloss, or the words Owner / Enforced in
/ Storage echo / Outcome into the domain model. Entity headings are
`### <Name> (сущность)`: do not write «агрегат» or define it. Do not
define `from(raw)` in prose; the signature states the rule.

The **Outcome** column holds whichever the rule produces: a named error (the
business says "you cannot"), a resulting state (the business says "and then X
happens"), or a derived value (the rule is a computation). Do not force a
consequence into an exception. When a deadline passing turns the action into a
different, legitimate outcome, an exception that also mutates state is the worst
of both: the caller must catch a "failure" that actually succeeded, and the new
state is invisible in the signature.

**Assumed rules belong in the table** when the agent must implement them —
otherwise the table is incomplete for implementation. Tag them `(A-n)` and
cross-reference `open-questions.md` so the customer can
strike a row without hunting for it.

If a rule has no natural owner, you are missing an entity or a value object —
or it is not a domain rule at all. Access policy (who may *invoke* the
endpoint) belongs to the controller guard. A named-transition role belongs on
the entity as a typed actor. Data-exposure rules belong in the
**boundary-checks table** (Rule → Shape → Proof), not here. A must-deliver
side effect belongs in the use case Ошибки table, not here. If one entity
owns rules about three unrelated concepts, you have merged entities that
should be separate.

Time belongs here too when the rules mention it: a calendar day, a month, a
quarter, "until end of day", "within N days". The domain receives time-zone-aware
instants. A `Clock` port supplies `Now` and the IANA location — it is not an
«Где проверяется» cell. **One** value object computes each boundary, named in the
table. Otherwise the agent computes the same boundary in three places with
naive datetimes, and the three disagree around midnight and at the quarter's
edge.

## When anemic is acceptable

- Plain CRUD with no rules beyond "field is required" — validation belongs to
  the request model, not the domain. The entity still lives in `domain/`
  (Modest is the floor): a short type with its constructor checks, no
  service beside it, so the first real rule has an obvious home.
- Read models / reporting projections — data shaped for a screen or export
  has no behavior by design; keep it in the adapters as a DTO or query
  result.
- Prototypes with a stated short life.

Even then, keep the one or two real rules in a single domain module that
imports nothing from the framework, so the day the rules multiply there is a
place for them to go.
