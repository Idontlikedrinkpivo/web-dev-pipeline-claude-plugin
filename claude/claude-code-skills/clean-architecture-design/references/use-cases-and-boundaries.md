# Use Cases and Boundaries

## Use cases are conductors, not a dumping ground

Entities are smart and independent. Someone has to decide which entity to call
when — that is the use case, also called an interactor. One use case equals
one user action: transfer money, create an order, confirm an email. The
musicians (entities) know their parts; the conductor (use case) shows when to
come in.

### Transfer money, step by step

The caller — a controller or anything else — knows the use case's interface
and asks: transfer money from one account to another; here are the
identifiers. The use case orchestrates:

1. It needs users, accounts, balances.
2. It calls the repository. It knows only the interface — find user, find
   account, find balance — never the implementation.
3. The repository returns entities (or data; see the debate below).
4. The use case tells the entities: perform the transfer.
5. The entities change their state, enforcing their rules.
6. If the transfer is allowed, the use case calls the repository again to
   save the updated entities.
7. The caller receives a response in the shape the use case defines.

The interactor does not check the balance, compute the fee, or apply limits.
Entities do. The interactor knows only the sequence. That is why a new
corporate account type with different withdrawal rules changes the *entity*,
and the scenario stays untouched.

### Boundaries and the shape of data

A boundary says: *if you want to work with me, give me data in my format.*
A DTO usually crosses it. The use case owns its contract. Whether the data
arrived as JSON, YAML, or protobuf, the caller converts into the use case's
shape, so the core does not inherit the volatility of the outer layers. This
is close to an anti-corruption layer: protecting the core from other people's
reasons to change.

The use case does not know who called it or how the result will be used.
Full isolation.

### Why a use case is a good unit of work for an LLM

"Build the Refund Payment use case" keeps the model inside orchestration: it
should not invent refund rules (those belong in the entity) or payment-gateway
details (those belong in the adapter). If `TransferMoney` is already in
context, the model assembles `Refund` on the same template with the same
isolation — standard blocks, like LEGO. Dependencies hide behind interfaces,
so tests are straightforward: mock the repository, use test entities, assert
the call sequence. TDD, plain unit tests, or model-generated tests all fit this
shape equally well.

## Use case specification

The published skeleton is in `output-template-scenarios.md`: one
subsection per use case in its area's scenarios document, headed with the
file path, with the Вход / Доступ / Выход / Операция API table, the Шаги
table (step → port method or entity method, transaction boundary marked)
and the Ошибки table. Nested `Input` / `Result` types in the same
use-case file count as one artifact. The Шаги table names port methods
only: each signature is written once, in foundation §4, and a signature
copied into every use case that calls it is the copy that stays stale
when the port changes. A step that asks the entity cites the rule id; the
rule itself is a row of the domain model's invariant table.

Two things in this template are deliberate. First, the step that asks the entity: an outcome the
business has a word for comes back as a **value**, and the use case only routes
it. If it would say "and then X happens", return a value; if it would say "you
cannot", raise a named error. Second, the Ошибки table is where most real
design decisions hide — an agent that finds it empty will call the external
system inline and hope. The outbox commitment is recorded **here**, not as a
row in the domain model's invariant table. Under the outbox the use case's obligation ends
at the committed intent; the relay owns delivery and the publisher lives
beside the relay, not on this use case.

A repeat of an idempotent request returns **what the first call returned**
— the stored ids, amounts, and balance of that moment — not a fresh read
of current state: the client retries because it lost the first answer,
and a different number would tell it something else happened. Store the
result with the key, and say so in the Ошибки table.

When the caller needs every violation at once rather than the first one, the
aggregate root validates them all and raises one error carrying the list; the
per-rule errors still exist as the elements of that list.

## Queries: reads are not use cases

"One use case per user action" applies to actions that change state. Reads —
fetch one record, search, show history — have no rules to orchestrate, and
giving each a use case plus an input DTO is ceremony that an agent will then
replicate everywhere. Where reads live depends on the level from Step 2:

- **Framework-first / Modest:** a query function in the persistence adapter (or
  a read-only repository method) that the controller calls directly. It returns
  a frozen read model when the screen needs fields the entity does not hold —
  a display name from a joined table, a computed count — and the storage record
  otherwise. Never the entity.
- **Full:** a query port in `application/` **next to the read models it
  returns**, one method per audience, implemented in adapters with a projection
  that never joins the tables it must not expose. Do not put query ports in
  `application/ports/` — that folder is write ports typed with domain types
  only. A projection that lacks the column is easier to prove safe than a
  presenter that strips it.

A query adapter **may call an entity method that answers a question without
persisting** (a pre-check before any write). That is not a use case; the
write path still calls the same method before it saves.

Do not mix the two levels — a query port at Modest is the ceremony this section
exists to prevent. Authorization on reads (each party sees only their own rows)
is an access policy: apply it in the controller guard or as the first line of
the query, and let the read model carry only what that audience may see.

Publish queries as a table in the scenarios document of the area that
reads, not a code fence — columns and the read-model field table:
`output-template-scenarios.md` → Запросы.

## Side effects and domain events

External systems fail, and an agent will otherwise pick "call it inline and
hope". Decide per gateway and record it in the use case's Ошибки table:

