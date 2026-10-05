"""
factory-template.py — factory_boy factories for test data generation.

Place factory files at: tests/factories/

Each factory provides:
  - Sensible defaults so tests can create objects with zero arguments
  - Overridable fields for specific test scenarios
  - Sequence-based unique values (emails) to avoid collisions
  - Both in-memory (.build()) and DB-persisted (.create()) usage

Primary keys are left to the database. A factory-assigned id (1, 2, ...) does not
advance the table's identity sequence, so the next row the app inserts gets the
same id and fails on the primary key.

sqlalchemy_session_persistence is left unset here, and the test or fixture awaits
`db_session.flush()` itself after create(). Before setting it to "flush" / "commit",
check whether the installed factory_boy awaits those calls on an AsyncSession
(SKILL.md, "Check before relying on it").

Session wiring goes in tests/integration/conftest.py, never the root conftest:

    @pytest.fixture(autouse=True)
    def set_factory_session(db_session):
        UserFactory._meta.sqlalchemy_session = db_session
        OrderFactory._meta.sqlalchemy_session = db_session
        OrderItemFactory._meta.sqlalchemy_session = db_session

Parents come from SubFactory, which assumes the relationships Order.user and
OrderItem.order. If a model has only the FK column, flush the parent and pass
its id explicitly.

Factories build storage records (SQLAlchemy models) for adapter and API tests.
Entity tests construct domain entities directly and need no factory. The imports
below are placeholders: with an architecture document the records live in
<area>/adapters/persistence/ (foundation §5); brownfield, wherever the repo keeps its models.
UserFactory assumes a record with email, hashed_password, is_admin. The password is hashed once at import: Argon2 is
slow on purpose, and hashing per instance would dominate the test run.

Dependencies:
  pip install factory-boy
"""

import factory
from datetime import datetime, timezone

from src.auth.models import User
from src.auth.service import hash_password
from src.orders.models import Order, OrderItem

TEST_PASSWORD = "test-password"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


# ─── User Factory ────────────────────────────────────────────────────────────────

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for creating User model instances.

    Usage:
        # In-memory (no DB write):
        user = UserFactory.build()

        # Persisted to DB (requires session wiring in tests/integration/conftest.py):
        user = UserFactory.create()
        await db_session.flush()

        # Override defaults:
        admin = UserFactory.build(is_admin=True)

        # Batch:
        users = UserFactory.build_batch(5)
    """

    class Meta:
        model = User
        sqlalchemy_session = None           # Set per-test via conftest fixture

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = TEST_PASSWORD_HASH     # log in with TEST_PASSWORD
    is_admin = False

    class Params:
        """Traits for common variations."""

        admin = factory.Trait(
            is_admin=True,
            email=factory.Sequence(lambda n: f"admin{n}@example.com"),
        )


# ─── Order Factory ───────────────────────────────────────────────────────────────

class OrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for creating Order model instances.

    Usage:
        # Basic order (builds its own user through SubFactory):
        order = OrderFactory.build()

        # Order for a specific user:
        order = OrderFactory.build(user=user)

        # Override status:
        shipped = OrderFactory.build(status="shipped")
    """

    class Meta:
        model = Order
        sqlalchemy_session = None

    user = factory.SubFactory(UserFactory)
    status = "pending"
    total_cents = factory.Faker("random_int", min=500, max=500000)
    currency = "USD"
    notes = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Traits for common order states."""

        completed = factory.Trait(
            status="completed",
        )

        cancelled = factory.Trait(
            status="cancelled",
            notes="Cancelled by customer",
        )


# ─── Order Item Factory ──────────────────────────────────────────────────────────

class OrderItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for creating OrderItem model instances.

    Usage:
        item = OrderItemFactory.build(order=order, product_name="Widget")
    """

    class Meta:
        model = OrderItem
        sqlalchemy_session = None

    order = factory.SubFactory(OrderFactory)
    product_name = factory.Faker("word")
    quantity = factory.Faker("random_int", min=1, max=10)
    unit_price_cents = factory.Faker("random_int", min=100, max=50000)


# ─── Usage Examples ──────────────────────────────────────────────────────────────
#
# # Build without persisting (unit tests):
# user = UserFactory.build()
# user = UserFactory.build(is_admin=True)
# users = UserFactory.build_batch(3)
#
# # Build with trait:
# admin = UserFactory.build(admin=True)
#
# # Persisted (integration tests with conftest session wiring):
# user = UserFactory.create()
# order = OrderFactory.create(user=user)
# await db_session.flush()
#
# # Related objects:
# order = OrderFactory.create()          # also adds its user
# items = OrderItemFactory.create_batch(3, order=order)
# await db_session.flush()
