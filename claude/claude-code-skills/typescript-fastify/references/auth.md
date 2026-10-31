# Password login with tokens (Fastify)

Read this only when the task implements registration, login, password hashing, token issue or check, or a route
guard. The decisions themselves — token kind and lifetime, where the token travels, hashing, roles — come from
architecture §1 «Решения по безопасности», or, with no architecture document, from the existing code or the user.
If those name an external identity provider (SSO), the token is the issuer's: check it by the issuer's keys as §1
says, and of this file only the guard rules (401 / 403, role from the database) apply. The Python twin is
`fastapi/references/jwt-auth.md`; the two say the same, so a project with both stacks has one auth behaviour.

## Libraries (house choice)

- Password hashing: Argon2id through `@node-rs/argon2` or `argon2`. Never a bare `crypto` digest, never a
  hand-rolled salt.
- Tokens: the library the project already has (`@fastify/jwt` or `jose`); with neither, `jose`. One library, so
  signing and checking cannot disagree.
- Rate limit: `@fastify/rate-limit`, on the login and registration routes only, unless §1 puts the limit in the
  proxy.
- Check the current releases and the signatures you call against the installed versions — which hash options are
  the defaults, how the JWT library takes the allowed algorithms (`references/version-checks.md` → Auth libraries).

## Where the pieces live

| Piece | With an architecture document | Brownfield |
|---|---|---|
| Hash / verify password | adapter behind a `PasswordHasher` port; the use case calls the port | the repo's auth module (e.g. `src/auth/auth.service.ts`) |
| Issue / verify token | adapter behind a `TokenIssuer` (or the foundation §4 name) port | same module |
| The guard (`onRequest` / `preValidation` hook) and the current-user decorator | `adapters/http/`, registered on the prefix it protects; the user is loaded through the repository port | the repo's auth plugin |
| Login / register routes | route module in `adapters/http/`, calling use cases built in `bootstrap/` | the repo's auth routes |

## Rules

- The signing key comes from the config parsed at startup with no default; no literal key anywhere in the code;
  `.env.example` has the line. Tests set a test value before building the app.
- Timing-safe check: when no user matches, still verify the password against a precomputed dummy hash before
  answering 401, so an unknown email and a wrong password cost the same time.
- The token carries `sub` = the user id as a string and `exp`. Nothing else the server must trust (no role claim).
- Verifying passes the allowed algorithms as an explicit list, never «whatever the header says». An invalid,
  expired or `sub`-less token, or a user that no longer exists, is 401 with `WWW-Authenticate: Bearer`.
- The guard runs in a hook before validation, registered on the prefix it protects so sibling route plugins
  inherit it (`SKILL.md` → Rule 9). No token → 401, authenticated without the role → 403.
- Role checks load the user from the database on each request and read the stored role, so a role change applies
  on the next request, not when the token expires.
- A role that may complete a named transition is a domain rule: the entity method takes the typed actor (domain
  model). The route guard is the second, separate question (who may call the endpoint at all).
- Login and registration are rate-limited by address and by account where architecture §1 «Решения по
  безопасности» puts it (the app or the proxy in front); the app's limit answers the contract's 429 with
  `Retry-After`. The SRS names the limit (its security checklist, «Rate limiting / abuse resistance»).
- Registration takes the password rule the SRS states — a minimum length and a check against known breached
  passwords, not composition rules — and, when the SRS says so, leaves the account unconfirmed until the emailed
  link is followed.
- Duplicate registration: rely on the unique constraint on email as the last line; the repository classifies its
  violation into a named error (`typescript-drizzle-orm`), answered with the status the contract gives it. A
  pre-check only makes the common case cheaper.
- 401 / 403 / 409 / 429 bodies are the contract's Problem, rendered by the one global error handler (`SKILL.md` →
  Errors); the guard throws named errors, it never builds a body.
