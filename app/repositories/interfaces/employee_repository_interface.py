
from abc import ABC, abstractmethod
from typing import Any

from app.models.employee import EmployeeData


class EmployeeRepositoryInterface(ABC):

    @abstractmethod
    async def create_employee( self, employee: EmployeeData  ) -> EmployeeData:
        """create a new employee """

    
    @abstractmethod
    async def get_all_employees( self, skip: int = 0, limit: int = 20) -> list[EmployeeData]:
        """display all the active employee using pagination"""

    
    @abstractmethod
    async def get_all_employees_inactive( self, skip: int = 0, limit: int = 20) -> list[EmployeeData]:
        """display all the inactive employee using pagination"""

    
    @abstractmethod
    async def get_employee_by_id(self,employee_id: int) -> EmployeeData | None:
        """display all the active employee using employee id"""

    
    @abstractmethod
    async def update_employee(self,employee: EmployeeData,update_data: dict[str, Any]) -> EmployeeData:
        """change the employee personal details"""

    
    @abstractmethod
    async def soft_delete_employee(self,employee: EmployeeData ) -> EmployeeData:
        """soft-delete an employee by changing the employee's status to inactive"""

    
    @abstractmethod
    async def reactivate_employee(self,employee: EmployeeData,) -> EmployeeData:
        """update the inactive employee to active employee"""


