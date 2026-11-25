from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.assessment import Assessment
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.models.batch import Batch
from app.models.employee import EmployeeData
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.assessment_result_schema import (
    AssessmentCancelRequest,
    AssessmentGradeRequest,
)
from app.services.implementations.assessment_result_service import (
    AssessmentResultService,
)


def create_result_service():
    result_repo = AsyncMock()
    assessment_repo = AsyncMock()
    batch_repo = AsyncMock()
    employee_repo = AsyncMock()
    service = AssessmentResultService(
        result_repo=result_repo,
        assessment_repo=assessment_repo,
        batch_repo=batch_repo,
        employee_repo=employee_repo,
    )
    return service, result_repo, assessment_repo, batch_repo, employee_repo


async def test_assign_assessment_scheduled_date_passed(
    sample_assessment: Assessment, sample_batch: Batch
):
    service, _, assessment_repo, batch_repo, _ = create_result_service()
    sample_assessment.scheduled_date_time = datetime.now() - timedelta(days=1)
    assessment_repo.get_assessment_by_id.return_value = sample_assessment
    batch_repo.get_by_id.return_value = sample_batch

    with pytest.raises(BadRequestException) as exc_info:
        await service.assign_assessment_to_batch(sample_assessment.id)

    assert "already passed" in str(exc_info.value.detail).lower()


async def test_assign_assessment_all_already_assigned(
    sample_assessment: Assessment,
    sample_batch: Batch,
    sample_enrollment: Enrollment,
):
    service, result_repo, assessment_repo, batch_repo, _ = create_result_service()
    sample_assessment.scheduled_date_time = datetime.now() + timedelta(days=5)
    assessment_repo.get_assessment_by_id.return_value = sample_assessment
    batch_repo.get_by_id.return_value = sample_batch
    result_repo.get_active_enrollments_for_batch.return_value = [sample_enrollment]
    result_repo.get_assigned_enrollment_ids.return_value = {
        sample_enrollment.enrollment_id
    }

    response = await service.assign_assessment_to_batch(sample_assessment.id)

    assert response.assigned_count == 0
    assert response.skipped_count == 1
    assert "already assigned" in response.message


async def test_assign_assessment_success(
    sample_assessment: Assessment,
    sample_batch: Batch,
    sample_enrollment: Enrollment,
):
    service, result_repo, assessment_repo, batch_repo, _ = create_result_service()
    sample_assessment.scheduled_date_time = datetime.now() + timedelta(days=5)
    assessment_repo.get_assessment_by_id.return_value = sample_assessment
    batch_repo.get_by_id.return_value = sample_batch
    result_repo.get_active_enrollments_for_batch.return_value = [sample_enrollment]
    result_repo.get_assigned_enrollment_ids.return_value = set()

    mock_created = [
        AssessmentResult(
            id=1,
            assessment_id=sample_assessment.id,
            enrollment_id=sample_enrollment.enrollment_id,
            status=AssessmentResultStatus.PENDING,
        )
    ]
    result_repo.bulk_create.return_value = mock_created

    response = await service.assign_assessment_to_batch(sample_assessment.id)

    assert response.assigned_count == 1
    assert response.assigned_enrollment_ids == [sample_enrollment.enrollment_id]


async def test_get_my_assessments_success(
    mock_employee_user: User,
    sample_employee: EmployeeData,
    sample_assessment_result: AssessmentResult,
):
    service, result_repo, _, _, employee_repo = create_result_service()
    employee_repo.get_employee_by_email.return_value = sample_employee
    result_repo.get_results_by_employee_id.return_value = [sample_assessment_result]

    results = await service.get_my_assessments(mock_employee_user)

    assert len(results) == 1
    assert results[0].result_id == sample_assessment_result.id
    assert results[0].title == sample_assessment_result.assessment.title