| Option | Use when | Cost |
|---|---|---|
| In-request call to the gateway | the action is meaningless without the external result (an authorization, a live quote) | the action fails when the system is down; retries are the caller's problem |
| Transactional outbox + relay | the requirement says "must notify", "must be synchronized", "must be reported", or a lost message is a real-world incident | an outbox table, a relay worker, idempotent adapters |

There is no third option. A broker the company already has (RabbitMQ, Kafka,
Service Bus) is *how the relay delivers*, not a different design: publishing
inside the request still loses the message when the process dies after the
commit, and publishing before the commit invents events that never happened.

So: the entity records what happened, the row that says "this must be delivered"
is written **in the same transaction as the state change** — through
`repository.save` or an `Outbox` port inside the same unit of work — and a relay
in adapters reads it, delivers with retries and a dead-letter path, and marks it
done. The use case does not call a gateway; the publisher the relay uses lives
beside the relay. Idempotency is the adapter's job: send a stable key the other
side can deduplicate on. The adapter also maps domain events to
integration-event contracts, which are separate types and version independently
of the domain. A projection materialized during that same save needs no
use-case port — name the type in adapters and the test that proves its shape.

## Can a use case return an entity?

Martin's 2012 article says plainly: pass simple data structures across
boundaries; do not cheat by handing over entities or database rows. Create a
DTO, then.

The contradiction sits right next to it. If the controller already depends on
the entity, passing an instance adds no new dependency — the Dependency Rule
is already satisfied at the import level. Martin's own examples have an Entity
Gateway that returns entities. Hence two camps.

**DTO everywhere:** full layer isolation; explicit contracts on every
boundary; the letter of the rule.

**Return the entity:** less code; no mountains of mapping; better
performance; no copying; the dependency already exists.

The principle is KISS — complicate only when needed. The practical criterion:

| Return a DTO when | Returning the entity is fine when |
|---|---|
| the public API is versioned | the application is internal |
| the entity carries sensitive data | performance is critical |
| different clients need different shapes | the team is small and has explicitly agreed |

If an entity does cross the boundary, it must not carry serialization
annotations, UI methods, or presentation logic. Otherwise the entity changes
for two reasons — a business rule and a screen requirement — and that is an
SRP violation. Example: an entity can render itself to JSON for a client; the
client asks to rename fields; you edit the entity. A second client asks for
something else; now there is a conflict inside the domain. So JSON and
external annotations leave the entity, and the adapter layer handles
representation both ways.

Principles beat practices: if you know *why* the boundary exists, you can
decide consciously instead of along party lines. Record the decision as a
row of foundation «Ключевые решения» and its proof as a row of the domain
model's Проверки границ (Правило / Форма / Доказательство), not as a
«DTO или сущность» heading.

## The layer roster: one row per layer

Foundation §3 opens with it. The document says «Слой», never «Кольцо».
Names already live in one place each — entities and named errors in the
domain model, use cases and queries in the scenarios documents, port
signatures in foundation §4, files in foundation §5 (and in the headings
of the other two documents). The roster does not copy them. It answers
which layers exist and where to read the names:

```markdown
| Слой | Что лежит | Где имена |
|---|---|---|
| domain | сущности, VO, именованные ошибки | доменная модель §1–§3 |
| application | сценарии, порты записи, запросы | документы сценариев (по области, §2) · 2 порта записи (§4) |
| adapters | контроллеры, реализации портов, шлюзы | §4 (порт → адаптер), файлы §5 |
| infrastructure | процессы и хранилища | §1 Хранилища |
| bootstrap | композиция | §5 `bootstrap/` |
```

Counts that grow with every use case (сценарии, запросы) are not written
in the roster: the foundation would change on every scenarios increment.

A layer with nothing in it is stated as empty with the reason, not omitted — an
absent `application` row reads as an oversight, `«application — пусто: уровень
Framework-first, запросы обслуживают контроллеры»` reads as a decision.

A roster cell that repeats an entity, use case, or port name is a
defect. Do not split a long name list with `<br>`. On an increment,
update the port count; do not paste a new name into §3.

Do not publish «Путь одного запроса». Orchestration is the scenarios
documents (and the sequence view of a key scenario). Named-error status,
the route-guard mechanism, and the wire schema are foundation §4.
Methods, paths, success codes, and bodies are the OpenAPI spec. Rule
changes touch the domain model.

## Types on boundaries: fewer degrees of freedom for the model

A DTO is a contract, but a contract can be written so that breaking it
unnoticed is impossible — or so that it breaks in the first PR and you learn in
production. The difference is static typing. A typed language removes whole
categories of invalid states and transitions before anything runs; the
compiler becomes a reviewer that checks the boundary for free, while the agent
is still writing.

What works is not just `any` → strict type but the **name** of the type.
`UserId`, `OrderId`, `SignedWebhookPayload` tell the model what this is and
where it may go without visiting the definition. `T` or `data: any` say
nothing, so the model guesses from context, and guessing produces inconsistent
generations.

This extends beyond one language:

- **Front ↔ back:** describe the contract in OpenAPI and generate typed
  clients on both sides; a mismatch is caught by the generator, not by a
  user.
- **Storage:** Postgres has a modest but real type system; add constraints
  and triggers for invariants that fit in a column or a check. If the agent
  tries to write invalid data, the database refuses loudly and immediately
  instead of silently accepting what will break the next use case.

A type on a boundary is the Dependency Rule for data: it stops an unstable
external format from leaking inward and quietly corrupting what should be
stable.
