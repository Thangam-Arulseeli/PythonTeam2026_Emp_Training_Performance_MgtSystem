from abc import ABC, abstractmethod
from typing import Any

from app.models.assessment_result import AssessmentResult
from app.models.enrollment import Enrollment


class AssessmentResultInterface(ABC):

    @abstractmethod
    async def get_active_enrollments_for_batch(
        self, batch_id: int
    ) -> list[Enrollment]:
        """Fetch all enrollments with status 'enrolled' for a batch."""
        pass

    @abstractmethod
    async def get_assigned_enrollment_ids(
        self, assessment_id: int
    ) -> set[int]:
        """Fetch set of enrollment IDs already assigned to an assessment."""
        pass

    @abstractmethod
    async def bulk_create(
        self, results: list[AssessmentResult]
    ) -> list[AssessmentResult]:
        """Insert multiple AssessmentResult records in a single transaction."""
        pass

    @abstractmethod
    async def get_by_id(self, result_id: int) -> AssessmentResult | None:
        """Fetch AssessmentResult by ID."""
        pass

    @abstractmethod
    async def get_by_assessment_and_enrollment(
        self, assessment_id: int, enrollment_id: int
    ) -> AssessmentResult | None:
        """Fetch AssessmentResult by assessment_id and enrollment_id."""
        pass

    @abstractmethod
    async def update(
        self, result: AssessmentResult, data: dict[str, Any]
    ) -> AssessmentResult:
        """Update an existing AssessmentResult with supplied fields."""
        pass

    @abstractmethod
    async def get_results_by_employee_id(
        self, employee_id: int
    ) -> list[AssessmentResult]:
        """Fetch all AssessmentResults for an employee with joined Assessment and Enrollment."""
        pass

    @abstractmethod
    async def get_result_by_id_with_details(
        self, result_id: int
    ) -> AssessmentResult | None:
        """Fetch AssessmentResult by ID with joined Assessment and Enrollment."""
        pass

    @abstractmethod
    async def get_results_by_assessment_id(
        self, assessment_id: int
    ) -> list[AssessmentResult]:
        """Fetch all AssessmentResults for an assessment with joined trainee details."""
        pass
