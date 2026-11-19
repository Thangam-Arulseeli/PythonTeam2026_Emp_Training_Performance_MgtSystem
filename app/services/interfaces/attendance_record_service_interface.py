from abc import ABC, abstractmethod

from app.core import AttendanceStatus
from app.models import AttendanceRecord, User
from app.schemas import AttendanceRecordCreate


class AttendanceRecordServiceInterface(ABC):
    @abstractmethod
    async def create_record(
        self, data: AttendanceRecordCreate, user: User
    ) -> AttendanceRecord:
        pass

    @abstractmethod
    async def update_record_status(
        self, record_id: int, status: AttendanceStatus, user: User
    ) -> AttendanceRecord: ...

    @abstractmethod
    async def get_records_by_session_id(
        self, session_id: int, user: User
    ) -> list[AttendanceRecord | None]:
        pass

    @abstractmethod
    async def get_record_by_id(self, record_id: int, user: User) -> AttendanceRecord:
        pass

    @abstractmethod
    async def get_user_attendance_records(
        self, user: User, limit: int, offset: int
    ) -> list[AttendanceRecord]:
        pass
