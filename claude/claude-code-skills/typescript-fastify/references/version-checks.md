# Fastify — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **Package and import names** of the type provider and schema library, and which of their majors match the
  installed Fastify major.
- **Validation errors** — the shape of a validation error as the error handler receives it (code, where per-field
  issues live), the status Fastify uses for its own validation and body-parse failures, and whether the provider
  changes either.
- **Response serialization** — what happens to properties not in the response schema, and to a body that does not
  match it (dropped, coerced, or a 500).
- **Validator defaults for request data** — coercion of query and params, removal of extra properties, applied
  `default`s, and which string `format`s are enforced.
- **Shared schemas** — how `addSchema` ids or a schema registry are referenced from routes and emitted by the
  OpenAPI generator (named components or inlined), so `operationId` and component names match.
- **Encapsulation and lifecycle** — whether a decorator or hook is visible where used, what `fastify-plugin`
  metadata enforces, and which hook runs before validation.
- **Async handlers** — returning a value versus `reply.send`, and empty bodies on 204.
- **Database errors** — where the database error code sits on an error that reaches the handler (raw driver error
  or wrapped by the ORM).
- **The app's OpenAPI** — how `@fastify/swagger` in dynamic mode emits a route's `response` content types, path
  parameters (`:id` → `{id}`) and shared schemas, which OpenAPI version it writes, and what `app.swagger()` returns
  when the app registered it in static mode.

## Zod type provider

- The provider's package name and which Zod and Fastify majors it supports.
- The names of its validator and serializer compilers, its validation-error guard, and its swagger transforms
  (`jsonSchemaTransform` and the like).
- How shared (`$ref`) schemas are registered and emitted, and how a Zod type shows in the generated JSON Schema
  (nullable, integer bounds, string formats with their own `pattern`).
