
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import EmployeeData

from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface
)


class EmployeeRepositoryImpl(EmployeeRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE EMPLOYEE
    async def create_employee(
        self,
        employee: EmployeeData
    ) -> EmployeeData:

        self.db.add(employee)
        await self.db.flush()

        return employee

    # GET ALL ACTIVE EMPLOYEES
    async def get_all_employees(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> list[EmployeeData]:

        statement = (
            select(EmployeeData)
            .where(EmployeeData.is_active.is_(True))
            .order_by(EmployeeData.employee_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    # GET EMPLOYEE BY ID
    async def get_employee_by_id(
        self,
        employee_id: int
    ) -> EmployeeData | None:

        statement = (
            select(EmployeeData)
            .where(
                EmployeeData.employee_id == employee_id,
                EmployeeData.is_active.is_(True)
            )
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    # PATCH EMPLOYEE
    async def update_employee(
        self,
        employee: EmployeeData,
        update_data: dict[str, Any]
    ) -> EmployeeData:

        for field, value in update_data.items():
            setattr(employee, field, value)

        await self.db.flush()

        return employee

    # SOFT DELETE EMPLOYEE
    async def soft_delete_employee(
        self,
        employee: EmployeeData
    ) -> EmployeeData:

        employee.is_active = False

        await self.db.flush()

        return employee
