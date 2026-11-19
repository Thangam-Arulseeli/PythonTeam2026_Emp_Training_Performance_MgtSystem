from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AttendanceSessionStatus
from app.exceptions import ConflictException, NotAuthorizedException, NotFoundException
from app.models import AttendanceSession, User
from app.repositories.interfaces import (
    AttendanceRecordRepositoryInterface,
    AttendanceSessionRepositoryInterface,
    EmployeeRepositoryInterface,
    EnrollmentRepositoryInterface,
)
from app.repositories.interfaces import BatchInterface as BatchRepositoryInterface
from app.repositories.interfaces import TrainerRepository as TrainerRepositoryInterface
from app.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionFilter,
    AttendanceSessionUpdate,
)
from app.services.interfaces import AttendanceSessionServiceInterface


class AttendanceSessionService(AttendanceSessionServiceInterface):
    def __init__(
        self,
        db: AsyncSession,
        repository: AttendanceSessionRepositoryInterface,
        batch_repository: BatchRepositoryInterface,
        trainer_repository: TrainerRepositoryInterface,
        employee_repository: EmployeeRepositoryInterface,
        enrollment_repository: EnrollmentRepositoryInterface,
        record_repository: AttendanceRecordRepositoryInterface,
    ):
        self.db = db
        self.repository = repository
        self.batch_repository = batch_repository
        self.trainer_repository = trainer_repository
        self.employee_repository = employee_repository
        self.enrollment_repository = enrollment_repository
        self.record_repository = record_repository

    async def create(
        self, data: AttendanceSessionCreate, user: User
    ) -> AttendanceSession:
        batch = await self.batch_repository.get_by_id(data.batch_id)

        if batch is None:
            raise NotFoundException(f"Batch with id {data.batch_id} not found")

        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )

            if batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to access this resouce"
                )

        attendance_session = AttendanceSession(**data.model_dump())
        try:
            result = await self.repository.create(attendance_session)
            await self.db.commit()
            return result
        except Exception:
            await self.db.rollback()
            raise

    async def update_session(
        self,
        session_id: int,
        data: AttendanceSessionUpdate,
        user: AttendanceSessionUpdate,
    ) -> AttendanceSession:
        attendance_session = await self.repository.get_by_id(session_id)

        if attendance_session is None:
            raise NotFoundException(
                f"Attendance session with id {session_id} not found"
            )
        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )

            if attendance_session.batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to access this resouce"
                )

        fields = data.model_dump(exclude_unset=True)
        # Completion must go through complete_session so absences are finalized.
        if (
            fields.get("status") == AttendanceSessionStatus.COMPLETED
            and attendance_session.status != AttendanceSessionStatus.COMPLETED
        ):
            raise ConflictException(
                "Use the complete-session endpoint to complete attendance"
            )

        new_start = fields.get("start_time", attendance_session.start_time)
        new_end = fields.get("end_time", attendance_session.end_time)
        if new_end <= new_start:
            raise ConflictException("End time must be later than start time")
        try:
            result = await self.repository.update(attendance_session, fields)
            await self.db.commit()
            return result
        except Exception:
            await self.db.rollback()
            raise

    async def get_session_by_id(
        self,
        session_id: int,
        user: User,
    ) -> AttendanceSession:

        attendance_session = await self.repository.get_by_id(session_id)

        if attendance_session is None:
            raise NotFoundException(f"Session with id {session_id} not found")

        if user.role == "employee":
            employee = await self.employee_repository.get_employee_by_email(user.email)

            if employee is None:
                raise NotFoundException("Employee profile not found")

            enrollments = await self.enrollment_repository.get_by_employee_id(
                employee.employee_id
            )

            enrolled_batch_ids = {enrollment.batch_id for enrollment in enrollments}

            if attendance_session.batch_id not in enrolled_batch_ids:
                raise NotAuthorizedException("You are not enrolled in this batch")

        elif user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)
            if (
                trainer is None
                or not trainer.is_active
                or attendance_session.batch.trainer_id != trainer.trainer_id
            ):
                raise NotAuthorizedException(
                    "You are not allowed to access this resource"
                )

        elif user.role != "admin":
            raise NotAuthorizedException("You are not allowed to access this resource")

        return attendance_session

    async def get_all_sessions(
        self, user: User, filters: AttendanceSessionFilter
    ) -> AttendanceSession:
        new_filters = {**filters.model_dump(exclude_unset=True)}

        new_filters["role"] = user.role

        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)
            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )
            new_filters["trainer_id"] = trainer.trainer_id

        if user.role == "employee":
            employee = await self.employee_repository.get_employee_by_email(user.email)
            if employee is None:
                raise NotFoundException("Employee profile attached to user not found")
            new_filters["employee_id"] = employee.employee_id

        result = await self.repository.get_all(new_filters)

        return result

    async def get_by_trainer_id(self, trainer_id: int) -> list[AttendanceSession]:
        result = await self.repository.get_by_trainer_id(trainer_id)

        return result

    async def get_current_user_sessions(self, user: User) -> list[AttendanceSession]:
        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )
            return await self.get_by_trainer_id(trainer.trainer_id)

        employee = await self.employee_repository.get_employee_by_email(user.email)

        if employee is None:
            raise NotFoundException("employee profile linked with the user not found")
        result = await self.repository.get_by_employee_id(employee.employee_id)
        return result

    async def complete_session(self, session_id: int, user: User) -> AttendanceSession:
        attendance_session = await self.repository.get_by_id(session_id)

        if attendance_session is None:
            raise NotFoundException(
                f"Attendance session with id {session_id} not found"
            )

        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )
            if attendance_session.batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to perform this operation"
                )

        try:
            await self.record_repository.finalize_session_attendance(
                session_id=attendance_session.id,
                batch_id=attendance_session.batch_id,
                marked_by=user.user_id,
            )
            result = await self.repository.complete(attendance_session)
            await self.db.commit()
            return result
        except Exception:
            await self.db.rollback()
            raise

    async def get_session_summary(self, session_id: int, user: User):
        attendance_session = await self.repository.get_by_id(session_id)

        if attendance_session is None:
            raise NotFoundException(
                f"Attendance session with id {session_id} not found"
            )

        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )
            if attendance_session.batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to perform this operation"
                )

        statistics = await self.repository.get_session_attendance_summary(session_id)

        result = {
            "session": attendance_session.id,
            "session_date": attendance_session.session_date,
            "total enrollments": statistics["total_records"],
            "present": statistics["present"],
            "absent": statistics["absent"],
            "unmarked": statistics["total_records"]
            - statistics["present"]
            - statistics["absent"],
            "attendance_percentage": round(
                (statistics["present"] / statistics["total_records"]) * 100, 2
            )
            if attendance_session.status != AttendanceSessionStatus.CANCELLED
            else None,
            "status": attendance_session.status,
            "is_finalized": attendance_session.status
            == AttendanceSessionStatus.COMPLETED,
        }

        return result
    