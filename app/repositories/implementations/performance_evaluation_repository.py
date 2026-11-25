from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import AttendanceStatus
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.models.attendance_record import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.performance_evaluation import PerformanceEvaluation
from app.repositories.interfaces.performance_evaluation_interface import (
    PerformanceEvaluationInterface,
)


class PerformanceEvaluationRepository(PerformanceEvaluationInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, evaluation: PerformanceEvaluation
    ) -> PerformanceEvaluation:
        self.db.add(evaluation)
        await self.db.commit()
        await self.db.refresh(evaluation)
        return evaluation

    async def get_by_id(self, evaluation_id: int) -> PerformanceEvaluation | None:
        return await self.db.get(PerformanceEvaluation, evaluation_id)

    async def get_by_enrollment_id(
        self, enrollment_id: int
    ) -> PerformanceEvaluation | None:
        stmt = select(PerformanceEvaluation).where(
            PerformanceEvaluation.enrollment_id == enrollment_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_enrollment_with_details(
        self, enrollment_id: int
    ) -> PerformanceEvaluation | None:
        stmt = (
            select(PerformanceEvaluation)
            .options(
                selectinload(PerformanceEvaluation.enrollment).selectinload(
                    Enrollment.employee
                ),
                selectinload(PerformanceEvaluation.enrollment).selectinload(
                    Enrollment.batch
                ),
            )
            .where(PerformanceEvaluation.enrollment_id == enrollment_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_enrollment_with_details(
        self, enrollment_id: int
    ) -> Enrollment | None:
        stmt = (
            select(Enrollment)
            .options(
                selectinload(Enrollment.employee),
                selectinload(Enrollment.batch),
            )
            .where(Enrollment.enrollment_id == enrollment_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_attendance_stats_for_enrollment(
        self, enrollment_id: int
    ) -> tuple[int, int]:
        stmt = select(AttendanceRecord).where(
            AttendanceRecord.enrollment_id == enrollment_id
        )
        res = await self.db.execute(stmt)
        records = list(res.scalars().all())
        total_sessions = len(records)
        present_sessions = sum(
            1 for r in records if r.status == AttendanceStatus.PRESENT
        )
        return total_sessions, present_sessions

    async def get_assessment_stats_for_enrollment(
        self, enrollment_id: int
    ) -> tuple[int, int, Decimal, Decimal]:
        stmt = (
            select(AssessmentResult)
            .options(selectinload(AssessmentResult.assessment))
            .where(
                AssessmentResult.enrollment_id == enrollment_id,
                AssessmentResult.status != AssessmentResultStatus.CANCELLED,
            )
        )
        res = await self.db.execute(stmt)
        results = list(res.scalars().all())

        total_assigned = len(results)
        total_completed = sum(
            1 for r in results if r.status == AssessmentResultStatus.GRADED
        )
        total_obtained = sum(
            (r.mark if r.mark is not None else Decimal("0.00"))
            for r in results
            if r.status == AssessmentResultStatus.GRADED
        )
        total_max = sum(
            (
                r.assessment.total_mark
                if r.assessment and r.assessment.total_mark is not None
                else Decimal("0.00")
            )
            for r in results
        )

        return total_assigned, total_completed, total_obtained, total_max

    async def update(
        self, evaluation: PerformanceEvaluation, data: dict[str, Any]
    ) -> PerformanceEvaluation:
        for key, value in data.items():
            setattr(evaluation, key, value)
        await self.db.commit()
        await self.db.refresh(evaluation)
        return evaluation
