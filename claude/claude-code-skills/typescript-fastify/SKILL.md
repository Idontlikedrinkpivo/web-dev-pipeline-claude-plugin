---
name: typescript-fastify
description: >-
  Conventions for Fastify services in TypeScript: routes that implement
  documentation/api/openapi.yaml (operationId, statuses, Problem Details, page shape),
  thin handlers that call use cases, plugins, auth hooks, one error handler,
  cursor validation, idempotency keys, side-by-side API versions. Use when
  creating or changing Fastify routes, handlers, plugins, hooks, auth,
  errors, pagination or idempotent writes. Not for Express or NestJS;
  persistence is `typescript-drizzle-orm`, schema rules are `zod-skill`.
---

# Fastify

## Which contract and layout apply

- **An architecture document exists** (`clean-architecture-design`): routes live where the foundation's §5 tree
  (`documentation/architecture/architecture.md`) puts the HTTP adapter; a handler parses, calls one use
  case, and maps the result. `documentation/api/openapi.yaml`
  (from `openapi-spec-generator`) is the only source for paths, `operationId`, statuses, the
  Problem body, the validation status, JSON casing, and the page shape; this skill defines none of
  them. Named errors map to statuses through the architecture's «Named error → HTTP» table.
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
- Three cases in the handler: framework validation errors (the status, `code`, and per-field list the
  contract defines), named errors (status from the mapping table, or the existing `AppError`
  hierarchy in a brownfield repo), everything else (log it; 500 with a generic `detail`, never the
  internal message, stack, or SQL).
- A driver error nobody classified (a future route without its own handling) is still mapped in the
  same handler by SQLSTATE through the persistence error helper: unique → 409, FK → the status the
  spec gives it, serialization or deadlock → 503 with `Retry-After`. The repository classifies the
  ones it expects first (`typescript-drizzle-orm`).
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
  catch { throw new InvalidCursor() }
  if (!isCursorFor(v, sort)) throw new InvalidCursor() // shape, value types, same sort
  return v
}
```

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

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- Package and import names of the type provider and schema library, and which of their majors match
  the installed Fastify major.
- The shape of a validation error as the error handler receives it (code, where per-field issues
  live), the status Fastify uses for its own validation and body-parse failures, and whether the
  provider changes either.
- Response serialization: what happens to properties not in the response schema, and to a body that
  does not match it (dropped, coerced, or a 500).
- Validator defaults for request data: coercion of query and params, removal of extra properties,
  applied `default`s, and which string `format`s are enforced.
- Shared schemas: how `addSchema` ids or a schema registry are referenced from routes and emitted by
  the OpenAPI generator (named components or inlined), so `operationId` and component names match.
- Encapsulation and lifecycle: whether a decorator or hook is visible where used, what
  `fastify-plugin` metadata enforces, and which hook runs before validation.
- Async handlers: returning a value versus `reply.send`, and empty bodies on 204.
- Where the database error code sits on an error that reaches the handler (raw driver error or
  wrapped by the ORM).
