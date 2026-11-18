from abc import ABC, abstractmethod

from app.schemas.assessment_result_schema import AssessmentAssignResponse


class AssessmentResultServiceInterface(ABC):

    @abstractmethod
    async def assign_assessment_to_batch(
        self, assessment_id: int
    ) -> AssessmentAssignResponse:
        """Assign an assessment to all currently active enrolled trainees in the batch."""
        pass
