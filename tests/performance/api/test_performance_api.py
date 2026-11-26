from typing import Generator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.dependencies.performance_dependencies import get_performance_service
from app.main import app
from app.schemas.performance_evaluation_schema import (
    PerformanceEvaluationDetailResponse,
    PerformancePreviewResponse,
)

pytestmark = [pytest.mark.api, pytest.mark.asyncio]
BASE_URL = "/api/performance"


@pytest.fixture
def mock_performance_service() -> Generator[AsyncMock]:
    mock = AsyncMock()
    app.dependency_overrides[get_performance_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_performance_service, None)


async def test_preview_performance_success(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
    sample_preview_response: PerformancePreviewResponse,
):
    as_role("trainer")
    mock_performance_service.get_preview.return_value = sample_preview_response

    response = await client.get(f"{BASE_URL}/preview/201")

    assert response.status_code == 200
    data = response.json()
    assert data["enrollment_id"] == 201
    assert float(data["assessment_score_pct"]) == 80.0
    assert float(data["attendance_pct"]) == 90.0
    mock_performance_service.get_preview.assert_awaited_once()


async def test_preview_performance_employee_forbidden(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
):
    as_role("employee")

    response = await client.get(f"{BASE_URL}/preview/201")

    assert response.status_code == 403
    mock_performance_service.get_preview.assert_not_awaited()


async def test_evaluate_trainee_success(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
    sample_detail_response: PerformanceEvaluationDetailResponse,
):
    as_role("trainer")
    mock_performance_service.evaluate_trainee.return_value = sample_detail_response

    payload = {
        "enrollment_id": 201,
        "communication_score": 85.0,
        "behaviour_score": 90.0,
        "teamwork_score": 85.0,
        "feedback": "Consistent effort and good engagement.",
    }

    response = await client.post(f"{BASE_URL}/evaluate", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 301
    assert data["grade"] == "Good"
    assert data["is_certified"] is True
    mock_performance_service.evaluate_trainee.assert_awaited_once()


async def test_evaluate_trainee_invalid_payload(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
):
    as_role("admin")

    # Score > 100 should fail schema validation with 422
    payload = {
        "enrollment_id": 201,
        "communication_score": 150.0,
        "behaviour_score": 90.0,
        "teamwork_score": 85.0,
    }

    response = await client.post(f"{BASE_URL}/evaluate", json=payload)

    assert response.status_code == 422
    mock_performance_service.evaluate_trainee.assert_not_awaited()


async def test_update_evaluation_success(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
    sample_detail_response: PerformanceEvaluationDetailResponse,
):
    as_role("trainer")
    sample_detail_response.feedback = "Updated feedback."
    mock_performance_service.update_evaluation.return_value = sample_detail_response

    payload = {"communication_score": 90.0, "feedback": "Updated feedback."}

    response = await client.patch(f"{BASE_URL}/evaluate/301", json=payload)

    assert response.status_code == 200
    assert response.json()["feedback"] == "Updated feedback."
    mock_performance_service.update_evaluation.assert_awaited_once()


async def test_get_evaluation_by_enrollment_success(
    client: AsyncClient,
    as_role,
    mock_performance_service: AsyncMock,
    sample_detail_response: PerformanceEvaluationDetailResponse,
):
    as_role("employee")
    mock_performance_service.get_evaluation_by_enrollment_id.return_value = (
        sample_detail_response
    )

    response = await client.get(f"{BASE_URL}/enrollment/201")

    assert response.status_code == 200
    assert response.json()["enrollment_id"] == 201
    mock_performance_service.get_evaluation_by_enrollment_id.assert_awaited_once()
