from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AttendanceSessionStatus, AttendanceStatus
from app.exceptions import ConflictException, NotAuthorizedException, NotFoundException
from app.models import AttendanceRecord, User
from app.repositories.interfaces import (
    AttendanceRecordRepositoryInterface,
    AttendanceSessionRepositoryInterface,
    EmployeeRepositoryInterface,
    EnrollmentRepositoryInterface,
)
from app.repositories.interfaces import TrainerRepository as TrainerRepositoryInterface
from app.schemas import AttendanceRecordCreate
from app.services.interfaces import AttendanceRecordServiceInterface


class AttendanceRecordService(AttendanceRecordServiceInterface):
    def __init__(
        self,
        db: AsyncSession,
        repository: AttendanceRecordRepositoryInterface,
        session_repository: AttendanceSessionRepositoryInterface,
        trainer_repository: TrainerRepositoryInterface,
        enrollment_repository: EnrollmentRepositoryInterface,
        employee_repository: EmployeeRepositoryInterface,
    ):
        self.db = db
        self.repository = repository
        self.session_repository = session_repository
        self.trainer_repository = trainer_repository
        self.enrollment_repository = enrollment_repository
        self.employee_repository = employee_repository

    async def create_record(
        self, data: AttendanceRecordCreate, user: User
    ) -> AttendanceRecord:
        attendance_session = await self.session_repository.get_by_id(data.session_id)

        if attendance_session is None:
            raise NotFoundException(f"Session with id {data.session_id} is not found")

        if attendance_session.status == AttendanceSessionStatus.CANCELLED:
            raise ConflictException("Session is cancelled, cannot mark attendance")

        enrollment = await self.enrollment_repository.get_by_id(data.enrollment_id)
        if enrollment is None:
            raise NotFoundException(
                f"enrollment with id {data.enrollment_id} is not found"
            )

        if attendance_session.batch_id != enrollment.batch_id:
            raise ConflictException("The enrollment id is not enrolled in this batch")

        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)
            if trainer is None:
                raise NotFoundException("Cannot find your trainer profile")

            if attendance_session.batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to perform this action"
                )
        attendance_record = AttendanceRecord(
            **data.model_dump(), marked_by=user.user_id
        )

        try:
            result = await self.repository.create(attendance_record)
            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def update_record_status(
        self, record_id: int, status: AttendanceStatus, user: User
    ) -> AttendanceRecord:
        record = await self.repository.get_by_id(record_id)

        if record is None:
            raise NotFoundException(f"Record with id {record_id} not found")

        if record.status == status:
            return record
        if user.role == "trainer" and record.marked_by_user.user_id != user.user_id:
            raise NotAuthorizedException(
                "you are not allowed to perform this operation"
            )
        if record.session.status == AttendanceSessionStatus.CANCELLED:
            raise ConflictException("Session is cancelled, cannot mark attendance")

        try:
            result = await self.repository.update_status(record, status)
            await self.db.commit()
            return result
        except Exception:
            await self.db.rollback()
            raise

    async def get_records_by_session_id(
        self, session_id: int, user: User
    ) -> list[AttendanceRecord | None]:

        attendance_session = await self.session_repository.get_by_id(session_id)

        if attendance_session is None:
            raise NotFoundException(f"Session with id {session_id} is not found")

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
        result = await self.repository.get_by_session_id(session_id)
        return result

    async def get_record_by_id(self, record_id: int, user: User) -> AttendanceRecord:
        attendance_record = await self.repository.get_by_id(record_id)

        if attendance_record is None:
            raise NotFoundException("Attendance not found")
        if user.role == "trainer":
            trainer = await self.trainer_repository.get_trainer_by_email(user.email)

            if trainer is None:
                raise NotFoundException(
                    "Trainer profile linked with the user not found"
                )
            if attendance_record.session.batch.trainer_id != trainer.trainer_id:
                raise NotAuthorizedException(
                    "You are not allowed to access this resouce"
                )
        return attendance_record

    async def get_user_attendance_records(
        self, user: User, limit: int, offset: int
    ) -> list[AttendanceRecord]:
        employee = await self.employee_repository.get_employee_by_email(user.email)

        if employee is None:
            raise NotFoundException("Employee profile attached with user not found")
        result = await self.repository.get_by_employee_id(
            employee.employee_id, limit, offset
        )
        return result
