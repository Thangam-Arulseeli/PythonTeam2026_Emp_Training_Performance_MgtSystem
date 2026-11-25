from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.enrollment_dependencies import get_enrollment_repository
from app.database.session import get_session
from app.repositories.implementations.performance_evaluation_repository import (
    PerformanceEvaluationRepository,
)
from app.repositories.interfaces.enrollment_interface import EnrollmentInterface
from app.repositories.interfaces.performance_evaluation_interface import (
    PerformanceEvaluationInterface,
)
from app.services.implementations.performance_evaluation_service import (
    PerformanceEvaluationService,
)
from app.services.interfaces.performance_evaluation_service import (
    PerformanceEvaluationServiceInterface,
)

DB_Session = Annotated[AsyncSession, Depends(get_session)]


def get_performance_repository(
    db: DB_Session,
) -> PerformanceEvaluationInterface:
    return PerformanceEvaluationRepository(db)


def get_performance_service(
    perf_repo: PerformanceEvaluationInterface = Depends(
        get_performance_repository
    ),
    enrollment_repo: EnrollmentInterface = Depends(get_enrollment_repository),
) -> PerformanceEvaluationServiceInterface:
    return PerformanceEvaluationService(perf_repo, enrollment_repo)
