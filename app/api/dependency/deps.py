from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.interface.course_interface import CourseInterface
from app.repositories.repositories.course_repository import CourseRepository
from app.services.course_service import CourseService
from app.repositories.interface.batch_interface import BatchInterface
from app.repositories.repositories.batch_repository import BatchRepository
from app.services.batch_service import BatchService
from app.repositories.interface.course_content_interface import (
    CourseContentInterface,
)
from app.repositories.repositories.course_content_repository import (
    CourseContentRepository,
)
from app.services.course_content_service import CourseContentService


# Course dependencies
def get_course_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseInterface:
    return CourseRepository(db)


def get_course_service(
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseService:
    return CourseService(course_repo)


# Batch dependencies
def get_batch_repository(
    db: AsyncSession = Depends(get_session),
) -> BatchInterface:
    return BatchRepository(db)


def get_batch_service(
    batch_repo: BatchInterface = Depends(get_batch_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> BatchService:
    return BatchService(batch_repo, course_repo)


# Course Content dependencies
def get_course_content_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseContentInterface:
    return CourseContentRepository(db)


def get_course_content_service(
    content_repo: CourseContentInterface = Depends(get_course_content_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseContentService:
    return CourseContentService(content_repo, course_repo)
