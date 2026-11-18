from datetime import datetime

from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.repositories.interfaces.assessment_result_interface import (
    AssessmentResultInterface,
)
from app.repositories.interfaces.batch_interface import BatchInterface
from app.schemas.assessment_result_schema import AssessmentAssignResponse
from app.services.interfaces.assessment_result_service import (
    AssessmentResultServiceInterface,
)


class AssessmentResultService(AssessmentResultServiceInterface):
    def __init__(
        self,
        result_repo: AssessmentResultInterface,
        assessment_repo: AssessmentInterface,
        batch_repo: BatchInterface,
    ):
        self.result_repo = result_repo
        self.assessment_repo = assessment_repo
        self.batch_repo = batch_repo

    async def assign_assessment_to_batch(
        self, assessment_id: int
    ) -> AssessmentAssignResponse:

        assessment = await self.assessment_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise NotFoundException("Assessment not found.")

        if not assessment.is_active:
            raise BadRequestException("Cannot assign an inactive assessment.")

        batch = await self.batch_repo.get_by_id(assessment.batch_id)
        if not batch:
            raise NotFoundException("Associated batch not found.")

        if not batch.is_active:
            raise BadRequestException("Associated batch is inactive.")

        if batch.status == "completed":
            raise BadRequestException(
                "Cannot assign an assessment to an already completed batch."
            )

        if datetime.now() >= assessment.scheduled_date_time:
            raise BadRequestException(
                "Cannot assign an assessment whose scheduled date/time has already passed."
            )

        active_enrollments = await self.result_repo.get_active_enrollments_for_batch(
            batch.id
        )
        if not active_enrollments:
            raise BadRequestException(
                "No active enrolled trainees found in this batch to assign."
            )

        already_assigned_ids = await self.result_repo.get_assigned_enrollment_ids(
            assessment.id
        )

        new_enrollments = [
            e for e in active_enrollments if e.enrollment_id not in already_assigned_ids
        ]

        if not new_enrollments:
            return AssessmentAssignResponse(
                assessment_id=assessment.id,
                batch_id=batch.id,
                assigned_count=0,
                skipped_count=len(already_assigned_ids),
                message="All active trainees in this batch are already assigned to this assessment.",
                assigned_enrollment_ids=[],
            )

        new_results = [
            AssessmentResult(
                assessment_id=assessment.id,
                enrollment_id=enrollment.enrollment_id,
                status=AssessmentResultStatus.PENDING,
            )
            for enrollment in new_enrollments
        ]

        created_results = await self.result_repo.bulk_create(new_results)

        return AssessmentAssignResponse(
            assessment_id=assessment.id,
            batch_id=batch.id,
            assigned_count=len(created_results),
            skipped_count=len(already_assigned_ids),
            message=f"Assessment successfully assigned to {len(created_results)} trainee(s).",
            assigned_enrollment_ids=[r.enrollment_id for r in created_results],
        )
