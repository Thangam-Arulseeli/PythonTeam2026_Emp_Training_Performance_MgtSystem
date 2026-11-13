
import select

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import EmployeeData

from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)

from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)

from app.exceptions.exceptions import (
    EmployeeNotFoundException,
    EmployeeAlreadyExistsException,
    InvalidEmployeeDataException,
)


class EmployeeService:

    def __init__( self, db: AsyncSession, repository: EmployeeRepositoryInterface, ):
        self.db = db
        self.repository = repository

    # CREATE EMPLOYEE
    async def create_employee(
        self,
        data: EmployeeCreate,
    ) -> EmployeeData:

        employee = EmployeeData( **data.model_dump() )

        try:
            employee = await self.repository.create_employee( employee)

            await self.db.commit()
            await self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            await self.db.rollback()

            if getattr( exc.orig, "sqlstate", None ) == "23505":
                raise EmployeeAlreadyExistsException( "email or phone") from exc

            raise

    # DISPLAY ALL ACTIVE EMPLOYEES
    async def get_all_employees(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[EmployeeData]:

        return await self.repository.get_all_employees( skip=skip, limit=limit, )

    # DISPLAY EMPLOYEE BY ID
    async def get_employee_by_id(
        self,
        employee_id: int,
    ) -> EmployeeData:

        employee = await self.repository.get_employee_by_id( employee_id)

        if employee is None:
            raise EmployeeNotFoundException()

        return employee

    # UPDATE EMPLOYEE USING PATCH
    async def update_employee(
        self,
        employee_id: int,
        data: EmployeeUpdate,
    ) -> EmployeeData:

        employee = await self.get_employee_by_id(employee_id)

        update_data = data.model_dump(exclude_unset=True)

        required_fields = {
            "full_name",
            "email",
            "department",
            "role"
        }

        for field in required_fields:
            if (
                field in update_data
                and update_data[field] is None
            ):
                raise InvalidEmployeeDataException( f"{field} cannot be null")

        # Keep deactivation exclusive to DELETE.
        if "is_active" in update_data:
            raise InvalidEmployeeDataException( "Use DELETE endpoint to deactivate an employee")

        try:
            employee = await self.repository.update_employee(
                employee,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            await self.db.rollback()

            if getattr(
                exc.orig, "sqlstate", None
            ) == "23505":
                raise EmployeeAlreadyExistsException(
                    "email or phone"
                ) from exc

            raise

    # SOFT DELETE EMPLOYEE
    async def delete_employee(
        self,
        employee_id: int,
    ) -> None:

        employee = await self.get_employee_by_id(employee_id)

        try:
            # Find matching user using email and role
            if employee.role in ("employee", "trainee"):

                result = await self.db.execute(
                    select(User).where(
                        User.email == employee.email,
                        User.role == "employee",
                    )
                )

                user = result.scalar_one_or_none()

                # Deactivate matching user account
                if user is not None:
                    user.is_active = False

            # Soft delete employee
            await self.repository.soft_delete_employee(employee)

            # Commit both changes together
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise
