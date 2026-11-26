from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.assessment import Assessment, AssessmentType
from app.models.batch import Batch
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentPatch,
)
from app.services.implementations.assessment_service import AssessmentService


def create_service():
    assessment_repo = AsyncMock()
    batch_repo = AsyncMock()
    service = AssessmentService(
        assessment_repository=assessment_repo,
        batch_repository=batch_repo,
    )
    return service, assessment_repo, batch_repo


async def test_get_assessment_by_id_success(sample_assessment: Assessment):
    service, assessment_repo, _ = create_service()
    assessment_repo.get_assessment_by_id.return_value = sample_assessment

    result = await service.get_assessment_by_id(1)

    assert result == sample_assessment
    assessment_repo.get_assessment_by_id.assert_awaited_once_with(1)


async def test_get_assessment_by_id_not_found():
    service, assessment_repo, _ = create_service()
    assessment_repo.get_assessment_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_assessment_by_id(999)

    assert "Assessment not found" in str(exc_info.value.detail)


async def test_create_assessment_success(
    sample_batch: Batch, sample_assessment: Assessment
):
    service, assessment_repo, batch_repo = create_service()
    batch_repo.get_by_id.return_value = sample_batch
    assessment_repo.insert_assessment.return_value = sample_assessment

    payload = AssessmentCreate(
        batch_id=1,
        title="Python Midterm Exam",
        description="Comprehensive midterm test covering OOP and FastAPI",
        assessment_type=AssessmentType.EXAM,
        scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
        total_mark=Decimal("100.00"),
        pass_mark=Decimal("50.00"),
    )

    result = await service.create_assessment(payload)

    assert result == sample_assessment
    batch_repo.get_by_id.assert_awaited_once_with(1)
    assessment_repo.insert_assessment.assert_awaited_once_with(payload)


async def test_create_assessment_batch_inactive(sample_batch: Batch):
    service, _, batch_repo = create_service()
    sample_batch.is_active = False
    batch_repo.get_by_id.return_value = sample_batch

    payload = AssessmentCreate(
        batch_id=1,
        title="Python Midterm Exam",
        description="Comprehensive midterm test covering OOP and FastAPI",
        assessment_type=AssessmentType.EXAM,
        scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
        total_mark=Decimal("100.00"),
        pass_mark=Decimal("50.00"),
    )

    with pytest.raises(BadRequestException) as exc_info:
        await service.create_assessment(payload)

    assert "inactive" in str(exc_info.value.detail).lower()


async def test_create_assessment_date_out_of_range(sample_batch: Batch):
    service, _, batch_repo = create_service()
    sample_batch.start_date = date(2026, 3, 1)
    sample_batch.end_date = date(2026, 5, 31)
    batch_repo.get_by_id.return_value = sample_batch

    payload = AssessmentCreate(
        batch_id=1,
        title="Python Midterm Exam",
        description="Comprehensive midterm test covering OOP and FastAPI",
        assessment_type=AssessmentType.EXAM,
        scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
        total_mark=Decimal("100.00"),
        pass_mark=Decimal("50.00"),
    )

    with pytest.raises(BadRequestException) as exc_info:
        await service.create_assessment(payload)

    assert "must be between the batch start and end dates" in str(exc_info.value.detail)


async def test_patch_assessment_success(sample_assessment: Assessment):
    service, assessment_repo, _ = create_service()
    assessment_repo.get_assessment_by_id.return_value = sample_assessment
    assessment_repo.update_assessment.return_value = sample_assessment

    patch_data = AssessmentPatch(title="Updated Midterm Title")

    result = await service.patch_assessment(1, patch_data)

    assert result == sample_assessment
    assessment_repo.update_assessment.assert_awaited_once()


async def test_patch_assessment_pass_mark_greater_than_total(
    sample_assessment: Assessment,
):
    service, assessment_repo, _ = create_service()
    assessment_repo.get_assessment_by_id.return_value = sample_assessment

    patch_data = AssessmentPatch(pass_mark=Decimal("120.00"))

    with pytest.raises(BadRequestException) as exc_info:
        await service.patch_assessment(1, patch_data)

    assert "Pass mark cannot be greater than total mark" in str(exc_info.value.detail)


async def test_get_all_assessments(sample_assessment: Assessment):
    service, assessment_repo, _ = create_service()
    mock_response = {
        "assessments": [sample_assessment],
        "total": 1,
        "page": 1,
        "limit": 5,
    }
    assessment_repo.get_all_assessments.return_value = mock_response
    filter_params = AssessmentFilterParams(page=1, limit=5)

    result = await service.get_all_assessments(filter_params)

    assert result == mock_response
    assessment_repo.get_all_assessments.assert_awaited_once_with(filter_params)
