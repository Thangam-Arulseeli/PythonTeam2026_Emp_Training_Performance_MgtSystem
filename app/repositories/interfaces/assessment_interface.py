from abc import ABC, abstractmethod
from typing import Any

from app.models.assessment import Assessment
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentPatch,
)


class AssessmentInterface(ABC):

    @abstractmethod
    async def get_assessment_by_id(self, id: int) -> Assessment | None:
        """Gets the Assessment details using assessment ID"""
        pass

    @abstractmethod
    async def get_all_assessments(
        self, filter_params: AssessmentFilterParams
    ) -> dict[str, Any]:
        """Gets all the Assessements with optional filters"""
        pass

    @abstractmethod
    async def insert_assessment(self, assessment_data: AssessmentCreate) -> Assessment:
        """Insert new assessment record"""
        pass

    @abstractmethod
    async def update_assessment(
        self, assessment: Assessment, assessment_data: dict[str, Any]
    ) -> Assessment:
        """Update the exisiting assessment record"""
        pass

    @abstractmethod
    async def update_assessment_activation(
        self, assessment: Assessment, status: bool
    ) -> Assessment:
        """Change the is_active to True/False"""
        pass
