---
name: typescript-fastify
description: >-
  Fastify rules (routes from openapi.yaml, problem+json errors, contract test); read before Fastify code.
---

# Fastify

## Which contract and layout apply

- **An architecture document exists** (`clean-architecture-design`): routes live where the foundation's §5 tree
  (`documentation/architecture/architecture.md`) puts the HTTP adapter; a handler parses, calls one use
  case or query (at Modest a read is a query function in the adapters, no use case), and maps the result.
  `documentation/api/openapi.yaml` (from `openapi-spec-generator`) is the only source for paths, `operationId`, statuses, the
  Problem body, the validation status, JSON casing, and the page shape; this skill defines none of
  them. Named errors map to statuses through the architecture's «Named error → HTTP» table — one module, an
  exhaustive `switch` over the errors' `kind` with `assertNever`, never a mapper per route (`typescript` →
  «Every named error is its own type», «One translation of failures to answers»).
  A failure of an outside call reaches the handler wrapped with its `cause`; where the client only sees a generic
  answer, the handler writes one warn line with the cause's name — never keys, addresses or secrets.
- **The level is Framework-first** (foundation §1 «Уровень»): no ports or use-case classes — a handler calls the
  one framework-free `domain/` module for the rules and the ORM directly for reads and writes; the request and
  response schemas are the boundary. The contract, the error handler and the rules below hold unchanged.
- **No architecture document, existing repo:** follow the repo's layout, error classes, error body,
  validation status, casing, and page shape for the change at hand, even where they differ from the
  spec defaults above. Do not migrate the contract or restructure unasked; propose it in the answer
  instead. A new business rule still goes into a module that imports no Fastify, Drizzle, or Zod
  (the service or a domain module), not into the handler — say so in one line.

## Rules

1. Read the owning package first: Fastify version, type provider, schema style, helpers, errors,
   lifecycle, test utilities. A second provider or schema style means two validation paths and two
   error shapes. Zod projects: [references/zod-type-provider.md](./references/zod-type-provider.md).
2. One explicit handler per route, no generic request executor, so schema, statuses, and inferred
   types stay visible where the route is declared. The handler holds no business rule.
3. A route implementing a spec operation carries its `operationId` and `tags` verbatim (and
   `summary` when present): `operationId` becomes the method name in generated clients. Change the
   spec first when the contract changes.
4. Internal refactors keep the public contract: paths, statuses, field names, error codes and
   bodies, headers. Suggested contract changes go into the answer as proposals, not into the diff.
5. Reuse registered schemas, format validators, auth hooks, and the global error handler; a duplicate
   schema `$id` is rejected at registration and a second handler answers the same failure twice.
6. Derive TypeScript types from the route schemas (or from the spec by a generator) when that is the
   project's pattern, so type and runtime validation cannot drift.
7. Plugins only for a real encapsulation, lifecycle, or shared-dependency need. Every plugin opens an
   encapsulation context; wrap with `fastify-plugin` only when its decorators or hooks must
   intentionally escape it. Add a close hook only for a resource the plugin owns.
8. Build the app in one module, call `listen` only in the entry point, so tests build the server with
   `inject` and no port. Wire use cases and adapters in the composition root, not inside plugins.
9. Auth: reuse the existing auth plugin or permission helper. Missing or invalid credentials are 401,
   missing permission 403. An auth check that must precede body validation runs in a hook that runs
   before validation, registered on the prefix it protects so sibling route plugins inherit it.
10. Reuse canonical identifiers; change the id format only when the task selects it.

## Errors

- **One global error handler renders the spec's Problem shape** as `application/problem+json`;
  statuses come from the spec. Handlers and hooks throw named errors; they never build error bodies.
- Three cases in the handler: validation errors — the framework's schema and a schema parse inside a
  handler alike — with the status, `code`, and per-field list the contract defines (a brownfield repo
  without a contract: its own 400 or 422; a client's bad input is never a 500), named errors (status from the mapping table, or the existing `AppError`
  hierarchy in a brownfield repo), everything else (log it; 500 with a generic `detail`, never the
  internal message, stack, or SQL).
- A database conflict is answered the way the contract declares it (`openapi-spec-generator` → Step 6),
  the same in both stacks:
  - a conflict the repository expects (a duplicate key, a dangling reference) it classifies into a named
    error (`typescript-drizzle-orm`), answered with the status the contract gives that error — never a
    bare 409;
  - a serialization failure (`40001`) or deadlock (`40P01`) is first rerun by the server: a use case
    whose transaction can lose to a concurrent one is wrapped in `bootstrap/` by one shared helper that
    reruns its whole run a bounded number of times (the repository never loops). When the attempts run
    out, the handler answers the contract's 503 with `Retry-After`, read through the persistence error
    helper;
  - any other driver error — an unexpected violation included — is the third case: logged with its
    SQLSTATE, the contract's 500.
- Every extension member an error can emit (`errors`, `retryable`, a context key) is declared in the
  spec's Problem schema and in the shared route response schema, or the serializer strips it. Do not
  open the schema to let undeclared members through; error context is not spread into the body
  unless the schema declares that member. 5xx context goes to logs only.

## Collections and cursors

- Page shape, parameter names, `limit` default and maximum come from the spec, including how the
  last page is marked; brownfield: the repo's existing casing and envelope. With neither a spec nor
  a precedent: `items` plus a next-cursor field that is null on the last page, in the repo's casing,
  no success/data wrapper. Never offset paging when the contract is keyset.
