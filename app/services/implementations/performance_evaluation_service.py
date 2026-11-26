from datetime import datetime
from decimal import Decimal

from app.exceptions.custom_exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.performance_evaluation import PerformanceEvaluation
from app.models.user import User
from app.repositories.interfaces.enrollment_interface import EnrollmentInterface
from app.repositories.interfaces.performance_evaluation_interface import (
    PerformanceEvaluationInterface,
)
from app.schemas.performance_evaluation_schema import (
    PerformanceEvaluationCreate,
    PerformanceEvaluationDetailResponse,
    PerformanceEvaluationUpdate,
    PerformancePreviewResponse,
)
from app.services.interfaces.performance_evaluation_service import (
    PerformanceEvaluationServiceInterface,
)


class PerformanceEvaluationService(PerformanceEvaluationServiceInterface):

    def __init__(
        self,
        perf_repo: PerformanceEvaluationInterface,
        enrollment_repo: EnrollmentInterface,
    ):
        self.perf_repo = perf_repo
        self.enrollment_repo = enrollment_repo

    async def get_preview(
        self, enrollment_id: int, current_user: User
    ) -> PerformancePreviewResponse:
        enrollment = await self.perf_repo.get_enrollment_with_details(enrollment_id)
        if not enrollment:
            raise NotFoundException("Enrollment not found.")

        total_sessions, present_sessions = (
            await self.perf_repo.get_attendance_stats_for_enrollment(enrollment_id)
        )
        attendance_pct = (
            round(
                Decimal(present_sessions) / Decimal(total_sessions) * Decimal("100"),
                2,
            )
            if total_sessions > 0
            else Decimal("0.00")
        )

        assigned_count, completed_count, total_obtained, total_max = (
            await self.perf_repo.get_assessment_stats_for_enrollment(enrollment_id)
        )
        assessment_pct = (
            round(total_obtained / total_max * Decimal("100"), 2)
            if total_max > Decimal("0.00")
            else Decimal("0.00")
        )

        return PerformancePreviewResponse(
            enrollment_id=enrollment.enrollment_id,
            employee_id=enrollment.employee.employee_id,
            employee_name=enrollment.employee.full_name,
            employee_email=enrollment.employee.email,
            batch_id=enrollment.batch.id,
            batch_name=enrollment.batch.batch_name,
            assessment_score_pct=assessment_pct,
            total_assessments_assigned=assigned_count,
            total_assessments_completed=completed_count,
            attendance_pct=attendance_pct,
            total_sessions_conducted=total_sessions,
            total_sessions_attended=present_sessions,
        )

    async def evaluate_trainee(
        self, payload: PerformanceEvaluationCreate, current_user: User
    ) -> PerformanceEvaluationDetailResponse:
        enrollment = await self.perf_repo.get_enrollment_with_details(
            payload.enrollment_id
        )
        if not enrollment:
            raise NotFoundException("Enrollment not found.")

        if enrollment.status not in ["enrolled", "completed"]:
            raise BadRequestException(
                f"Cannot evaluate an enrollment with status '{enrollment.status}'."
            )

        existing = await self.perf_repo.get_by_enrollment_id(payload.enrollment_id)
        if existing:
            raise ConflictException(
                "A performance evaluation already exists for this enrollment. Use the update endpoint to modify it."
            )

        total_sessions, present_sessions = (
            await self.perf_repo.get_attendance_stats_for_enrollment(
                payload.enrollment_id
            )
        )
        attendance_pct = (
            round(
                Decimal(present_sessions) / Decimal(total_sessions) * Decimal("100"),
                2,
            )
            if total_sessions > 0
            else Decimal("0.00")
        )

        total_assigned, total_completed, total_obtained, total_max = (
            await self.perf_repo.get_assessment_stats_for_enrollment(
                payload.enrollment_id
            )
        )
        assessment_pct = (
            round(total_obtained / total_max * Decimal("100"), 2)
            if total_max > Decimal("0.00")
            else Decimal("0.00")
        )

        final_score = round(
            (Decimal("0.50") * assessment_pct)
            + (Decimal("0.20") * attendance_pct)
            + (Decimal("0.10") * payload.communication_score)
            + (Decimal("0.10") * payload.behaviour_score)
            + (Decimal("0.10") * payload.teamwork_score),
            2,
        )

        if final_score >= Decimal("85.00"):
            grade = "Excellent"
        elif final_score >= Decimal("70.00"):
            grade = "Good"
        elif final_score >= Decimal("50.00"):
            grade = "Average"
        else:
            grade = "Needs Improvement"

        is_certified = final_score >= Decimal("50.00") and attendance_pct >= Decimal(
            "75.00"
        )

        evaluation = PerformanceEvaluation(
            enrollment_id=payload.enrollment_id,
            evaluator_id=current_user.user_id,
            assessment_score_pct=assessment_pct,
            attendance_pct=attendance_pct,
            communication_score=payload.communication_score,
            behaviour_score=payload.behaviour_score,
            teamwork_score=payload.teamwork_score,
            final_score=final_score,
            grade=grade,
            is_certified=is_certified,
            feedback=payload.feedback,
            evaluated_at=datetime.now(),
        )

        created = await self.perf_repo.create(evaluation)
        return await self.get_evaluation_by_enrollment_id(
            created.enrollment_id, current_user
        )

    async def update_evaluation(
        self,
        evaluation_id: int,
        payload: PerformanceEvaluationUpdate,
        current_user: User,
    ) -> PerformanceEvaluationDetailResponse:
        evaluation = await self.perf_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise NotFoundException("Performance evaluation not found.")

        total_sessions, present_sessions = (
            await self.perf_repo.get_attendance_stats_for_enrollment(
                evaluation.enrollment_id
            )
        )
        attendance_pct = (
            round(
                Decimal(present_sessions) / Decimal(total_sessions) * Decimal("100"),
                2,
            )
            if total_sessions > 0
            else Decimal("0.00")
        )

        total_assigned, total_completed, total_obtained, total_max = (
            await self.perf_repo.get_assessment_stats_for_enrollment(
                evaluation.enrollment_id
            )
        )
        assessment_pct = (
            round(total_obtained / total_max * Decimal("100"), 2)
            if total_max > Decimal("0.00")
            else Decimal("0.00")
        )

        comm = (
            payload.communication_score
            if payload.communication_score is not None
            else evaluation.communication_score
        )
        behav = (
            payload.behaviour_score
            if payload.behaviour_score is not None
            else evaluation.behaviour_score
        )
        team = (
            payload.teamwork_score
            if payload.teamwork_score is not None
            else evaluation.teamwork_score
        )
        feed = payload.feedback if payload.feedback is not None else evaluation.feedback

        final_score = round(
            (Decimal("0.50") * assessment_pct)
            + (Decimal("0.20") * attendance_pct)
            + (Decimal("0.10") * comm)
            + (Decimal("0.10") * behav)
            + (Decimal("0.10") * team),
            2,
        )

        if final_score >= Decimal("85.00"):
            grade = "Excellent"
        elif final_score >= Decimal("70.00"):
            grade = "Good"
        elif final_score >= Decimal("50.00"):
            grade = "Average"
        else:
            grade = "Needs Improvement"

        is_certified = final_score >= Decimal("50.00") and attendance_pct >= Decimal(
            "75.00"
        )

        update_data = {
            "assessment_score_pct": assessment_pct,
            "attendance_pct": attendance_pct,
            "communication_score": comm,
            "behaviour_score": behav,
            "teamwork_score": team,
            "final_score": final_score,
            "grade": grade,
            "is_certified": is_certified,
            "feedback": feed,
            "evaluator_id": current_user.user_id,
            "evaluated_at": datetime.now(),
        }

        await self.perf_repo.update(evaluation, update_data)
        return await self.get_evaluation_by_enrollment_id(
            evaluation.enrollment_id, current_user
        )

    async def get_evaluation_by_enrollment_id(
        self, enrollment_id: int, current_user: User
    ) -> PerformanceEvaluationDetailResponse:
        eval_record = await self.perf_repo.get_by_enrollment_with_details(enrollment_id)
        if not eval_record:
            raise NotFoundException(
                "Performance evaluation not found for this enrollment."
            )

        if current_user.role == "employee":
            if eval_record.enrollment.employee.email != current_user.email:
                raise ForbiddenException(
                    "You are not authorized to view this performance evaluation."
                )

        return PerformanceEvaluationDetailResponse(
            id=eval_record.id,
            enrollment_id=eval_record.enrollment_id,
            evaluator_id=eval_record.evaluator_id,
            employee_id=eval_record.enrollment.employee.employee_id,
            employee_name=eval_record.enrollment.employee.full_name,
            employee_email=eval_record.enrollment.employee.email,
            batch_id=eval_record.enrollment.batch.id,
            batch_name=eval_record.enrollment.batch.batch_name,
            assessment_score_pct=eval_record.assessment_score_pct,
            attendance_pct=eval_record.attendance_pct,
            communication_score=eval_record.communication_score,
            behaviour_score=eval_record.behaviour_score,
            teamwork_score=eval_record.teamwork_score,
            final_score=eval_record.final_score,
            grade=eval_record.grade,
            is_certified=eval_record.is_certified,
            feedback=eval_record.feedback,
            evaluated_at=eval_record.evaluated_at,
            created_at=eval_record.created_at,
            updated_at=eval_record.updated_at,
        )
