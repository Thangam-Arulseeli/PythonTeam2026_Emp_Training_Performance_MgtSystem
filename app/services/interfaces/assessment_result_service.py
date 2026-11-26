from abc import ABC, abstractmethod
from fastapi import UploadFile

from app.models.assessment_result import AssessmentResult
from app.models.user import User
from app.schemas.assessment_result_schema import (
    AssessmentAssignResponse,
    AssessmentCancelRequest,
    AssessmentGradeRequest,
    AssessmentDetailResponse,
    TraineeAssessmentDetailResponse,
)


class AssessmentResultServiceInterface(ABC):

    @abstractmethod
    async def assign_assessment_to_batch(
        self, assessment_id: int
    ) -> AssessmentAssignResponse:
        """Assign an assessment to all currently active enrolled trainees in the batch."""
        pass

    @abstractmethod
    async def get_my_assessments(
        self, current_user: User
    ) -> list[TraineeAssessmentDetailResponse]:
        """Fetch all assigned assessments for the currently logged-in trainee."""
        pass

    @abstractmethod
    async def get_result_by_id(
        self, result_id: int, current_user: User
    ) -> TraineeAssessmentDetailResponse:
        """Fetch a single assessment result by ID with authorization check."""
        pass

    @abstractmethod
    async def get_results_by_assessment_id(
        self, assessment_id: int
    ) -> list[AssessmentDetailResponse]:
        """Fetch all trainee results for a specific assessment (trainer/admin view)."""
        pass

    @abstractmethod
    async def submit_assessment(
        self,
        result_id: int,
        file: UploadFile | None,
        current_user: User,
    ) -> AssessmentResult:
        """Submit an assessment with optional file upload, validating deadlines and trainee status."""
        pass

    @abstractmethod
    async def grade_assessment(
        self,
        result_id: int,
        payload: AssessmentGradeRequest,
    ) -> AssessmentResult:
        """Grade a submitted assessment, validating score bounds and updating evaluation status."""
        pass

    @abstractmethod
    async def cancel_assessment_result(
        self,
        result_id: int,
        payload: AssessmentCancelRequest,
    ) -> AssessmentResult:
        """Cancel a pending assessment with an optional reason."""
        pass
