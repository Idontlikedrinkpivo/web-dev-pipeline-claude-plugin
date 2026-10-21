---
name: python
description: >-
  Python rules agents break by default: strict typing, domain exceptions with fields and `raise … from`, no silent
  except, exhaustive match, closed sets as Literal or StrEnum, aware datetimes, kept asyncio tasks. Use whenever
  Python code is written or reviewed. Not FastAPI, SQLAlchemy or pytest specifics.
---

# Python

The same rules as `typescript`, in Python's words. A machine-checked rule is one line with its rule; the config is
`repo-scaffold/references/quality-gates.md`.

## The machine checks

| Rule | Check |
|---|---|
| strict typing, the tests included | `mypy --strict` or pyright `strict` (ty only beside them while it is in beta) |
| no bare `except`, no `except Exception: pass`, no silent fallback | Ruff `E722`, `BLE001`, `S110` |
| a wrapped exception keeps its cause: `raise StorageWriteFailed("put") from e` | Ruff `B904` |
| a `match` over a union or an enum ends with `assert_never` | pyright `reportMatchNotExhaustive` |
| an `asyncio.create_task` result is kept; no blocking call inside `async def` | Ruff `RUF006`, `ASYNC` |
| datetimes carry a time zone | Ruff `DTZ` |
| raise idioms, pytest style, FastAPI dependencies with `Annotated` | Ruff `TRY`, `PT`, `FAST`, `UP` |

## The reviewer checks

1. **A domain exception the route needs to tell apart is a class with fields**, not an empty `pass` — the
   handler maps it in one place, and the cause travels with `from e`.
2. **A failure the user only sees as a generic answer writes one log line** with the cause's name, never secrets,
   keys or addresses.
3. **Closed sets are `Literal` or `StrEnum`; value objects are `@dataclass(frozen=True, slots=True)`** — the type
   checker then refuses a misspelt status and a value changed after it was checked.
4. **One rule, one module**: a format, a status list, a limit is imported from its owner (the domain model's
   «Кто ещё применяет»), never typed again — a copy matches today and drifts at the next change.
5. **A shared step lives in a module of shared steps**, never imported from another use case's module — otherwise
   a change to one use case silently changes the other.
