from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.course_dependencies import get_course_repository
from app.database.session import get_session
from app.repositories.implementations.course_content_repository import (
    CourseContentRepository,
)
from app.repositories.interfaces.course_content_interface import CourseContentInterface
from app.repositories.interfaces.course_interface import CourseInterface
from app.services.implementations.course_content_service import (
    CourseContentServiceImpl,
)
from app.services.interfaces.course_content_service import CourseContentService


def get_course_content_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseContentInterface:
    return CourseContentRepository(db)


def get_course_content_service(
    content_repo: CourseContentInterface = Depends(get_course_content_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseContentService:
    return CourseContentServiceImpl(content_repo, course_repo)
