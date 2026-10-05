# Env vars and the fail-fast config contract

Every variable belongs to exactly one of four categories. Getting a variable
into the wrong category is how a mock leaks into prod or a real secret ends
up committed.

| Category | Where it lives | Example |
|---|---|---|
| **Env selector** | inline `environment:` in each compose file, one fixed value per file | `APP_ENV=test\|dev\|prod` |
| **Environment-fixed behavior flag** | inline `environment:` in each compose file — never in an env file, so a stray `.env.*.local` edit cannot override the environment's own safety posture | the mock gate, the TLS/secure-cookie flag, worker count, log level |
| **Local-infra connection string** | inline `environment:` for test/dev (points at the compose service by name); `.env.prod.local` for prod (points at the external instance) | `DATABASE_URL`, the object-store endpoint |
| **Secret / third-party credential** | `.env.<environment>.local`, gitignored, `required: true` for dev/prod | API keys, DB passwords for anything not a disposable local fixture, encryption keys |

Every `DATABASE_URL` in every environment carries the same
`search_path`/schema option, pointed at the dedicated schema from
`db-schema-design` §0 — never the default `public` schema. The schema name
is a project constant, not an environment variable: test, dev, and prod
differ in *which server* hosts the schema, never in the schema's name. If
the prod DBA provisions the external instance with a different schema name
than test/dev use locally, that is a real deployment fact worth recording in
`.env.prod.local`'s comment, not silently absorbed by search_path (a
misnamed schema on the external instance fails migrate loudly instead of
each environment quietly using a different name).

CI that runs `make test` on the runner (see `ci-pipeline`) must rewrite
compose hostnames to `127.0.0.1` and still copy `APP_ENV`, the mock-gate
variable, and that same `search_path`. The four categories do not change.

`.env.example` documents all four categories with a one-line comment on what
test/dev/prod each expect — it is the map a human reads before filling in
`.env.dev.local` or `.env.prod.local`. Compose never reads it directly; say
so in a comment at the top of the file itself, or the next person to touch
this assumes editing `.env.example` changes runtime behavior.

## The fail-fast rules, as a checklist for the app's own config/settings code

Write these as validation in the same place the app already parses its
config (a `Settings` class, a config module, whatever the stack's convention
is) — not as a compose-time check, not as a comment asking someone to
remember:

1. **Env selector is required.** No default. An unset selector must crash
   at startup, not silently pick one environment's behavior.
2. **The mock gate refuses outside test.** If the mock-fixtures variable is
   set and the env selector is not `test`, crash with a message naming both
   values — this is the one rule most likely to matter, because it is the
   rule that turns "someone copied a compose file wrong" into "prod served
   fixture data" if it is missing.
3. **Security flags that assume a network topology contradict, not just
   default.** A flag like "cookies require HTTPS" being true is not itself
   proof a TLS terminator exists — but that flag being true while a paired
   "we are behind TLS" flag is false (or vice versa) is a real
   contradiction worth crashing on, where the app can express one.
4. **No default for a prod/dev secret.** A missing required secret is a
   startup crash naming the variable, in code and in the compose file both
   — an empty string that silently "works" until the first real call fails
   is worse than a crash at boot.
5. **Resource-budget arithmetic, if the architecture named one.** Worker
   count × per-worker connection/resource usage ≤ the configured limit,
   checked at startup. A misconfiguration should fail the health check
   before it exhausts a shared resource under load.

## The `.env.example` sync test

One test, in the project's own suite, with two assertions:

- Every variable the config layer treats as required-somewhere appears in
  `.env.example`. (Nothing required is undocumented.)
- Every key in `.env.example` is a variable the config layer actually
  recognizes. (Nothing documented is a leftover nobody reads anymore.)

This test is cheap to write once the config layer already exposes "what do
I require" and "what do I recognize" as introspectable data (a function, a
class attribute — whatever the stack makes easiest), and it is the guard
that keeps the human-readable template from drifting out of sync with the
machine-enforced contract as the app grows past this skill's first pass.
