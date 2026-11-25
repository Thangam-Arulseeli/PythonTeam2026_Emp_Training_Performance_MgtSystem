from app.schemas.auth_schema import (
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.schemas.batchSchema import (
    BatchCreate,
    BatchEndDateUpdate,
    BatchListResponse,
    BatchResponse,
    BatchUpdate,
)
from app.schemas.course_content_schema import (
    CourseContentListResponse,
    CourseContentResponse,
)
from app.schemas.courseSchema import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)

from .attendance_record import (
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
)
from .attendance_session import (
    AttendanceSessionBase,
    AttendanceSessionCreate,
    AttendanceSessionFilter,
    AttendanceSessionResponse,
    AttendanceSessionUpdate,
    AttendanceSummaryResponse,
)
from .performance_evaluation_schema import (
    PerformanceEvaluationCreate,
    PerformanceEvaluationDetailResponse,
    PerformanceEvaluationResponse,
    PerformanceEvaluationUpdate,
    PerformancePreviewResponse,
)

__all__ = [
    # Auth schemas
    "RegisterRequest",
    "TokenResponse",
    "RefreshRequest",
    "MessageResponse",
    "UserProfileResponse",
    # Course schemas
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseListResponse",
    # Batch schemas
    "BatchCreate",
    "BatchEndDateUpdate",
    "BatchUpdate",
    "BatchResponse",
    "BatchListResponse",
    # Course Content schemas
    "CourseContentResponse",
    "CourseContentListResponse",
    # attendence session
    "AttendanceSessionBase",
    "AttendanceSessionCreate",
    "AttendanceSessionResponse",
    "AttendanceSessionUpdate",
    "AttendanceSessionFilter",
    "AttendanceRecordCreate",
    "AttendanceRecordUpdate",
    "AttendanceRecordResponse",
    "AttendanceSummaryResponse",
    # Performance Evaluation schemas
    "PerformancePreviewResponse",
    "PerformanceEvaluationCreate",
    "PerformanceEvaluationUpdate",
    "PerformanceEvaluationResponse",
    "PerformanceEvaluationDetailResponse",
]
