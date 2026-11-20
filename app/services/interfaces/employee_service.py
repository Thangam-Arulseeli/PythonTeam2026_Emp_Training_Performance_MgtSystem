from abc import ABC, abstractmethod

from app.models.employee import EmployeeData
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeServiceInterface(ABC):
    @abstractmethod
    async def create_employee(self, data: EmployeeCreate) -> EmployeeData:
        """create a new employee"""

    @abstractmethod
    async def get_all_employees(
        self, skip: int = 0, limit: int = 10
    ) -> list[EmployeeData]:
        """display all the active employee using pagination"""

    @abstractmethod
    async def get_all_employees_inactive(
        self, skip: int = 0, limit: int = 10
    ) -> list[EmployeeData]:
        """display all the inactive employee using pagination"""

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> EmployeeData:
        """display all the active employee using employee id"""

    @abstractmethod
    async def update_employee(
        self, employee_id: int, data: EmployeeUpdate
    ) -> EmployeeData:
        """change the employee personal details"""

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> dict:
        """soft-delete an employee by changing the employee's status to inactive"""

    @abstractmethod
    async def reactivate_employee(self, employee_id: int) -> EmployeeData:
        """update the inactive employee to active employee"""
