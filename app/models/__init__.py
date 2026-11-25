"""Import all ORM models so their relationships are registered with Base."""

from app.models.assessment import Assessment, AssessmentType
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.models.batch import Batch
from app.models.course import Course
from app.models.course_content import CourseContent
from app.models.employee import EmployeeData
from app.models.employee_document import EmployeeDocument
from app.models.enrollment import Enrollment
from app.models.performance_evaluation import PerformanceEvaluation
from app.models.refresh_token import RefreshToken
from app.models.trainer import Trainer
from app.models.trainer_resume import TrainerResume
from app.models.user import User

from .attendance_record import AttendanceRecord
from .attendance_session import AttendanceSession

__all__ = [
    "Assessment",
    "AssessmentResult",
    "AssessmentResultStatus",
    "AssessmentType",
    "AttendanceRecord",
    "AttendanceSession",
    "Batch",
    "Course",
    "CourseContent",
    "EmployeeData",
    "EmployeeDocument",
    "Enrollment",
    "PerformanceEvaluation",
    "RefreshToken",
    "Trainer",
    "TrainerResume",
    "User",
]
