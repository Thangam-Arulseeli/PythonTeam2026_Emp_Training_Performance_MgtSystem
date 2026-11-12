from datetime import date, datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

from app.schemas.trainer_resume import TrainerResumeResponse

SpecializationType = Annotated[
    str,
    StringConstraints(min_length=1, max_length=10),
]


class TrainerCreate(BaseModel):
    trainer_name: str = Field(min_length=2, max_length=100)

    dob: date

    experience: int = Field(ge=0)

    joining_date: date

    specialization: list[SpecializationType] = Field(min_length=1)

    qualification: str = Field(min_length=2, max_length=150)

    email: EmailStr

    phone_number: str = Field(min_length=10, max_length=15)

    address: str = Field(min_length=5)

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class TrainerUpdate(BaseModel):
    trainer_name: str | None = Field(default=None, min_length=2, max_length=100)

    dob: date | None = None

    experience: int | None = Field(default=None, ge=0)

    joining_date: date | None = None

    specialization: list[SpecializationType] | None = Field(
        default=None,
        min_length=1,
    )

    qualification: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=15,
    )

    address: str | None = Field(default=None, min_length=5)

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class TrainerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trainer_id: int
    trainer_name: str
    dob: date
    experience: int
    joining_date: date
    specialization: list[str]
    qualification: str
    email: str
    phone_number: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    resume: TrainerResumeResponse | None = None
