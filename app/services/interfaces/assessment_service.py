from abc import ABC, abstractmethod

from app.models.assessment import Assessment
from app.schemas.assessment_schema import AssessmentCreate, AssessmentPatch


class AssessmentServiceInterface(ABC):

    @abstractmethod
    async def get_assessment_by_id(self, id: int) -> Assessment:
        pass

    @abstractmethod
    async def create_assessment(self, assessment_data: AssessmentCreate) -> Assessment:
        pass

    @abstractmethod
    async def patch_assessment(
        self, assessment_id: int, assessment_data: AssessmentPatch
    ) -> Assessment:
        pass
