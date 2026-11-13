
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import (
    EmployeeAlreadyExistsException,
    EmployeeNotFoundException,
    InvalidEmployeeDataException,
)
from app.models.employee import EmployeeData
from app.models.user import User
from app.repositories.interfaces.employee_repository_interface import (
    EmployeeRepositoryInterface,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)


class EmployeeService:

    def __init__( self, db: AsyncSession, repository: EmployeeRepositoryInterface, ):
        self.db = db
        self.repository = repository


    # CREATE EMPLOYEE
    async def create_employee( self, data: EmployeeCreate,) -> EmployeeData:

        """create a new employee"""

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

            raise InvalidEmployeeDataException(str(exc)) from exc


    # DISPLAY ALL ACTIVE EMPLOYEES
    async def get_all_employees(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[EmployeeData]:

        """display all the active employee using pagination"""

        return await self.repository.get_all_employees( skip=skip, limit=limit, )


    # DISPLAY ALL INACTIVE EMPLOYEES
    async def get_all_employees_inactive(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[EmployeeData]:

        """display all the inactive employee using pagination"""

        return await self.repository.get_all_employees_inactive( skip=skip, limit=limit, )



    # DISPLAY EMPLOYEE BY ID
    async def get_employee_by_id( self, employee_id: int,) -> EmployeeData:

        """display all the active employee using employee id"""

        employee = await self.repository.get_employee_by_id( employee_id)

        if employee is None:
            raise EmployeeNotFoundException()

        return employee


    # UPDATE EMPLOYEE DETAILS USING PATCH
    async def update_employee(
        self,
        employee_id: int,
        data: EmployeeUpdate,
    ) -> EmployeeData:

        """change the employee personal details"""

        employee = await self.get_employee_by_id(employee_id)

        # Extract only the fields provided in the PATCH request.
        update_data = data.model_dump(exclude_unset=True)

        # Define mandatory employee fields that cannot be set to null.
        required_fields = {
            "full_name",
            "email",
            "department",
            "role"
        }

        # Validate that any provided mandatory field is not null.
        for field in required_fields:
            if (
                field in update_data
                and update_data[field] is None
            ):
                raise InvalidEmployeeDataException( f"{field} cannot be null")


        try:
            employee = await self.repository.update_employee(employee,update_data,)

            await self.db.commit()
            await self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            await self.db.rollback()

            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise EmployeeAlreadyExistsException("email or phone") from exc

            raise InvalidEmployeeDataException(str(exc)) from exc


    # SOFT DELETE EMPLOYEE - MAKE EMPLOYEE INACTIVE
    async def delete_employee(self,employee_id: int,) -> dict:

        """soft-delete an employee by changing the employee's status to inactive"""
       
        employee = await self.get_employee_by_id(employee_id)

        try:
            # Find matching user table using email and role
            if employee.role == "employee":

                #remove the authoriztion to login using user table as delete in employee
                result = await self.db.execute(
                    select(User).where(
                        User.email == employee.email,
                        User.role == "employee",
                    )
                )

                user = result.scalar_one_or_none()

                if user is not None:
                    user.is_active = False

            # Soft delete employee
            await self.repository.soft_delete_employee(employee)

            # Commit both changes
            await self.db.commit()

            return {
                "message": "Employee deleted successfully",
                "employee_id": employee.employee_id,
                "full_name": employee.full_name,
            }

        except Exception as exc:
            await self.db.rollback()
            raise InvalidEmployeeDataException(str(exc)) from exc


    # UPDATE THE EMPLOYEE TO ACTIVE EMPLOYEE
    async def reactivate_employee(
        self,
        employee_id: int,
    ) -> EmployeeData:

        """update the inactive employee to active employee"""

        employee = ( await self.repository.get_inactive_employee_by_id(employee_id) )

        if employee is None:
            raise EmployeeNotFoundException()

        try:
            # Find matching user table using email and role
            if employee.role == "employee":

                #add the authoriztion to login using user table as delete in employee
                result = await self.db.execute(
                    select(User).where(
                        User.email == employee.email,
                        User.role == "employee",
                    )
                )

                user = result.scalar_one_or_none()

                if user is not None:
                    user.is_active = True

            # Reactivate employee through repository
            employee = await self.repository.reactivate_employee(employee)

            #Commit both changes
            await self.db.commit()
            await self.db.refresh(employee)

            return employee

        except Exception:
            await self.db.rollback()
            raise
