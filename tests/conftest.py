from collections.abc import AsyncGenerator
from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.models
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.database.base import Base
from app.database.session import get_session
from app.main import app
from app.models.trainer import Trainer
from app.models.user import User

settings = get_settings()

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database="collaborative_work_test",
)


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_session):
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(test_session):
    admin = User(
        username="test_admin",
        email="admin_test@example.com",
        hashed_password=hash_password("Admin@123"),
        role="admin",
        is_active=True,
    )

    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)

    return admin


@pytest_asyncio.fixture
async def trainer_user(test_session):
    user = User(
        username="test_trainer",
        email="trainer_test@gmail.com",
        hashed_password=hash_password("Trainer@123"),
        role="trainer",
        is_active=True,
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest.fixture
def trainer_data():
    return {
        "trainer_name": "testtrainer",
        "dob": "1995-05-10",
        "experience": 3,
        "joining_date": "2024-01-01",
        "specialization": ["Python"],
        "qualification": "MCA",
        "email": "testtrainer@gmail.com",
        "phone_number": "9876543211",
        "address": "Coimbatore",
    }



@pytest_asyncio.fixture
async def trainer_record(test_session, trainer_user):
    trainer = Trainer(
        trainer_name="Test Trainer",
        dob=date(1990, 5, 10),
        experience=5,
        joining_date=date(2022, 1, 1),
        specialization=["Python"],
        qualification="MCA",
        email=trainer_user.email,
        phone_number="9876543210",
        address="Coimbatore",
    )

    test_session.add(trainer)
    await test_session.commit()
    await test_session.refresh(trainer)

    return trainer


@pytest_asyncio.fixture
async def admin_headers(admin_user):
    token = create_access_token(admin_user.user_id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def trainer_headers(trainer_user):
    token = create_access_token(trainer_user.user_id, trainer_user.role)
    return {"Authorization": f"Bearer {token}"}


