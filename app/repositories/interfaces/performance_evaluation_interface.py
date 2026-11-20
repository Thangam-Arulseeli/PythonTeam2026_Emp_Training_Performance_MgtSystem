from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from app.models.enrollment import Enrollment
from app.models.performance_evaluation import PerformanceEvaluation


class PerformanceEvaluationInterface(ABC):

    @abstractmethod
    async def create(
        self, evaluation: PerformanceEvaluation
    ) -> PerformanceEvaluation:
        """Persist a new PerformanceEvaluation record."""
        pass

    @abstractmethod
    async def get_by_id(self, evaluation_id: int) -> PerformanceEvaluation | None:
        """Fetch a PerformanceEvaluation record by primary key."""
        pass

    @abstractmethod
    async def get_by_enrollment_id(
        self, enrollment_id: int
    ) -> PerformanceEvaluation | None:
        """Fetch a PerformanceEvaluation record by enrollment_id."""
        pass

    @abstractmethod
    async def get_by_enrollment_with_details(
        self, enrollment_id: int
    ) -> PerformanceEvaluation | None:
        """Fetch a PerformanceEvaluation record with eagerly loaded enrollment, employee, and batch."""
        pass

    @abstractmethod
    async def get_enrollment_with_details(
        self, enrollment_id: int
    ) -> Enrollment | None:
        """Fetch an Enrollment record with eagerly loaded employee and batch."""
        pass

    @abstractmethod
    async def get_attendance_stats_for_enrollment(
        self, enrollment_id: int
    ) -> tuple[int, int]:
        """Fetch attendance statistics (total_sessions_conducted, total_sessions_attended) for an enrollment."""
        pass

    @abstractmethod
    async def get_assessment_stats_for_enrollment(
        self, enrollment_id: int
    ) -> tuple[int, int, Decimal, Decimal]:
        """Fetch assessment statistics (total_assigned, total_completed, total_obtained_marks, total_max_marks)."""
        pass

    @abstractmethod
    async def update(
        self, evaluation: PerformanceEvaluation, data: dict[str, Any]
    ) -> PerformanceEvaluation:
        """Update an existing PerformanceEvaluation record with supplied fields."""
        pass
