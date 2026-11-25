from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.dependencies.auth import get_current_user, require_roles
from app.api.dependencies.performance_dependencies import get_performance_service
from app.models.user import User
from app.schemas.performance_evaluation_schema import (
    PerformanceEvaluationCreate,
    PerformanceEvaluationDetailResponse,
    PerformanceEvaluationUpdate,
    PerformancePreviewResponse,
)
from app.services.interfaces.performance_evaluation_service import (
    PerformanceEvaluationServiceInterface,
)

router = APIRouter(prefix="/api/performance", tags=["Performance Evaluations"])

Performance_Service = Annotated[
    PerformanceEvaluationServiceInterface, Depends(get_performance_service)
]


@router.get(
    "/preview/{enrollment_id}",
    response_model=PerformancePreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview trainee performance metrics",
    description="Pre-calculate objective assessment score percentage and attendance percentage for a trainee prior to evaluation. Restricted to trainers and administrators.",
)
async def preview_performance(
    enrollment_id: Annotated[
        int, Path(description="Unique ID of the trainee enrollment", ge=1)
    ],
    service: Performance_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> PerformancePreviewResponse:
    return await service.get_preview(
        enrollment_id=enrollment_id, current_user=current_user
    )


@router.post(
    "/evaluate",
    response_model=PerformanceEvaluationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create trainee performance evaluation",
    description="Record a performance evaluation for a trainee by scoring communication, behaviour, and teamwork skills. Objective assessment and attendance percentages, final composite score, grade, and certification status are calculated automatically. Restricted to trainers and administrators.",
)
async def evaluate_trainee(
    payload: PerformanceEvaluationCreate,
    service: Performance_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> PerformanceEvaluationDetailResponse:
    return await service.evaluate_trainee(
        payload=payload, current_user=current_user
    )


@router.patch(
    "/evaluate/{evaluation_id}",
    response_model=PerformanceEvaluationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update performance evaluation",
    description="Partially update qualitative scores (communication, behaviour, teamwork) or feedback on an existing evaluation. Recalculates final composite score, grade, and certification status. Restricted to trainers and administrators.",
)
async def update_evaluation(
    evaluation_id: Annotated[
        int, Path(description="Unique ID of the performance evaluation", ge=1)
    ],
    payload: PerformanceEvaluationUpdate,
    service: Performance_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> PerformanceEvaluationDetailResponse:
    return await service.update_evaluation(
        evaluation_id=evaluation_id, payload=payload, current_user=current_user
    )


@router.get(
    "/enrollment/{enrollment_id}",
    response_model=PerformanceEvaluationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get performance evaluation by enrollment ID",
    description="Retrieve the complete performance evaluation card for a specific enrollment. Trainees can only view their own evaluation; trainers and administrators can view any evaluation.",
)
async def get_evaluation_by_enrollment(
    enrollment_id: Annotated[
        int, Path(description="Unique ID of the trainee enrollment", ge=1)
    ],
    service: Performance_Service,
    current_user: User = Depends(get_current_user),
) -> PerformanceEvaluationDetailResponse:
    return await service.get_evaluation_by_enrollment_id(
        enrollment_id=enrollment_id, current_user=current_user
    )
