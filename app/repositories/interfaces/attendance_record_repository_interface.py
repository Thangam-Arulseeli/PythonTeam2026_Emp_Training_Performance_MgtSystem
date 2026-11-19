from abc import ABC, abstractmethod

from app.core import AttendanceStatus
from app.models import AttendanceRecord


class AttendanceRecordRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, attendance_record: AttendanceRecord) -> AttendanceRecord:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> AttendanceRecord | None:
        pass

    @abstractmethod
    async def update_status(
        self, attendance_record: AttendanceRecord, status: AttendanceStatus
    ) -> AttendanceRecord:
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: int) -> list[AttendanceRecord | None]:
        pass

    @abstractmethod
    async def finalize_session_attendance(
        self,
        session_id: int,
        batch_id: int,
        marked_by: int,
    ) -> int:
        pass

    @abstractmethod
    async def get_by_employee_id(
        self, employee_id: int, limit: int, offset: int
    ) -> list[AttendanceRecord | None]:
        pass
