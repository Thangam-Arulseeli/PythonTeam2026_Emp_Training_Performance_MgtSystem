from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.enrollment import Enrollment
from app.models.performance_evaluation import PerformanceEvaluation
from app.models.user import User
from app.schemas.performance_evaluation_schema import (
    PerformanceEvaluationCreate,
    PerformanceEvaluationDetailResponse,
    PerformanceEvaluationUpdate,
)
from app.services.implementations.performance_evaluation_service import (
    PerformanceEvaluationService,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


def create_performance_service():
    perf_repo = AsyncMock()
    enrollment_repo = AsyncMock()
    service = PerformanceEvaluationService(
        perf_repo=perf_repo,
        enrollment_repo=enrollment_repo,
    )
    return service, perf_repo, enrollment_repo


async def test_get_preview_success(
    mock_trainer_user: User, sample_enrollment: Enrollment
):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_enrollment_with_details.return_value = sample_enrollment
    perf_repo.get_attendance_stats_for_enrollment.return_value = (20, 18)  # 90.00%
    perf_repo.get_assessment_stats_for_enrollment.return_value = (
        5,
        5,
        Decimal("400.00"),
        Decimal("500.00"),
    )  # 80.00%

    preview = await service.get_preview(sample_enrollment.enrollment_id, mock_trainer_user)

    assert preview.enrollment_id == sample_enrollment.enrollment_id
    assert preview.attendance_pct == Decimal("90.00")
    assert preview.assessment_score_pct == Decimal("80.00")
    perf_repo.get_enrollment_with_details.assert_awaited_once_with(sample_enrollment.enrollment_id)


async def test_get_preview_enrollment_not_found(mock_trainer_user: User):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_enrollment_with_details.return_value = None

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_preview(999, mock_trainer_user)

    assert "Enrollment not found" in str(exc_info.value.detail)


async def test_evaluate_trainee_conflict_already_evaluated(
    mock_trainer_user: User,
    sample_enrollment: Enrollment,
    sample_performance_evaluation: PerformanceEvaluation,
):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_enrollment_with_details.return_value = sample_enrollment
    perf_repo.get_by_enrollment_id.return_value = sample_performance_evaluation

    payload = PerformanceEvaluationCreate(
        enrollment_id=sample_enrollment.enrollment_id,
        communication_score=Decimal("85.00"),
        behaviour_score=Decimal("90.00"),
        teamwork_score=Decimal("85.00"),
    )

    with pytest.raises(ConflictException) as exc_info:
        await service.evaluate_trainee(payload, mock_trainer_user)

    assert "already exists" in str(exc_info.value.detail).lower()


async def test_evaluate_trainee_composite_formula_and_grade(
    mock_trainer_user: User,
    sample_enrollment: Enrollment,
    sample_performance_evaluation: PerformanceEvaluation,
    sample_detail_response: PerformanceEvaluationDetailResponse,
):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_enrollment_with_details.return_value = sample_enrollment
    perf_repo.get_by_enrollment_id.return_value = None
    perf_repo.get_attendance_stats_for_enrollment.return_value = (20, 18)  # 90.00%
    perf_repo.get_assessment_stats_for_enrollment.return_value = (
        5,
        5,
        Decimal("400.00"),
        Decimal("500.00"),
    )  # 80.00%

    perf_repo.create.return_value = sample_performance_evaluation
    perf_repo.get_by_enrollment_with_details.return_value = sample_performance_evaluation

    payload = PerformanceEvaluationCreate(
        enrollment_id=sample_enrollment.enrollment_id,
        communication_score=Decimal("85.00"),
        behaviour_score=Decimal("90.00"),
        teamwork_score=Decimal("85.00"),
        feedback="Consistent effort.",
    )

    result = await service.evaluate_trainee(payload, mock_trainer_user)

    perf_repo.create.assert_awaited_once()
    created_eval: PerformanceEvaluation = perf_repo.create.await_args.args[0]

    # Formula: 0.5*80 + 0.2*90 + 0.1*85 + 0.1*90 + 0.1*85 = 40 + 18 + 8.5 + 9.0 + 8.5 = 84.00
    assert created_eval.final_score == Decimal("84.00")
    assert created_eval.grade == "Good"
    assert created_eval.is_certified is True
    assert result.final_score == Decimal("84.00")


async def test_update_evaluation_recalculates_composite_score(
    mock_trainer_user: User,
    sample_performance_evaluation: PerformanceEvaluation,
):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_by_id.return_value = sample_performance_evaluation
    perf_repo.get_attendance_stats_for_enrollment.return_value = (20, 20)  # 100.00%
    perf_repo.get_assessment_stats_for_enrollment.return_value = (
        5,
        5,
        Decimal("450.00"),
        Decimal("500.00"),
    )  # 90.00%
    perf_repo.get_by_enrollment_with_details.return_value = sample_performance_evaluation

    payload = PerformanceEvaluationUpdate(
        communication_score=Decimal("95.00"),
        behaviour_score=Decimal("95.00"),
        teamwork_score=Decimal("95.00"),
        feedback="Promoted to excellent standing.",
    )

    await service.update_evaluation(sample_performance_evaluation.id, payload, mock_trainer_user)

    perf_repo.update.assert_awaited_once()
    update_data = perf_repo.update.await_args.args[1]

    # Formula: 0.5*90 + 0.2*100 + 0.1*95 + 0.1*95 + 0.1*95 = 45 + 20 + 28.5 = 93.50
    assert update_data["final_score"] == Decimal("93.50")
    assert update_data["grade"] == "Excellent"
    assert update_data["is_certified"] is True


async def test_get_evaluation_by_enrollment_forbidden_other_trainee(
    sample_performance_evaluation: PerformanceEvaluation,
    make_user,
):
    service, perf_repo, _ = create_performance_service()
    perf_repo.get_by_enrollment_with_details.return_value = sample_performance_evaluation

    other_trainee = make_user(
        user_id=99,
        username="other_trainee",
        email="other@example.com",
        role="employee",
    )

    with pytest.raises(ForbiddenException) as exc_info:
        await service.get_evaluation_by_enrollment_id(
            sample_performance_evaluation.enrollment_id, other_trainee
        )

    assert "not authorized to view" in str(exc_info.value.detail).lower()
