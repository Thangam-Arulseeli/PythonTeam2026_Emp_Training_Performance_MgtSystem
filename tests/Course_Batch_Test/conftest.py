"""Isolated database and HTTP fixtures for Batch, Course, Course Content.

Create etpms_test_db separately. This suite never connects to the application's
normal database URL. The same SQLAlchemy schema is created if missing.
"""
import os
from collections.abc import AsyncIterator, Callable
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

load_dotenv()

import app.models  # noqa: E402: register all ORM relationships
from app.api.dependencies.auth import get_current_user
from app.database.base import Base
from app.database.session import get_session
from app.main import app
from app.models.course import Course
from app.models.trainer import Trainer


def _test_database_url() -> URL:
    name = os.getenv("TEST_DB_NAME", "etpms_test_db")
    if name != "etpms_test_db":
        raise RuntimeError("Refusing unsafe database: TEST_DB_NAME must equal etpms_test_db")
    user = os.getenv("TEST_DB_USER")
    password = os.getenv("TEST_DB_PASSWORD")
    if not user or not password:
        pytest.skip("Set TEST_DB_USER and TEST_DB_PASSWORD to enable database-backed tests")
    return URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=os.getenv("TEST_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=name,
    )


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(_test_database_url(), echo=False, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # create_all() creates missing tables but does not update existing
            # tables. Keep the dedicated test database aligned with the current
            # batch model when it was created by an older test run.
            await conn.execute(
                text(
                    "ALTER TABLE batches "
                    "ADD COLUMN IF NOT EXISTS end_date_remark TEXT"
                )
            )
            await conn.execute(
                text("ALTER TABLE batches DROP CONSTRAINT IF EXISTS ck_batch_status")
            )
            await conn.execute(
                text(
                    "UPDATE batches SET status = CASE status "
                    "WHEN 'completed' THEN 'Completed' "
                    "WHEN 'not_completed' THEN 'Not Completed' ELSE status END"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE batches ALTER COLUMN status "
                    "SET DEFAULT 'Not Completed'"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE batches ADD CONSTRAINT ck_batch_status "
                    "CHECK (status IN ('Completed', 'Not Completed'))"
                )
            )
            await conn.execute(
                text("ALTER TABLE batches DROP CONSTRAINT IF EXISTS ck_batch_dates")
            )
            await conn.execute(
                text(
                    "ALTER TABLE batches ADD CONSTRAINT ck_batch_dates "
                    "CHECK (end_date >= start_date)"
                )
            )
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as db:
            try:
                yield db
            finally:
                await db.close()
                if transaction.is_active:
                    await transaction.rollback()


@pytest.fixture
def role_user() -> Callable[[str], SimpleNamespace]:
    def make(role: str = "admin") -> SimpleNamespace:
        return SimpleNamespace(role=role, is_active=True, user_id=1)
    return make


@pytest_asyncio.fixture
async def client(
    test_session: AsyncSession,
    role_user: Callable[[str], SimpleNamespace],
) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield test_session

    async def override_user() -> SimpleNamespace:
        return role_user("admin")

    original = dict(app.dependency_overrides)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_user
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original)


@pytest.fixture
def as_role(role_user: Callable[[str], SimpleNamespace]) -> Callable[[str], None]:
    def switch(role: str) -> None:
        async def override() -> SimpleNamespace:
            return role_user(role)
        app.dependency_overrides[get_current_user] = override
    return switch


@pytest_asyncio.fixture
async def sample_course(test_session: AsyncSession) -> AsyncIterator[Course]:
    course = Course(
        course_name="Test course " + uuid4().hex[:12],
        description="pytest", duration_value=2, duration_unit="weeks",
    )
    test_session.add(course)
    await test_session.flush()
    return course


@pytest_asyncio.fixture
async def sample_trainer(test_session: AsyncSession) -> AsyncIterator[Trainer]:
    key = uuid4().hex[:12]
    trainer = Trainer(
        trainer_name="Trainer " + key, dob=date(1990, 1, 1),
        experience=5, joining_date=date(2020, 1, 1),
        specialization=["python"], qualification="BSc",
        email=key + "@example.com",
        phone_number="9" + str(int(key[:8], 16)).zfill(10)[-9:],
        address="Test address",
    )
    test_session.add(trainer)
    await test_session.flush()
    return trainer
