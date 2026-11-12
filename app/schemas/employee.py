
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


FULL_NAME = { "min_length": 1, "max_length": 50}

EMAIL = {"max_length": 300}

PHONE = { "pattern": r"^[0-9]{10}$"}

DEPARTMENT = {
    "min_length": 1,
    "max_length": 30
}

ROLE = { "pattern": r"^(employee|trainee)$" }


class EmployeeBase(BaseModel):

    full_name: str = Field(**FULL_NAME)

    email: EmailStr = Field(**EMAIL)

    phone: str | None = Field( default=None, **PHONE)

    department: str = Field( default="Unassigned",**DEPARTMENT)

    role: str = Field(default="employee",**ROLE)

    date_of_birth: date | None = None
    joining_date: date | None = None

    @field_validator("full_name", "department")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):

    full_name: str | None = Field( default=None, **FULL_NAME )

    email: EmailStr | None = Field( default=None, **EMAIL )

    phone: str | None = Field( default=None, **PHONE )

    department: str | None = Field( default=None, **DEPARTMENT )

    role: str | None = Field( default=None, **ROLE )

    date_of_birth: date | None = None
    joining_date: date | None = None
    is_active: bool | None = None

    @field_validator("full_name", "department")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Field cannot be empty")

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        return value


class EmployeeResponse(EmployeeBase):

    employee_id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
