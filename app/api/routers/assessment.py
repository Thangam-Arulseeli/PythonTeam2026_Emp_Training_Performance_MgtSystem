from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.assessment_dependencies import get_assessment_service
from app.models.assessment import Assessment
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentPatch,
    AssessmentResponse,
)
from app.services.interfaces.assessment_service import AssessmentServiceInterface

router = APIRouter(prefix="/api/assessment", tags=["Assessments"])

Assessment_Service = Annotated[
    AssessmentServiceInterface, Depends(get_assessment_service)
]


@router.get("/{id}", response_model=AssessmentResponse, status_code=status.HTTP_200_OK)
async def get_assessment_by_id(id: int, service: Assessment_Service) -> Assessment:
    return await service.get_assessment_by_id(id)


@router.post(
    "/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_assessment(
    assessment_data: AssessmentCreate, service: Assessment_Service
) -> Assessment:
    return await service.create_assessment(assessment_data)


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def patch_assessment(
    assessment_id: int, assessment_data: AssessmentPatch, service: Assessment_Service
) -> Assessment:
    return await service.patch_assessment(assessment_id, assessment_data)
