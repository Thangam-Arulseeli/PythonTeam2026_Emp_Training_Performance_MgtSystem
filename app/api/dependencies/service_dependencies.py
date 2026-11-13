from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.implementations.batch_repository import BatchRepository
from app.repositories.implementations.course_content_repository import (
    CourseContentRepository,
)
from app.repositories.implementations.course_repository import CourseRepository
from app.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.implementations.user_repository import UserRepository
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.course_content_interface import CourseContentInterface
from app.repositories.interfaces.course_interface import CourseInterface
from app.services.auth_service import AuthService
from app.services.batch_service import BatchService
from app.services.course_content_service import CourseContentService
from app.services.course_service import CourseService


def get_course_repository(db: AsyncSession = Depends(get_session)) -> CourseInterface:
    """Build a course repository using the request's async database session."""
    return CourseRepository(db)


def get_course_service(
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseService:
    """Build the course service with its repository dependency."""
    return CourseService(course_repo)


def get_batch_repository(db: AsyncSession = Depends(get_session)) -> BatchInterface:
    """Build a batch repository using the request's async database session."""
    return BatchRepository(db)


def get_batch_service(
    batch_repo: BatchInterface = Depends(get_batch_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> BatchService:
    """Build the batch service with batch and course repositories."""
    return BatchService(batch_repo, course_repo)


def get_course_content_repository(
    db: AsyncSession = Depends(get_session),
) -> CourseContentInterface:
    """Build a course-content repository using the request's async session."""
    return CourseContentRepository(db)


def get_course_content_service(
    content_repo: CourseContentInterface = Depends(get_course_content_repository),
    course_repo: CourseInterface = Depends(get_course_repository),
) -> CourseContentService:
    """Build the course-content service with content and course repositories."""
    return CourseContentService(content_repo, course_repo)


def get_auth_service() -> AuthService:
    """Build the authentication service with user and refresh-token repositories."""
    return AuthService(
        user_repository=UserRepository(),
        refresh_token_repository=RefreshTokenRepository()
    )
