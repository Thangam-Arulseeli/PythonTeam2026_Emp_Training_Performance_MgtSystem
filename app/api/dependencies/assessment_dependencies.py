from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.batch_dependencies import get_batch_repository
from app.api.dependencies.employee import get_employee_repository
from app.database.session import get_session
from app.repositories.implementations.assessment_repository import AssessmentRepository
from app.repositories.implementations.assessment_result_repository import (
    AssessmentResultRepository,
)
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.repositories.interfaces.assessment_result_interface import (
    AssessmentResultInterface,
)
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.services.implementations.assessment_service import AssessmentService
from app.services.implementations.assessment_result_service import (
    AssessmentResultService,
)
from app.services.interfaces.assessment_service import AssessmentServiceInterface
from app.services.interfaces.assessment_result_service import (
    AssessmentResultServiceInterface,
)

DB_Session = Annotated[AsyncSession, Depends(get_session)]


def get_assessment_repository(db: DB_Session) -> AssessmentInterface:
    return AssessmentRepository(db)


def get_assessment_service(
    assessment_repository: AssessmentInterface = Depends(get_assessment_repository),
    batch_repository: BatchInterface = Depends(get_batch_repository),
) -> AssessmentServiceInterface:
    return AssessmentService(assessment_repository, batch_repository)


def get_assessment_result_repository(
    db: DB_Session,
) -> AssessmentResultInterface:
    return AssessmentResultRepository(db)


def get_assessment_result_service(
    result_repo: AssessmentResultInterface = Depends(
        get_assessment_result_repository
    ),
    assessment_repo: AssessmentInterface = Depends(get_assessment_repository),
    batch_repo: BatchInterface = Depends(get_batch_repository),
    employee_repo: EmployeeRepositoryInterface = Depends(get_employee_repository),
) -> AssessmentResultServiceInterface:
    return AssessmentResultService(
        result_repo, assessment_repo, batch_repo, employee_repo
    )