- The cursor is opaque (base64url of the last row's sort values plus the sort it was issued for),
  carries values at the column's full stored precision, and is **validated before it reaches the
  query**: decode inside `try`, check it is an object of the expected shape, each value has the
  column's type, and its sort equals the request's sort. Anything else is the spec's 400, never a 500.

```typescript
function decodeCursor(raw: string, sort: Sort): Cursor {
  let v: unknown
  try { v = JSON.parse(Buffer.from(raw, 'base64url').toString('utf8')) }
  catch (e) { throw new InvalidCursor('undecodable', { cause: e }) } // options second (`typescript` → errorClassNames)
  if (!isCursorFor(v, sort)) throw new InvalidCursor('shape') // shape, value types, same sort
  return v
}
```

The cursor is not signed: it only says where the caller's own page continues, and every query still applies the
caller's access predicate.

## Idempotency keys

When the spec (or the task) declares an `Idempotency-Key` header on a create: requests without it
behave as before; with it, the key is stored under a unique index and a replay returns the first
call's status and resource instead of a conflict. The race is settled by the constraint (insert on
conflict do nothing, or catch the unique violation, then re-read), never by an in-process map.

## Versions side by side

Only for an API with external consumers — its spec carries the contract's own SemVer with the major
in the path (`openapi-spec-generator` → Contract version). An API called only by the project's own
client has no version prefix: a breaking change ships with the client in the same release.

A breaking change (renamed or removed field, changed status) ships as the next major path prefix
(`/api/v2`) registered next to the old one, with its own schemas and the same use cases or services;
the old major keeps its schemas and tests unchanged and stays until the sunset the spec announces —
its removal is its own change, never part of the one that adds the new major. No header or
query-parameter versioning unless the repo already does it. Both majors use the one global error
handler; `Location` headers point into the major that created the resource.

## Service endpoints, logs and shutdown

The platform the service is handed to probes it, scrapes it, collects its stdout and stops it with SIGTERM. The code
for all four is written once, in `bootstrap/` and the entry point, from
[references/service-endpoints.md](./references/service-endpoints.md) — read it before touching them.

- `GET /health/live` touches nothing; `GET /health/ready` checks the database (2 s) and each store the app cannot
  serve without, never a partner's API; `GET /metrics` serves the app's own `prom-client` registry with
  `http_request_duration_seconds` labelled by the route template. The three sit outside the contract
  (`NOT_IN_CONTRACT`) and outside auth.
- Logs are the built-in pino logger, one JSON object per line with `time`, `level`, `msg`, `logger`, `request_id`
  and `err`; code logs through `request.log` or a child of `app.log`, never `console`. No secret, token or personal
  data in a line.
- The entry point owns SIGTERM and SIGINT: `app.close()` within `SHUTDOWN_TIMEOUT_SEC`, a resource closed in an
  `onClose` hook, exit 0.

## The contract test

`tests/contract/openapi.contract.test.ts` compares the OpenAPI the app builds (`@fastify/swagger` in dynamic mode,
`app.swagger()`) with `documentation/api/openapi.yaml`: every operation the app serves exists there with the same
method, path and `operationId`, the same error statuses, and the same request and success-response schemas. It is
written once from [references/contract-test-template.ts](./references/contract-test-template.ts)
(`repo-scaffold`); a unit that adds or changes a route keeps it green — a red contract test is a route that differs
from the contract, never a reason to loosen the comparison. Routes therefore declare the contract's error statuses
in their `response` schema with the shared Problem schema.

**Version-sensitive points** — [references/version-checks.md](./references/version-checks.md). In a `work` packet
their answers come in `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead
of fetching docs. Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **A handler parses, calls one use case or query, and maps the result** — no business rule, no body of an error
   built in a route or hook.
2. **Every status a route can answer is one the contract declares for that operation**: a duplicate is a named
   error, never a bare 409 from a SQLSTATE; a serialization failure or deadlock is 503 with `Retry-After` only
   after the bounded reruns.
3. **A cursor is decoded inside `try` and checked for shape, value types and sort before the query**; anything else
   is the contract's 400, never a 500.
4. **An idempotency key or a duplicate is settled by the database constraint**, never by an in-process map or a
   read-then-insert alone.
5. **Auth runs in a hook before validation, registered on the prefix it protects**; missing credentials 401, a
   missing permission 403.
6. **A new or changed route carries the contract's `operationId` and `tags`**, and the contract test passes.
7. **`/health/live` touches nothing; `/health/ready` checks only stores the app cannot serve without**, each bounded,
   never a partner's API — a partner outage must not take every pod out of rotation.
8. **No metric label or log field comes from raw input**: `route` is the template (`request.routeOptions.url`),
   never `request.url`; no user id, email, token or body in a label or a log line.
9. **A password is hashed with Argon2id** (`@node-rs/argon2` or `argon2`), never a bare `crypto` digest or a
   hand-rolled salt; an unknown email still verifies against a dummy hash, so it costs the time a wrong password
   does. Login and registration are rate-limited by address and by account where architecture §1 puts it — in the
   app, `@fastify/rate-limit` on those routes, answering the contract's 429 with `Retry-After`.
10. **A write takes the contract's fields by name**: the body is never spread into an insert or an update, and a
    field the client may not set — the owner, a role, a status, a price — is not in the request schema
    (`additionalProperties: false`), so a sent one is refused, not stored.
