from typing import Any

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentFilterParams,
)


class AssessmentRepository(AssessmentInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_assessment_by_id(self, id: int) -> Assessment | None:
        assessment = await self.db.get(Assessment, id)

        return assessment

    async def get_all_assessments(
        self, filter_params: AssessmentFilterParams
    ) -> dict[str, Any]:
        stmnt = select(Assessment)

        if filter_params.batch_id:
            stmnt = stmnt.where(Assessment.batch_id == filter_params.batch_id)
        if filter_params.is_active in [True, False]:
            stmnt = stmnt.where(Assessment.is_active == filter_params.is_active)
        if filter_params.assessment_type:
            stmnt = stmnt.where(
                Assessment.assessment_type == filter_params.assessment_type
            )
        if filter_params.title:
            stmnt = stmnt.where(Assessment.title.ilike(f"%{filter_params.title}%"))
        if filter_params.total_mark:
            stmnt = stmnt.where(Assessment.total_mark == filter_params.total_mark)
        if filter_params.pass_mark:
            stmnt = stmnt.where(Assessment.pass_mark == filter_params.pass_mark)
        if filter_params.scheduled_date:
            stmnt = stmnt.where(
                cast(Assessment.scheduled_date_time, Date)
                == filter_params.scheduled_date
            )

        count = select(func.count()).select_from(stmnt.subquery())

        total = await self.db.execute(count)

        total = total.scalar_one() or 0

        stmnt = stmnt.order_by(Assessment.scheduled_date_time.desc())
        offset = (filter_params.page - 1) * filter_params.limit
        stmnt = stmnt.limit(filter_params.limit).offset(offset)

        rows = await self.db.execute(stmnt)

        assessments = rows.scalars().all()

        return {
            "assessments": assessments,
            "total": total,
            "page": filter_params.page,
            "limit": filter_params.limit,
        }

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

    async def update_assessment_activation(self, assessment: Assessment, status: bool):
        assessment.is_active = status
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment
