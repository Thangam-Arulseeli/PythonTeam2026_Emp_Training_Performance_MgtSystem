
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

def validate_employee_age(value: date | None) -> date | None:
    if value is None:
        return value

    today = date.today()

    age = today.year - value.year - (
        (today.month, today.day) <
        (value.month, value.day)
    )

    if not 18 <= age <= 65:
        raise ValueError(
            "Employee age must be between 18 and 65 years"
        )

    return value

def validate_employee_joining_date(value: date | None,) -> date | None:

    if value is None:
        return value

    today = date.today()

    if not 2000 <= value.year <= 2026:
        raise ValueError(
            "Joining year must be between 2000 and 2026"
        )

    if value > today:
        raise ValueError(
            "Joining date cannot be in the future"
        )

    return value

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

    
class EmployeeCreate(EmployeeBase):

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        return validate_employee_age(value)

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date( cls,value: date | None,) -> date | None:
        return validate_employee_joining_date(value)



class EmployeeUpdate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field( default=None, **FULL_NAME )

    email: EmailStr | None = Field( default=None, **EMAIL )

    phone: str | None = Field( default=None, **PHONE )

    department: str | None = Field( default=None, **DEPARTMENT )

    role: str | None = Field( default=None, **ROLE )

    date_of_birth: date | None = None
    
    joining_date: date | None = None

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
        return validate_employee_age(value)

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date( cls,value: date | None,) -> date | None:
        return validate_employee_joining_date(value)


class EmployeeResponse(EmployeeBase):

    employee_id: int
    is_active: bool
    created_at: datetime
    modified_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
