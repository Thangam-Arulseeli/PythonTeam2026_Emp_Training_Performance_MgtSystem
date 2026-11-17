from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.batch_dependencies import get_batch_repository
from app.database.session import get_session
from app.repositories.implementations.assessment_repository import AssessmentRepository
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.services.implementations.assessment_service import AssessmentService
from app.services.interfaces.assessment_service import AssessmentServiceInterface

DB_Session = Annotated[AsyncSession, Depends(get_session)]


def get_assessment_repository(db: DB_Session) -> AssessmentInterface:
    return AssessmentRepository(db)


def get_assessment_service(
    assessment_repository=Depends(get_assessment_repository),
    batch_repository=Depends(get_batch_repository),
) -> AssessmentServiceInterface:
    return AssessmentService(assessment_repository, batch_repository)
