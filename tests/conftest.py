"""Isolated database and HTTP fixtures for Batch, Course, Course Content.

Create etpms_test_db separately. This suite never connects to the application's
normal database URL. The same SQLAlchemy schema is created if missing.
"""
import os
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

load_dotenv()

import app.models  # noqa: E402: register all ORM relationships
from app.api.dependencies.auth import get_current_user
from app.database.base import Base
from app.database.session import get_session
from app.main import app
from app.models.course import Course
from app.models.trainer import Trainer


def _test_database_url():
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
async def test_engine():
    engine = create_async_engine(_test_database_url(), echo=False, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
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
def role_user():
    def make(role="admin"):
        return SimpleNamespace(role=role, is_active=True, user_id=1)
    return make


@pytest_asyncio.fixture
async def client(test_session, role_user):
    async def override_get_session():
        yield test_session

    async def override_user():
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
def as_role(role_user):
    def switch(role):
        async def override():
            return role_user(role)
        app.dependency_overrides[get_current_user] = override
    return switch


@pytest_asyncio.fixture
async def sample_course(test_session):
    course = Course(
        course_name="Test course " + uuid4().hex[:12],
        description="pytest", duration_value=2, duration_unit="weeks",
    )
    test_session.add(course)
    await test_session.flush()
    return course


@pytest_asyncio.fixture
async def sample_trainer(test_session):
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
