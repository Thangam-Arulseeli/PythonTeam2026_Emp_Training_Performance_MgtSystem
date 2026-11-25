from unittest.mock import AsyncMock
from typing import Generator
import pytest
from httpx import AsyncClient

from app.api.dependencies.assessment_dependencies import get_assessment_service
from app.exceptions.custom_exceptions import NotFoundException
from app.main import app
from app.models.assessment import Assessment
from app.schemas.assessment_schema import AssessmentListResponse, AssessmentResponse

BASE_URL = "/api/assessment"


@pytest.fixture
def mock_assessment_service() -> Generator[AsyncMock]:
    mock = AsyncMock()
    app.dependency_overrides[get_assessment_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_assessment_service, None)


async def test_create_assessment_success(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
    sample_assessment: Assessment,
):
    as_role("trainer")
    mock_assessment_service.create_assessment.return_value = sample_assessment

    payload = {
        "batch_id": 1,
        "title": "Python Midterm Exam",
        "description": "Comprehensive midterm test covering OOP and FastAPI",
        "assessment_type": "exam",
        "scheduled_date_time": "2026-06-15T10:00:00",
        "total_mark": 100.0,
        "pass_mark": 50.0,
    }

    response = await client.post(f"{BASE_URL}/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == sample_assessment.id
    assert data["title"] == sample_assessment.title
    mock_assessment_service.create_assessment.assert_awaited_once()


async def test_create_assessment_employee_forbidden(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
):
    as_role("employee")

    payload = {
        "batch_id": 1,
        "title": "Python Midterm Exam",
        "assessment_type": "exam",
        "scheduled_date_time": "2026-06-15T10:00:00",
        "total_mark": 100.0,
        "pass_mark": 50.0,
    }

    response = await client.post(f"{BASE_URL}/", json=payload)

    assert response.status_code == 403
    mock_assessment_service.create_assessment.assert_not_awaited()


async def test_create_assessment_invalid_payload(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
):
    as_role("admin")

    # Invalid marks and missing required title
    payload = {
        "batch_id": 1,
        "assessment_type": "exam",
        "total_mark": -10,
    }

    response = await client.post(f"{BASE_URL}/", json=payload)

    assert response.status_code == 422
    mock_assessment_service.create_assessment.assert_not_awaited()


async def test_get_assessment_by_id_success(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
    sample_assessment: Assessment,
):
    as_role("employee")
    mock_assessment_service.get_assessment_by_id.return_value = sample_assessment

    response = await client.get(f"{BASE_URL}/{sample_assessment.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_assessment.id
    assert data["title"] == sample_assessment.title
    mock_assessment_service.get_assessment_by_id.assert_awaited_once_with(
        sample_assessment.id
    )


async def test_get_assessment_by_id_not_found(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
):
    as_role("admin")
    mock_assessment_service.get_assessment_by_id.side_effect = NotFoundException(
        "Assessment not found."
    )

    response = await client.get(f"{BASE_URL}/999")

    assert response.status_code == 404
    mock_assessment_service.get_assessment_by_id.assert_awaited_once_with(999)


async def test_patch_assessment_success(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
    sample_assessment: Assessment,
):
    as_role("trainer")
    mock_assessment_service.patch_assessment.return_value = sample_assessment

    payload = {"title": "Updated Assessment Title"}

    response = await client.patch(f"{BASE_URL}/{sample_assessment.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_assessment.id
    mock_assessment_service.patch_assessment.assert_awaited_once()


async def test_get_all_assessments_success(
    client: AsyncClient,
    as_role,
    mock_assessment_service: AsyncMock,
    sample_assessment: Assessment,
):
    as_role("trainer")
    mock_response = AssessmentListResponse(
        assessments=[AssessmentResponse.model_validate(sample_assessment)],
        total=1,
        page=1,
        limit=5,
    )
    mock_assessment_service.get_all_assessments.return_value = mock_response

    response = await client.get(f"{BASE_URL}/?page=1&limit=5&batch_id=1")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["assessments"]) == 1
    mock_assessment_service.get_all_assessments.assert_awaited_once()
