from datetime import datetime
from decimal import Decimal
from typing import Generator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.dependencies.assessment_dependencies import (
    get_assessment_result_service,
)
from app.main import app
from app.models.assessment import AssessmentType
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.schemas.assessment_result_schema import (
    AssessmentAssignResponse,
    AssessmentDetailResponse,
    TraineeAssessmentDetailResponse,
)

BASE_URL = "/api/assessment"


@pytest.fixture
def mock_assessment_result_service() -> Generator[AsyncMock]:
    mock = AsyncMock()
    app.dependency_overrides[get_assessment_result_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_assessment_result_service, None)


async def test_assign_assessment_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
):
    as_role("trainer")
    mock_response = AssessmentAssignResponse(
        assessment_id=1,
        batch_id=1,
        assigned_count=3,
        skipped_count=0,
        message="Assessment successfully assigned to 3 trainee(s).",
        assigned_enrollment_ids=[10, 11, 12],
    )
    mock_assessment_result_service.assign_assessment_to_batch.return_value = (
        mock_response
    )

    response = await client.post(f"{BASE_URL}/1/assign")

    assert response.status_code == 201
    assert response.json()["assigned_count"] == 3
    mock_assessment_result_service.assign_assessment_to_batch.assert_awaited_once_with(
        1
    )


async def test_assign_assessment_employee_forbidden(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
):
    as_role("employee")

    response = await client.post(f"{BASE_URL}/1/assign")

    assert response.status_code == 403
    mock_assessment_result_service.assign_assessment_to_batch.assert_not_awaited()


async def test_get_my_assessments_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
):
    as_role("employee")
    mock_items = [
        TraineeAssessmentDetailResponse(
            result_id=1,
            enrollment_id=10,
            status=AssessmentResultStatus.PENDING,
            mark=None,
            grade=None,
            feedback=None,
            file_name=None,
            submitted_date_time=None,
            evaluated_date_time=None,
            assessment_id=1,
            batch_id=1,
            title="Python Midterm",
            description="Test",
            assessment_type=AssessmentType.EXAM,
            scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
            total_mark=Decimal("100.00"),
            pass_mark=Decimal("50.00"),
        )
    ]
    mock_assessment_result_service.get_my_assessments.return_value = mock_items

    response = await client.get(f"{BASE_URL}/my-assessments")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_assessment_result_service.get_my_assessments.assert_awaited_once()


async def test_get_result_by_id_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
):
    as_role("employee")
    mock_item = TraineeAssessmentDetailResponse(
        result_id=100,
        enrollment_id=10,
        status=AssessmentResultStatus.PENDING,
        mark=None,
        grade=None,
        feedback=None,
        file_name=None,
        submitted_date_time=None,
        evaluated_date_time=None,
        assessment_id=1,
        batch_id=1,
        title="Python Midterm",
        description="Test",
        assessment_type=AssessmentType.EXAM,
        scheduled_date_time=datetime(2026, 6, 15, 10, 0, 0),
        total_mark=Decimal("100.00"),
        pass_mark=Decimal("50.00"),
    )
    mock_assessment_result_service.get_result_by_id.return_value = mock_item

    response = await client.get(f"{BASE_URL}/results/100")

    assert response.status_code == 200
    assert response.json()["result_id"] == 100


async def test_get_results_by_assessment_id_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
):
    as_role("trainer")
    mock_results = [
        AssessmentDetailResponse(
            result_id=1,
            assessment_id=1,
            enrollment_id=10,
            employee_id=101,
            employee_name="John Doe",
            employee_email="john@example.com",
            status=AssessmentResultStatus.SUBMITTED,
            mark=None,
            grade=None,
            feedback=None,
            file_name="solution.pdf",
            submitted_date_time=datetime(2026, 6, 15, 11, 0, 0),
            evaluated_date_time=None,
        )
    ]
    mock_assessment_result_service.get_results_by_assessment_id.return_value = (
        mock_results
    )

    response = await client.get(f"{BASE_URL}/1/results")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_assessment_result_service.get_results_by_assessment_id.assert_awaited_once_with(
        1
    )


async def test_submit_assessment_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
    sample_assessment_result: AssessmentResult,
):
    as_role("employee")
    sample_assessment_result.status = AssessmentResultStatus.SUBMITTED
    mock_assessment_result_service.submit_assessment.return_value = (
        sample_assessment_result
    )

    response = await client.post(
        f"{BASE_URL}/results/{sample_assessment_result.id}/submit"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    mock_assessment_result_service.submit_assessment.assert_awaited_once()


async def test_grade_assessment_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
    sample_assessment_result: AssessmentResult,
):
    as_role("trainer")
    sample_assessment_result.status = AssessmentResultStatus.GRADED
    sample_assessment_result.mark = Decimal("85.00")
    sample_assessment_result.grade = "PASS"
    sample_assessment_result.feedback = "Well done!"
    mock_assessment_result_service.grade_assessment.return_value = (
        sample_assessment_result
    )

    payload = {
        "mark": 85.0,
        "grade": "PASS",
        "feedback": "Well done!",
    }

    response = await client.post(
        f"{BASE_URL}/results/{sample_assessment_result.id}/grade",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "graded"
    assert float(data["mark"]) == 85.0
    mock_assessment_result_service.grade_assessment.assert_awaited_once()


async def test_cancel_assessment_result_success(
    client: AsyncClient,
    as_role,
    mock_assessment_result_service: AsyncMock,
    sample_assessment_result: AssessmentResult,
):
    as_role("admin")
    sample_assessment_result.status = AssessmentResultStatus.CANCELLED
    sample_assessment_result.feedback = "Cancelled: Medical leave"
    mock_assessment_result_service.cancel_assessment_result.return_value = (
        sample_assessment_result
    )

    payload = {"reason": "Medical leave"}

    response = await client.patch(
        f"{BASE_URL}/results/{sample_assessment_result.id}/cancel",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    mock_assessment_result_service.cancel_assessment_result.assert_awaited_once()
