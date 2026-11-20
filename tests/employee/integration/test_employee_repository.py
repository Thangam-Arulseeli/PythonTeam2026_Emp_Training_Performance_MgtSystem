from datetime import date
from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.employee import EmployeeData
from app.repositories.implementations.employee_repository import EmployeeRepositoryImpl

pytestmark = pytest.mark.integration


def make_employee(email=None, phone=None):
    return EmployeeData(full_name="Test Person", email=email or f"emp_{uuid4().hex}@example.com", phone=phone, role="employee", department="QA", joining_date=date(2024, 1, 2))


@pytest.mark.asyncio
async def test_create_employee_persists(test_session):
    repo = EmployeeRepositoryImpl(test_session)
    item = await repo.create_employee(make_employee())
    assert item.employee_id is not None
    assert (await repo.get_employee_by_id(item.employee_id)).email == item.email


@pytest.mark.asyncio
async def test_create_employee_duplicate_email_rejected(test_session, sample_employee):
    with pytest.raises(IntegrityError):
        await EmployeeRepositoryImpl(test_session).create_employee(make_employee(email=sample_employee.email))






@pytest.mark.asyncio
async def test_list_active_excludes_inactive(test_session, sample_employee):
    repo = EmployeeRepositoryImpl(test_session)
    await repo.soft_delete_employee(sample_employee)
    assert sample_employee.employee_id not in [x.employee_id for x in await repo.get_all_employees()]


@pytest.mark.asyncio
async def test_list_inactive_returns_inactive(test_session, sample_employee):
    repo = EmployeeRepositoryImpl(test_session)
    await repo.soft_delete_employee(sample_employee)
    assert sample_employee.employee_id in [x.employee_id for x in await repo.get_all_employees_inactive()]








@pytest.mark.asyncio
async def test_update_employee_persists(test_session, sample_employee):
    repo = EmployeeRepositoryImpl(test_session)
    await repo.update_employee(sample_employee, {"full_name":"Changed"})
    assert (await repo.get_employee_by_id(sample_employee.employee_id)).full_name == "Changed"


@pytest.mark.asyncio
async def test_soft_delete_employee(test_session, sample_employee):
    repo = EmployeeRepositoryImpl(test_session)
    result = await repo.soft_delete_employee(sample_employee)
    assert result.is_active is False
    assert await repo.get_employee_by_id(sample_employee.employee_id) is None


@pytest.mark.asyncio
async def test_reactivate_employee(test_session, sample_employee):
    repo = EmployeeRepositoryImpl(test_session)
    await repo.soft_delete_employee(sample_employee)
    result = await repo.reactivate_employee(sample_employee)
    assert result.is_active is True
    assert (await repo.get_employee_by_id(sample_employee.employee_id)).is_active is True




