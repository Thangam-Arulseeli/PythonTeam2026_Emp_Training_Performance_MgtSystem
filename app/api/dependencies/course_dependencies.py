from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.implementations.course_repository import CourseRepository
from app.repositories.interfaces.course_interface import CourseInterface
from app.services.implementations.course_service import CourseServiceImpl
from app.services.interfaces.course_service import CourseService


def get_course_repository(db: AsyncSession = Depends(get_session)) -> CourseInterface:
    return CourseRepository(db)


def get_course_service(
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseService:
    return CourseServiceImpl(course_repo)
