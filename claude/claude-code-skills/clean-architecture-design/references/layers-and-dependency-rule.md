# Layers and the Dependency Rule

Clean Architecture (Robert C. Martin, 2012) combines Cockburn's Ports and
Adapters with Palermo's Onion Architecture: four concentric rings, the most
stable in the center, with one rule that makes the picture work.

## The Dependency Rule

**Source-code dependencies point inward only.** Outer rings know about inner
rings; inner rings know nothing about outer ones.

- Controller imports the use case.
- Use case imports entities and port interfaces.
- Entity imports nothing but the language.

Data flows in both directions — the request travels inward, the response
travels outward — but an `import` never points outward. Control flow may run
"outward" (the use case calls a repository) while the *dependency* still points
inward, because the use case depends on an interface it owns and the adapter
implements that interface. This inversion is the whole trick.

## The four rings

### Entities (Enterprise Business Rules)

Business objects that carry the rules that would exist without software: an
order computes its total, an account knows about overdraft, a product knows its
discounts. They change only when a fundamental rule changes — "you cannot sell
what is not in stock" is nearly eternal.

Depend on: the language only. No frameworks, libraries, databases.

### Use Cases (Application Business Rules)

Application-specific orchestration. `CreateOrder` checks availability, creates
the order, sends an email. Add "manager approval required" and the *scenario*
changes; the entity does not.

Depend on: entities and the port interfaces (repositories, gateways) the use
case itself defines.

### Interface Adapters

Translators between the outside world and the core:

- controllers that build an input DTO from HTTP/JSON and call the use case;
- repositories that map entities to storage models and back;
- gateways into neighboring services;
- presenters and format converters.

Change when an external interface changes — REST to GraphQL touches adapters,
not the core.

Depend on: use cases and entities.

### Frameworks and Drivers

Spring, Django, NestJS, PostgreSQL, Redis, React — everything replaceable.
Change constantly: new framework major, Mongo instead of Postgres.

Depend on: everything inside.

## The stability gradient

Closer to the center means more stable; farther out means more volatile. The
arrows point inward so the unstable depends on the stable, never the reverse.
Think of a building: entities are the foundation, use cases the load-bearing
walls, adapters the partitions, frameworks the furniture. You rearrange
furniture weekly and never touch the foundation for it.

Popular frameworks are often built the other way round — which is the next
section.

## Why the framework becomes the center of the universe

Spring, Django, Rails, Laravel, Express are convenient, and their default shape
says: *the framework is the center, follow my rules*. Clean Architecture says
the opposite: business logic is the center, the framework is a detail.

Symptoms of framework-everywhere:

- models inherit a framework base class;
- business logic uses framework types;
- configuration lives in annotations, decorators, and magic;
- a test needs the whole framework booted.

Active Record makes it worse: `user.save()` means the entity knows about the
database, so the rule and the storage mechanism are welded together. Clean
Architecture writes `repository.save(user)` — the model does not know how it
is stored.

**When framework-first is fine:** a throwaway prototype with a stated short
life — nothing else in this pipeline. Standard CRUD is Modest (SKILL.md
Step 2): the same layers in every repository keep the pattern an agent
copies the same, and the full four rings with mappers wait for a Full
trigger.

**The working compromise — hybrid:** keep the framework, but the core never
imports it. Adapters and controllers know Spring or Django; the domain does
not. Dependency injection binds the layers at a single composition root. More
code, yes; but three years later moving from Django to FastAPI or Express to
Next rewrites adapters, not the system.

For an LLM, isolated rules are also cheaper to read: a rule interleaved with
framework machinery costs more context than the same rule standing alone.

## Where does X go? Quick placement table

Match the requirement's *kind*, not its topic.

| Kind of thing in the requirements | Ring | Why |
|---|---|---|
| A limit, threshold, or eligibility a clerk could check | Entity or value object | Exists without software |
| A threshold plus "who is allowed to sign it off" | Entity: an explicit state for "waiting" and a method taking the actor as a typed value; the use case only passes it | Both the number and who counts as that role are business facts. Guarding the HTTP route for that role is a second, transport question — not a competing home |
| A deadline whose expiry changes what the thing *is* | Entity: a state transition returned by the method, plus a job that advances it | The consequence is business vocabulary, not a failure |
| A count of past events crossing a threshold | Entity or a history value object on it | The rule is arithmetic over state the aggregate owns |
| The order of steps for this app ("do this, then notify") | Use case | Sequence, not permission |
| Who may *invoke this endpoint or job* at all | Controller guard for a role on the endpoint; first step of the use case when the check needs the loaded record | Access policy. Never inside the entity |
| Who may *complete a named transition* (override, lift, sign-off) | Typed actor on the entity method | Domain rule. The controller still guards the route so an unsigned caller never arrives |
| Which data may reach which audience | Adapter: a read model per audience that has no such member, plus a sentinel structural test | Boundary rule; record it in the boundary-checks table, not the invariant table |
| A pre-check that asks an entity a question and persists nothing | Query adapter calling the entity method | Not a use case. The write path still calls the same method before it saves |
| Parsing the incoming payload | Adapter (controller / request model) | Transport format |
| Mapping an entity to its table | Adapter (repository) | Storage format |
| Retry policy for an external system | Adapter (gateway) | The other system's behavior |
| Reads: one record, search, history | Query function in adapters (Modest) or query port + read model in `application/` (Full); no use case | Reads have no rules to orchestrate; a use case here is ceremony |
| "Must be synchronized" / "must not be lost" | Entity records the event; `repository.save` writes the outbox row in the same transaction; a relay in adapters delivers through a publisher that lives beside the relay | The use case does not call a gateway. Publishing after the save is a crash window. Record this once in the use case Ошибки table, not as an invariant-table row |
| Events consumed by other systems | Integration-event contracts in adapters, mapped from domain events | Keeps the broker out of the core; contracts version independently |
| A projection materialized during save | Adapter: named type + the test that proves its shape | No use-case port. The next reader is a query |
| Transaction spanning two aggregates | `UnitOfWork` port defined by the use case, implemented by an adapter | Only then. A single-aggregate save's transaction lives inside `repository.save` |
| Current time, random ids | `Clock` when a quoted rule names a calendar boundary or a test must freeze now — Clock supplies `Now` and the IANA location; calendar math lives on a value object. `IdGenerator` only when a named test asserts an id | Otherwise the adapter calls the language directly. Scattered `Guid.NewGuid()` is not a reason for a port |
| Feature flags, auth context, connectors | `shared/providers/` | May import `shared/domain/` (typed actors) and the framework; must not import any `<area>/`. Omit `shared/` when there is a single area |

