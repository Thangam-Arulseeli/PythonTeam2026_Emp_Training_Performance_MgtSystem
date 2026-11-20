from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import require_roles
from app.api.dependencies.enrollment_dependencies import get_enrollment_service
from app.models.user import User
from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    EnrollmentListResponse,
    EnrollmentResponse,
    EnrollmentStatus,
    EnrollmentStatusUpdate,
)
from app.services.interfaces.enrollment_service import EnrollmentServiceInterface

router = APIRouter(
    prefix="/api/enrollments",
    tags=["Enrollments"],
)


# CREATE ENROLLMENT
@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment(
    payload: EnrollmentCreate,
    current_user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
) -> EnrollmentResponse:

    return await service.create_enrollment(payload, current_user)


# GET BY ID
@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
)
async def get_enrollment(
    enrollment_id: int,
    current_user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
) -> EnrollmentResponse:

    return await service.get_enrollment(enrollment_id, current_user)


# GET ALL ENROLLMENTS
@router.get(
    "/",
    response_model=EnrollmentListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_enrollments(
    current_user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    enrollment_status: EnrollmentStatus | None = Query(default=None, alias="status"),
):

    return await service.list_enrollments(
        page=page,
        size=size,
        status=enrollment_status,
        current_user=current_user,
    )


# GET ENROLLMENTS BY BATCH ID
@router.get(
    "/batch/{batch_id}",
    response_model=list[EnrollmentResponse]
)
async def get_enrollments_by_batch(
    current_user : Annotated[User, Depends(require_roles("admin","trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
    batch_id:int
)->list[EnrollmentResponse]:
    return await service.get_enrollments_by_batch(
        batch_id=batch_id,
        current_user=current_user
    )


# GET ENROLLMENTS BY EMPLOYEE ID
@router.get(
    "/employee/{employee_id}",
    response_model=list[EnrollmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_enrollments_by_employee(
    current_user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
    employee_id: int,
) -> list[EnrollmentResponse]:

    return await service.get_enrollments_by_employee(
        employee_id=employee_id, current_user=current_user
    )


# UPDATE ENROLLMENT STATUS
@router.patch(
    "/{enrollment_id}/status",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_200_OK,
    description="Status value includes 'enrolled','paused','cancelled','completed'"
)
async def update_enrollment_status(
    enrollment_id: int,
    payload: EnrollmentStatusUpdate,
    current_user: Annotated[User, Depends(require_roles("admin", "trainer"))],
    service: Annotated[EnrollmentServiceInterface, Depends(get_enrollment_service)],
) -> EnrollmentResponse:

    return await service.update_enrollment_status(
        enrollment_id=enrollment_id,
        payload=payload,
        current_user=current_user,
    )
