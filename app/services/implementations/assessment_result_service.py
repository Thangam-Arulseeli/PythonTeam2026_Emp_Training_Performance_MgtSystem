from datetime import datetime, time
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.exceptions.custom_exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.assessment_result import AssessmentResult, AssessmentResultStatus
from app.models.user import User
from app.repositories.interfaces.assessment_interface import AssessmentInterface
from app.repositories.interfaces.assessment_result_interface import (
    AssessmentResultInterface,
)
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.schemas.assessment_result_schema import (
    AssessmentAssignResponse,
    AssessmentCancelRequest,
    AssessmentGradeRequest,
    AssessmentDetailResponse,
    TraineeAssessmentDetailResponse,
)
from app.services.interfaces.assessment_result_service import (
    AssessmentResultServiceInterface,
)


class AssessmentResultService(AssessmentResultServiceInterface):
    def __init__(
        self,
        result_repo: AssessmentResultInterface,
        assessment_repo: AssessmentInterface,
        batch_repo: BatchInterface,
        employee_repo: EmployeeRepositoryInterface,
    ):
        self.result_repo = result_repo
        self.assessment_repo = assessment_repo
        self.batch_repo = batch_repo
        self.employee_repo = employee_repo

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

    async def get_my_assessments(
        self, current_user: User
    ) -> list[TraineeAssessmentDetailResponse]:
        employee = await self.employee_repo.get_employee_by_email(current_user.email)
        if not employee:
            raise NotFoundException("Employee profile not found for current user.")

        results = await self.result_repo.get_results_by_employee_id(
            employee.employee_id
        )

        return [
            TraineeAssessmentDetailResponse(
                result_id=r.id,
                enrollment_id=r.enrollment_id,
                status=r.status,
                mark=r.mark,
                grade=r.grade,
                feedback=r.feedback,
                file_name=r.file_name,
                submitted_date_time=r.submitted_date_time,
                evaluated_date_time=r.evaluated_date_time,
                assessment_id=r.assessment.id,
                batch_id=r.assessment.batch_id,
                title=r.assessment.title,
                description=r.assessment.description,
                assessment_type=r.assessment.assessment_type,
                scheduled_date_time=r.assessment.scheduled_date_time,
                total_mark=r.assessment.total_mark,
                pass_mark=r.assessment.pass_mark,
            )
            for r in results
        ]

    async def get_result_by_id(
        self, result_id: int, current_user: User
    ) -> TraineeAssessmentDetailResponse:
        result = await self.result_repo.get_result_by_id_with_details(result_id)
        if not result:
            raise NotFoundException("Assessment result not found.")

        if current_user.role == "employee":
            employee = await self.employee_repo.get_employee_by_email(
                current_user.email
            )
            if not employee or result.enrollment.employee_id != employee.employee_id:
                raise ForbiddenException(
                    "You are not authorized to view this assessment result."
                )

        return TraineeAssessmentDetailResponse(
            result_id=result.id,
            enrollment_id=result.enrollment_id,
            status=result.status,
            mark=result.mark,
            grade=result.grade,
            feedback=result.feedback,
            file_name=result.file_name,
            submitted_date_time=result.submitted_date_time,
            evaluated_date_time=result.evaluated_date_time,
            assessment_id=result.assessment.id,
            batch_id=result.assessment.batch_id,
            title=result.assessment.title,
            description=result.assessment.description,
            assessment_type=result.assessment.assessment_type,
            scheduled_date_time=result.assessment.scheduled_date_time,
            total_mark=result.assessment.total_mark,
            pass_mark=result.assessment.pass_mark,
        )

    async def get_results_by_assessment_id(
        self, assessment_id: int
    ) -> list[AssessmentDetailResponse]:
        assessment = await self.assessment_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise NotFoundException("Assessment not found.")

        results = await self.result_repo.get_results_by_assessment_id(assessment_id)

        return [
            AssessmentDetailResponse(
                result_id=r.id,
                assessment_id=r.assessment_id,
                enrollment_id=r.enrollment_id,
                employee_id=r.enrollment.employee.employee_id,
                employee_name=r.enrollment.employee.full_name,
                employee_email=r.enrollment.employee.email,
                status=r.status,
                mark=r.mark,
                grade=r.grade,
                feedback=r.feedback,
                file_name=r.file_name,
                submitted_date_time=r.submitted_date_time,
                evaluated_date_time=r.evaluated_date_time,
            )
            for r in results
        ]

    async def submit_assessment(
        self,
        result_id: int,
        file: UploadFile | None,
        current_user: User,
    ) -> AssessmentResult:
        result = await self.result_repo.get_result_by_id_with_details(result_id)
        if not result:
            raise NotFoundException("Assessment result not found.")

        if result.status != AssessmentResultStatus.PENDING:
            raise ConflictException(
                f"Cannot submit an assessment that is currently '{result.status}'."
            )

        if not result.assessment.is_active:
            raise BadRequestException("Cannot submit for an inactive assessment.")

        if result.enrollment.status != "enrolled":
            raise BadRequestException("Trainee enrollment is not active.")

        if not result.enrollment.employee.is_active:
            raise BadRequestException("Employee account is inactive.")

        if current_user.role == "employee":
            employee = await self.employee_repo.get_employee_by_email(
                current_user.email
            )
            if not employee or result.enrollment.employee_id != employee.employee_id:
                raise ForbiddenException(
                    "You are not authorized to submit this assessment."
                )

        now = datetime.now()
        if now < result.assessment.scheduled_date_time:
            raise BadRequestException(
                "Assessment has not started yet. Submissions are not allowed."
            )

        midnight = datetime.combine(
            result.assessment.scheduled_date_time.date(), time(23, 59, 59)
        )
        if now > midnight and current_user.role == "employee":
            raise BadRequestException(
                "Submission deadline has passed. Please contact your trainer."
            )

        file_path_str = None
        file_name_str = None

        if file and file.filename:
            upload_dir = Path("uploads/assessment_submissions")
            upload_dir.mkdir(parents=True, exist_ok=True)
            extension = Path(file.filename).suffix
            saved_filename = f"{uuid4().hex}{extension}"
            file_path = upload_dir / saved_filename

            with file_path.open("wb") as buffer:
                buffer.write(await file.read())

            file_path_str = str(file_path)
            file_name_str = file.filename

        update_data = {
            "status": AssessmentResultStatus.SUBMITTED,
            "submitted_date_time": now,
            "file_name": file_name_str,
            "file_path": file_path_str,
        }

        return await self.result_repo.update(result, update_data)

    async def grade_assessment(
        self,
        result_id: int,
        payload: AssessmentGradeRequest,
    ) -> AssessmentResult:
        result = await self.result_repo.get_result_by_id_with_details(result_id)
        if not result:
            raise NotFoundException("Assessment result not found.")

        if result.status != AssessmentResultStatus.SUBMITTED:
            raise BadRequestException(
                f"Cannot grade an assessment with status '{result.status}'. Only 'submitted' assessments can be graded."
            )

        if payload.mark > result.assessment.total_mark:
            raise BadRequestException(
                f"Mark ({payload.mark}) cannot exceed total marks ({result.assessment.total_mark})."
            )

        if payload.grade:
            final_grade = payload.grade
        else:
            final_grade = (
                "PASS" if payload.mark >= result.assessment.pass_mark else "FAIL"
            )

        update_data = {
            "mark": payload.mark,
            "grade": final_grade,
            "feedback": payload.feedback,
            "status": AssessmentResultStatus.GRADED,
            "evaluated_date_time": datetime.now(),
        }

        return await self.result_repo.update(result, update_data)

    async def cancel_assessment_result(
        self,
        result_id: int,
        payload: AssessmentCancelRequest,
    ) -> AssessmentResult:
        result = await self.result_repo.get_by_id(result_id)
        if not result:
            raise NotFoundException("Assessment result not found.")

        if result.status != AssessmentResultStatus.PENDING:
            raise BadRequestException(
                f"Cannot cancel an assessment with status '{result.status}'. Only 'pending' assessments can be cancelled."
            )

        feedback_text = (
            f"Cancelled: {payload.reason.strip()}"
            if payload.reason and payload.reason.strip()
            else "Assessment cancelled by trainer/admin"
        )

        update_data = {
            "status": AssessmentResultStatus.CANCELLED,
            "feedback": feedback_text,
            "mark": None,
            "grade": None,
        }

        return await self.result_repo.update(result, update_data)
