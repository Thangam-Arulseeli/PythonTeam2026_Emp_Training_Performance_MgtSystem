from abc import ABC, abstractmethod

from app.models import AttendanceSession, User
from app.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionFilter,
    AttendanceSessionUpdate,
)


class AttendanceSessionServiceInterface(ABC):
    @abstractmethod
    async def create(
        self, data: AttendanceSessionCreate, user: User
    ) -> AttendanceSession:
        pass

    @abstractmethod
    async def update_session(
        self,
        session_id: int,
        data: AttendanceSessionUpdate,
        user: AttendanceSessionUpdate,
    ) -> AttendanceSession:
        pass

    @abstractmethod
    async def get_session_by_id(self, session_id: int, user: User) -> AttendanceSession:
        pass

    @abstractmethod
    async def get_all_sessions(
        self, user: User, filters: AttendanceSessionFilter
    ) -> AttendanceSession:
        pass

    @abstractmethod
    async def get_by_trainer_id(self, trainer_id: int) -> list[AttendanceSession]:
        pass

    @abstractmethod
    async def get_current_user_sessions(self , user:User ) -> list[AttendanceSession] :
        pass 

    @abstractmethod 
    async def complete_session(self , session_id:int , user:User) -> AttendanceSession :
        pass  
