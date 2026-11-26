from collections.abc import AsyncIterator, Callable
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.assessment_dependencies import (
    get_assessment_result_service,
    get_assessment_service,
)
from app.api.dependencies.auth import get_current_user
from app.main import app
from app.models.assessment import Assessment, AssessmentType
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.models.batch import Batch
from app.models.employee import EmployeeData
from app.models.enrollment import Enrollment
from app.models.user import User


@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make(
        user_id: int = 1,
        username: str = "testuser",
        email: str = "testuser@example.com",
        role: str = "admin",
        is_active: bool = True,
    ) -> User:
        return User(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password="mockhashedpassword",
            role=role,
            is_active=is_active,
        )

    return _make


@pytest.fixture
def mock_admin_user(make_user: Callable[..., User]) -> User:
    return make_user(
        user_id=1, username="admin", email="admin@example.com", role="admin"
    )


@pytest.fixture
def mock_trainer_user(make_user: Callable[..., User]) -> User:
    return make_user(
        user_id=2, username="trainer", email="trainer@example.com", role="trainer"
    )


@pytest.fixture
def mock_employee_user(make_user: Callable[..., User]) -> User:
    return make_user(
        user_id=3, username="employee", email="employee@example.com", role="employee"
    )


@pytest.fixture
def as_role(make_user: Callable[..., User]) -> Callable[[str], User]:
    def switch(role: str) -> User:
        user = make_user(
            user_id=10,
            username=f"{role}_user",
            email=f"{role}@example.com",
            role=role,
        )

        async def override_current_user() -> User:
            return user

        app.dependency_overrides[get_current_user] = override_current_user
        return user

    return switch


@pytest_asyncio.fixture
async def client(mock_admin_user: User) -> AsyncIterator[AsyncClient]:
    original_overrides = dict(app.dependency_overrides)

    async def override_user() -> User:
        return mock_admin_user

    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture
def sample_batch() -> Batch:
    return Batch(
        id=1,
        batch_name="Python Automation 2026",
        course_id=10,
        trainer_id=20,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status="Not Completed",
        is_active=True,
    )


@pytest.fixture
def sample_assessment() -> Assessment:
    return Assessment(
        id=1,
        batch_id=1,
        title="Python Midterm Exam",
        description="Comprehensive midterm test covering OOP and FastAPI",
        assessment_type=AssessmentType.EXAM.value,
        scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
        total_mark=Decimal("100.00"),
        pass_mark=Decimal("50.00"),
        is_active=True,
        created_at=datetime(2026, 1, 15, 10, 0, 0),
        updated_at=datetime(2026, 1, 15, 10, 0, 0),
    )


@pytest.fixture
def sample_employee() -> EmployeeData:
    return EmployeeData(
        employee_id=101,
        full_name="John Doe",
        email="employee@example.com",
        role="employee",
        department="Engineering",
        is_active=True,
    )


@pytest.fixture
def sample_enrollment(sample_employee: EmployeeData) -> Enrollment:
    enrollment = Enrollment(
        enrollment_id=201,
        employee_id=sample_employee.employee_id,
        batch_id=1,
        status="enrolled",
    )
    enrollment.employee = sample_employee
    return enrollment


@pytest.fixture
def sample_assessment_result(
    sample_assessment: Assessment, sample_enrollment: Enrollment
) -> AssessmentResult:
    result = AssessmentResult(
        id=501,
        assessment_id=sample_assessment.id,
        enrollment_id=sample_enrollment.enrollment_id,
        status=AssessmentResultStatus.PENDING,
        mark=None,
        grade=None,
        feedback=None,
        file_name=None,
        file_path=None,
        submitted_date_time=None,
        evaluated_date_time=None,
        created_at=datetime(2026, 6, 1, 10, 0, 0),
        updated_at=datetime(2026, 6, 1, 10, 0, 0),
    )
    result.assessment = sample_assessment
    result.enrollment = sample_enrollment
    return result
