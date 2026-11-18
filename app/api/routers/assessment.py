from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.assessment_dependencies import (
    get_assessment_result_service,
    get_assessment_service,
)
from app.api.dependencies.auth import get_current_user, require_roles
from app.models.assessment import Assessment
from app.models.user import User
from app.schemas.assessment_result_schema import AssessmentAssignResponse
from app.schemas.assessment_schema import (
    AssessmentActivation,
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentListResponse,
    AssessmentPatch,
    AssessmentResponse,
)
from app.services.interfaces.assessment_result_service import (
    AssessmentResultServiceInterface,
)
from app.services.interfaces.assessment_service import AssessmentServiceInterface

router = APIRouter(prefix="/api/assessment", tags=["Assessments"])

Assessment_Service = Annotated[
    AssessmentServiceInterface, Depends(get_assessment_service)
]
Assessment_Result_Service = Annotated[
    AssessmentResultServiceInterface, Depends(get_assessment_result_service)
]


@router.get("/{id}", response_model=AssessmentResponse, status_code=status.HTTP_200_OK)
async def get_assessment_by_id(
    id: int,
    service: Assessment_Service,
    current_user: User = Depends(get_current_user),
) -> Assessment:
    return await service.get_assessment_by_id(id)


@router.post(
    "/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_assessment(
    assessment_data: AssessmentCreate,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.create_assessment(assessment_data)


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def patch_assessment(
    assessment_id: int,
    assessment_data: AssessmentPatch,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.patch_assessment(assessment_id, assessment_data)


@router.patch(
    "/{assessment_id}/activation",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_assessment_activation(
    assessment_id: int,
    status_data: AssessmentActivation,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.update_assessment_activation(
        assessment_id, status_data.is_active
    )


@router.get("/", response_model=AssessmentListResponse, status_code=status.HTTP_200_OK)
async def get_all_assessments(
    filter_params: Annotated[AssessmentFilterParams, Depends()],
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
):
    return await service.get_all_assessments(filter_params)


@router.post(
    "/{assessment_id}/assign",
    response_model=AssessmentAssignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign an assessment to all active trainees in its batch",
)
async def assign_assessment(
    assessment_id: int,
    service: Assessment_Result_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> AssessmentAssignResponse:
    return await service.assign_assessment_to_batch(assessment_id)
