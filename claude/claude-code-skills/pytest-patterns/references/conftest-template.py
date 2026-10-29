"""
conftest-template.py — Production-grade root conftest for FastAPI + SQLAlchemy async tests.

Place this file at: tests/conftest.py

Provides:
  - A PostgreSQL test database migrated by the project's own migration command, and the
    async SQLAlchemy engine and per-test session over it
  - httpx.AsyncClient fixture wired to the FastAPI app with DB override
  - Authentication helper fixtures (persisted standard user and admin user)
  - Sample data fixtures (built by factories, persisted through db_session)

Nothing here is autouse: `engine` is created only when a test requests a DB fixture,
so unit tests run without a database. Factory session wiring (autouse) goes into
tests/integration/conftest.py — see SKILL.md, "Test layout".

Dependencies:
  pip install pytest pytest-asyncio httpx sqlalchemy[asyncio] asyncpg factory-boy

Requires asyncio_mode = "auto", asyncio_default_test_loop_scope = "session" and
asyncio_default_fixture_loop_scope = "session" in [tool.pytest.ini_options]. The session-scoped `engine`
must share the event loop with the tests that use it; which options set fixture and test
loop scope depends on the installed pytest-asyncio — check it (references/version-checks.md,
"Event-loop scope") before copying this file.

The session options in `db_session` and the ASGITransport wiring in `client` are
version-sensitive too (same file): verify them against the installed SQLAlchemy and
httpx rather than trusting this template.

Requires a reachable PostgreSQL test database (e.g. `docker run -e POSTGRES_PASSWORD=postgres
-e POSTGRES_DB=app_test -p 5433:5432 postgres`), named by TEST_DATABASE_URL. The schema is dropped and
rebuilt here, so the URL is required, its database name contains «test», and outside CI it differs from
DATABASE_URL (locally a database of its own, not the one a running stand serves): a default address once
pointed these tests at a running stand and wiped its data.
House convention: test on the project's real engine, not SQLite.

The schema comes from the SQL files in documentation/db/migrations/, applied by the same
command production uses (`alembic upgrade head`), never from `Base.metadata.create_all`: the
CHECK constraints, the project schema and every object the files create take part in the tests,
and a model that disagrees with the files fails here (fastapi-sqlalchemy → Migrations). The
command runs as its own process because an async Alembic env.py calls asyncio.run, which cannot
run inside the tests' event loop. Only a brownfield repo with no migration files at all keeps
create_all — the commented fallback in `engine`.
"""

import asyncio
import os
import subprocess

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

os.environ.setdefault("SECRET_KEY", "test-secret-not-for-production")  # before importing src.*

# Placeholders — import from where the project really keeps each piece:
#   with an architecture document, the foundation §5 paths, e.g.
#     app                  <root>.bootstrap.main
#     Base, UserRecord     <root>.<area>.adapters.persistence (storage records, not entities)
#     get_db               the session dependency adapters/http resolves
#     create_access_token  the token adapter behind the TokenIssuer port
#   brownfield, the repo's own modules (e.g. src.main, src.database, src.auth.service).
from src.main import app  # noqa: E402
from src.database import get_db  # noqa: E402
from src.auth.models import User  # noqa: E402
from src.auth.service import create_access_token  # noqa: E402

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")


def _refuse_unsafe_test_database() -> None:
    """No default address: fail the database tests rather than drop a schema a stand or a person uses."""
    name = TEST_DATABASE_URL.rsplit("/", 1)[-1].split("?", 1)[0]
    same_as_app = TEST_DATABASE_URL == os.environ.get("DATABASE_URL") and not os.environ.get("CI")
    if not TEST_DATABASE_URL or "test" not in name or same_as_app:
        pytest.fail(
            "TEST_DATABASE_URL must name a separate test database (its name contains «test»; outside CI "
            "not DATABASE_URL): these tests drop and rebuild its schema",
            pytrace=False,
        )

# The project schema the migrations create and set as search_path (db-schema-design §0) — placeholder.
PROJECT_SCHEMA = "app"
# The command `make migrate` runs; the project's env.py reads the database URL from DATABASE_URL.
MIGRATE_COMMAND = ["uv", "run", "alembic", "upgrade", "head"]


# ─── Engine & Session ────────────────────────────────────────────────────────────

# pytest-asyncio 1.x runs each test in a function-scoped loop by default; a session engine must live in the
# session loop: `loop_scope="session"` here, and `asyncio_default_test_loop_scope = "session"` plus
# `asyncio_default_fixture_loop_scope = "session"` in pytest config (unset, a fixture's loop follows its own scope).
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine():
    """Migrate a clean project schema once per session with the project's command; drop it at the end."""
    _refuse_unsafe_test_database()
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"server_settings": {"search_path": PROJECT_SCHEMA}},  # asyncpg; psycopg: options=-csearch_path=
    )
    async with engine.begin() as conn:  # a run that was killed may have left the schema behind
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{PROJECT_SCHEMA}" CASCADE'))
    await asyncio.to_thread(  # its own process, off the event loop (Ruff ASYNC221)
        subprocess.run, MIGRATE_COMMAND, env={**os.environ, "DATABASE_URL": TEST_DATABASE_URL}, check=True
    )
    # Brownfield repo with no migration files at all — the only case for create_all:
    #     async with engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{PROJECT_SCHEMA}" CASCADE'))
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Outer transaction per test; code under test may call commit() — it only releases a SAVEPOINT."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


# ─── HTTP Client ─────────────────────────────────────────────────────────────────

@pytest.fixture
async def client(db_session: AsyncSession):
    """
    Async HTTP client pointing at the FastAPI app.

    The app's database dependency is overridden to use the test session,
    so all requests share the same transactional session (and its rollback).
    """
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── Authentication Helpers ──────────────────────────────────────────────────────

# Tokens carry only sub=str(user.id); get_current_user loads the row and admin
# checks read user.is_admin, so the user must exist in db_session.

def _make_auth_headers(user: User) -> dict[str, str]:
    """Create Authorization headers with a JWT for a persisted user."""
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(sample_user: User) -> dict[str, str]:
    """Authorization headers for sample_user (is_admin=False)."""
    return _make_auth_headers(sample_user)


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    """Authorization headers for admin_user (is_admin=True)."""
    return _make_auth_headers(admin_user)


@pytest.fixture
async def authenticated_client(client: AsyncClient, auth_headers: dict) -> AsyncClient:
    """AsyncClient pre-configured with standard user auth headers."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
async def admin_client(client: AsyncClient, admin_headers: dict) -> AsyncClient:
    """AsyncClient pre-configured with admin auth headers."""
    client.headers.update(admin_headers)
    return client


# ─── Sample Data Fixtures ────────────────────────────────────────────────────────
# .build() needs no factory session; the fixture adds and flushes explicitly.

@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create and persist a standard user for tests that need an existing user."""
    from tests.factories.user_factory import UserFactory

    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create and persist an admin user (is_admin=True)."""
    from tests.factories.user_factory import UserFactory

    user = UserFactory.build(admin=True)
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def sample_order(db_session: AsyncSession, sample_user):
    """Create and persist an order linked to the sample_user."""
    from tests.factories.order_factory import OrderFactory

    order = OrderFactory.build(user=sample_user)
    db_session.add(order)
    await db_session.flush()
    return order
