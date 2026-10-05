---
name: zod-skill
description: >-
  Where and how to validate with Zod in TypeScript: parse untrusted data
  once at the boundary, give the use case its own input type, keep zod out
  of the domain and raw input out of errors and logs, evolve schemas safely,
  and test them. Use when code imports zod or touches z.object, z.infer,
  safeParse, env parsing, or request, form or external-API validation. Not a
  Zod API catalogue: signatures come from the installed version.
license: MIT
compatibility: "TypeScript projects using zod"
metadata:
  author: Anivar Aravind
  author_url: https://anivar.net
  version: 2.0.0
  tags: zod, validation, schema, typescript, parsing, boundaries, testing
---

# Zod

Adapted from Anivar Aravind's zod skill (MIT, see `LICENSE`).

Zod validates at **runtime** data the app does not control: request bodies, query strings, forms,
env vars, external API responses, queue messages. Compile-time-only types stay plain TypeScript.

**Which layout applies.** With an architecture document (`clean-architecture-design`), schemas live
in the adapters the foundation's §5 tree (`documentation/architecture/architecture.md`) names (HTTP, config, gateways); `domain/` and `application/` never import
zod or a wire schema. Without one, in an existing repo, keep its schema files and the types its
services already take; do not restructure unasked. A new business rule still goes into a module with
no Zod, Fastify, or Drizzle import — say so in one line.

## Boundary rules

- **Parse once, at the boundary.** The entry point turns `unknown` into a typed value; nothing
  further in sees `unknown`, and no service or repository parses again (two error paths, the second
  usually a generic 500).
- **The use case receives its own input type**, declared in `application/`. The HTTP adapter maps
  the parsed wire value to it (snake_case wire names to the input's names, strings to value objects),
  so a wire rename never reaches the domain. Keep the mapping type-checked: the schema's output must
  be assignable to the input type without a cast.
- **Wire types come from the schema** (`z.infer` / output type) or from the spec by a generator,
  never a hand-written interface that mirrors a schema.
- **`safeParse` for untrusted input**; a throwing `parse` only for startup config, where crashing is
  the point. Never throw inside a refinement or transform; report an issue through the context.
- **Fastify routes:** the route `schema` through the Zod type provider parses, not `safeParse` in the
  handler (`typescript-fastify`). Env: once at startup, fail fast with every bad variable named.
  External API responses: right after fetch, log the mismatch with the schema name. DB rows from a
  typed ORM need no second parse.

## Failure response

A request that fails its schema answers with the body and status `documentation/api/openapi.yaml` declares for a
field validation failure (a Problem with per-field errors as `application/problem+json`); malformed
JSON gets the spec's status for an unparsable request. In a brownfield repo: the status and body its
error handler already sends. The global error handler builds it, never the route:

```typescript
const result = CreateUserBody.safeParse(input) // outside Fastify: a handler or middleware
if (!result.success) throw new RequestValidationFailed(toFieldErrors(result.error)) // field paths + messages
await registerUser.execute(toRegisterUserInput(result.data)) // use case gets its own type
```

- Never return raw issues or attach raw input to issues outside development (passwords, tokens, PII
  end up in logs and responses). Log structured: request id, schema name, failing field paths.

## Schema evolution and tests

- Additive changes are safe (new optional field, loosened constraint, new union member); anything
  else breaks consumers: ship it optional or deprecated first, remove in the next major. Object
  schemas drop unknown keys by default, so a removed field fails silently.
- Test through `safeParse`. Cover valid data, each invalid case, and boundaries (min/max, empty,
  optional vs nullable, unknown keys). Assert on issue path and code, not message text, unless the
  message is the contract. For boundary code, test the handler's error response too.

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **Major line and import path** (`zod`, a versioned subpath, the mini build): string formats, enums,
  object strictness helpers, error-customisation params and error formatters differ between majors.
- **Cross-field refinements on an object:** whether the parent check still runs when some fields
  failed, and with what data.
- **Defaults, prefaults and catch:** whether the default is validated or transformed, and when.
- **String → boolean/number for env and query params:** which strings a helper accepts, versus what
  a generic coerce does (a coerced `"false"` may be truthy).
- **Optional vs explicit `undefined`** under `exactOptionalPropertyTypes`, and what the output type
  says about it.
- **Date/ISO and URL helpers:** string format or codec, offsets accepted, schemes and hosts accepted.
- **Parse options and global config:** the raw-input-in-issues option, error maps and their timing.
