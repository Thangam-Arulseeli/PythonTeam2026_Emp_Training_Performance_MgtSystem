from datetime import date, datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    ValidatorFunctionWrapHandler,
    WrapValidator,
    field_validator,
)
from pydantic_core import PydanticCustomError

FULL_NAME = {"min_length": 1, "max_length": 50}

EMAIL = {"max_length": 300}

DEPARTMENT = {"min_length": 1, "max_length": 30}


def validate_phone(value: object, handler: ValidatorFunctionWrapHandler) -> str:
    try:
        return handler(value)
    except ValidationError as exc:
        if exc.errors()[0]["type"] == "string_pattern_mismatch":
            raise PydanticCustomError(
                "string_pattern_mismatch",
                "Phone number must be 10 digits and start with 6",
            ) from exc
        raise


EmployeePhone = Annotated[
    str, Field(pattern=r"^6[0-9]{9}$"), WrapValidator(validate_phone)
]


def validate_employee_age(value: date | None) -> date | None:
    if value is None:
        return value

    today = date.today()

    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )

    if not 18 <= age <= 65:
        raise ValueError("Employee age must be between 18 and 65 years")

    return value


def validate_employee_joining_date(
    value: date | None,
) -> date | None:

    if value is None:
        return value

    today = date.today()

    if not 2000 <= value.year <= 2026:
        raise ValueError("Joining year must be between 2000 and 2026")

    if value > today:
        raise ValueError("Joining date cannot be in the future")

    return value


class EmployeeBase(BaseModel):
    full_name: str = Field(**FULL_NAME)

    email: EmailStr = Field(**EMAIL)

    department: str = Field(default="Unassigned", **DEPARTMENT)

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
    phone: EmployeePhone | None = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        return validate_employee_age(value)

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(
        cls,
        value: date | None,
    ) -> date | None:
        return validate_employee_joining_date(value)


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, **FULL_NAME)

    email: EmailStr | None = Field(default=None, **EMAIL)

    phone: EmployeePhone | None = None

    department: str | None = Field(default=None, **DEPARTMENT)

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
    def validate_joining_date(
        cls,
        value: date | None,
    ) -> date | None:
        return validate_employee_joining_date(value)


class EmployeeResponse(EmployeeBase):
    phone: str | None = Field(default=None, pattern=r"^[0-9]{10}$")
    role: str
    employee_id: int
    is_active: bool
    created_at: datetime
    modified_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value.strip().lower() != "employee":
            raise ValueError("Role must be employee")

        return "employee"
