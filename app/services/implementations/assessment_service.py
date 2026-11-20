from typing import Any

from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.assessment import Assessment
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.repositories.interfaces.batch_interface import BatchInterface
from app.schemas.assessment_schema import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentPatch,
)
from app.services.interfaces.assessment_service import AssessmentServiceInterface


class AssessmentService(AssessmentServiceInterface):

    def __init__(
        self,
        assessment_repository: AssessmentInterface,
        batch_repository: BatchInterface,
    ):
        self.assessment_repository = assessment_repository
        self.batch_repository = batch_repository

    async def get_assessment_by_id(self, assessment_id: int) -> Assessment:

        assessment = await self.assessment_repository.get_assessment_by_id(
            assessment_id
        )
        if not assessment:
            raise NotFoundException("Assessment not found.")

        return assessment

    async def create_assessment(self, assessment_data: AssessmentCreate) -> Assessment:
        batch = await self.batch_repository.get_by_id(assessment_data.batch_id)

        if not batch:
            raise NotFoundException(f"Batch not found")
        if batch.is_active == False:
            raise BadRequestException(f"Batch is inactive.")

        if batch.status == "completed":
            raise BadRequestException("The was already completed.")

        assessment_date = assessment_data.scheduled_date_time.date()

        if not (batch.start_date <= assessment_date <= batch.end_date):
            raise BadRequestException(
                "Scheduled date must be between the batch start and end dates"
            )

        assessment = await self.assessment_repository.insert_assessment(assessment_data)

        return assessment

    async def patch_assessment(
        self, assessment_id: int, assessment_data: AssessmentPatch
    ) -> Assessment:
        existing_assessment = await self.get_assessment_by_id(assessment_id)

        if not existing_assessment:
            raise NotFoundException("Assessment not found")

        if existing_assessment.is_active == False:
            raise BadRequestException("Assessment is inactive")

        new_total_mark = (
            assessment_data.total_mark
            if assessment_data.total_mark
            else existing_assessment.total_mark
        )

        new_pass_mark = (
            assessment_data.pass_mark
            if assessment_data.pass_mark
            else existing_assessment.pass_mark
        )

        if new_pass_mark > new_total_mark:
            raise BadRequestException("Pass mark cannot be greater than total mark.")

        if assessment_data.scheduled_date_time or assessment_data.batch_id:
            batch_id = (
                assessment_data.batch_id
                if assessment_data.batch_id
                else existing_assessment.batch_id
            )

            batch = await self.batch_repository.get_by_id(batch_id)

            if not batch:
                raise NotFoundException(f"Batch not found")
            if batch.is_active == False:
                raise BadRequestException(f"Batch is inactive.")

            if batch.status == "completed":
                raise BadRequestException("The batch was already completed.")

            assessment_date = (
                assessment_data.scheduled_date_time.date()
                if assessment_data.scheduled_date_time
                else existing_assessment.scheduled_date_time.date()
            )

            if not (batch.start_date <= assessment_date <= batch.end_date):
                raise BadRequestException(
                    "Scheduled date must be between the batch start and end dates"
                )

        assessment = await self.assessment_repository.update_assessment(
            existing_assessment, assessment_data.model_dump(exclude_unset=True)
        )

        return assessment

    async def update_assessment_activation(
        self, assessment_id: int, status: bool
    ) -> Assessment:
        existing_assessment = await self.get_assessment_by_id(assessment_id)

        if not existing_assessment:
            raise NotFoundException("Assessment Not Found")

        if status is True:
            batch = await self.batch_repository.get_by_id(existing_assessment.batch_id)

            if not batch:
                raise NotFoundException(f"Batch not found")
            if batch.is_active == False:
                raise BadRequestException(f"Coressponding Batch is inactive.")

            if batch.status == "completed":
                raise BadRequestException("The batch was already completed.")

        updated_assessment = (
            await self.assessment_repository.update_assessment_activation(
                existing_assessment, status
            )
        )

        return updated_assessment

    async def get_all_assessments(
        self, filter_params: AssessmentFilterParams
    ) -> dict[str, Any]:
        return await self.assessment_repository.get_all_assessments(filter_params)
