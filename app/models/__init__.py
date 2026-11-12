"""Import all ORM models so their tables and relationships register with Base."""

from app.models.batch import Batch
from app.models.course import Course
from app.models.course_content import CourseContent
from app.models.employee import EmployeeData
from app.models.employee_document import EmployeeDocument
from app.models.refresh_token import RefreshToken
from app.models.trainer import Trainer
from app.models.trainer_resume import TrainerResume
from app.models.user import User

__all__ = [
    "Batch",
    "Course",
    "CourseContent",
    "EmployeeData",
    "EmployeeDocument",
    "RefreshToken",
    "Trainer",
    "TrainerResume",
    "User",
]