## Wiring the composition root per framework

The rule is the same everywhere: adapters and the core are constructed and
connected in one place (`bootstrap/`), adapters never import that place, and
use cases are plain classes with constructor parameters typed as ports. The
mechanics differ by framework, and this is exactly where teams drift back:

| Framework | Pattern that keeps the arrows inward |
|---|---|
| **FastAPI** | Use cases built in `bootstrap/wiring.py`; routers are **factories** — `build_<area>_router(<use_case>: <UseCase>, ...) -> APIRouter` in `adapters/http/` — and `bootstrap/main.py` calls them and includes the routers. `Depends()` may resolve the request-scoped session inside the adapter, but never construct use cases |
| **Django** | No container: class-based views take use cases via `as_view(<use_case>=...)` from `urls.py`, which acts as the composition root; or a tiny module-level container in `bootstrap/` imported only by `urls.py`. Django discovers models only via `<app>/models.py` — keep a one-line re-export there pointing at `adapters/persistence/records.py`. `apps.py` and `migrations/` stay at the app root, templates under `adapters/web/templates/`, and `admin.py` is read-only or absent, since a `ModelAdmin` writing through the ORM bypasses every entity rule |
| **NestJS** | Use cases are undecorated classes. A Nest module in `bootstrap/` (or `adapters/nest/`) declares **factory providers** with injection tokens: `{ provide: <USE_CASE>, useFactory: (repo, clock) => new <UseCase>(repo, clock), inject: [<REPOSITORY>, <CLOCK>] }`. Controllers inject by token. The habit to break: `@Injectable()` on domain or application classes |
| **Spring** | Same idea: `@Configuration` classes in the outermost package produce use-case beans with `@Bean`; domain and application packages have no Spring annotations; ArchUnit guards it |
| **Express / Koa** | Route factories receive use cases; `bootstrap/server.ts` constructs adapters, use cases, and mounts routers |
| **chi / pgx** | Router factory `NewRouter(uc <UseCase>, ...) chi.Router` in `adapters/httpserver` (not package `http` — that is the stdlib). `cmd/` or `internal/bootstrap` constructs the pgx pool, repositories, use cases, and mounts the router. No chi or pgx import in `domain/` or `application/`. Persistence is plain structs + explicit map; sqlc/pgx stays in `adapters/persistence` |
| **ASP.NET Core** | Composition root is `Program.cs` plus `IServiceCollection` extension methods in `bootstrap/`. Controllers live in the HTTP project and take use cases via constructor. No `[ApiController]` / `[HttpGet]` / `[FromServices]` on use cases; no `DbContext` in controller constructors. The HTTP csproj references Application, not Persistence — Persistence is referenced only from Host. Do not let MediatR `IRequestHandler` become the dumping ground: a handler is a one-line adapter that calls a use-case class, or skip MediatR. Fluent API and `[Table]` target **storage types** in the persistence project, not the aggregate |
| **Rails** | Interactors under `app/domain/` and `app/use_cases/` as plain Ruby objects; controllers instantiate them through a small `Container` in `config/initializers/`; ActiveRecord models stay in `app/models/` as storage models with a repository wrapper |

Whatever the framework, the test that proves the wiring is right: a use case
can be instantiated in a unit test with in-memory fakes and no framework
import. If constructing it requires the framework, the composition root has
leaked inward. The composition root itself (`bootstrap/`, `Host`, `cmd/`)
**may depend on every project** — do not give it an inward-only lint rule.

## The same rule, one floor up

When an agent changes the code, the environment that changes it — repository
map, tools, checks, merge decision — has the same shape. The rule of a role
("compare implementation to the contract and return one of the allowed
verdicts") should not live only in a system prompt, or swapping the model means
redesigning the role. `run_check(check_id, candidate)` should not care whether
it is pytest, a CI job, or a remote service. Same arrow: contract belongs to
the rule, adapter belongs to the tool. Mention this in the design only when the
user is also setting up the agent workflow; otherwise stay on the product
floor.
