from abc import ABC, abstractmethod

from app.models.user import User
from app.schemas.performance_evaluation_schema import (
    PerformanceEvaluationCreate,
    PerformanceEvaluationDetailResponse,
    PerformanceEvaluationUpdate,
    PerformancePreviewResponse,
)


class PerformanceEvaluationServiceInterface(ABC):

    @abstractmethod
    async def get_preview(
        self, enrollment_id: int, current_user: User
    ) -> PerformancePreviewResponse:
        """Pre-calculate and preview objective assessment and attendance metrics for a trainee."""
        pass

    @abstractmethod
    async def evaluate_trainee(
        self, payload: PerformanceEvaluationCreate, current_user: User
    ) -> PerformanceEvaluationDetailResponse:
        """Create a new performance evaluation for an enrolled trainee with calculated composite scores."""
        pass

    @abstractmethod
    async def update_evaluation(
        self,
        evaluation_id: int,
        payload: PerformanceEvaluationUpdate,
        current_user: User,
    ) -> PerformanceEvaluationDetailResponse:
        """Update an existing performance evaluation with updated scores or feedback."""
        pass

    @abstractmethod
    async def get_evaluation_by_enrollment_id(
        self, enrollment_id: int, current_user: User
    ) -> PerformanceEvaluationDetailResponse:
        """Retrieve a trainee's detailed performance evaluation card with role authorization checks."""
        pass
