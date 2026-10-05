# Machine-Checkable Boundaries, File Layout, and Tests

- [When four rings are too early](#when-four-rings-are-too-early-but-boundaries-are-already-needed)
- [Encoding the Dependency Rule as lint](#encoding-the-dependency-rule-as-lint)
- [TypeScript / JavaScript](#typescript--javascript--dependency-cruiser)
- [Python](#python--import-linter)
- [Java / Kotlin](#java--kotlin--archunit)
- [C# / .NET](#c--net--netarchtest--csproj)
- [Go](#go--go-arch-lint-component-graph--depguard-vendor-bans)
- [Structural tests](#structural-tests-where-a-linter-cannot-reach)
- [Test plan](#test-plan-by-layer)
- [File layout](#file-layout-the-tree-is-an-interface)
- [Modules table](#the-modules-table-foundation-2)
- [Review as a system](#review-as-a-system-when-the-agent-writes-the-code)

## When four rings are too early but boundaries are already needed

There is a false fork: "Clean Architecture is premature on an MVP" versus
"an agent will multiply any mess, so the rings are needed on day one". Both
are true once you separate two meanings of "architecture".

Four rings, piles of DTOs, and a separate domain are not mandatory for a
prototype or plain CRUD. Speed beats form there, and framework + AI is often
enough. The full scheme pays off on long life, complex logic, and probable
technology change — and the team must be ready to invest in understanding the
boundaries; if there is no capacity to review, rings on paper will not help.

Any boundary you *do* choose is different. The agent copies the pattern it
finds in the repository, including bad ones. If the direction of dependencies
cannot be checked by a machine, speed becomes accelerated drift. Three folders
with a linter beat four rings without a check.

So:

- do not roll out the full product scheme "for growth";
- make the chosen boundaries — even very modest ones — machine-checkable
  immediately when an agent writes the code;
- add the next boundary after friction, not from an ideal diagram.

Diagnostics → remedy: scope keeps getting confused → a map with anchors in the
code. Implementation drifts from the task → fix the contract before writing
code. Review too expensive → identity for results, provenance of checks, a
separate reviewer. Agent bypasses layers → a linter, not another paragraph in
the instructions.

## Encoding the Dependency Rule as lint

Write the allowed directions first, as a table in the design document:

| From | May import | Must not import |
|---|---|---|
| `<area>/domain/` | same area's `domain/`, `shared/domain/`, language stdlib | everything else |
| `<area>/application/` (use cases + query ports + read models) | `domain/`, `shared/domain/`, its own read models | `adapters/`, framework, DB drivers, `bootstrap/` |
| `<area>/application/ports/` (write ports at Full) | `domain/`, `shared/domain/` | read models, adapters, framework, `bootstrap/` |
| `<area>/adapters/` | `application/`, `ports/`, `domain/`, `shared/providers/`, framework | other areas' adapters, `bootstrap/` |
| `shared/domain/` | stdlib | anything else |
| `shared/providers/` | framework, libraries, `shared/domain/` | any `<area>/` |
| `bootstrap/` / Host (composition root) | everything | — (exempt from inward-only) |

Every production folder that appears in the file tree must appear in this table
and in the lint config; a folder the linter does not know about is an unguarded
door (the usual victim is `ports/`). Do not give Host/`bootstrap/` an
inward-only rule — it is the one place that may reference every project.

Every «Must not import» cell maps to a named rule in the sketch, including
«other areas' adapters». With two or more areas, add a no-cycles rule and an
area-isolation rule: an `orders ↔ billing` cycle passes every per-area layer
rule. An allowed cross-area call is only the one foundation §2 names,
through the callee's `application/`.

On stacks with a compile-unit graph (csproj, Go modules, Maven modules) the
ring boundary is the project or module; the folder tree mirrors it. The HTTP
project must not reference the persistence project. NetArchTest / ArchUnit
then confirm what the project graph already forbids, plus namespace rules
inside a project.

Then pick the enforcer for the stack and sketch its config. Lint messages
should tell the agent how to fix ("move this rule into `domain/` or call it
through a port"), not only that it failed.

### TypeScript / JavaScript — dependency-cruiser

```js
// .dependency-cruiser.cjs
module.exports = {
  forbidden: [
    { name: 'domain-imports-only-domain', severity: 'error',
      comment: 'domain/ may import its own area domain/ and shared/domain/. Move framework/IO code to adapters/.',
      from: { path: '^src/([^/]+)/domain' },
      to:   { pathNot: '^src/(?:$1/domain|shared/domain)', dependencyTypesNot: ['core', 'type-only'] } },
    { name: 'domain-no-type-imports-from-outside', severity: 'error',
      comment: 'Even `import type` from an ORM, HTTP, or validation package leaks its shape into the domain. Map in the adapter.',
      from: { path: '^src/[^/]+/domain' },
      to:   { path: 'node_modules/(@prisma|@nestjs|typeorm|express|drizzle-orm|zod|fastify|@fastify)' } },
    { name: 'application-no-adapters-no-framework', severity: 'error',
      comment: 'Use cases talk to the outside through ports. Inject the adapter in bootstrap/.',
      from: { path: '^src/[^/]+/application' },
      to:   { path: '^src/[^/]+/adapters|^src/bootstrap|node_modules/(express|@nestjs|@prisma|typeorm|drizzle-orm|fastify|@fastify)' } },
    { name: 'adapters-do-not-import-bootstrap', severity: 'error',
      from: { path: '^src/[^/]+/adapters' }, to: { path: '^src/bootstrap' } },
    { name: 'shared-domain-is-leaf', severity: 'error',
      from: { path: '^src/shared/domain' }, to: { pathNot: '^src/shared/domain', dependencyTypesNot: ['core'] } },
    { name: 'no-circular', severity: 'error',
      comment: 'Areas and layers form a DAG. Break the cycle with a port owned by the inner side.',
      from: {}, to: { circular: true } },
    { name: 'adapters-not-into-other-area-adapters', severity: 'error',
      comment: 'Call another area through its application/, never its adapters/.',
      from: { path: '^src/([^/]+)/adapters' },
      to:   { path: '^src/[^/]+/adapters', pathNot: '^src/$1/adapters' } },
    { name: 'no-utils-dumping-ground', severity: 'error',
      from: {}, to: { path: '^src/(utils|helpers|common)/' } },
    { name: 'not-to-unresolvable', severity: 'error',
      comment: 'An import that does not resolve has no path, so every path rule above skips it. Fix the alias or add the package.',
      from: {}, to: { couldNotResolve: true } },
  ],
  // tsPreCompilationDeps: `import type { X } from '@prisma/client'` enters the graph;
  // without it the type-only rules above silently pass.
  // tsConfig: `paths` aliases (`@/orders/...`) resolve to `src/...`; without it the path rules silently pass.
  options: { tsPreCompilationDeps: true, tsConfig: { fileName: 'tsconfig.json' } },
};
```

Keep `severity: 'error'` on every rule: dependency-cruiser's default is
`warn`, and a warning does not fail the command, so a copied rule without it
guards nothing.

Note the `$1` in `to.pathNot`: without it, `orders/domain` importing
`billing/domain` passes by accident. `from` and `to` are separate regexes, so a
regex back-reference (`\k<area>`, `\1`) cannot reach across them — instead
dependency-cruiser substitutes the groups captured by `from.path` into `to.path`
and `to.pathNot` as `$1`, `$2`. Plain unnamed groups only. Alternative:
`eslint-plugin-boundaries` with `element-types` per folder.

### Python — import-linter

Substitute your own package and area names; `<root>` is the project package and
`<area>` each top folder from the tree.

```toml
# pyproject.toml
[tool.importlinter]
root_package = "<root>"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Clean layers inside <area>"
type = "layers"
layers = [
  "<root>.<area>.adapters",
  "<root>.<area>.application",   # use cases and ports
  "<root>.<area>.domain",
]

[[tool.importlinter.contracts]]
name = "Domain and application import no framework"
type = "forbidden"
source_modules = ["<root>.<area>.domain", "<root>.<area>.application", "<root>.shared.domain"]
forbidden_modules = ["fastapi", "starlette", "sqlalchemy", "django", "pydantic", "requests", "httpx", "celery"]

[[tool.importlinter.contracts]]
name = "Nobody imports the composition root"
type = "forbidden"
source_modules = ["<root>.<area>", "<root>.shared"]
forbidden_modules = ["<root>.bootstrap"]

# Two or more areas only.
[[tool.importlinter.contracts]]
name = "Areas are independent"
type = "independence"
modules = ["<root>.<area_a>", "<root>.<area_b>"]
# a call foundation §2 names: ignore_imports = ["<root>.<area_a>.application.* -> <root>.<area_b>.application.*"]
```

One `layers` contract per area, listing that area's rings only. Layers in one
contract must be siblings under a common parent: a top-level `bootstrap` is
never a layer next to `<area>.adapters` — keep it in the `forbidden` contract
above. Add one contract per area rather than one contract mixing areas. `ports/` as its own package (Full): list write ports as their own layer
between `application` and `domain`. Query ports stay in `application` next to
read models, so they are not that layer. Name the root package after the
project: `app` collides with the composition-root folder in prose, and
`platform` shadows the standard library.

### Java / Kotlin — ArchUnit

```java
@AnalyzeClasses(packages = "com.acme")
class ArchitectureTest {
  // Two or more areas: no cycles between com.acme.<area> packages.
  @ArchTest static final ArchRule areasFreeOfCycles =
      slices().matching("com.acme.(*)..").should().beFreeOfCycles();

  @ArchTest static final ArchRule layers = layeredArchitecture().consideringAllDependencies()
      .layer("Domain").definedBy("..domain..")
      .layer("Application").definedBy("..application..")
      .layer("Adapters").definedBy("..adapters..")
      .whereLayer("Adapters").mayNotBeAccessedByAnyLayer()
      .whereLayer("Application").mayOnlyBeAccessedByLayers("Adapters")
      .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Adapters");

  @ArchTest static final ArchRule domainIsPure = noClasses().that().resideInAPackage("..domain..")
      .should().dependOnClassesThat().resideInAnyPackage("org.springframework..", "jakarta.persistence..");
}
```

### C# / .NET — NetArchTest + csproj

The real wall is the project graph. Domain and Application csproj files must
not reference EF, ASP.NET, or Persistence. The HTTP project references
Application, not Persistence. Host references everything and is **not** given
an inward-only rule.

```csharp
using NetArchTest.Rules;
using Xunit;

public class ArchitectureTests
{
    [Fact]
    public void Domain_does_not_depend_on_application_or_framework()
    {
        var result = Types.InAssembly(typeof(/* a Domain type */).Assembly)
            .That().ResideInNamespace("Company.Area.Domain")
            .ShouldNot().HaveDependencyOn("Company.Area.Application")
            .GetResult();
        Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? Array.Empty<string>()));
    }

    [Fact]
    public void Domain_does_not_reference_EF_or_ASPNET()
    {
        var result = Types.InAssembly(typeof(/* a Domain type */).Assembly)
            .That().ResideInNamespace("Company.Area.Domain")
            .ShouldNot().HaveDependencyOn("Microsoft.EntityFrameworkCore")
            .GetResult();
        Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? Array.Empty<string>()));
    }

    [Fact]
    public void Application_does_not_depend_on_adapters()
    {
        var result = Types.InAssembly(typeof(/* a use case */).Assembly)
            .That().ResideInNamespace("Company.Area.Application")
            .ShouldNot().HaveDependencyOn("Company.Area.Adapters")
            .GetResult();
        Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? Array.Empty<string>()));
    }

    [Fact]
    public void Http_controllers_do_not_depend_on_persistence()
    {
        var result = Types.InAssembly(typeof(/* a controller */).Assembly)
            .That().ResideInNamespace("Company.Area.Http")
            .ShouldNot().HaveDependencyOn("Company.Area.Persistence")
            .GetResult();
        Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? Array.Empty<string>()));
    }
}
```

One `[Fact]` per direction. Do not chain `.ShouldNot().HaveDependencyOn(A).And().HaveDependencyOn(B)` —
`And()` after `ShouldNot()` is easy to invert. Cover every production project
except Host. Fluent API and `[Table]` live on storage types in Persistence, not
on the aggregate; a structural test grepping `domain/` for
`Microsoft.EntityFrameworkCore` catches the .NET analogue of type-only leakage.

### Go — go-arch-lint (component graph) + depguard (vendor bans)

Schema version **3**. There is no `anyOf` / `except` key. `deps` is a sibling
of `components`, not nested inside them. `workdir` is relative to the module
root (`internal` when that is the stack-shaped root).

```yaml
# .go-arch-lint.yml
version: 3
workdir: internal
allow:
  depOnAnyVendor: false
excludeFiles:
  - "^.*_test\\.go$"
components:
  domain:       { in: <area>/domain/** }
  usecases:     { in: <area>/application }       # files directly in application/
  writeports:   { in: <area>/application/ports/** }  # Full; omit at Modest
  adapters:     { in: <area>/adapters/** }
  bootstrap:    { in: bootstrap/** }             # or cmd/** + bootstrap/**
deps:
  domain:
    mayDependOn: []
  usecases:
    mayDependOn: [domain, writeports]
  writeports:
    mayDependOn: [domain]
  adapters:
    anyVendorDeps: true
    mayDependOn: [usecases, writeports, domain]
  bootstrap:
    anyProjectDeps: true
    anyVendorDeps: true
```

At Modest there is no `writeports` component: put port files next to use cases
and let `usecases` cover `in: <area>/application/**`. Package `http` is the
stdlib — the HTTP adapter directory is `httpserver`. `shared/domain` becomes a
`commonComponents` entry only when a second area exists.

depguard is a vendor-ban backup, not a substitute for the component graph:

```yaml
# .golangci.yml
version: "2"
linters:
  enable:
    - depguard
  settings:
    depguard:
      rules:
        domain:
          list-mode: lax
          files:
            - "**/domain/**/*.go"
            - "!**/*_test.go"
          deny:
            - pkg: github.com/jackc/pgx
              desc: "pgx belongs in adapters/persistence, not domain"
            - pkg: github.com/go-chi/chi
              desc: "chi belongs in adapters/httpserver or bootstrap"
```

### Other stacks

| Stack | Tool |
|---|---|
| PHP | deptrac |
| Rust | crate boundaries + `cargo-deny` for allowed deps per crate |
| Any | a structural test that walks the tree and greps imports — crude but honest; not a substitute for the stack's real enforcer |

## Structural tests where a linter cannot reach

- No class in `domain/` inherits from a framework base class.
- Every use case module in `application/` exports exactly one class with one
  `execute` (or `__call__`) — keeps the unit of work uniform for the agent.
  Query functions live in adapters and are exempt.
- Every port has at least one adapter and one in-memory fake.
- No `toJson`/`serialize` method on any domain type.
- Repository implementations return domain types, never ORM records (check
  return annotations).
- For boundary rules: the read model for the restricted audience has no member
  named like the protected data, and a test stores a sentinel value in the
  protected column, renders every shape that audience can reach (responses,
  exports, payloads sent to them), and asserts the sentinel never appears.
  A mapper that strips fields passes review and fails in production; a type
  without the field cannot.

## Test plan by layer

**Entity tests** — one per invariant-table row. Plain constructors, no
framework, no database. Given state X, action Y → new state or named error.
These are the cheapest and most durable tests in the system.

**Use case tests** — an in-memory fake per port (an in-memory repository, a
frozen clock, a recording gateway). Assert the *sequence* of port calls and
the returned DTO; one test per failure branch in the spec. If a use case is
hard to test this way, a rule has leaked into it or a dependency bypasses a
port.

**Adapter tests** — contract tests against the real store (container) or the
real API (recorded): the controller turns each domain error into the
documented status code. **Every mapper has a round-trip test** — build the
entity with every field set to a non-default value, map it to the storage
record and back, assert equality. A field added to the entity without its
mapper line then fails the build instead of being dropped on save; a
review cannot see that omission, a test can.

**Tenant isolation** (several tenants in one database) — an adapter test
against the real store seeds two tenants and proves a read and a write
through each tenant-owned port for tenant A neither return nor change B's
rows; the in-memory fakes key their rows by tenant too, so use-case tests
see the same rule.

**One end-to-end path** — at least one automated test drives the real wiring
(HTTP → use case → real repository against a test database) for the primary
action. It proves the composition root, not the rules.

**Structural and lint tests** — run in the same command as unit tests, so a
boundary violation fails the build like a failing assertion.

Size the plan to the level: at Framework-first the whole plan is a dozen
lines (rule tests + one end-to-end test); at Full it maps every invariant row
and every use-case failure branch to a named test. Do not require 100% of
`application/` on a days-horizon. First proof of a clear core: take one use
case and generate its tests. Easy → the shape is legible. Hard → fix the
shape before writing more code.

### Coverage as a protocol, not a metric

With partial coverage (80%, 95%) some code is uncovered because someone
decided it mattered less — and the agent cannot see that decision. At 100%
the uncertainty disappears: an uncovered line can only mean "the current
change just touched it", and the coverage report becomes a to-do list rather
than a judgment call. It also forces unreachable code out (you cannot write a
meaningful test for it) and surfaces hidden edge cases (you must name a branch
to cover it). This only holds if the suite is fast, isolated, and parallel —
thousands of checks in under a minute — otherwise the rule turns into
punishment and gets faked. Propose 100% for `domain/` when the horizon is not
days and the suite is fast; treat 100% of `application/` as Full-and-fast
only. The finish checklist in SKILL.md is the level-sized plan, not this
ideal.

## File layout: the tree is an interface

The agent works through the file system — lists directories, reads names,
greps, pulls files into context whole or in parts. Directory and file names
are therefore an interface on par with an API signature. `billing/invoices/compute_total.ts`
tells the model more than `utils/helpers.ts` with identical content. The path
is the cheapest hint about ring and area, available before a single line is
read.

Size matters too. Agents truncate or summarize large files on the way into the
working context, and summaries lose detail. A file that fits whole is held
whole. Many small files, one responsibility each, serve the same goal as a rich
entity: compress meaning into something visible at once.

Recommended default — **area-first, then ring**. Root folder is stack-shaped
(`src/` for TS/Python/C#; `internal/` for Go). On csproj / Go-module / Maven
graphs, each ring is a project and this tree is the inside of those projects.

```
<src|internal>/
  <area>/
    domain/          entities, value objects — one type per file; errors grouped per aggregate
    application/     one use case per file; query ports + read models (Full)
                     ports.py (Modest) or ports/ (Full, write ports only, one interface per file)
    adapters/
      httpserver/    controllers / routers, request and response schemas
                     (TS/Python/C# may name this folder `http/`; Go must not)
      persistence/   repository implementations, storage models, queries, migrations
      <external>/    one folder per external system
  shared/            omit when there is a single area
    domain/          shared value objects only (Money, ids)
    providers/       auth context, feature flags, config; may import shared/domain/
  bootstrap/         composition root: wiring, main (Go often `cmd/` + this)
```

The sketch above is a *shape*; what lands in the document is not. Write the
real names: `place_mark.py`, not `<use_case>.py`; `adapters/persistence/` and
`adapters/s3/` on separate lines, not `adapters/persistence|s3/`; no `…` row
standing in for "the rest". The tree is how an agent decides where to put the
next file, and a placeholder makes it guess. Each file name has one home:
entity, value-object and error files in the domain model's headings, use-case
and query files in the scenarios headings, everything else (ports, adapters,
mappers, storage models, `bootstrap/`) as a line of foundation §5, which
shows each area's `domain/` and `application/` as a folder line pointing at
the document that names its files. Cross-check both ways before you ship:
every port and adapter of §4 has a line in §5, every path in a domain or
scenarios heading sits in a folder §5 draws, and every line in §5 traces
back to one of them.

Layer-first (`domain/`, `application/`, `adapters/` at the top, areas inside)
is acceptable for a single-area service. Whichever you pick, state it and lint
it — and lint **every** production folder you drew. Host/bootstrap is listed
as "may import everything".

Cross-cutting concerns — authorization, connectors, feature flags — enter
through `shared/providers/` instead of spreading across every module.
`utils/`, `helpers/`, `common/` are forbidden as top-level dumping grounds.
Avoid folder names that collide with the language's standard library or the
framework's conventions: in Python, `platform`, `types`, `logging`, `test`;
in Go, `http`, `log` as a package root; in Django, anything but `models.py`
for model discovery (keep a re-export shim there).

### Known traps per stack

Not architecture, but an agent following the tree will hit them:

| Stack | Trap | Fix |
|---|---|---|
| Django | models are discovered only via `<app>/models.py`; migrations must live in the app package | `models.py` re-exports from `adapters/persistence/records.py`; keep `migrations/` in the Django app |
| Django / Postgres | `ArrayField`, GIN indexes, `EXCLUDE` constraints fail on SQLite test DBs | run tests against Postgres (container); say so in the test plan |
| FastAPI | `Depends()` pulls wiring into route modules | router factories receive use cases from `bootstrap/` |
| NestJS | `@Injectable()` on use cases drags Nest into the application layer | factory providers with tokens in a module under `bootstrap/` |
| Prisma / TypeORM | generated types leak into the domain through `import type` | lint forbids `type-only` imports from the ORM in `domain/`; map records to entities in the repository |
| ASP.NET Core | Fluent API configured against the aggregate; HTTP project references Persistence; MediatR handlers hold the rules | storage types in the persistence project; HTTP csproj → Application only; handlers are one-line adapters; Host is the only project that references everything |
| Go | package name `http` collides with `net/http`; template root `src/` fights `internal/` | adapter package `httpserver`; stack-shaped root `internal/` |
| Go | empty `shared/domain` for a one-area service | omit `shared/` until a second area needs a VO |
| Any ORM | lazy-loading relations from inside an entity | entities receive fully loaded data; repositories decide what to load |

## The modules table (foundation §2)

A rich entity compresses a rule. It does not answer "which parts of the system
take part in this behavior and whom will the change affect". Search answers
where a name occurs; the agent more often needs to know who owns the state,
which route is affected, who consumes the contract, which invariant must not
break.

One giant instruction file fails predictably: context is scarce, the file
crowds out the task, "everything important" means nothing is, and the sheet
goes stale in ways no machine can detect. The working form is a short entry
map (about a hundred lines) that acts as a table of contents, plus a system of
record next to the code: domain structure, specs, plans, quality invariants.
The agent starts small and unfolds context per task.

In the foundation this is §2 «Модули и функциональные области», always
present — even one area gets its row, because the row links the area's
scenarios document:

| Область | Модуль | Группа SRS | Документ сценариев | Владеет состоянием | Потребители контракта |
|---|---|---|---|---|---|
| one row per area, kebab-case English | the folder in §5 | the SRS capability group, verbatim | `scenarios/<area>/<area>.md` | the entities (domain model) that hold its state | who breaks if its contract changes: API versions, partners, other areas, jobs |

Key invariants are not listed here: they are rows of the domain model,
and a copy here would drift.

The map does not validate itself. Current behavior is confirmed by code and
executable checks; intent by the accepted task. If an anchor disappears or
drifts, revoke the guarantee — otherwise documentation becomes an attractive
lie. The file tree has no such problem: it *is* the code at read time. Map and
tree answer different questions — "what does it mean and whom does it affect"
versus "where is it and how big" — trust both, differently.

## Review as a system (when the agent writes the code)

Include a short version of this only when the user is also organizing the
agent workflow.

- Boundaries are caught before a human sees the diff: dependency direction,
  parsing at the edge, naming and logging conventions live in linters and
  structural tests. Taste that used to live in PR comments is written once as
  a rule and applied to every following diff.
- The executor does not approve itself. A separate reviewer session treats
  the implementation as an untrusted candidate and judges it against the
  contract, the observable diff, and reproducible checks.
- "Tests passed" is meaningless without the test set, the command, and the
  commit it refers to. Bind a green run to a specific commit; a branch name
  is not enough.
- Observation and decision are separate acts. "127 tests passed" is a fact
  about a run. "Candidate is ready to integrate" is a verdict over facts and
  acceptance rules.
- The verification loop must be cheap enough to run constantly, and
  environments must be disposable and isolated so parallel attempts do not
  share state.
