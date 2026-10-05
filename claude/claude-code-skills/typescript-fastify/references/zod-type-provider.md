# Zod Type Provider

Use when the project already validates with Zod (`zod` in the manifest). Follow the
`zod-skill` skill for schema rules.

- Declare Zod schemas in the route `schema` through the project's Zod type provider; do not
  call `safeParse` in handlers, because there must be one validation path and one error format.
- Set the provider's validator and serializer compilers once, where the app is built, and reuse
  them; never mix them with TypeBox/JSON Schema routes in the same route.
- Translate the provider's validation errors in the existing global error handler into the
  contract's error body (SKILL.md, Errors); do not answer them from the route.
- When the OpenAPI document is generated from the routes, wire the provider's schema transform
  into the swagger plugin; the spec stays the contract, so `operationId` equals the spec.

Check before relying on it (see SKILL.md, Version-sensitive behaviour): the provider's package
name and which Zod and Fastify majors it supports, the names of its compilers, error guard and
swagger transforms, and how shared (`$ref`) schemas are registered and emitted.
