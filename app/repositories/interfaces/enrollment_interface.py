from abc import ABC, abstractmethod

from app.models.enrollment import Enrollment


class EnrollmentInterface(ABC):
    @abstractmethod
    async def count_active_by_employee(self, employee_id: int) -> int:
        pass

    @abstractmethod
    async def create(self, data: dict[str, object]) -> Enrollment:
        pass

    @abstractmethod
    async def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int,
        limit: int,
        status: str | None = None,
        trainer_id: int | None = None,
    ) -> tuple[list[Enrollment], int]:
        pass

    @abstractmethod
    async def get_by_employee_id(
        self, employee_id: int, trainer_id: int | None = None
    ) -> list[Enrollment]:
        pass

    @abstractmethod
    async def update(self, enrollment: Enrollment) -> Enrollment:
        pass
