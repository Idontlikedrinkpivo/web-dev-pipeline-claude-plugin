# Coverage configuration

`pyproject.toml` block for the one threshold in SKILL.md → Coverage. `fail_under` makes a `pytest --cov` run fail below 80% (or the foundation §6 number) without repeating the flag in CI; the matching command line is `uv run pytest --cov=src`. A run without `--cov` (a unit's focused tests) measures nothing and is not held to it.

```toml
[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "src/__init__.py"]  # Alembic's migrations/ sits outside src/
# concurrency = [...]  -- required for async SQLAlchemy code; see below

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ ==",
    "@overload",
]
```

This block alone is not enough for an app that uses SQLAlchemy's async API: without the right `concurrency` setting, lines that run after an awaited DB call are not traced and the report comes out several points low. Which values the installed coverage.py needs is version-sensitive — look it up (`version-checks.md` → coverage of async SQLAlchemy paths) and confirm by comparing the report with and without the setting.
