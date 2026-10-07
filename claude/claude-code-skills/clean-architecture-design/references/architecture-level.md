# Step 2. Decide how much architecture is justified

Read at Step 2 — the orchestrator before grading (Orchestrator step 4) and
the foundation writer before recording «Уровень».

Every system this pipeline designs gets the same shape: rich entities in
`domain/`, use cases in `application/`, frameworks in `adapters/`, the
edge linted. **Modest is the floor**, plain CRUD included. Why: an agent
copies the pattern it finds, so the same layers in every repository are
worth more than the few files a framework-first CRUD saves; a CRUD
entity at Modest is short (constructor checks, no service), not
ceremony. What grows with the system is the ceremony on top — output
DTOs, write ports as their own layer, storage models with mappers — and
that is the Modest / Full choice.

The foundation records one level as the «Уровень» row of §1 «Ключевые
решения»; every mode then **stays inside its limits** — the scope
decision is worthless if the domain model or a scenario adds the
ceremony of the level above. The limits are about what the design
contains, never about how long a document is:

| Level | When | What the design contains | Limits |
|---|---|---|---|
| **Framework-first + one boundary** | only a throwaway prototype the user or the SRS names as one, with a stated short life (days to weeks). Never by your own judgment, and never for plain CRUD | framework shape kept; the few real rules in one framework-free `domain/` module; one lint rule on that edge; reads via the ORM directly | no ports folder, no output DTO (the framework's request/response model is the boundary), ≤ 1 lint rule |
| **Modest** | the default: any system that outlives a prototype and has no Full trigger, from plain CRUD to a handful of real rules | `domain/`, `application/`, `adapters/`; rich entities for the real rules; ports as plain interfaces next to the use cases; framework models as storage models; reads via query functions in adapters, no use case | ≤ 3 lint contracts; a frozen input type per write use case, entity or read model out, no output-DTO layer; no `Clock`/`IdGenerator`/`UnitOfWork` unless a named test or a multi-aggregate save needs it |
| **Full** | **any Full trigger below** | all of the above plus input and output types on the use-case boundary, write ports in `application/ports/` as their own lint layer, separate storage models with mappers, domain events where the requirements need them | one artifact per file |

**Full triggers** — any one of these is Full even on a two-person team:

- a versioned public or partner API: an external consumer the team does
  not deploy depends on it. A `/v1` URL prefix alone is not one;
- sensitive data that different audiences must not see (query ports per
  audience): two or more actor groups with different field sets across
  several read models. Hiding the owner or some fields on other users'
  rows is a projection in one read model, not audiences;
- a mandatory external report that must not be lost. A notification
  retried until delivered is an outbox, not a report.

**Otherwise Modest.** Long life or many rules without a trigger stay
Modest. "We want Clean Architecture", "so we don't have to rewrite it
later", and "we write code with an AI agent" are not promotions; they
raise the enforcement bar (foundation §6), not the layer count. Never
build layers "for later" — add the next boundary after friction appears,
and say in `open-questions.md` what that friction would look like.