async def test_get_result_by_id_other_employee_forbidden(
    mock_employee_user: User,
    sample_assessment_result: AssessmentResult,
):
    service, result_repo, _, _, employee_repo = create_result_service()
    result_repo.get_result_by_id_with_details.return_value = sample_assessment_result
    other_employee = EmployeeData(
        employee_id=999, full_name="Other", email="other@example.com", is_active=True
    )
    employee_repo.get_employee_by_email.return_value = other_employee

    with pytest.raises(ForbiddenException) as exc_info:
        await service.get_result_by_id(sample_assessment_result.id, mock_employee_user)

    assert "not authorized to view" in str(exc_info.value.detail).lower()


async def test_submit_assessment_conflict_not_pending(
    mock_employee_user: User, sample_assessment_result: AssessmentResult
):
    service, result_repo, _, _, _ = create_result_service()
    sample_assessment_result.status = AssessmentResultStatus.SUBMITTED
    result_repo.get_result_by_id_with_details.return_value = sample_assessment_result

    with pytest.raises(ConflictException) as exc_info:
        await service.submit_assessment(
            sample_assessment_result.id, None, mock_employee_user
        )

    assert "Cannot submit an assessment that is currently" in str(exc_info.value.detail)


async def test_submit_assessment_success_without_file(
    mock_employee_user: User,
    sample_employee: EmployeeData,
    sample_assessment_result: AssessmentResult,
):
    service, result_repo, _, _, employee_repo = create_result_service()
    today_start = datetime.now() - timedelta(hours=1)
    sample_assessment_result.assessment.scheduled_date_time = today_start
    sample_assessment_result.status = AssessmentResultStatus.PENDING
    result_repo.get_result_by_id_with_details.return_value = sample_assessment_result
    employee_repo.get_employee_by_email.return_value = sample_employee

    async def fake_update(entity, update_data):
        for k, v in update_data.items():
            setattr(entity, k, v)
        return entity

    result_repo.update.side_effect = fake_update

    res = await service.submit_assessment(
        sample_assessment_result.id, None, mock_employee_user
    )

    assert res.status == AssessmentResultStatus.SUBMITTED
    result_repo.update.assert_awaited_once()


@pytest.mark.parametrize(
    "mark,expected_grade",
    [
        (Decimal("75.00"), "PASS"),
        (Decimal("35.00"), "FAIL"),
    ],
)
async def test_grade_assessment_auto_grades(
    sample_assessment_result: AssessmentResult,
    mark: Decimal,
    expected_grade: str,
):
    service, result_repo, _, _, _ = create_result_service()
    sample_assessment_result.status = AssessmentResultStatus.SUBMITTED
    sample_assessment_result.assessment.total_mark = Decimal("100.00")
    sample_assessment_result.assessment.pass_mark = Decimal("50.00")
    result_repo.get_result_by_id_with_details.return_value = sample_assessment_result

    payload = AssessmentGradeRequest(mark=mark)

    async def fake_update(entity, update_data):
        for k, v in update_data.items():
            setattr(entity, k, v)
        return entity

    result_repo.update.side_effect = fake_update

    res = await service.grade_assessment(sample_assessment_result.id, payload)

    assert res.grade == expected_grade
    update_call = result_repo.update.await_args.args[1]
    assert update_call["grade"] == expected_grade
    assert update_call["status"] == AssessmentResultStatus.GRADED


async def test_cancel_assessment_result_success(
    sample_assessment_result: AssessmentResult,
):
    service, result_repo, _, _, _ = create_result_service()
    sample_assessment_result.status = AssessmentResultStatus.PENDING
    result_repo.get_by_id.return_value = sample_assessment_result

    payload = AssessmentCancelRequest(reason="Exemption approved")

    async def fake_update(entity, update_data):
        for k, v in update_data.items():
            setattr(entity, k, v)
        return entity

    result_repo.update.side_effect = fake_update

    res = await service.cancel_assessment_result(sample_assessment_result.id, payload)

    assert res.status == AssessmentResultStatus.CANCELLED
    update_call = result_repo.update.await_args.args[1]
    assert update_call["status"] == AssessmentResultStatus.CANCELLED
    assert "Exemption approved" in update_call["feedback"]
