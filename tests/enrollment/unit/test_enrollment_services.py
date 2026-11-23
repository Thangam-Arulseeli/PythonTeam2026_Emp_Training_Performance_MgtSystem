
import pytest

from pydantic import ValidationError

from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    EnrollmentStatusUpdate,
)
from unittest.mock import AsyncMock, MagicMock

from app.services.implementations.enrollment_service import EnrollmentService
from app.exceptions import (
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
)
from datetime import date, timedelta


#test enrollment schema

def test_valid_enrollment_create():
    data = EnrollmentCreate(employee_id=100, batch_id=1)
    assert data.employee_id == 100
    assert data.batch_id == 1


def test_invalid_employee_id():
    with pytest.raises(ValidationError):
        EnrollmentCreate(employee_id=0,batch_id=1)


def test_invalid_batch_id():
    with pytest.raises(ValidationError):
        EnrollmentCreate(employee_id=100, batch_id=-1)


@pytest.mark.parametrize(
    "status",
    ["Enrolled", "Paused", "Cancelled", "Completed"],
)
def test_valid_enrollment_status(status):
    data = EnrollmentStatusUpdate(status=status)
    assert data.status == status


def test_invalid_enrollment_status():
    with pytest.raises(ValidationError):
        EnrollmentStatusUpdate(status="Pending")


def test_empty_remarks_become_none():
    data = EnrollmentStatusUpdate(status="Enrolled",remarks="   ")
    assert data.remarks is None
    

# test enrollment services 

@pytest.fixture
def service():

    enrollment_repo = AsyncMock()
    employee_repo = AsyncMock()
    batch_repo = AsyncMock()
    trainer_repo = AsyncMock()
    email_service = AsyncMock()

    return EnrollmentService(
        enrollment_repo=enrollment_repo,
        employee_repo=employee_repo,
        batch_repo=batch_repo,
        trainer_repo=trainer_repo,
        email_service=email_service,
    )


@pytest.fixture
def admin_user():
    user = MagicMock()
    user.role = "admin"
    user.email = "admin@gmail.com"

    return user


@pytest.mark.asyncio
async def test_employee_not_found(service, admin_user):
    batch = MagicMock()
    batch.is_active = True
    batch.status = "not_completed"
    batch.start_date = __import__("datetime").date.today()
    batch.end_date = __import__("datetime").date.today()

    service.batch_repo.get_by_id.return_value = batch
    service.employee_repo.get_employee_by_id.return_value = None

    payload = EnrollmentCreate(employee_id=100,batch_id=1)

    with pytest.raises(NotFoundException):
        await service.create_enrollment(payload, admin_user)


@pytest.mark.asyncio
async def test_inactive_batch(service, admin_user):
    batch = MagicMock()
    batch.is_active = False
    batch.status = "not_completed"
    service.batch_repo.get_by_id.return_value = batch

    employee = MagicMock()
    employee.is_active = True
    service.employee_repo.get_employee_by_id.return_value = employee

    payload = EnrollmentCreate(employee_id=100, batch_id=1)

    with pytest.raises(UnprocessableEntityException):
        await service.create_enrollment(payload,admin_user)


@pytest.mark.asyncio
async def test_employee_already_enrolled(service, admin_user):
    batch = MagicMock()
    batch.is_active = True
    batch.status = "not_completed"
    batch.start_date = date.today() + timedelta(days=10)
    batch.end_date = date.today() + timedelta(days=40)
    employee = MagicMock()
    employee.is_active = True

    service.batch_repo.get_by_id.return_value = batch
    service.employee_repo.get_employee_by_id.return_value = employee
    service.enrollment_repo.count_active_by_employee.return_value = 1

    payload = EnrollmentCreate(employee_id=100, batch_id=1)

    with pytest.raises(ConflictException):
        await service.create_enrollment(payload,admin_user)


