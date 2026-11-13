
from abc import ABC, abstractmethod
from typing import Any

from app.models.employee import EmployeeData


class EmployeeRepositoryInterface(ABC):

    @abstractmethod
    async def create_employee( self, employee: EmployeeData  ) -> EmployeeData:
        pass

    @abstractmethod
    async def get_all_employees( self, skip: int = 0, limit: int = 20) -> list[EmployeeData]:
        pass

    @abstractmethod
    async def get_all_employees_inactive( self, skip: int = 0, limit: int = 20) -> list[EmployeeData]:
        pass

    @abstractmethod
    async def get_employee_by_id(self,employee_id: int) -> EmployeeData | None:
        pass

    @abstractmethod
    async def update_employee(self,employee: EmployeeData,update_data: dict[str, Any]) -> EmployeeData:
        pass

    @abstractmethod
    async def soft_delete_employee(self,employee: EmployeeData ) -> EmployeeData:
        pass
    
    @abstractmethod
    async def reactivate_employee(self,employee: EmployeeData,) -> EmployeeData:
        pass


