---
name: zod-skill
description: >-
  Internal: Zod at the boundary (parse untrusted input once, no zod in the domain); read by work's executors before
  zod code.
license: MIT
compatibility: "TypeScript projects using zod"
metadata:
  author: Anivar Aravind
  author_url: https://anivar.net
  upstream_version: 1.1.0
  tags: zod, validation, schema, typescript, parsing, boundaries, testing
---

# Zod

Adapted from Anivar Aravind's zod skill (MIT, see `LICENSE`).

Zod validates at **runtime** data the app does not control: request bodies, query strings, forms,
env vars, external API responses, queue messages. Compile-time-only types stay plain TypeScript.

**Which layout applies.** With an architecture document (`clean-architecture-design`), schemas live
in the adapters the foundation's §5 tree (`documentation/architecture/architecture.md`) names (HTTP, config, gateways); `domain/` and `application/` never import
zod or a wire schema — the boundary lint refuses it (`clean-architecture-design/references/machine-checkable-boundaries.md`).
At the Framework-first level (foundation §1 «Уровень») the route's schema is the boundary and there is no
separate input type; the one `domain/` module still imports no zod. Without an architecture document, in an
existing repo, keep its schema files and the types its services already take; do not restructure unasked. A new
business rule still goes into a module with no Zod, Fastify, or Drizzle import — say so in one line.

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

## On the frontend

A form's format rule comes from the schema generated from the contract (or the one rules module the domain model's
«Кто ещё применяет» names), never a regex typed into the form — a copy of a server rule drifts from it (`react` →
«A form is one library (React Hook Form) and one schema»).

**Version-sensitive points** — [references/version-checks.md](./references/version-checks.md). In a `work` packet
their answers come in `CURRENT LIB DOCS`; where it says `none`, probe the installed version in the project instead
of fetching docs. Outside `work`, read the file and check each point you rely on against the installed version.

## The reviewer checks

1. **Untrusted data is parsed once, at the entry point**; no service or repository parses it again.
2. **The use case receives its own input type**, mapped from the parsed wire value without a cast.
3. **Wire types come from the schema or the generated contract**, never a hand-written interface mirroring one.
4. **`safeParse` for untrusted input**, a throwing `parse` only for startup config; no throw inside a refinement or
   transform.
5. **No raw input or raw issues in a response or a log line** — field paths and the schema name only.
6. **A form's format rule comes from the generated schema or the rules module**, never a regex typed into the form.
