from abc import ABC, abstractmethod

from app.models import AttendanceSession


class AttendanceSessionRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, attendance_session: AttendanceSession) -> AttendanceSession:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> AttendanceSession | None:
        pass

    @abstractmethod
    async def update(
        self, attendance_session: AttendanceSession, fields: dict
    ) -> AttendanceSession:
        pass

    @abstractmethod
    async def get_all(self, filters):
        pass

    @abstractmethod
    async def get_by_trainer_id(self, id: int) -> list[AttendanceSession]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: int) -> list[AttendanceSession]:
        pass

    @abstractmethod 
    async def complete(self , attendance_session:AttendanceSession) -> AttendanceSession :
        pass 