# Which layout governs — decide first

The backend and test skills of both stacks (`fastapi`, `fastapi-sqlalchemy`, `pytest-patterns`,
`typescript-fastify`, `typescript-drizzle-orm`, `vitest`, `zod-skill`) share these cases and point here; each keeps
only its own stack's placement. Read it once per unit, before the first file: one text, so a unit with three or four
stack skills does not read four copies that drift apart.

- **An architecture document exists** (`documentation/architecture/architecture.md`, the foundation, from
  `clean-architecture-design`): its §5 tree is the layout; do not add folders §5 does not list. Entity and use-case
  file paths come from the headings of the domain model (`domain.md`) and the scenarios documents
  (`scenarios/<area>/<group>.md`); foundation §4 holds the ports, the wiring and the named-error → HTTP table, the
  domain model §4 the invariant table, foundation §1 the security decisions, foundation §6 the test plan (one row per
  test file). Use those names.
- **The level is Framework-first** (foundation §1 «Уровень», `clean-architecture-design/references/architecture-level.md`):
  no ports, use-case classes, repository adapters or mappers — a handler or a small service calls the one
  framework-free `domain/` module for the rules and the ORM directly for reads and writes; that module takes and
  returns plain values, never a record. Everything else the skill says (the contract, the error handler, auth,
  sessions, migrations, driver-error classification, race tests) holds unchanged.
- **No architecture document, existing repo**: follow the repo's layout, patterns, error classes and test suite for
  the change at hand; do not restructure the project, move code into new layers or reorganise the suite unasked —
  propose it in the answer instead. A new business rule still goes into a function, class or module that imports no
  web framework, ORM or validation library, not into a handler, a route or a repository; say so in one line of the
  final answer.
- **Contract**: paths, `operationId`, status codes, bodies, the error body, the validation status with its `code` and
  field list, JSON casing and the page shape come from `documentation/api/openapi.yaml` when it exists
  (`openapi-spec-generator` is their one source); no stack skill defines them, and a test's expected statuses and
  bodies are the contract's, never typed from memory. Change the spec first when the contract changes. Without a
  spec, keep the shapes the repo already returns.
