---
name: python
description: >-
  Internal: Python rules (strict typing, domain exceptions, exhaustive match); read by work's executors before Python
  code.
---

# Python

The same rules as `typescript`, in Python's words. A machine-checked rule is one line with its rule; the config is
`repo-scaffold/references/quality-gates.md`.

## The machine checks

| Rule | Check |
|---|---|
| strict typing, the tests included | `mypy --strict` or pyright `strict` — the checker `repo-scaffold/references/quality-gates.md` names |
| no bare `except`, no `except Exception: pass`, no silent fallback | Ruff `E722`, `BLE001`, `S110` |
| a wrapped exception keeps its cause: `raise StorageWriteFailed("put") from e` | Ruff `B904` |
| a `match` over a union or an enum ends with `case _: assert_never(x)` | the type checker refuses the call when a case is missing — any checker; pyright `reportMatchNotExhaustive` and mypy `exhaustive-match` (opt-in, not part of `--strict`) also catch a `match` written without it |
| an `asyncio.create_task` result is kept; no blocking call inside `async def` | Ruff `RUF006`, `ASYNC` |
| datetimes carry a time zone | Ruff `DTZ` |
| raise idioms, pytest style, FastAPI dependencies with `Annotated` | Ruff `TRY`, `PT`, `FAST`, `UP` |
| output goes through `logging`, never `print` — stdout carries only the JSON lines the formatter in `bootstrap/` writes (`fastapi` → Service endpoints, logs and shutdown) | Ruff `T20` |

## The reviewer checks

1. **A domain exception the route needs to tell apart is a class with fields**, not an empty `pass`; an
   operation's expected failures are a known set of such classes, and the cause travels with `from e`.
2. **One translation of failures to answers**, in one module (the exception handlers), as a `match` closed by
   `assert_never` or a table keyed by the exception class — never a mapper per route.
3. **A failure the user only sees as a generic answer writes one log line** with the cause's name, never secrets,
   keys or addresses.
4. **Impossible states are unrepresentable**: a union of frozen dataclasses with a `Literal` status
   (`Loading | Failed(error) | Ready(data)`), not `is_loading`, `error: str | None` and `data: … | None` side by
   side.
5. **Narrowing is real**: by `match`, `isinstance`, or a `TypeIs` / `TypeGuard` function whose body actually checks
   — a lying guard is worse than a `cast`, and `cast` on outside data is the same lie.
6. **Independent awaits run together** (`asyncio.TaskGroup`, or `gather`); a sequence is a sequence only when one
   needs the other. Not over one `AsyncSession`: a session is one connection (`fastapi-sqlalchemy` → Session and
   unit of work).
7. **Ids of different things are different types** (`NewType("UserId", UUID)` or a value object): a user id is
   not an email, and the checker refuses one where the other is expected.
8. **Closed sets are `Literal` or `StrEnum`; value objects are `@dataclass(frozen=True, slots=True)`**; domain
   collections are tuples or `frozenset`, and a function does not change its arguments — the checker then refuses a
   misspelt status and a value changed after it was checked.
9. **One rule, one module**: a format, a status list, a limit is imported from its owner (the domain model's
   «Кто ещё применяет»), never typed again — a copy matches today and drifts at the next change.
10. **A shared step lives in a module of shared steps**, never imported from another use case's module — otherwise
    a change to one use case silently changes the other.
