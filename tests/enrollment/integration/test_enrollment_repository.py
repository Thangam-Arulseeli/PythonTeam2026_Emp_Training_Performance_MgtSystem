
import pytest

from app.repositories.implementations.enrollment_repository import (
    EnrollmentRepository,
)


@pytest.mark.asyncio
async def test_create_enrollment(db_session,employee,batch):
    repo = EnrollmentRepository(db_session)
    enrollment = await repo.create({
        "employee_id": employee.employee_id,
        "batch_id": batch.id,
        "status": "Enrolled",
    })

    assert enrollment.enrollment_id is not None
    assert enrollment.status == "Enrolled"
    assert enrollment.employee.full_name == "Test Employee"
    assert enrollment.batch.batch_name == "Python Batch 01"


@pytest.mark.asyncio
async def test_get_enrollment_by_id(db_session, enrollment):
    repo = EnrollmentRepository(db_session)
    result = await repo.get_by_id(enrollment.enrollment_id)

    assert result is not None
    assert result.enrollment_id == enrollment.enrollment_id


@pytest.mark.asyncio
async def test_get_enrollment_not_found(db_session):
    repo = EnrollmentRepository(db_session)
    result = await repo.get_by_id(99999)

    assert result is None


@pytest.mark.asyncio
async def test_get_all_enrollments(db_session,enrollment):
    repo = EnrollmentRepository(db_session)
    results, total = await repo.get_all(skip=0, limit=10)

    assert total == 1
    assert len(results) == 1


@pytest.mark.asyncio
async def test_filter_enrollments_by_status(db_session,enrollment):
    repo = EnrollmentRepository(db_session)
    results, total = await repo.get_all(
        skip=0,
        limit=10,
        status="Enrolled",
    )

    assert total == 1
    assert results[0].status == "Enrolled"


@pytest.mark.asyncio
async def test_count_active_enrollments(
    db_session,
    enrollment,
    employee,
):
    repo = EnrollmentRepository(db_session)
    count = await repo.count_active_by_employee(employee.employee_id)
    assert count == 1


@pytest.mark.asyncio
async def test_get_enrollments_by_employee(
    db_session,
    enrollment,
    employee
):
    repo = EnrollmentRepository(db_session)
    results = await repo.get_by_employee_id(employee.employee_id)

    assert len(results) == 1
    assert results[0].employee_id == employee.employee_id


@pytest.mark.asyncio
async def test_get_enrollments_by_batch(
    db_session,
    enrollment,
    batch
):
    repo = EnrollmentRepository(db_session)
    results = await repo.get_by_batch_id(batch.id)

    assert len(results) == 1
    assert results[0].batch_id == batch.id


@pytest.mark.asyncio
async def test_update_enrollment_status(db_session,enrollment):
    repo = EnrollmentRepository(db_session)
    enrollment.status = "Paused"
    enrollment.remarks = "Training postponed"
    result = await repo.update(enrollment)

    assert result.status == "Paused"
    assert result.remarks == "Training postponed"


@pytest.mark.asyncio
async def test_count_paused_enrollment(db_session,enrollment,employee):
    repo = EnrollmentRepository(db_session)
    enrollment.status = "Paused"
    await db_session.commit()
    count = await repo.count_active_by_employee(employee.employee_id)
    assert count == 1
