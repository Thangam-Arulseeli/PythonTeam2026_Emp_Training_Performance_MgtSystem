from datetime import date
import pytest
import pytest_asyncio

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from fastapi import HTTPException

from app.core.config import get_settings
from app.database.base import Base

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.employee import EmployeeData
from app.models.employee_document import EmployeeDocument
from app.models.trainer import Trainer
from app.models.trainer_resume import TrainerResume

from app.services.auth_service import AuthService
from app.repositories.implementations.user_repository import UserRepository
from app.repositories.implementations.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth_schema import RegisterRequest


@pytest_asyncio.fixture
async def integration_db():
    settings = get_settings()
    database_url = settings.database_url

    test_db_name = "test_emp_training_db"
    admin_url = database_url.set(database="postgres")

    admin_engine = create_async_engine(
        admin_url,
        isolation_level="AUTOCOMMIT"
    )

    test_engine = None
    database_created = False

    try:
        async with admin_engine.connect() as connection:
            await connection.execute(
                text(f'CREATE DATABASE "{test_db_name}"')
            )

        database_created = True

        test_url = database_url.set(database=test_db_name)
        test_engine = create_async_engine(test_url)

        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(
            test_engine,
            expire_on_commit=False
        )

        async with session_factory() as session:
            yield session

    finally:
        if test_engine is not None:
            await test_engine.dispose()

        if database_created:
            async with admin_engine.connect() as connection:
                await connection.execute(
                    text(f'DROP DATABASE IF EXISTS "{test_db_name}"')
                )
        await admin_engine.dispose()


@pytest.fixture
def real_auth_service():
    return AuthService(
        user_repository=UserRepository(),
        refresh_token_repository=RefreshTokenRepository()
    )



# employee register,login,refresh,logout
@pytest.mark.asyncio
async def test_employee_registration_login_refresh_logout(
    integration_db,
    real_auth_service
):
    employee = EmployeeData(
        full_name="Ramesh Kumar",
        email="integration.employee@gmail.com",
        phone="9876500001",
        department="IT",
        role="employee",
        joining_date=date(2024, 1, 1),
        is_active=True
    )
    integration_db.add(employee)
    await integration_db.commit()
    registration_data = RegisterRequest(
        username="integration_employee",
        email="integration.employee@gmail.com",
        password="Employee123",
        role="employee"
    )

    await real_auth_service.register(
        integration_db,
        registration_data
    )
    user = await UserRepository().get_by_username(
        integration_db,
        "integration_employee"
    )

    assert user is not None
    assert user.email == "integration.employee@gmail.com"
    assert user.role == "employee"


    login_result = await real_auth_service.login(
        integration_db,
        "integration_employee",
        "Employee123"
    )

    assert login_result["access_token"]
    assert login_result["refresh_token"]


    refresh_result = await real_auth_service.refresh_tokens(
        integration_db,
        login_result["refresh_token"]
    )

    assert refresh_result["access_token"]
    assert refresh_result["refresh_token"]


    await real_auth_service.logout(
        integration_db,
        refresh_result["refresh_token"],
        user.user_id
    )
    with pytest.raises(HTTPException) as exc:
        await real_auth_service.refresh_tokens(
            integration_db,
            refresh_result["refresh_token"]
        )

    assert exc.value.status_code == 401


# duplicate registration
@pytest.mark.asyncio
async def test_duplicate_registration(
    integration_db,
    real_auth_service
):
    employee = EmployeeData(
        full_name="Test Employee",
        email="duplicate.employee@gmail.com",
        phone="9876500002",
        department="IT",
        role="employee",
        joining_date=date(2024, 1, 1),
        is_active=True
    )

    integration_db.add(employee)
    await integration_db.commit()

    data = RegisterRequest(
        username="duplicate_user",
        email="duplicate.employee@gmail.com",
        password="Employee123",
        role="employee"
    )

    await real_auth_service.register(integration_db, data)

    with pytest.raises(HTTPException) as exc:
        await real_auth_service.register(integration_db, data)

    assert exc.value.status_code == 409



# checking with wrong email
@pytest.mark.asyncio
async def test_trainer_email_must_match(integration_db):
    trainer = Trainer(
        trainer_name="Test Trainer",
        dob=date(1990, 5, 15),
        experience=5,
        joining_date=date(2023, 1, 1),
        specialization=["Python"],
        qualification="MCA",
        email="integration.trainer@gmail.com",
        phone_number="9876500003",
        address="Coimbatore",
        is_active=True
    )

    integration_db.add(trainer)
    await integration_db.commit()
    repository = UserRepository()
    matching_email = await repository.staff_email_exists(
        integration_db,
        "integration.trainer@gmail.com",
        "trainer"
    )

    different_email = await repository.staff_email_exists(
        integration_db,
        "another.trainer@gmail.com",
        "trainer"
    )

    assert matching_email is True
    assert different_email is False


