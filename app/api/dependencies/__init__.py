from app.api.dependencies.auth import get_current_user, require_roles
from app.api.dependencies.batch_dependencies import (
    get_batch_repository,
    get_batch_service,
)
from app.api.dependencies.course_content_dependencies import (
    get_course_content_repository,
    get_course_content_service,
)
from app.api.dependencies.course_dependencies import (
    get_course_repository,
    get_course_service,
)
from app.api.dependencies.auth_service_dependencies import (
    get_auth_service,
)

from .attendance_dependency import (
    get_attendance_record_repository,
    get_attendance_record_service,
    get_attendance_session_service,
)

__all__ = [
    "get_attendance_record_repository",
    "get_attendance_record_service",
    "get_attendance_session_service",
    "get_auth_service",
    "get_batch_repository",
    "get_batch_service",
    "get_course_content_repository",
    "get_course_content_service",
    "get_course_repository",
    "get_course_service",
    "get_current_user",
    "require_roles",
]
