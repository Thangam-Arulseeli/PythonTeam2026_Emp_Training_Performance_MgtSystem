from sqlalchemy import literal, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.core import AttendanceStatus
from app.models import AttendanceRecord, AttendanceSession, Enrollment
from app.repositories.interfaces import AttendanceRecordRepositoryInterface


class AttendanceRecordRepository(AttendanceRecordRepositoryInterface):
    def __init__(self, db):
        self.db = db

    async def create(self, attendance_record: AttendanceRecord) -> AttendanceRecord:
        self.db.add(attendance_record)
        await self.db.flush()
        await self.db.refresh(attendance_record)
        return attendance_record

    async def get_by_id(self, id: int) -> AttendanceRecord | None:
        query = (
            select(AttendanceRecord)
            .options(
                selectinload(AttendanceRecord.enrollment),
                selectinload(AttendanceRecord.marked_by_user),
                selectinload(AttendanceRecord.session).selectinload(
                    AttendanceSession.batch
                ),
            )
            .where(AttendanceRecord.id == id)
        )

        return await self.db.scalar(query)

    async def update_status(
        self, attendance_record: AttendanceRecord, status: AttendanceStatus
    ) -> AttendanceRecord:
        attendance_record.status = status
        await self.db.flush()
        await self.db.refresh(attendance_record)
        return attendance_record

    async def get_by_session_id(self, session_id: int) -> list[AttendanceRecord]:
        query = (
            select(AttendanceRecord)
            .where(AttendanceRecord.session_id == session_id)
            .options(
                selectinload(AttendanceRecord.enrollment),
                selectinload(AttendanceRecord.marked_by_user),
            )
            .order_by(AttendanceRecord.id)
        )

        result = await self.db.scalars(query)
        return result.all()

    async def finalize_session_attendance(
        self,
        session_id: int,
        batch_id: int,
        marked_by: int,
    ) -> int:

        enrollment_query = select(
            literal(session_id),
            Enrollment.enrollment_id,
            literal(AttendanceStatus.PRESENT),
            literal(marked_by),
        ).where(Enrollment.batch_id == batch_id)

        query = (
            insert(AttendanceRecord)
            .from_select(
                ["session_id", "enrollment_id", "status", "marked_by"],
                enrollment_query,
            )
            .on_conflict_do_nothing(constraint="uq_session_enrollment")
        )

        result = await self.db.execute(query)

        return result.rowcount

    async def get_by_employee_id(
        self, employee_id: int, limit: int, offset: int
    ) -> list[AttendanceRecord | None]:
        query = (
            select(AttendanceRecord)
            .join(AttendanceRecord.enrollment)
            .join(AttendanceRecord.session)
            .where(Enrollment.employee_id == employee_id)
            .options(selectinload(AttendanceRecord.session))
            .order_by(AttendanceSession.session_date.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.scalars(query)
        return result.all()
