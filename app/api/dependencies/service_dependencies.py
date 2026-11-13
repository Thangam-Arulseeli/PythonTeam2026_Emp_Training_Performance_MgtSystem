from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.interfaces.course_interface import CourseInterface
from app.repositories.implementations.course_repository import CourseRepository
from app.services.course_service import CourseService
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.implementations.batch_repository import BatchRepository
from app.services.batch_service import BatchService
from app.repositories.interfaces.course_content_interface import CourseContentInterface
from app.repositories.implementations.course_content_repository import CourseContentRepository
from app.services.course_content_service import CourseContentService

from app.repositories.implementations.user_repository import (
    UserRepository
)
from app.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository
)
from app.services.auth_service import AuthService


def get_course_repository(db: AsyncSession = Depends(get_session)) -> CourseInterface:
    return CourseRepository(db)


def get_course_service(
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseService:
    return CourseService(course_repo)


def get_batch_repository(db: AsyncSession = Depends(get_session)) -> BatchInterface:
    return BatchRepository(db)


def get_batch_service(
    batch_repo: BatchInterface = Depends(get_batch_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> BatchService:
    return BatchService(batch_repo, course_repo)


def get_course_content_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseContentInterface:
    return CourseContentRepository(db)


def get_course_content_service(
    content_repo: CourseContentInterface = Depends(get_course_content_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseContentService:
    return CourseContentService(content_repo, course_repo)


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
        refresh_token_repository=RefreshTokenRepository()
    )
