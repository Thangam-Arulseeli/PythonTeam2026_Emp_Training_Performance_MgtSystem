from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.batch_dependencies import get_batch_repository
from app.api.dependencies.employee import get_employee_repository
from app.api.dependencies.trainer_dependencies import get_trainer_repository
from app.database.session import get_session
from app.repositories.implementations.enrollment_repository import (
    EnrollmentRepository,
)
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.repositories.interfaces.enrollment_interface import EnrollmentInterface
from app.repositories.interfaces.trainer_repository import TrainerRepository
from app.services.implementations.enrollment_service import EnrollmentService
from app.services.interfaces.enrollment_service import EnrollmentServiceInterface

# Build the enrollment repository.
def get_enrollment_repository(db: AsyncSession = Depends(get_session)) -> EnrollmentInterface:
    return EnrollmentRepository(db)


def get_enrollment_service(
    enrollment_repo: Annotated[EnrollmentInterface , Depends(get_enrollment_repository)],
    employee_repo: Annotated[EmployeeRepositoryInterface , Depends(get_employee_repository)],
    batch_repo: Annotated[BatchInterface , Depends(get_batch_repository)],
    trainer_repo: Annotated[TrainerRepository , Depends(get_trainer_repository)],
) -> EnrollmentServiceInterface:
    # Build the enrollment service with its repositories.

    return EnrollmentService(
        enrollment_repo=enrollment_repo,
        employee_repo=employee_repo,
        batch_repo=batch_repo,
        trainer_repo=trainer_repo,
    )

