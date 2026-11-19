from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.course_dependencies import get_course_repository
from app.database.session import get_session
from app.repositories.implementations.batch_repository import BatchRepository
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.course_interface import CourseInterface
from app.services.implementations.batch_service import BatchServiceImpl
from app.services.interfaces.batch_service import BatchService


def get_batch_repository(db: AsyncSession = Depends(get_session)) -> BatchInterface:
    return BatchRepository(db)


def get_batch_service(
    batch_repo: BatchInterface = Depends(get_batch_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> BatchService:
    return BatchServiceImpl(batch_repo, course_repo)
