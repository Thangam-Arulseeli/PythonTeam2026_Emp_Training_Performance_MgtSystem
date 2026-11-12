from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.interface.course_interface import CourseInterface
from app.repositories.repositories.course_repository import CourseRepository
from app.services.course_service import CourseService


def get_course_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseInterface:
    return CourseRepository(db)


def get_course_service(
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseService:
    return CourseService(course_repo)
