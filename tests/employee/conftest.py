"""Employee-only pytest fixtures. Never connect tests to the application DB."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from datetime import date
from collections.abc import AsyncIterator, Callable
from typing import Protocol, TypedDict
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_session
from app.main import app
from app.models import EmployeeData  # registers every ORM relationship
from app.api.dependencies.auth import get_current_user
from app.models.user import User


class SampleEmployeeData(TypedDict):
    full_name: str
    email: str
    phone: str | None
    department: str
    joining_date: str


class RoleUserFactory(Protocol):
    def __call__(self, role: str = "admin") -> User: ...


def _test_database_url() -> URL:
    """Require explicit test credentials, and an exact, dedicated database name."""
    name = os.getenv('TEST_DB_NAME', 'etpms_test_db')
    if name != 'etpms_test_db':
        raise RuntimeError('Refusing unsafe database name: TEST_DB_NAME must be etpms_test_db')
    user = os.getenv('TEST_DB_USER')
    password = os.getenv('TEST_DB_PASSWORD')
    if not user or not password:
        pytest.skip('Set TEST_DB_USER and TEST_DB_PASSWORD to run DB/API tests')
    return URL.create(
        'postgresql+asyncpg', username=user, password=password,
        host=os.getenv('TEST_DB_HOST', '127.0.0.1'),
        port=int(os.getenv('TEST_DB_PORT', '5432')), database=name,
    )

@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    url = _test_database_url()

    engine = create_async_engine(
        url,
        echo=False,
        poolclass=NullPool,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

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
def sample_employee_data() -> SampleEmployeeData:
    return {
        'full_name': 'Test Employee',
        'email': f'employee_{uuid4().hex[:16]}@example.com',
        'phone': None,
        'department': 'Engineering',
        'joining_date': '2024-06-01',
    }


@pytest_asyncio.fixture
async def sample_employee(
    test_session: AsyncSession, sample_employee_data: SampleEmployeeData
) -> EmployeeData:
    values = dict(sample_employee_data)
    values['joining_date'] = date.fromisoformat(sample_employee_data['joining_date'])
    employee = EmployeeData(**values)
    test_session.add(employee)
    await test_session.flush()
    await test_session.refresh(employee)
    return employee


@pytest.fixture
def mock_employee_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_employee_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def role_user() -> RoleUserFactory:
    def factory(role: str = 'admin') -> User:
        return User(user_id=1, username=f'{role}_test', email=f'{role}@example.com',
                    hashed_password='unused', role=role, is_active=True)
    return factory


@pytest_asyncio.fixture
async def client(
    test_session: AsyncSession, role_user: RoleUserFactory
) -> AsyncIterator[AsyncClient]:
    """Your requested override pattern; override auth independently for employee endpoints."""
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield test_session

    async def override_get_current_user() -> User:
        return role_user('admin')

    previous_db = app.dependency_overrides.get(get_session)
    previous_auth = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as http:
            yield http
    finally:
        if previous_db is None:
            app.dependency_overrides.pop(get_session, None)
        else:
            app.dependency_overrides[get_session] = previous_db
        if previous_auth is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = previous_auth


@pytest.fixture
def as_role(role_user: RoleUserFactory) -> Callable[[str], None]:
    """Switch API identity without talking to the auth module or real users table."""
    def switch(role: str) -> None:
        async def override() -> User:
            return role_user(role)
        app.dependency_overrides[get_current_user] = override
    return switch
