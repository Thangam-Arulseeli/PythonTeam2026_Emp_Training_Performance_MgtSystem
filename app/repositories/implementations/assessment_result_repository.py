from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment_result import AssessmentResult
from app.models.enrollment import Enrollment
from app.repositories.interfaces.assessment_result_interface import (
    AssessmentResultInterface,
)


class AssessmentResultRepository(AssessmentResultInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_enrollments_for_batch(self, batch_id: int) -> list[Enrollment]:

        stmt = select(Enrollment).where(
            Enrollment.batch_id == batch_id,
            Enrollment.status == "enrolled",
        )
        res = await self.db.execute(stmt)

        return list(res.scalars().all())

    async def get_assigned_enrollment_ids(self, assessment_id: int) -> set[int]:
        stmt = select(AssessmentResult.enrollment_id).where(
            AssessmentResult.assessment_id == assessment_id
        )
        res = await self.db.execute(stmt)

        return set(res.scalars().all())

    async def bulk_create(
        self, results: list[AssessmentResult]
    ) -> list[AssessmentResult]:
        if not results:
            return []
        self.db.add_all(results)
        await self.db.commit()

        for result in results:
            await self.db.refresh(result)

        return results

    async def get_by_id(self, result_id: int) -> AssessmentResult | None:
        return await self.db.get(AssessmentResult, result_id)

    async def get_by_assessment_and_enrollment(
        self, assessment_id: int, enrollment_id: int
    ) -> AssessmentResult | None:
        stmt = select(AssessmentResult).where(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.enrollment_id == enrollment_id,
        )
        res = await self.db.execute(stmt)

        return res.scalar_one_or_none()

    async def update(
        self, result: AssessmentResult, data: dict[str, Any]
    ) -> AssessmentResult:
        for key, value in data.items():
            setattr(result, key, value)
        await self.db.commit()
        await self.db.refresh(result)

        return result

    async def get_results_by_employee_id(
        self, employee_id: int
    ) -> list[AssessmentResult]:
        stmt = (
            select(AssessmentResult)
            .options(
                selectinload(AssessmentResult.assessment),
                selectinload(AssessmentResult.enrollment),
            )
            .join(
                Enrollment,
                AssessmentResult.enrollment_id == Enrollment.enrollment_id,
            )
            .where(Enrollment.employee_id == employee_id)
            .order_by(AssessmentResult.created_at.desc())
        )
        res = await self.db.execute(stmt)

        return list(res.scalars().all())

    async def get_result_by_id_with_details(
        self, result_id: int
    ) -> AssessmentResult | None:
        stmt = (
            select(AssessmentResult)
            .options(
                selectinload(AssessmentResult.assessment),
                selectinload(AssessmentResult.enrollment).selectinload(
                    Enrollment.employee
                ),
            )
            .where(AssessmentResult.id == result_id)
        )
        res = await self.db.execute(stmt)

        return res.scalar_one_or_none()

    async def get_results_by_assessment_id(
        self, assessment_id: int
    ) -> list[AssessmentResult]:
        stmt = (
            select(AssessmentResult)
            .options(
                selectinload(AssessmentResult.assessment),
                selectinload(AssessmentResult.enrollment).selectinload(
                    Enrollment.employee
                ),
            )
            .where(AssessmentResult.assessment_id == assessment_id)
            .order_by(AssessmentResult.id)
        )
        res = await self.db.execute(stmt)

        return list(res.scalars().all())
