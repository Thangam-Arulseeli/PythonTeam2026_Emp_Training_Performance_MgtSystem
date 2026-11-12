"""Import all ORM models so their relationships are registered with Base."""

from app.models.batch import Batch
from app.models.course import Course
from app.models.course_content import CourseContent
from app.models.employee import EmployeeData
from app.models.employee_document import EmployeeDocument
from app.models.trainer import Trainer
from app.models.trainer_resume import TrainerResume

__all__ = [
    "Batch",
    "Course",
    "CourseContent",
    "EmployeeData",
    "EmployeeDocument",
    "Trainer",
    "TrainerResume",
]
