from abc import ABC, abstractmethod
from typing import Any

from app.models.assessment import Assessment
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentPatch,
)


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

    @abstractmethod
    async def update_assessment_activation(
        self, assessment_id: int, status: bool
    ) -> Assessment:
        pass

    @abstractmethod
    async def get_all_assessments(
        self, filter_params: AssessmentFilterParams
    ) -> dict[str, Any]:
        """Gets all the Assessements with optional filters"""
        pass
