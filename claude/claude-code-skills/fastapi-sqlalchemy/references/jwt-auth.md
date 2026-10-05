# Password login with JWT

Read this only when the task implements registration, login or protected routes. The decisions themselves — token kind and lifetime, where the token travels, hashing, roles — come from architecture §1 «Решения по безопасности», or, with no architecture document, from the existing code or the user. If those name sessions, cookies or an external identity provider instead, follow them and skip this file.

## Libraries (house choice)

- Tokens: PyJWT (`import jwt`). Password hashing: `pwdlib` with the Argon2 extra (`PasswordHash`). Not `python-jose`, `passlib` or `bcrypt` directly, and never a bare `hashlib` digest for passwords.
- Check current releases and the signatures you call against the installed versions (SKILL.md → Version-sensitive behaviour).

## Where the pieces live

| Piece | With an architecture document | Brownfield |
|---|---|---|
| Hash / verify password | adapter behind a `PasswordHasher` port; the use case calls the port | the repo's auth module (e.g. `src/auth/service.py`) |
| Issue / decode token | adapter behind a `TokenIssuer` (or the foundation §4 name) port | same module |
| `get_current_user`, `CurrentUser`, `CurrentAdmin` | `adapters/http/` dependencies; the user is loaded through the repository port | `src/auth/dependencies.py` or where the repo keeps them |
| Login / register routes | router factory in `adapters/http/`, calling use cases built in `bootstrap/` | the repo's auth router |

## Rules

- `SECRET_KEY` comes from settings with no default; no literal signing key anywhere in the code; `.env.example` has the line. Tests set a test value before importing the app.
- Login: a `POST` route taking `OAuth2PasswordRequestForm` (the `username` field carries the email), and `OAuth2PasswordBearer(tokenUrl=...)` names that route's full path exactly — otherwise the docs' Authorize button posts to a route that does not exist.
- Timing-safe check: when no user matches, still verify the password against a precomputed dummy hash before answering 401, so an unknown email and a wrong password cost the same time.
- The token carries `sub = str(user.id)` and `exp` from a timezone-aware UTC `datetime`. Nothing else the server must trust (no role claim).
- Decoding passes `algorithms=[...]` as an explicit list. An invalid, expired or `sub`-less token, or a user that no longer exists, is 401 with `WWW-Authenticate: Bearer`.
- Admin and role checks load the user from the database on each request and read the stored flag or role, so a role change applies on the next request, not when the token expires. No token → 401, authenticated without the role → 403.
- A role that may complete a named transition is a domain rule: the entity method takes the typed actor (domain model). The route guard is the second, separate question (who may call the endpoint at all).
- Duplicate registration: rely on the unique constraint on email as the last line and map its violation to the contract's 409 error; a pre-check only makes the common case cheaper.
- 401 / 403 / 409 bodies follow the contract: problem+json per `documentation/api/openapi.yaml`, or the repo's existing error format when there is no spec.
