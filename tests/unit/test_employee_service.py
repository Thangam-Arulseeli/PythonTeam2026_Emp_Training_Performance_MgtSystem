from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions.exceptions import (EmployeeAlreadyExistsException,
    EmployeeNotFoundException, InvalidEmployeeDataException)
from app.models.employee import EmployeeData
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.implementations.employee_service import EmployeeServiceImpl

pytestmark = pytest.mark.unit


def employee():
    return EmployeeData(employee_id=100, full_name='Alex', email='alex@example.com',
                        role='employee', department='QA', is_active=True)


def service():
    db = AsyncMock()
    repo = AsyncMock()
    return EmployeeServiceImpl(db, repo), db, repo


def integrity_error(code='23505'):
    return IntegrityError('insert', {}, SimpleNamespace(sqlstate=code))


@pytest.mark.asyncio
async def test_create_success(sample_employee_data):
    svc, db, repo = service()
    async def create(value):
        return value
    repo.create_employee.side_effect = create
    result = await svc.create_employee(EmployeeCreate(**sample_employee_data))
    assert result.email == sample_employee_data['email']
    repo.create_employee.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
@pytest.mark.parametrize('code,error', [('23505', EmployeeAlreadyExistsException),
                                          ('23503', InvalidEmployeeDataException)])
async def test_create_integrity_error(sample_employee_data, code, error):
    svc, db, repo = service()
    repo.create_employee.side_effect = integrity_error(code)
    with pytest.raises(error):
        await svc.create_employee(EmployeeCreate(**sample_employee_data))
    db.rollback.assert_awaited_once()






@pytest.mark.asyncio
async def test_update_success():
    svc, db, repo = service()
    item = employee()
    repo.get_employee_by_id.return_value = item
    repo.update_employee.return_value = item
    await svc.update_employee(100, EmployeeUpdate(role='employee', full_name='Updated'))
    args = repo.update_employee.await_args.args
    assert args[0] is item
    assert args[1] == {'role': 'employee', 'full_name': 'Updated'}
    db.commit.assert_awaited_once()






@pytest.mark.asyncio
@pytest.mark.parametrize('linked', [True, False])
async def test_delete_deactivates_employee_and_optional_user(linked):
    svc, db, repo = service()
    item = employee()
    user = SimpleNamespace(is_active=True) if linked else None
    db.execute.return_value = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = user
    repo.get_employee_by_id.return_value = item
    result = await svc.delete_employee(100)
    assert result['employee_id'] == 100
    if linked:
        assert user.is_active is False
    repo.soft_delete_employee.assert_awaited_once_with(item)
    db.commit.assert_awaited_once()




@pytest.mark.asyncio
@pytest.mark.parametrize('linked', [True, False])
async def test_reactivate_restores_employee_and_optional_user(linked):
    svc, db, repo = service()
    item = employee()
    item.is_active = False
    user = SimpleNamespace(is_active=False) if linked else None
    db.execute.return_value = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = user
    repo.get_inactive_employee_by_id.return_value = item
    repo.reactivate_employee.return_value = item
    assert await svc.reactivate_employee(100) is item
    if linked:
        assert user.is_active is True
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(item)


