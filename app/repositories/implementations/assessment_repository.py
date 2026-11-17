from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.schemas.assessment_schema import AssessmentCreate, AssessmentPatch


class AssessmentRepository(AssessmentInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_assessment_by_id(self, id: int) -> Assessment | None:
        assessment = await self.db.get(Assessment, id)

        return assessment

    async def insert_assessment(self, assessment_data: AssessmentCreate) -> Assessment:

        assessment = Assessment(**assessment_data.model_dump())
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment

    async def update_assessment(
        self, assessment: Assessment, assessment_data: dict[str, Any]
    ) -> Assessment:
        for key, value in assessment_data.items():
            setattr(assessment, key, value)
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment
