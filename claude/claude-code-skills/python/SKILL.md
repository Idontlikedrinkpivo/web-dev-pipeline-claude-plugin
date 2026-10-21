---
name: python
description: >-
  Python language rules an agent breaks by default: strict typing with the tests included, domain exceptions with
  fields and `raise … from`, no bare or silent `except`, exhaustive `match` with `assert_never`, closed sets as
  `Literal` or `StrEnum`, frozen value objects, kept asyncio task references, aware datetimes, one home per rule.
  Most are Ruff and type-checker rules (`repo-scaffold/references/quality-gates.md`). Loaded by `work` for every
  Python unit and by `code-review-unit`; use whenever Python code is written or reviewed. Not FastAPI
  (`fastapi`), SQLAlchemy (`fastapi-sqlalchemy`) or tests (`pytest-patterns`).
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
3. **Closed sets are `Literal` or `StrEnum`; value objects are `@dataclass(frozen=True, slots=True)`.**
4. **One rule, one module**: a format, a status list, a limit is imported from its owner (the domain model's
   «Кто ещё применяет»), never typed again.
5. **A shared step lives in a module of shared steps**, never imported from another use case's module.
