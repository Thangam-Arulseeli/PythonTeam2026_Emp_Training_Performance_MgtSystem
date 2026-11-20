
from datetime import date, datetime, timezone

from fastapi import HTTPException, status 

from app.exceptions import (
    NotFoundException,
    UnprocessableEntityException,
    ConflictException
)
from app.models.batch import Batch
from app.models.user import User
from app.repositories.interfaces.batch_interface import BatchInterface
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.repositories.interfaces.enrollment_interface import EnrollmentInterface
from app.repositories.interfaces.trainer_repository import TrainerRepository
from app.schemas.enrollment_schema import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentListResponse,
    EnrollmentStatus,
    EnrollmentStatusUpdate
)
from app.services.interfaces.enrollment_service import EnrollmentServiceInterface
from app.utils.logger import logger
from app.utils.email_service import EmailService


class EnrollmentService(EnrollmentServiceInterface):

    def __init__(
        self,
        enrollment_repo: EnrollmentInterface,
        employee_repo: EmployeeRepositoryInterface,
        batch_repo: BatchInterface,
        trainer_repo: TrainerRepository,
        email_service : EmailService
    ) -> None:

        self.enrollment_repo = enrollment_repo
        self.employee_repo = employee_repo
        self.batch_repo = batch_repo
        self.trainer_repo = trainer_repo
        self.email_service = email_service


    # GET BATCH OR RAISE ERROR
    async def get_batch(self, batch_id: int) -> Batch:
        batch = await self.batch_repo.get_by_id(batch_id)
        if batch is None:
            raise NotFoundException("Batch not found")

        return batch


    # VALIDATE ADMIN / TRAINER ACCESS TO BATCH
    async def validate_batch_access(
        self,
        batch_id: int,
        current_user: User
    ) -> Batch:

        batch = await self.get_batch(batch_id)

        # Admin can manage every batch
        if current_user.role == "admin":
            return batch

        # Only trainers are allowed beyond this point
        if current_user.role != "trainer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and trainers can manage enrollments",
            )

        # Find the trainer profile belonging to the logged-in user
        trainer = await self.trainer_repo.get_trainer_by_email(current_user.email)

        if trainer is None or not trainer.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active trainer is not found",
            )

        # Check whether this trainer owns the requested batch
        if trainer.trainer_id != batch.trainer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can manage enrollments only for your assigned batches",
            )

        return batch


    # CREATE ENROLLMENT
    async def create_enrollment(
        self,
        payload: EnrollmentCreate,
        current_user: User,
    ) -> EnrollmentResponse:

        # Validate batch access
        batch = await self.validate_batch_access(payload.batch_id, current_user)

        # Check whether employee exists and is active
        employee = await self.employee_repo.get_employee_by_id(payload.employee_id)
        if employee is None or not employee.is_active:
            raise NotFoundException("Active employee not found")

        # Check batch availability
        if not batch.is_active:
            raise UnprocessableEntityException(
                "Cannot enroll employees in an inactive batch"
            )

        if batch.status == "completed":
            raise UnprocessableEntityException(
                "Cannot enroll employees in a completed batch"
            )

        today=date.today()

        if today > batch.start_date:
            raise ConflictException(
                "Cannot enroll after the batch start date"
            )

        if batch.end_date < today:
            raise UnprocessableEntityException(
                "Cannot enroll employees in a batch that has ended"
            )

        # check whether the employee already enrolled in other batch
        active_count = (await self.enrollment_repo.count_active_by_employee(
            payload.employee_id)
        ) 

        if active_count >=1:
            raise ConflictException(
                "Employee already have an active enrollment. So complete or cancel the existing enrollment"
            )

        # Create enrollment
        enrollment = await self.enrollment_repo.create(
            {
                "employee_id": payload.employee_id,
                "batch_id": payload.batch_id,
                "status": "Enrolled",
            }
        )

        logger.info(
            "Enrollment created successfully: enrollment_id=%s, employee_id=%s, batch_id=%s",
            enrollment.enrollment_id,
            enrollment.employee_id,
            enrollment.batch_id,
        )

        # TO send enrollment confirmation mail
        await self.email_service.send_enrollment_confirmation_async(
            employee_name=employee.full_name,
            employee_email=employee.email,
            enrollment_id=enrollment.enrollment_id,
            enrollment_date=enrollment.enrollment_date,
            course_name=batch.course.course_name,
            batch_name=batch.batch_name,
            start_date=batch.start_date,
            end_date=batch.end_date,
            duration_value=batch.course.duration_value,
            duration_unit=batch.course.duration_unit,
            trainer_name=batch.trainer.trainer_name
        )

        return EnrollmentResponse.model_validate(enrollment)


    # GET ENROLLMENT BY ID
    async def get_enrollment(
        self,
        enrollment_id: int,
        current_user: User,
    ) -> EnrollmentResponse:

        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)

        if enrollment is None:
            raise NotFoundException("Enrollment not found")
        
        # Check whether the user can access this enrollment's batch
        await self.validate_batch_access(enrollment.batch_id, current_user)
        return EnrollmentResponse.model_validate(enrollment)


    # GET ALL ENROLLMENTS
    async def list_enrollments(
        self,
        page: int = 1,
        size: int = 10,
        status: EnrollmentStatus | None = None,
        current_user=None,
    ) -> EnrollmentListResponse:

        skip = (page - 1) * size
        trainer_id = None

        # Trainers can view only their assigned batches
        if current_user.role == "trainer":
            trainer = await self.trainer_repo.get_trainer_by_email(current_user.email)

            if not trainer or not trainer.is_active:
                raise NotFoundException("Active trainer not found")

            trainer_id = trainer.trainer_id

        enrollments, total = await self.enrollment_repo.get_all(
            skip=skip,
            limit=size,
            status=status,
            trainer_id=trainer_id,
        )

        enrollment_responses = [
            EnrollmentResponse.model_validate(enrollment)
            for enrollment in enrollments
        ]


        return EnrollmentListResponse(
            items=enrollment_responses,
            total=total,
            page=page,
            size=size,
        )


    async def update_enrollment_status(
        self,
        enrollment_id: int,
        payload: EnrollmentStatusUpdate,
        current_user,
    ):
        # Get enrollment
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise NotFoundException("Enrollment not found")

        old_status = enrollment.status

        # Get associated batch
        batch = await self.batch_repo.get_by_id(enrollment.batch_id)
        if not batch:
            raise NotFoundException("Batch not found")

        # Check trainer authorization
        if current_user.role == "trainer":
            trainer = await self.trainer_repo.get_trainer_by_email( current_user.email)

            if not trainer or not trainer.is_active:
                raise NotFoundException("Active trainer not found")

            if trainer.trainer_id != batch.trainer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to update this enrollment"
                )

        # Prevent updating terminal statuses
        if enrollment.status in ["Cancelled", "Completed"]:
            raise ConflictException(f"Cannot update an enrollment with status '{enrollment.status}'" )

        # Validate remarks
        if payload.status in ["Paused", "Cancelled"]:
            if not payload.remarks:
                raise ConflictException(
                    "Remarks are required when pausing or cancelling enrollment"
                )

        # Validate completion
        if payload.status == "Completed":
            if batch.status != "completed":
                raise ConflictException("Enrollment can be completed only after batch completion")

        # prevent duplicate status change
        if old_status == payload.status:
            raise ConflictException(
                f"Enrollment is already in '{old_status}' status"
            )

        # Update enrollment
        enrollment.status = payload.status
        enrollment.status_update_date = datetime.now(timezone.utc)
        enrollment.updated_at = datetime.now(timezone.utc)
        enrollment.remarks = payload.remarks

        # Save changes
        updated_enrollment = await self.enrollment_repo.update(enrollment)

        # Get employee details for email notification
        employee = await self.employee_repo.get_employee_by_id(updated_enrollment.employee_id)
        if employee:
            await self.email_service.send_enrollment_status_email_async(
                employee_name=employee.full_name,
                employee_email=employee.email,
                enrollment_id=updated_enrollment.enrollment_id,
                batch_name=batch.batch_name,
                old_status=old_status,
                new_status=updated_enrollment.status,
                remarks=updated_enrollment.remarks,
            )

        return EnrollmentResponse.model_validate(updated_enrollment)


    # Get Enrollment by employee_id
    async def get_enrollments_by_employee(
        self,
        employee_id: int,
        current_user: User
    ) -> list[EnrollmentResponse]:

        trainer_id = None
        # Trainer can view only enrollments from assigned batches
        if current_user.role == "trainer":
            trainer = await self.trainer_repo.get_trainer_by_email( current_user.email)

            if not trainer or not trainer.is_active:
                raise NotFoundException("Active trainer not found")
            trainer_id = trainer.trainer_id

        enrollments = await self.enrollment_repo.get_by_employee_id(
            employee_id=employee_id,
            trainer_id=trainer_id
        )

        return [
            EnrollmentResponse.model_validate(enrollment)
            for enrollment in enrollments
        ]


    async def get_enrollments_by_batch(
        self, 
        batch_id : int ,
        current_user: User
    )->list[EnrollmentResponse]:
        batch = await self.validate_batch_access(batch_id, current_user)
        enrollments = await self.enrollment_repo.get_by_batch_id(
            batch_id= batch_id
        )

        return [
            EnrollmentResponse.model_validate(enrollment)
            for enrollment in enrollments
        ]




