from datetime import date, time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core import AttendanceSessionStatus
from app.exceptions import (
    ConflictException,
    NotAuthorizedException,
    NotFoundException,
)
from app.models import AttendanceSession
from app.schemas import AttendanceSessionCreate, AttendanceSessionUpdate


def make_user(role="admin", user_id=1, email="user@test.com"):
    return SimpleNamespace(user_id=user_id, role=role, email=email)


def make_session(batch_id=10, status=AttendanceSessionStatus.SCHEDULED):
    return SimpleNamespace(
        id=1,
        batch_id=batch_id,
        status=status,
        session_date=date(2026, 11, 20),
        start_time=time(10),
        end_time=time(11),
        topic="Python",
        description=None,
        batch=SimpleNamespace(trainer_id=5),
    )


@pytest.fixture
def session_data():
    return AttendanceSessionCreate(
        batch_id=10,
        session_date=date(2026, 11, 20),
        start_time=time(9),
        end_time=time(10),
        topic="Python",
        status=AttendanceSessionStatus.SCHEDULED,
    )


@pytest.mark.asyncio
async def test_create_success(session_dependencies, session_data):
    d = session_dependencies
    user = make_user()

    d.batch_repository.get_by_id.return_value = SimpleNamespace(id=10)
    created = MagicMock(spec=AttendanceSession)
    d.repository.create.return_value = created

    result = await d.service.create(session_data, user)

    assert result == created
    d.repository.create.assert_awaited_once()
    d.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_batch_not_found(session_dependencies, session_data):
    d = session_dependencies
    d.batch_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await d.service.create(session_data, make_user())

    d.repository.create.assert_not_awaited()
    d.db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_trainer_success(session_dependencies, session_data):
    d = session_dependencies
    user = make_user("trainer")

    d.batch_repository.get_by_id.return_value = SimpleNamespace(trainer_id=5)
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5
    )
    d.repository.create.return_value = make_session()

    result = await d.service.create(session_data, user)

    assert result is not None
    d.repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_trainer_profile_not_found(session_dependencies, session_data):
    d = session_dependencies
    d.batch_repository.get_by_id.return_value = SimpleNamespace(trainer_id=5)
    d.trainer_repository.get_trainer_by_email.return_value = None

    with pytest.raises(NotFoundException):
        await d.service.create(session_data, make_user("trainer"))

    d.repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_trainer_wrong_batch(session_dependencies, session_data):
    d = session_dependencies
    d.batch_repository.get_by_id.return_value = SimpleNamespace(trainer_id=99)
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5
    )

    with pytest.raises(NotAuthorizedException):
        await d.service.create(session_data, make_user("trainer"))

    d.repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_database_failure_rolls_back(session_dependencies, session_data):
    d = session_dependencies
    d.batch_repository.get_by_id.return_value = SimpleNamespace(id=10)
    d.repository.create.side_effect = RuntimeError("Database failure")

    with pytest.raises(RuntimeError):
        await d.service.create(session_data, make_user())

    d.db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_success(session_dependencies):
    d = session_dependencies
    session = make_session()

    d.repository.get_by_id.return_value = session
    d.repository.update.return_value = session

    data = AttendanceSessionUpdate(topic="Advanced Python")

    result = await d.service.update_session(1, data, make_user())

    assert result == session
    d.repository.update.assert_awaited_once()
    d.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_session_not_found(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await d.service.update_session(
            999, AttendanceSessionUpdate(topic="Python"), make_user()
        )

    d.repository.update.assert_not_awaited()


def test_update_invalid_time():
    with pytest.raises(ValidationError, match="End time must be later"):
        AttendanceSessionUpdate(
            start_time=time(11),
            end_time=time(10),
        )


@pytest.mark.asyncio
async def test_update_partial_invalid_time(session_dependencies):
    d = session_dependencies
    session = make_session()  # Existing: 09:00 - 10:00
    d.repository.get_by_id.return_value = session

    # Only changing start time makes it later than existing end time
    data = AttendanceSessionUpdate(
        start_time=time(11),
    )

    with pytest.raises(ConflictException):
        await d.service.update_session(1, data, make_user())

    d.repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_cannot_directly_complete_session(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()

    data = AttendanceSessionUpdate(status=AttendanceSessionStatus.COMPLETED)

    with pytest.raises(ConflictException):
        await d.service.update_session(1, data, make_user())

    d.repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_trainer_unauthorized(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=99
    )

    with pytest.raises(NotAuthorizedException):
        await d.service.update_session(
            1,
            AttendanceSessionUpdate(topic="Updated"),
            make_user("trainer"),
        )

    d.repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_session_not_found(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await d.service.get_session_by_id(1, make_user())


@pytest.mark.asyncio
async def test_get_session_admin_success(session_dependencies):
    d = session_dependencies
    session = make_session()
    d.repository.get_by_id.return_value = session

    result = await d.service.get_session_by_id(1, make_user())

    assert result == session


@pytest.mark.asyncio
async def test_get_session_employee_enrolled(session_dependencies):
    d = session_dependencies
    session = make_session()
    d.repository.get_by_id.return_value = session

    d.employee_repository.get_employee_by_email.return_value = SimpleNamespace(
        employee_id=20
    )
    d.enrollment_repository.get_by_employee_id.return_value = [
        SimpleNamespace(batch_id=10)
    ]

    result = await d.service.get_session_by_id(1, make_user("employee"))

    assert result == session


@pytest.mark.asyncio
async def test_get_session_employee_not_enrolled(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()

    d.employee_repository.get_employee_by_email.return_value = SimpleNamespace(
        employee_id=20
    )
    d.enrollment_repository.get_by_employee_id.return_value = [
        SimpleNamespace(batch_id=99)
    ]

    with pytest.raises(NotAuthorizedException):
        await d.service.get_session_by_id(1, make_user("employee"))


@pytest.mark.asyncio
async def test_get_session_trainer_success(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5, is_active=True
    )

    result = await d.service.get_session_by_id(1, make_user("trainer"))

    assert result.id == 1


@pytest.mark.asyncio
async def test_get_session_inactive_trainer(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5, is_active=False
    )

    with pytest.raises(NotAuthorizedException):
        await d.service.get_session_by_id(1, make_user("trainer"))


@pytest.mark.asyncio
async def test_get_all_admin(session_dependencies):
    d = session_dependencies
    d.repository.get_all.return_value = []

    await d.service.get_all_sessions(
        make_user(), MagicMock(model_dump=MagicMock(return_value={}))
    )

    d.repository.get_all.assert_awaited_once_with({"role": "admin"})


@pytest.mark.asyncio
async def test_get_all_trainer(session_dependencies):
    d = session_dependencies
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5
    )
    d.repository.get_all.return_value = []

    filters = MagicMock(model_dump=MagicMock(return_value={"limit": 20}))

    await d.service.get_all_sessions(make_user("trainer"), filters)

    d.repository.get_all.assert_awaited_once_with(
        {"limit": 20, "role": "trainer", "trainer_id": 5}
    )


@pytest.mark.asyncio
async def test_get_all_employee(session_dependencies):
    d = session_dependencies
    d.employee_repository.get_employee_by_email.return_value = SimpleNamespace(
        employee_id=20
    )
    d.repository.get_all.return_value = []

    filters = MagicMock(model_dump=MagicMock(return_value={}))

    await d.service.get_all_sessions(make_user("employee"), filters)

    d.repository.get_all.assert_awaited_once_with(
        {"role": "employee", "employee_id": 20}
    )


@pytest.mark.asyncio
async def test_get_by_trainer_id(session_dependencies):
    d = session_dependencies
    d.repository.get_by_trainer_id.return_value = []

    result = await d.service.get_by_trainer_id(5)

    assert result == []
    d.repository.get_by_trainer_id.assert_awaited_once_with(5)


@pytest.mark.asyncio
async def test_get_current_user_sessions_trainer(session_dependencies):
    d = session_dependencies
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=5
    )
    d.repository.get_by_trainer_id.return_value = []

    result = await d.service.get_current_user_sessions(make_user("trainer"))

    assert result == []


@pytest.mark.asyncio
async def test_get_current_user_sessions_employee(session_dependencies):
    d = session_dependencies
    d.employee_repository.get_employee_by_email.return_value = SimpleNamespace(
        employee_id=20
    )
    d.repository.get_by_employee_id.return_value = []

    result = await d.service.get_current_user_sessions(make_user("employee"))

    assert result == []


@pytest.mark.asyncio
async def test_complete_session_success(session_dependencies):
    d = session_dependencies
    session = make_session()
    d.repository.get_by_id.return_value = session
    d.repository.complete.return_value = session

    result = await d.service.complete_session(1, make_user())

    assert result == session
    d.record_repository.finalize_session_attendance.assert_awaited_once_with(
        session_id=1,
        batch_id=10,
        marked_by=1,
    )
    d.repository.complete.assert_awaited_once_with(session)
    d.db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_session_not_found(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await d.service.complete_session(1, make_user())

    d.record_repository.finalize_session_attendance.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_session_trainer_unauthorized(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()
    d.trainer_repository.get_trainer_by_email.return_value = SimpleNamespace(
        trainer_id=99
    )

    with pytest.raises(NotAuthorizedException):
        await d.service.complete_session(1, make_user("trainer"))

    d.repository.complete.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_session_rollback(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()
    d.repository.complete.side_effect = RuntimeError("Database failure")

    with pytest.raises(RuntimeError):
        await d.service.complete_session(1, make_user())

    d.db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_summary_success(session_dependencies):
    d = session_dependencies
    session = make_session()
    d.repository.get_by_id.return_value = session

    d.repository.get_session_attendance_summary.return_value = {
        "total_records": 10,
        "present": 8,
        "absent": 2,
    }

    result = await d.service.get_session_summary(1, make_user())

    assert result["total enrollments"] == 10
    assert result["present"] == 8
    assert result["absent"] == 2
    assert result["unmarked"] == 0
    assert result["attendance_percentage"] == 80.0
    assert result["is_finalized"] is False


@pytest.mark.asyncio
async def test_session_summary_cancelled(session_dependencies):
    d = session_dependencies
    session = make_session(status=AttendanceSessionStatus.CANCELLED)
    d.repository.get_by_id.return_value = session

    d.repository.get_session_attendance_summary.return_value = {
        "total_records": 10,
        "present": 8,
        "absent": 2,
    }

    result = await d.service.get_session_summary(1, make_user())

    assert result["attendance_percentage"] is None


@pytest.mark.asyncio
async def test_session_summary_zero_records(session_dependencies):
    d = session_dependencies
    d.repository.get_by_id.return_value = make_session()

    d.repository.get_session_attendance_summary.return_value = {
        "total_records": 0,
        "present": 0,
        "absent": 0,
    }

    with pytest.raises(ZeroDivisionError):
        await d.service.get_session_summary(1, make_user())
