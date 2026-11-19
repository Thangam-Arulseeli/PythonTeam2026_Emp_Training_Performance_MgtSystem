from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import AttendanceSessionStatus, AttendanceStatus
from app.models import AttendanceRecord, AttendanceSession, Batch, Enrollment
from app.repositories.interfaces import AttendanceSessionRepositoryInterface


class AttendanceSessionRepository(AttendanceSessionRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, attendance_session: AttendanceSession) -> AttendanceSession:
        self.db.add(attendance_session)
        await self.db.flush()
        await self.db.refresh(attendance_session)

        return attendance_session

    async def get_by_id(self, id: int) -> AttendanceSession | None:
        query = (
            select(AttendanceSession)
            .options(
                selectinload(AttendanceSession.batch),
                selectinload(AttendanceSession.attendance_records),
            )
            .where(AttendanceSession.id == id)
        )
        return await self.db.scalar(query)

    async def update(
        self, attendance_session: AttendanceSession, fields: dict
    ) -> AttendanceSession:
        for field, value in fields.items():
            setattr(attendance_session, field, value)

        await self.db.flush()
        await self.db.refresh(attendance_session)
        return attendance_session

    async def get_all(
        self,
        filters: dict,
    ) -> list[AttendanceSession]:

        query_filters = dict(filters)
        role = query_filters.pop("role", None)
        query = select(AttendanceSession)

        if role == "trainer":
            trainer_id = query_filters.pop("trainer_id", None)

            if trainer_id is None:
                raise ValueError("trainer_id is required for trainer access")

            query = query.join(Batch, AttendanceSession.batch_id == Batch.id).where(
                Batch.trainer_id == trainer_id
            )

        elif role == "employee":
            employee_id = query_filters.pop("employee_id", None)

            if employee_id is None:
                raise ValueError("employee_id is required for employee access")

            enrolled_batches = select(Enrollment.batch_id).where(
                Enrollment.employee_id == employee_id
            )

            query = query.where(AttendanceSession.batch_id.in_(enrolled_batches))

        elif role == "admin":
            pass

        else:
            raise ValueError("Invalid role for attendance session access")

        if query_filters.get("batch_id") is not None:
            query = query.where(AttendanceSession.batch_id == query_filters["batch_id"])

        if query_filters.get("session_date") is not None:
            query = query.where(
                AttendanceSession.session_date == query_filters["session_date"]
            )

        if query_filters.get("start_date") is not None:
            query = query.where(
                AttendanceSession.session_date >= query_filters["start_date"]
            )

        if query_filters.get("end_date") is not None:
            query = query.where(
                AttendanceSession.session_date <= query_filters["end_date"]
            )

        if query_filters.get("status") is not None:
            query = query.where(AttendanceSession.status == query_filters["status"])

        if query_filters.get("topic") is not None:
            query = query.where(
                AttendanceSession.topic.ilike(f"%{query_filters['topic']}%")
            )

        offset = query_filters.get("offset", 0)
        limit = query_filters.get("limit", 20)

        query = (
            query.order_by(
                AttendanceSession.session_date.desc(),
                AttendanceSession.start_time.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        sessions = list(result.scalars().all())

        return sessions

    async def get_by_trainer_id(self, id: int) -> list[AttendanceSession]:
        query = (
            select(AttendanceSession)
            .options(
                selectinload(AttendanceSession.batch),
                selectinload(AttendanceSession.attendance_records),
            )
            .join(Batch)
            .where(Batch.trainer_id == id)
            .order_by(AttendanceSession.session_date.desc())
        )

        result = await self.db.scalars(query)
        return list(result.all())

    async def get_by_employee_id(self, employee_id: int) -> list[AttendanceSession]:
        query = (
            select(AttendanceSession)
            .join(Batch, AttendanceSession.batch_id == Batch.id)
            .join(Enrollment, Enrollment.batch_id == Batch.id)
            .where(Enrollment.employee_id == employee_id)
            .order_by(AttendanceSession.session_date.desc())
            .distinct()
        )

        result = await self.db.scalars(query)
        return list(result.all())

    async def complete(
        self, attendance_session: AttendanceSession
    ) -> AttendanceSession:
        attendance_session.status = AttendanceSessionStatus.COMPLETED
        await self.db.flush()
        await self.db.refresh(attendance_session)
        return attendance_session

    async def get_session_attendance_summary(self, session_id: int):
        query = select(
            func.count(AttendanceRecord.id).label("total_records"),
            func.count(
                case((AttendanceRecord.status == AttendanceStatus.PRESENT, 1))
            ).label("present"),
            func.count(
                case((AttendanceRecord.status == AttendanceStatus.ABSENT, 1))
            ).label("absent"),
        ).where(AttendanceRecord.session_id == session_id)

        result = await self.db.execute(query)
        return result.mappings().one()
