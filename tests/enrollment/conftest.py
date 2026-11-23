
import os
import sys
from pathlib import Path
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient


# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


# Set test database before importing application modules
os.environ["DB_NAME"] = "employee_training_test"


# import app.models

from app.core.config import get_settings
from app.database.base import Base
from app.database.session import get_session
from app.main import app

from app.api.dependencies.auth import get_current_user

from app.models.user import User
from app.models.employee import EmployeeData
from app.models.course import Course
from app.models.trainer import Trainer
from app.models.batch import Batch
from app.models.enrollment import Enrollment

from app.utils.email_service import EmailService


# Check test database
if get_settings().db_name != "employee_training_test":
    raise RuntimeError("Wrong database selected for testing")


# TEST DATABASE ENGINE
@pytest_asyncio.fixture(loop_scope="function")
async def test_engine():
    test_engine = create_async_engine(
        get_settings().database_url,
        echo=False,
        poolclass=NullPool,
    )
    yield test_engine
    await test_engine.dispose()


# DATABASE FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def db_session(test_engine):
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        autoflush=True,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


# ADMIN USER FIXTURE
@pytest.fixture
def admin_user():
    return User(
        user_id=1,
        username="test_admin",
        email="admin@gmail.com",
        hashed_password="test_password",
        role="admin",
        is_active=True,
    )


# EMPLOYEE FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def employee(db_session):
    employee = EmployeeData(
        full_name="Test Employee",
        email="employee@gmail.com",
        phone="9876543210",
        department="IT",
        role="employee",
        joining_date=date.today(),
        is_active=True,
    )
    db_session.add(employee)
    await db_session.commit()
    await db_session.refresh(employee)

    return employee


# COURSE FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def course(db_session):
    course = Course(
        course_name="Python Testing",
        description="Python testing course",
        duration_value=4,
        duration_unit="weeks",
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    return course


# TRAINER FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def trainer(db_session):
    trainer = Trainer(
        trainer_name="Test Trainer",
        dob=date(1995, 1, 1),
        experience=3,
        joining_date=date.today() - timedelta(days=365),
        specialization=["Python"],
        qualification="MCA",
        email="trainer@gmail.com",
        phone_number="9876543211",
        address="Chennai",
        is_active=True,
    )
    db_session.add(trainer)
    await db_session.commit()
    await db_session.refresh(trainer)

    return trainer


# BATCH FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def batch(db_session, course, trainer):
    batch = Batch(
        batch_name="Python Batch 01",
        course_id=course.id,
        trainer_id=trainer.trainer_id,
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=40),
        status="not_completed",
        is_active=True,
    )
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)

    return batch


# ENROLLMENT FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def enrollment(db_session, employee, batch):
    enrollment = Enrollment(
        employee_id=employee.employee_id,
        batch_id=batch.id,
        status="Enrolled",
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)

    return enrollment


# EMAIL MOCK FIXTURE
@pytest.fixture
def disable_email(monkeypatch):
    async def fake_email(self, *args, **kwargs):
        return True
    monkeypatch.setattr(
        EmailService,
        "send_enrollment_confirmation_async",
        fake_email,
    )
    monkeypatch.setattr(
        EmailService,
        "send_enrollment_status_email_async",
        fake_email,
    )


# API CLIENT FIXTURE
@pytest_asyncio.fixture(loop_scope="function")
async def client(db_session, admin_user, disable_email):

    async def override_get_session():
        yield db_session

    async def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as test_client:
            yield test_client

    finally:
        app.dependency_overrides.clear()


