from app.api.routers.assessment import router as assessment_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.batch import router as batch_router
from app.api.routers.course import router as course_router
from app.api.routers.course_content import router as course_content_router
from app.api.routers.enrollment_router import router as enrollment_router
from app.api.routers.health import router as health_router

from .attendance_record import router as attendance_record_router
from .attendance_session import router as attendance_session_router

__all__ = [
    "assessment_router",
    "attendance_record_router",
    "attendance_session_router",
    "auth_router",
    "batch_router",
    "course_content_router",
    "course_router",
    "enrollment_router",
    "health_router",
]
