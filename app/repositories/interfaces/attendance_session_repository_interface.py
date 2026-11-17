from abc import ABC, abstractmethod

from app.models import AttendanceSession


class AttendanceSessionRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, attendance_session: AttendanceSession) -> AttendanceSession:
        pass

    async def get_by_id(self, id: int) -> AttendanceSession | None:
        pass

    async def update(
        self, attendance_session: AttendanceSession, fields: dict
    ) -> AttendanceSession:
        pass

    async def get_all(self, filters):
        pass

    async def get_by_trainer_id(self, id: int) -> list[AttendanceSession]:
        pass
